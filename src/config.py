"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # General
    app_name: str = "Quant Smart Money Tracker"
    environment: str = "development"
    log_level: str = "INFO"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_positions: str = "trader.positions"
    kafka_topic_leaderboard: str = "trader.leaderboard"
    kafka_topic_signals: str = "signals.generated"

    # ClickHouse
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_db: str = "quant_smart_money"
    clickhouse_user: str = "default"
    clickhouse_password: str = "quant_password"

    # Exchanges (API keys should be in .env)
    binance_api_key: Optional[str] = None
    binance_api_secret: Optional[str] = None
    okx_api_key: Optional[str] = None
    okx_api_secret: Optional[str] = None
    okx_passphrase: Optional[str] = None
    bybit_api_key: Optional[str] = None
    bybit_api_secret: Optional[str] = None

    # Safety
    enable_shadow_mode: bool = True
    max_concurrent_signals: int = 5
    circuit_breaker_threshold: int = 10  # signals in short window

    # AI
    trust_score_threshold: float = 0.55
    anomaly_threshold: float = 0.4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
