from typing import Generator

import pytest
from mock import patch, MagicMock


@pytest.fixture
def mock_google_cloud_storage() -> Generator:
    with patch("google.cloud.storage.Client") as mock_client:
        mock_bucket = MagicMock()
        mock_client.return_value.bucket.return_value = mock_bucket

        yield mock_client, mock_bucket
