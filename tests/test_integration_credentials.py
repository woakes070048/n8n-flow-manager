"""Integration tests for Credential API."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from n8n_manager.api.credentials import CredentialAPI
from n8n_manager.exceptions import N8NNotFoundError
from n8n_manager.models.credential import Credential


@pytest.fixture
def mock_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def credential_api(mock_client):
    """Create CredentialAPI instance with mock client."""
    return CredentialAPI(mock_client)


@pytest.mark.asyncio
async def test_list_credentials(credential_api, mock_client):
    """Test listing credentials."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"id": "1", "name": "Test Cred", "type": "httpBasicAuth"}]
    }
    mock_client.get.return_value = mock_response

    credentials = await credential_api.list()

    assert len(credentials) == 1
    assert credentials[0].name == "Test Cred"


@pytest.mark.asyncio
async def test_list_credentials_with_type(credential_api, mock_client):
    """Test listing credentials filtered by type."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}
    mock_client.get.return_value = mock_response

    await credential_api.list(credential_type="httpBasicAuth")

    mock_client.get.assert_called_once_with("/credentials", params={"type": "httpBasicAuth"})


@pytest.mark.asyncio
async def test_get_credential(credential_api, mock_client):
    """Test getting a specific credential."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "1",
        "name": "My Cred",
        "type": "httpBasicAuth",
    }
    mock_client.get.return_value = mock_response

    credential = await credential_api.get("1")

    assert credential.id == "1"
    assert credential.name == "My Cred"


@pytest.mark.asyncio
async def test_get_credential_not_found(credential_api, mock_client):
    """Test getting non-existent credential."""
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404, content=b"", json=lambda: {}),
    )

    with pytest.raises(N8NNotFoundError, match="Credential 999 not found"):
        await credential_api.get("999")


@pytest.mark.asyncio
async def test_create_credential(credential_api, mock_client):
    """Test creating a credential."""
    credential = Credential(name="New Cred", type="httpBasicAuth", data={"username": "test"})

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "new1",
        "name": "New Cred",
        "type": "httpBasicAuth",
    }
    mock_client.post.return_value = mock_response

    created = await credential_api.create(credential)

    assert created.id == "new1"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_update_credential(credential_api, mock_client):
    """Test updating a credential."""
    credential = Credential(name="Updated", type="httpBasicAuth")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "1",
        "name": "Updated",
        "type": "httpBasicAuth",
    }
    mock_client.patch.return_value = mock_response

    updated = await credential_api.update("1", credential)

    assert updated.name == "Updated"


@pytest.mark.asyncio
async def test_delete_credential(credential_api, mock_client):
    """Test deleting a credential."""
    mock_response = MagicMock()
    mock_client.delete.return_value = mock_response

    result = await credential_api.delete("1")

    assert result is True
    mock_client.delete.assert_called_once_with("/credentials/1")
