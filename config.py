from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GITHUB_TOKEN: str
    GITHUB_USERNAME: str
    STUDENT_SECRET: str = "secret123"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()