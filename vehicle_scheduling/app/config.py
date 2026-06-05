from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    
    api_key: str
    base_url: str = "http://4.224.186.213/evaluation-service"
    
    
    app_name: str = "Vehicle Maintenance Scheduler"
    debug: bool = False
    
    
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    
    request_timeout: int = 30
    max_tasks_limit: int = 10000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()