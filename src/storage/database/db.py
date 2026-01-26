import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
logger = logging.getLogger(__name__)

MAX_RETRY_TIME = 20  # 连接最大重试时间（秒）
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_db_url() -> str:
    """Build database URL from environment."""
    # 1. 首先嘗試從環境變量獲取
    url = os.getenv("PGDATABASE_URL") or ""
    if url and url != "":
        return url

    # 2. 本地開發模式：使用 SQLite（如果配置了本地數據庫文件）
    sqlite_db = os.getenv("LOCAL_DB_FILE", "bookstore.db")
    sqlite_path = os.path.join(os.getcwd(), sqlite_db)

    # 檢查是否為本地開發環境
    is_local_dev = os.getenv("COZE_PROJECT_ENV") == "LOCAL" or not os.getenv("COZE_WORKLOAD_IDENTITY_CLIENT_ID")

    if is_local_dev:
        logger.info(f"Local development mode detected, using SQLite: {sqlite_path}")
        return f"sqlite:///{sqlite_path}"

    # 3. 雲端環境：使用 Coze Workload Identity 獲取數據庫配置
    try:
        from coze_workload_identity import Client
        client = Client()
        env_vars = client.get_project_env_vars()
        client.close()
        for env_var in env_vars:
            if env_var.key == "PGDATABASE_URL":
                url = env_var.value.replace("'", "'\\''")
                return url
    except Exception as e:
        logger.warning(f"Error loading PGDATABASE_URL from Coze: {e}")
        logger.info(f"Falling back to SQLite: {sqlite_path}")
        # 失敗時使用本地 SQLite 作為後備
        return f"sqlite:///{sqlite_path}"

    logger.error("PGDATABASE_URL is not set")
    return f"sqlite:///{sqlite_path}"  # 最後的後備方案

_engine = None
_SessionLocal = None

def _create_engine_with_retry():
    url = get_db_url()
    if url is None or url == "":
        logger.error("PGDATABASE_URL is not set")
        raise ValueError("PGDATABASE_URL is not set")

    # 對於 SQLite，使用簡化的連接配置
    if url.startswith("sqlite"):
        size = 1
        overflow = 0
        recycle = 3600
        timeout = 30
        echo = True  # 本地開發時打印 SQL 語句
    else:
        size = 100
        overflow = 100
        recycle = 1800
        timeout = 30
        echo = False

    engine = create_engine(
        url,
        pool_size=size,
        max_overflow=overflow,
        pool_pre_ping=True,
        pool_recycle=recycle,
        pool_timeout=timeout,
        echo=echo
    )

    # 验证连接，带重试
    start_time = time.time()
    last_error = None
    while time.time() - start_time < MAX_RETRY_TIME:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database connection successful: {url}")
            return engine
        except OperationalError as e:
            last_error = e
            elapsed = time.time() - start_time
            logger.warning(f"Database connection failed, retrying... (elapsed: {elapsed:.1f}s)")
            time.sleep(min(1, MAX_RETRY_TIME - elapsed))
    logger.error(f"Database connection failed after {MAX_RETRY_TIME}s: {last_error}")
    raise last_error  # pyright: ignore [reportGeneralTypeIssues]

def get_engine():
    global _engine
    if _engine is None:
        _engine = _create_engine_with_retry()
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_session():
    return get_sessionmaker()()

__all__ = [
    "get_db_url",
    "get_engine",
    "get_sessionmaker",
    "get_session",
]
