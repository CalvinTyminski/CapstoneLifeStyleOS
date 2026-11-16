
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set the test database BEFORE importing application code.
TEST_DATABASE_URL = (
    "postgresql+psycopg://lifestyle:local_dev_only"
    "@localhost:5432/lifestyle_os_test"
)

# Never allow these fixtures to target the development database.
if not TEST_DATABASE_URL.endswith("/lifestyle_os_test"):
    raise RuntimeError("Unsafe test database configuration")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["JWT_SECRET_KEY"] = "test-only-secret-not-for-production"

from app.db.base import Base
import app.models  # Register SQLAlchemy models
from app.db.session import get_db
from app.main import app


engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # These tests are destructive to the dedicated TEST database.
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    if database_name != "lifestyle_os_test":
        raise RuntimeError("Refusing to use a non-test database")

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database(prepare_database):
    # Clear records between tests while preserving the schema.
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE users "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield


@pytest.fixture
def client(prepare_database):
    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
