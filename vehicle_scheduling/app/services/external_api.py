import httpx
import logging
from fastapi import HTTPException
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

async def fetch_vehicles():
    url = f"{settings.base_url}/vehicles"
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Fetching vehicles from {url}")
    
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data.get('vehicles', []))} vehicles")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching vehicles: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch vehicles: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching vehicles: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def fetch_depots():
    url = f"{settings.base_url}/depots"
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Fetching depots from {url}")
    
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched depots data")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching depots: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch depots: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching depots: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def fetch_tasks(depot_id: str):
    url = f"{settings.base_url}/depots/{depot_id}/tasks"
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Fetching tasks for depot {depot_id}")
    
    async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} tasks for depot {depot_id}")
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching tasks: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch tasks: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching tasks: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")