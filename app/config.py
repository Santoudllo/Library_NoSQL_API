from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://library_admin:LibraryMongo2026!@mongodb:27017/?authSource=admin"
    mongodb_database: str = "library"
    redis_url: str = "redis://:LibraryRedis2026!@redis:6379/0"
    cassandra_hosts: str = "cassandra"
    cassandra_keyspace: str = "library"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "LibraryNeo4j2026!"
    open_library_base_url: str = "https://openlibrary.org"
    open_library_user_agent: str = "LibraryNoSQLStudentProject/1.0 (educational use)"
    cache_ttl_seconds: int = 300
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
