import requests
from datetime import datetime
from typing import List, Dict
import heapq
from dataclasses import dataclass
from enum import Enum
from fastapi import FastAPI



class NotificationType(Enum):
    PLACEMENT = 3
    RESULT = 2
    EVENT = 1


@dataclass
class Notification:
    id: str
    notification_type: str
    message: str
    timestamp: datetime
    priority_score: float = 0.0
    
    def __lt__(self, other):
        return self.priority_score < other.priority_score


# Calculate priority score
def calculate_priority_score(
    notification_type: str,
    timestamp: datetime,
    type_weight: float = 0.6,
    recency_weight: float = 0.4
) -> float:
    try:
        type_score = NotificationType[notification_type.upper()].value
    except KeyError:
        type_score = 0
    
    normalized_type_score = type_score / 3.0
    
    hours_old = (datetime.now() - timestamp).total_seconds() / 3600
    recency_score = max(0, 1 - (hours_old / 168))
    
    final_score = (type_weight * normalized_type_score) + (recency_weight * recency_score)
    
    return round(final_score, 4)


# Parse API response
def parse_notifications(response_data: Dict) -> List[Notification]:
    notifications = []
    notification_list = response_data.get('notifications', [])
    
    for notif_data in notification_list:
        timestamp_str = notif_data.get('Timestamp', '')
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = datetime.now()
        
        notif = Notification(
            id=notif_data.get('ID', ''),
            notification_type=notif_data.get('Type', ''),
            message=notif_data.get('Message', ''),
            timestamp=timestamp
        )
        
        notif.priority_score = calculate_priority_score(
            notif.notification_type,
            notif.timestamp
        )
        
        notifications.append(notif)
    
    return notifications


# Priority Inbox Manager
class PriorityInbox:
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.heap: List[Notification] = []
        self.notification_ids = set()
    
    def add_notification(self, notification: Notification):
        if notification.id in self.notification_ids:
            return
        
        if len(self.heap) < self.max_size:
            heapq.heappush(self.heap, notification)
            self.notification_ids.add(notification.id)
        else:
            if notification.priority_score > self.heap[0].priority_score:
                removed = heapq.heapreplace(self.heap, notification)
                self.notification_ids.discard(removed.id)
                self.notification_ids.add(notification.id)
    
    def get_top_notifications(self) -> List[Notification]:
        return sorted(self.heap, key=lambda x: x.priority_score, reverse=True)


# Fetch and rank notifications
def get_priority_inbox_from_api(api_url: str, top_n: int = 10) -> List[Dict]:
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching notifications: {e}")
        return []
    
    notifications = parse_notifications(data)
    
    inbox = PriorityInbox(max_size=top_n)
    for notif in notifications:
        inbox.add_notification(notif)
    
    top_notifications = inbox.get_top_notifications()
    
    result = []
    for rank, notif in enumerate(top_notifications, 1):
        result.append({
            'rank': rank,
            'id': notif.id,
            'type': notif.notification_type,
            'message': notif.message,
            'timestamp': notif.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'priority_score': notif.priority_score,
            'age_hours': round((datetime.now() - notif.timestamp).total_seconds() / 3600, 1)
        })
    
    return result



app = FastAPI(title="Campus Notifications Priority Inbox")


@app.get("/")
async def root():
    return {
        "message": "Campus Notifications Priority Inbox API",
        "endpoints": {
            "priority_inbox": "/api/priority-inbox",
            "health": "/health"
        }
    }


@app.get("/api/priority-inbox")
async def get_priority_inbox(top_n: int = 10):
    API_URL = "http://4.224.186.213/evaluation-service/notifications"
    
    priority_notifications = get_priority_inbox_from_api(API_URL, top_n)
    
    return {
        "status": "success",
        "total_notifications": len(priority_notifications),
        "priority_inbox": priority_notifications
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Test function
def test_priority_inbox():
    print("="*80)
    print("Testing Priority Inbox System")
    print("="*80)
    print()
    
    API_URL = "http://4.224.186.213/evaluation-service/notifications"
    
    print(f"Fetching notifications from: {API_URL}")
    priority_notifications = get_priority_inbox_from_api(API_URL, top_n=10)
    
    if not priority_notifications:
        print("No notifications found or API error!")
        return
    
    print(f"\nFound {len(priority_notifications)} priority notifications:\n")
    
    for notif in priority_notifications:
        print(f"Rank #{notif['rank']}")
        print(f"  Type: {notif['type'].upper()}")
        print(f"  Message: {notif['message']}")
        print(f"  Priority Score: {notif['priority_score']}")
        print(f"  Timestamp: {notif['timestamp']}")
        print(f"  Age: {notif['age_hours']} hours")
        print()


if __name__ == "__main__":
    test_priority_inbox()