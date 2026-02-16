import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["APP_PASSWORD"] = "test_password"
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["TMDB_API_KEY"] = "test_tmdb_key"


@pytest.fixture(scope="function")
def client():
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    test_db_url = f"sqlite:///{db_path}"
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from database import Base, get_db
    Base.metadata.create_all(bind=engine)

    from main import app

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    os.unlink(db_path)


@pytest.fixture
def auth_headers(client):
    response = client.post("/api/login", json={"password": "test_password"})
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
