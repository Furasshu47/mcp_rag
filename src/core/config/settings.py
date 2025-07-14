import os
from dotenv import load_dotenv
from typing import List

class Settings:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        dotenv_path = os.path.join(BASE_DIR, '.env')
        load_dotenv(dotenv_path=dotenv_path)

        self.PROJECT_NAME: str = "Asbestos Register PDF Processor"
        self.PROJECT_DESCRIPTION: str = "API to extract structured asbestos register data from PDF files using Generative AI."
        self.PROJECT_VERSION: str = "1.0.0"
        self.API_V1_STR: str = "/v1"

        self.GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
        if not self.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        self.MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
        # if not self.MISTRAL_API_KEY:
        #     raise ValueError("MISTRAL_API_KEY environment variable not set.")

        self.LOG_DIR: str = os.path.join(BASE_DIR, "logging")
        self.LOG_FILE_PATH: str = os.path.join(self.LOG_DIR, "api_usage.log")
        #self.DATABASE_URL: str = f'sqlite:///{os.path.join(BASE_DIR, "api_usage.db")}'
        self.DATABASE_URI: str = os.getenv("MONGO_DB_URI")
        if not self.DATABASE_URI:
            raise ValueError("MONGO_DB_URI environment variable not set.")
        self.API_USAGE_LOG_LIMIT: int = 100 # Limit for retrieving API usage logs

        self.FLOOR_PLAN_PATH: str = 'src/services/extraction/floor plans'
        self.FLOOR_PLAN_PDF_PATH: str = 'src/services/extraction/floor plans pdf'
        self.IMAGE_PATH: str = 'src/services/extraction/images'

        self.R2_PUBLIC_ACCESS_KEY_ID: str = os.getenv("R2_PUBLIC_ACCESS_KEY_ID")
        if not self.R2_PUBLIC_ACCESS_KEY_ID:
            raise ValueError("R2_PUBLIC_ACCESS_KEY_ID environment variable not set.")
        self.R2_PUBLIC_SECRET_ACCESS_KEY: str = os.getenv("R2_PUBLIC_SECRET_ACCESS_KEY")
        if not self.R2_PUBLIC_SECRET_ACCESS_KEY:
            raise ValueError("R2_PUBLIC_SECRET_ACCESS_KEY environment variable not set.")

        self.R2_PUBLIC_BUCKET='rexolve-ai-test'
        self.R2_PUBLIC_ENDPOINT='https://e27b72d07e0a1beed7a1c690519bf19c.r2.cloudflarestorage.com'
        self.R2_PUBLIC_VIEW_ENDPOINT='https://pub-a8e24de4735647df88f75c49481cc6e7.r2.dev'

        self.DAILY_API_CALL_LIMIT: int = 100
        self.API_RATE_LIMIT: str = '2/second'
        self.API_RATE_LIMIT_ACTIVE: bool = True
        self.TRACKED_ENDPOINTS: List[str] = [ # Moved to settings for easy config
            "/v1/extract/extract-asbestos-data/",
            "/v1/extract/count-buildings/",
            "/v1/extract/extract-floorplans/"
        ]


settings = Settings()