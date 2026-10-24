
from fastapi.testclient import TestClient
from backend.app.auth.security import create_access_token
from backend.app.documents import routes as document_routes

from backend.app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_document_list_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/documents")

    assert response.status_code == 401
from backend.app.auth.security import create_access_token


def test_other_user_cannot_download_document_without_permission(
    client, test_users, test_document
):
    _, other_user = test_users

    token = create_access_token(
        user_id=other_user.id,
        role=other_user.role,
    )

    response = client.get(
        f"/documents/{test_document.id}/download",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404

def test_owner_can_download_document(
    client, test_users, test_document, tmp_path, monkeypatch
):
    owner, _ = test_users

    # Create a real test file in temporary storage.
    storage_dir = tmp_path / "private_storage"
    storage_dir.mkdir()
    file_path = storage_dir / test_document.stored_filename
    file_path.write_text("TrustVault test", encoding="utf-8")

    # Point the route at temporary storage, not real project files.
    monkeypatch.setattr(document_routes, "STORAGE_DIR", storage_dir)

    token = create_access_token(
        user_id=owner.id,
        role=owner.role,
    )

    response = client.get(
        f"/documents/{test_document.id}/download",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.content == b"TrustVault test"