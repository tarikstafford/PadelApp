from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.security import create_access_token
from app.models import User, UserRole
import io

client = TestClient(app)

def test_upload_profile_picture_success(mocker):
    # Mock the get_current_active_user dependency
    mock_user = User(id=1, email="test@example.com", role=UserRole.PLAYER, is_active=True)
    mocker.patch("app.core.security.get_current_active_user", return_value=mock_user)

    # Mock the file_service.save_profile_picture function
    mocker.patch("app.services.file_service.save_profile_picture", return_value="http://cloudinary.com/image.jpg")

    # Mock the user_crud.update_user function
    mocker.patch("app.crud.user_crud.update_user", return_value=mock_user)

    token = create_access_token(subject=mock_user.email)
    headers = {"Authorization": f"Bearer {token}"}

    # Create a dummy file
    file_content = b"fake image data"
    file = io.BytesIO(file_content)
    file.name = "test.jpg"
    
    response = client.post(
        "/api/v1/auth/users/me/profile-picture",
        headers=headers,
        files={"file": (file.name, file, "image/jpeg")}
    )

    assert response.status_code == 200
    assert response.json()["profile_picture_url"] == "http://cloudinary.com/image.jpg"

def test_upload_profile_picture_invalid_file_type(mocker):
    mock_user = User(id=1, email="test@example.com", role=UserRole.PLAYER, is_active=True)
    mocker.patch("app.core.security.get_current_active_user", return_value=mock_user)

    token = create_access_token(subject=mock_user.email)
    headers = {"Authorization": f"Bearer {token}"}

    file_content = b"fake file data"
    file = io.BytesIO(file_content)
    file.name = "test.txt"

    response = client.post(
        "/api/v1/auth/users/me/profile-picture",
        headers=headers,
        files={"file": (file.name, file, "text/plain")}
    )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"] 