import time
from pymongo import MongoClient
from redis import Redis
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from neo4j import GraphDatabase
from app.config import settings

mongo_client = mongo_db = redis_client = cassandra_cluster = cassandra_session = neo4j_driver = None

def get_mongo(): return mongo_db
def get_redis(): return redis_client
def get_cassandra(): return cassandra_session
def get_neo4j(): return neo4j_driver

def initialize_connections():
    global mongo_client, mongo_db, redis_client, cassandra_cluster, cassandra_session, neo4j_driver
    mongo_client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")
    mongo_db = mongo_client[settings.mongodb_database]
    mongo_db.books.create_index("openlibrary_key", unique=True, sparse=True)
    mongo_db.books.create_index("title")
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    redis_client.ping()

    hosts = [x.strip() for x in settings.cassandra_hosts.split(",") if x.strip()]
    last_error = None
    for _ in range(36):
        try:
            cassandra_cluster = Cluster(hosts)
            session = cassandra_cluster.connect()
            session.execute(
                f"CREATE KEYSPACE IF NOT EXISTS {settings.cassandra_keyspace} "
                "WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}"
            )
            session.set_keyspace(settings.cassandra_keyspace)
            session.row_factory = dict_factory
            session.execute('''
                CREATE TABLE IF NOT EXISTS user_history (
                    user_id text, event_time timestamp, book_key text,
                    action text, title text,
                    PRIMARY KEY ((user_id), event_time, book_key)
                ) WITH CLUSTERING ORDER BY (event_time DESC)
            ''')
            cassandra_session = session
            last_error = None
            break
        except Exception as exc:
            last_error = exc
            if cassandra_cluster:
                try: cassandra_cluster.shutdown()
                except Exception: pass
            cassandra_cluster = None
            time.sleep(5)
    if last_error:
        raise RuntimeError(f"Impossible d'initialiser Cassandra : {last_error}")

    neo4j_driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_username, settings.neo4j_password))
    neo4j_driver.verify_connectivity()

def close_connections():
    if mongo_client: mongo_client.close()
    if redis_client: redis_client.close()
    if cassandra_cluster: cassandra_cluster.shutdown()
    if neo4j_driver: neo4j_driver.close()
