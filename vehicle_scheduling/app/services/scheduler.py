from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)

def optimize_schedule(tasks: List[Dict], max_hours: float) -> Tuple[List[Dict], int]:
    """
    Optimized 0/1 Knapsack using Dynamic Programming
    """
    n = len(tasks)
    
    logger.info(f"Optimizing schedule for {n} tasks with {max_hours} hours capacity")
    
    if n == 0:
        logger.warning("No tasks to schedule")
        return [], 0
    
    if max_hours <= 0:
        logger.warning("Invalid max_hours value")
        return [], 0
    
    # Convert to integer capacity
    capacity = int(max_hours * 10)
    
    # Create DP table
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        task_time = int(tasks[i-1]["Duration"] * 10)
        task_score = tasks[i-1]["Impact"]
        
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]
            
            if task_time <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - task_time] + task_score)
    
    # Backtrack to find selected tasks
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(tasks[i-1])
            w -= int(tasks[i-1]["Duration"] * 10)
    
    total_score = dp[n][capacity]
    
    logger.info(f"Schedule optimized: {len(selected)} tasks selected, total score: {total_score}")
    
    return selected, total_score