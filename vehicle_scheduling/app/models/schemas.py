from pydantic import BaseModel
from typing import List

class Vehicle(BaseModel):
    TaskID: str
    Duration: float
    Impact: int

class VehiclesResponse(BaseModel):
    total_vehicles: int
    vehicles: List[Vehicle]

class Depot(BaseModel):
    ID: str
    MechanicHours: float

class Task(BaseModel):
    TaskID: str
    Duration: float
    Impact: int

class ScheduleResponse(BaseModel):
    depot_id: str
    max_hours: float
    scheduled_tasks: List[Task]
    total_score: int
    total_time_used: float
    tasks_count: int