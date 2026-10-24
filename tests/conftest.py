from backend.app.auth.security import hash_password
from backend.app.models.database import User, Document
from backend.app.models.database import Base, User, Document
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.dependencies import get_db
from backend.app.models.database import Base


@pytest.fixture
def test_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

from backend.app.auth.security import hash_password
from backend.app.models.database import User, Document


@pytest.fixture
def test_users(test_db):
    owner = User(
        email="owner-test@example.com",
        password_hash=hash_password("Owner-Test-Password-123!"),
        role="viewer",
        is_active=True,
    )
    other_user = User(
        email="other-test@example.com",
        password_hash=hash_password("Other-Test-Password-123!"),
        role="viewer",
        is_active=True,
    )

    test_db.add_all([owner, other_user])
    test_db.commit()
    test_db.refresh(owner)
    test_db.refresh(other_user)

    return owner, other_user


@pytest.fixture
def test_document(test_db, test_users):
    owner, _ = test_users

    document = Document(
        owner_id=owner.id,
        title="Test document",
        stored_filename="test-document-fixture.bin",
        content_type="text/plain",
        size_bytes=12,
    )

    test_db.add(document)
    test_db.commit()
    test_db.refresh(document)

    return document	

@pytest.fixture
def test_users(test_db):
    owner = User(
        email="owner-test@example.com",
        password_hash=hash_password("Owner-Test-Password-123!"),
        role="viewer",
        is_active=True,
    )

    other_user = User(
        email="other-test@example.com",
        password_hash=hash_password("Other-Test-Password-123!"),
        role="viewer",
        is_active=True,
    )

    test_db.add_all([owner, other_user])
    test_db.commit()

    test_db.refresh(owner)
    test_db.refresh(other_user)

    return owner, other_user


@pytest.fixture
def test_document(test_db, test_users):
    owner, _ = test_users

    document = Document(
        owner_id=owner.id,
        title="Test document",
        stored_filename="test-document-fixture.bin",
        content_type="text/plain",
        size_bytes=12,
    )

    test_db.add(document)
    test_db.commit()
    test_db.refresh(document)

    return document
