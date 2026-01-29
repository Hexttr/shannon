from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./shannon.db"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Claude API
    anthropic_api_key: str
    
    # SSH Server
    ssh_host: str
    ssh_user: str
    ssh_password: str
    ssh_port: int = 22
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Logging
    log_level: str = "INFO"
    
    # Brute Force Protection
    brute_force_max_attempts: int = 5
    brute_force_lockout_time_minutes: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


