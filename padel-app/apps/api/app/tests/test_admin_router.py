from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.security import create_access_token
from app.models import User, UserRole, Club
import io

client = TestClient(app)

def test_upload_club_picture_success(mocker):
    # Mock the get_current_active_user dependency
    mock_user = User(id=1, email="test@example.com", role=UserRole.CLUB_ADMIN, is_active=True)
    mocker.patch("app.core.security.get_current_active_user", return_value=mock_user)

    # Mock the club_crud.get_club_by_owner_id function
    mock_club = Club(id=1, owner_id=1)
    mocker.patch("app.crud.club_crud.get_club_by_owner_id", return_value=mock_club)

    # Mock the file_service.save_club_picture function
    mocker.patch("app.services.file_service.save_club_picture", return_value="http://cloudinary.com/image.jpg")

    # Mock the club_crud.update_club function
    mocker.patch("app.crud.club_crud.update_club", return_value=mock_club)

    token = create_access_token(subject=mock_user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dummy file
    file_content = b"fake image data"
    file = io.BytesIO(file_content)
    file.name = "test.jpg"
    
    response = client.post(
        "/api/v1/admin/club/profile-picture",
        headers=headers,
        files={"file": (file.name, file, "image/jpeg")}
    )

    assert response.status_code == 200
    assert response.json()["image_url"] == "http://cloudinary.com/image.jpg"

def test_upload_club_picture_not_found(mocker):
    mock_user = User(id=1, email="test@example.com", role=UserRole.CLUB_ADMIN, is_active=True)
    mocker.patch("app.core.security.get_current_active_user", return_value=mock_user)

    mocker.patch("app.crud.club_crud.get_club_by_owner_id", return_value=None)

    token = create_access_token(subject=mock_user.email)
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"fake image data"
    file = io.BytesIO(file_content)
    file.name = "test.jpg"

    response = client.post(
        "/api/v1/admin/club/profile-picture",
        headers=headers,
        files={"file": (file.name, file, "image/jpeg")}
    )

    assert response.status_code == 404
    assert "Club not found" in response.json()["detail"] 