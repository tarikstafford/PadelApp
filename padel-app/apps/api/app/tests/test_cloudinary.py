import cloudinary


def test_cloudinary_config():
    """
    Tests that the Cloudinary SDK can be configured.
    Note: This test uses dummy credentials and does not connect to Cloudinary.
    Remember to set the actual credentials in your environment.
    """
    cloudinary.config(
        cloud_name="dummy_cloud_name",
        api_key="dummy_api_key",
        api_secret="dummy_api_secret",
        secure=True,
    )

    config = cloudinary.config()
    assert config.cloud_name == "dummy_cloud_name"
    assert config.api_key == "dummy_api_key"
    assert config.api_secret == "dummy_api_secret"
