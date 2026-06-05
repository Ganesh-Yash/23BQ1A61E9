from fastapi import APIRouter, HTTPException
import logging
from app.services.external_api import fetch_vehicles, fetch_depots, fetch_tasks
from app.services.scheduler import optimize_schedule
from app.models.schemas import VehiclesResponse, ScheduleResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Vehicle Maintenance Scheduler API",
        "status": "active",
        "version": "1.0.0",
        "endpoints": [
            "GET /vehicles - List all vehicles",
            "GET /vehicles/{task_id} - Get vehicle by TaskID",
            "GET /schedule/{depot_id} - Get optimal schedule for depot"
        ]
    }

@router.get("/vehicles", response_model=VehiclesResponse)
async def list_vehicles():
    try:
        logger.info("Listing all vehicles")
        vehicles_data = await fetch_vehicles()
        return {
            "total_vehicles": len(vehicles_data.get("vehicles", [])),
            "vehicles": vehicles_data.get("vehicles", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_vehicles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/vehicles/{task_id}")
async def get_vehicle_by_task(task_id: str):
    try:
        logger.info(f"Fetching vehicle with TaskID: {task_id}")
        vehicles_data = await fetch_vehicles()
        vehicles = vehicles_data.get("vehicles", [])
        
        vehicle = next((v for v in vehicles if v["TaskID"] == task_id), None)
        
        if not vehicle:
            logger.warning(f"Vehicle not found: {task_id}")
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        logger.info(f"Vehicle found: {task_id}")
        return vehicle
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_vehicle_by_task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/schedule/{depot_id}", response_model=ScheduleResponse)
async def create_schedule(depot_id: str):
    try:
        logger.info(f"Creating schedule for depot: {depot_id}")
        
        depots = await fetch_depots()
        depot = next((d for d in depots if str(d["ID"]) == depot_id), None)
        
        if not depot:
            logger.warning(f"Depot not found: {depot_id}")
            raise HTTPException(status_code=404, detail="Depot not found")
        
        tasks = await fetch_tasks(depot_id)
        max_hours = depot["MechanicHours"]
        
        logger.info(f"Processing {len(tasks)} tasks with {max_hours} hours capacity")
        
        selected_tasks, total_score = optimize_schedule(tasks, max_hours)
        total_time = sum(task["Duration"] for task in selected_tasks)
        
        logger.info(f"Schedule created: {len(selected_tasks)} tasks, score: {total_score}")
        
        return {
            "depot_id": depot_id,
            "max_hours": max_hours,
            "scheduled_tasks": selected_tasks,
            "total_score": total_score,
            "total_time_used": round(total_time, 2),
            "tasks_count": len(selected_tasks)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_schedule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")