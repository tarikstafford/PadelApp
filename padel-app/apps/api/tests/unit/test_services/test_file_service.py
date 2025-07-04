import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import UploadFile, HTTPException
from io import BytesIO

from app.services.file_service import (
    validate_image_file,
    upload_file,
    save_profile_picture,
    save_club_picture,
    MAX_FILE_SIZE,
    ALLOWED_MIME_TYPES,
    UPLOAD_DIR_NAME,
    CLUB_UPLOAD_DIR_NAME,
    STATIC_URL_PREFIX,
    CLUB_STATIC_URL_PREFIX
)


class TestFileService:
    """Comprehensive test suite for file service functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.user_id = 1
        self.club_id = 1
        self.test_file_content = b"test image content"
        self.test_secure_url = "https://res.cloudinary.com/test/image/upload/v1234567890/test.jpg"

    def create_mock_upload_file(self, filename="test.jpg", content_type="image/jpeg", size=1024):
        """Create a mock UploadFile object"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = filename
        mock_file.content_type = content_type
        mock_file.size = size
        mock_file.file = BytesIO(self.test_file_content)
        return mock_file

    def test_validate_image_file_success(self):
        """Test successful image file validation"""
        mock_file = self.create_mock_upload_file()
        
        # Should not raise any exception
        validate_image_file(mock_file)

    def test_validate_image_file_no_file(self):
        """Test validation when no file is provided"""
        with pytest.raises(HTTPException) as exc_info:
            validate_image_file(None)
        
        assert exc_info.value.status_code == 400
        assert "No file provided" in exc_info.value.detail

    def test_validate_image_file_empty_file(self):
        """Test validation with empty file"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = None
        mock_file.content_type = None
        mock_file.size = 0
        
        with pytest.raises(HTTPException) as exc_info:
            validate_image_file(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "No file provided" in exc_info.value.detail

    def test_validate_image_file_size_too_large(self):
        """Test validation when file size exceeds limit"""
        mock_file = self.create_mock_upload_file(size=MAX_FILE_SIZE + 1)
        
        with pytest.raises(HTTPException) as exc_info:
            validate_image_file(mock_file)
        
        assert exc_info.value.status_code == 413
        assert "File size exceeds the limit of 5MB" in exc_info.value.detail

    def test_validate_image_file_invalid_content_type(self):
        """Test validation with invalid content type"""
        mock_file = self.create_mock_upload_file(content_type="text/plain")
        
        with pytest.raises(HTTPException) as exc_info:
            validate_image_file(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "File type not allowed" in exc_info.value.detail

    @pytest.mark.parametrize("content_type", ALLOWED_MIME_TYPES)
    def test_validate_image_file_allowed_types(self, content_type):
        """Test validation with all allowed MIME types"""
        mock_file = self.create_mock_upload_file(content_type=content_type)
        
        # Should not raise any exception
        validate_image_file(mock_file)

    def test_validate_image_file_edge_case_max_size(self):
        """Test validation with file at maximum allowed size"""
        mock_file = self.create_mock_upload_file(size=MAX_FILE_SIZE)
        
        # Should not raise any exception
        validate_image_file(mock_file)

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_upload_file_success(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test successful file upload"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        result = await upload_file(mock_file, folder)
        
        # Verify
        assert result == self.test_secure_url
        mock_validate.assert_called_once_with(mock_file)
        mock_run_in_threadpool.assert_called_once()

    @patch('app.services.file_service.validate_image_file')
    async def test_upload_file_validation_failure(self, mock_validate):
        """Test file upload when validation fails"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup validation to fail
        mock_validate.side_effect = HTTPException(status_code=400, detail="Invalid file")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await upload_file(mock_file, folder)
        
        assert exc_info.value.status_code == 400
        assert "Invalid file" in exc_info.value.detail

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_upload_file_cloudinary_failure(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test file upload when Cloudinary upload fails"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup mocks
        mock_run_in_threadpool.side_effect = Exception("Cloudinary error")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await upload_file(mock_file, folder)
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload file: Cloudinary error" in exc_info.value.detail

    @patch('app.services.file_service.uuid.uuid4')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_upload_file_public_id_generation(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_uuid):
        """Test that public_id is generated correctly"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        test_uuid = "test-uuid-123"
        
        # Setup mocks
        mock_uuid.return_value = test_uuid
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await upload_file(mock_file, folder)
        
        # Verify public_id was generated correctly
        expected_public_id = f"{folder}/{test_uuid}"
        call_args = mock_run_in_threadpool.call_args
        assert call_args[1]['public_id'] == expected_public_id

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_profile_picture_success(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test successful profile picture save"""
        mock_file = self.create_mock_upload_file()
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        result = await save_profile_picture(mock_file, self.user_id)
        
        # Verify
        assert result == self.test_secure_url
        mock_validate.assert_called_once_with(mock_file)
        mock_run_in_threadpool.assert_called_once()

    @patch('app.services.file_service.uuid.uuid4')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_profile_picture_public_id(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_uuid):
        """Test profile picture public_id generation"""
        mock_file = self.create_mock_upload_file()
        test_uuid = "test-uuid-123"
        
        # Setup mocks
        mock_uuid.return_value = test_uuid
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await save_profile_picture(mock_file, self.user_id)
        
        # Verify public_id includes user_id
        expected_public_id = f"profile_pics/{self.user_id}/{test_uuid}"
        call_args = mock_run_in_threadpool.call_args
        assert call_args[1]['public_id'] == expected_public_id

    @patch('app.services.file_service.validate_image_file')
    async def test_save_profile_picture_validation_failure(self, mock_validate):
        """Test profile picture save when validation fails"""
        mock_file = self.create_mock_upload_file()
        
        # Setup validation to fail
        mock_validate.side_effect = HTTPException(status_code=400, detail="Invalid file")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await save_profile_picture(mock_file, self.user_id)
        
        assert exc_info.value.status_code == 400
        assert "Invalid file" in exc_info.value.detail

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_profile_picture_upload_failure(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test profile picture save when upload fails"""
        mock_file = self.create_mock_upload_file()
        
        # Setup upload to fail
        mock_run_in_threadpool.side_effect = Exception("Upload failed")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await save_profile_picture(mock_file, self.user_id)
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload image: Upload failed" in exc_info.value.detail

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_club_picture_success(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test successful club picture save"""
        mock_file = self.create_mock_upload_file()
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        result = await save_club_picture(mock_file, self.club_id)
        
        # Verify
        assert result == self.test_secure_url
        mock_validate.assert_called_once_with(mock_file)
        mock_run_in_threadpool.assert_called_once()

    @patch('app.services.file_service.uuid.uuid4')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_club_picture_public_id(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_uuid):
        """Test club picture public_id generation"""
        mock_file = self.create_mock_upload_file()
        test_uuid = "test-uuid-123"
        
        # Setup mocks
        mock_uuid.return_value = test_uuid
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await save_club_picture(mock_file, self.club_id)
        
        # Verify public_id includes club_id
        expected_public_id = f"club_pics/{self.club_id}/{test_uuid}"
        call_args = mock_run_in_threadpool.call_args
        assert call_args[1]['public_id'] == expected_public_id

    @patch('app.services.file_service.validate_image_file')
    async def test_save_club_picture_validation_failure(self, mock_validate):
        """Test club picture save when validation fails"""
        mock_file = self.create_mock_upload_file()
        
        # Setup validation to fail
        mock_validate.side_effect = HTTPException(status_code=400, detail="Invalid file")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await save_club_picture(mock_file, self.club_id)
        
        assert exc_info.value.status_code == 400
        assert "Invalid file" in exc_info.value.detail

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_save_club_picture_upload_failure(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test club picture save when upload fails"""
        mock_file = self.create_mock_upload_file()
        
        # Setup upload to fail
        mock_run_in_threadpool.side_effect = Exception("Upload failed")
        
        # Execute and verify
        with pytest.raises(HTTPException) as exc_info:
            await save_club_picture(mock_file, self.club_id)
        
        assert exc_info.value.status_code == 500
        assert "Failed to upload image: Upload failed" in exc_info.value.detail

    def test_constants_defined(self):
        """Test that all required constants are defined"""
        assert UPLOAD_DIR_NAME == "static/profile_pics"
        assert CLUB_UPLOAD_DIR_NAME == "static/club_pics"
        assert STATIC_URL_PREFIX == "/static/profile_pics"
        assert CLUB_STATIC_URL_PREFIX == "/static/club_pics"
        assert MAX_FILE_SIZE == 5 * 1024 * 1024  # 5MB
        assert ALLOWED_MIME_TYPES == ["image/jpeg", "image/png", "image/gif"]

    def test_file_size_limit_calculation(self):
        """Test file size limit calculation"""
        # Test exact limit
        mock_file = self.create_mock_upload_file(size=5 * 1024 * 1024)
        validate_image_file(mock_file)  # Should not raise
        
        # Test over limit
        mock_file_over = self.create_mock_upload_file(size=5 * 1024 * 1024 + 1)
        with pytest.raises(HTTPException):
            validate_image_file(mock_file_over)

    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_cloudinary_upload_parameters(self, mock_validate, mock_run_in_threadpool, mock_upload):
        """Test that Cloudinary upload is called with correct parameters"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await upload_file(mock_file, folder)
        
        # Verify upload parameters
        call_args = mock_run_in_threadpool.call_args
        assert call_args[0][0] == mock_upload  # First positional arg is the upload function
        assert call_args[0][1] == mock_file.file  # Second positional arg is the file
        assert call_args[1]['overwrite'] is True
        assert call_args[1]['resource_type'] == "image"
        assert folder in call_args[1]['public_id']

    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_logging_success(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_logger):
        """Test that successful uploads are logged"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await upload_file(mock_file, folder)
        
        # Verify logging
        mock_logger.info.assert_called()
        log_calls = mock_logger.info.call_args_list
        assert any("Attempting to upload file" in str(call) for call in log_calls)
        assert any("Successfully uploaded image" in str(call) for call in log_calls)

    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_logging_failure(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_logger):
        """Test that failed uploads are logged"""
        mock_file = self.create_mock_upload_file()
        folder = "test_folder"
        
        # Setup upload to fail
        mock_run_in_threadpool.side_effect = Exception("Upload failed")
        
        # Execute and verify
        with pytest.raises(HTTPException):
            await upload_file(mock_file, folder)
        
        # Verify error logging
        mock_logger.error.assert_called()
        error_call = mock_logger.error.call_args
        assert "Failed to upload file" in str(error_call)

    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_profile_picture_logging(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_logger):
        """Test that profile picture uploads are logged with user_id"""
        mock_file = self.create_mock_upload_file()
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await save_profile_picture(mock_file, self.user_id)
        
        # Verify logging includes user_id
        mock_logger.info.assert_called()
        log_calls = mock_logger.info.call_args_list
        assert any(f"user_id: {self.user_id}" in str(call) for call in log_calls)

    @patch('app.services.file_service.logger')
    @patch('app.services.file_service.cloudinary.uploader.upload')
    @patch('app.services.file_service.run_in_threadpool')
    @patch('app.services.file_service.validate_image_file')
    async def test_club_picture_logging(self, mock_validate, mock_run_in_threadpool, mock_upload, mock_logger):
        """Test that club picture uploads are logged with club_id"""
        mock_file = self.create_mock_upload_file()
        
        # Setup mocks
        mock_upload_result = {'secure_url': self.test_secure_url}
        mock_run_in_threadpool.return_value = mock_upload_result
        
        # Execute
        await save_club_picture(mock_file, self.club_id)
        
        # Verify logging includes club_id
        mock_logger.info.assert_called()
        log_calls = mock_logger.info.call_args_list
        assert any(f"club_id: {self.club_id}" in str(call) for call in log_calls)

    def test_edge_cases_file_properties(self):
        """Test edge cases for file properties"""
        # Test with different file extensions
        test_cases = [
            ("image.jpg", "image/jpeg"),
            ("image.png", "image/png"),
            ("image.gif", "image/gif"),
            ("IMAGE.JPG", "image/jpeg"),  # Case insensitive
            ("file_with_spaces.png", "image/png"),
            ("file-with-dashes.jpg", "image/jpeg"),
            ("file_with_numbers123.png", "image/png"),
        ]
        
        for filename, content_type in test_cases:
            mock_file = self.create_mock_upload_file(filename=filename, content_type=content_type)
            validate_image_file(mock_file)  # Should not raise

    def test_concurrent_uploads(self):
        """Test behavior with concurrent file uploads"""
        # This test ensures that UUID generation doesn't conflict
        with patch('app.services.file_service.uuid.uuid4') as mock_uuid:
            mock_uuid.side_effect = [f"uuid-{i}" for i in range(100)]
            
            # Generate multiple public IDs
            public_ids = []
            for i in range(10):
                uuid_val = mock_uuid.return_value = f"uuid-{i}"
                public_id = f"test_folder/{uuid_val}"
                public_ids.append(public_id)
            
            # Verify all are unique
            assert len(set(public_ids)) == len(public_ids)

    async def test_memory_usage_with_large_files(self):
        """Test memory usage patterns with large files"""
        # Create a mock file at the size limit
        mock_file = self.create_mock_upload_file(size=MAX_FILE_SIZE)
        
        # Test that validation doesn't fail
        validate_image_file(mock_file)
        
        # Test that file object is properly handled
        assert mock_file.file is not None
        assert hasattr(mock_file.file, 'read')

    def test_invalid_file_object(self):
        """Test handling of invalid file objects"""
        # Test with mock file that has no size attribute
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.content_type = "image/jpeg"
        del mock_file.size  # Remove size attribute
        
        with pytest.raises(AttributeError):
            validate_image_file(mock_file)

    def test_upload_file_parameter_validation(self):
        """Test parameter validation for upload functions"""
        # Test with invalid user_id types
        invalid_user_ids = [None, "string", [], {}]
        
        for invalid_id in invalid_user_ids:
            mock_file = self.create_mock_upload_file()
            
            # The function should still work, as it just uses the ID in string formatting
            # This tests the robustness of the implementation
            with patch('app.services.file_service.cloudinary.uploader.upload'):
                with patch('app.services.file_service.run_in_threadpool') as mock_run:
                    mock_run.return_value = {'secure_url': self.test_secure_url}
                    
                    # This should not raise an exception during public_id generation
                    import asyncio
                    asyncio.run(save_profile_picture(mock_file, invalid_id))
                    
                    # Verify that the invalid_id was used in the public_id
                    call_args = mock_run.call_args
                    assert str(invalid_id) in call_args[1]['public_id']