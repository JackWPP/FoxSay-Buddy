from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # 运行
    environment: str = "local"
    log_level: str = "INFO"

    # 数据库
    database_url: str = "postgresql+asyncpg://foxsay:foxsay_dev@localhost:5432/foxsay"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_client_id: str = "foxsay-backend-bridge"
    mqtt_qos: int = 1

    # 对象存储（S3 兼容 / MinIO）
    s3_endpoint: str = "localhost:9000"
    s3_access_key: str = "foxsay"
    s3_secret_key: str = "foxsay_dev_password"
    s3_bucket: str = "foxsay-content"
    s3_secure: bool = False

    # 配对
    pairing_code_ttl_seconds: int = 600
    pairing_code_length: int = 6

    @property
    def s3_host(self) -> str:
        """MinIO client 只接受 host:port，去掉 scheme。"""
        return self.s3_endpoint.replace("http://", "").replace("https://", "")


settings = Settings()
