
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
def test_owner_can_grant_read_permission(
    client, test_users, test_document
):
    owner, other_user = test_users

    token = create_access_token(
        user_id=owner.id,
        role=owner.role,
    )

    response = client.put(
        f"/documents/{test_document.id}/permissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": other_user.id,
            "can_read": True,
            "can_edit": False,
        },
    )

    assert response.status_code == 200
    assert response.json()["can_read"] is True


def test_non_owner_cannot_grant_permission(
    client, test_users, test_document
):
    _, other_user = test_users

    token = create_access_token(
        user_id=other_user.id,
        role=other_user.role,
    )

    response = client.put(
        f"/documents/{test_document.id}/permissions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": other_user.id,
            "can_read": True,
            "can_edit": False,
        },
    )

    assert response.status_code == 404

def test_revoked_permission_blocks_download(
    client, test_users, test_document, tmp_path, monkeypatch
):
    from backend.app.documents import routes as document_routes
    from backend.app.models.database import DocumentPermission

    owner, other_user = test_users

    # Create a temporary file for the test document.
    storage_dir = tmp_path / "private_storage"
    storage_dir.mkdir()
    file_path = storage_dir / test_document.stored_filename
    file_path.write_text("TrustVault test", encoding="utf-8")
    monkeypatch.setattr(document_routes, "STORAGE_DIR", storage_dir)

    # Grant read permission.
    permission = DocumentPermission(
        document_id=test_document.id,
        user_id=other_user.id,
        can_read=True,
        can_edit=False,
    )
    client.app.dependency_overrides
    from backend.app.db.dependencies import get_db
    db = next(client.app.dependency_overrides[get_db]())
    db.add(permission)
    db.commit()

    # Revoke permission as the document owner.
    owner_token = create_access_token(
        user_id=owner.id,
        role=owner.role,
    )
    revoke_response = client.delete(
        f"/documents/{test_document.id}/permissions/{other_user.id}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert revoke_response.status_code == 204

    # Verify the other user can no longer download it.
    other_token = create_access_token(
        user_id=other_user.id,
        role=other_user.role,
    )
    download_response = client.get(
        f"/documents/{test_document.id}/download",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert download_response.status_code == 404

def test_inactive_user_cannot_access_documents(
    client, test_db, test_users
):
    from backend.app.auth.security import create_access_token

    _, other_user = test_users
    other_user.is_active = False
    test_db.commit()

    token = create_access_token(
        user_id=other_user.id,
        role=other_user.role,
    )

    response = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
