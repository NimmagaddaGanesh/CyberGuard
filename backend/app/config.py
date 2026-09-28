import os

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "CyberGuard API Engine")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Hindsight Settings
    HINDSIGHT_API_KEY: str = os.getenv("HINDSIGHT_API_KEY", "")
    HINDSIGHT_BASE_URL: str = os.getenv("HINDSIGHT_BASE_URL", "https://ui.hindsight.vectorize.io/api/v1")

    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Bayesian Scoring Weights
    WEIGHT_SEMANTIC: float = float(os.getenv("WEIGHT_SEMANTIC", "0.40"))
    WEIGHT_EMPIRICAL: float = float(os.getenv("WEIGHT_EMPIRICAL", "0.60"))

settings = Settings()
