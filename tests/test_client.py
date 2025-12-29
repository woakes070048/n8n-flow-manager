"""Tests for N8NClient."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest
from n8n_manager import N8NClient
from n8n_manager.exceptions import N8NAPIError, N8NAuthError


def test_client_initialization_with_params():
    """Test client initialization with explicit parameters."""
    client = N8NClient(api_key="test_key", base_url="https://n8n.example.com")

    assert client.api_key == "test_key"
    assert client.base_url == "https://n8n.example.com"
    assert "X-N8N-API-KEY" in client.headers


@patch("n8n_manager.client.load_dotenv")  # Prevent loading .env
@patch.dict("os.environ", {"N8N_BASE_URL": "https://n8n.example.com"}, clear=True)
def test_client_initialization_without_api_key(mock_dotenv):
    """Test that missing API key raises error."""
    with pytest.raises(N8NAuthError, match="API key is required"):
        N8NClient()


@patch("n8n_manager.client.load_dotenv")  # Prevent loading .env
@patch.dict("os.environ", {"N8N_API_KEY": "test_key"}, clear=True)
def test_client_initialization_without_base_url(mock_dotenv):
    """Test that missing base URL raises error."""
    with pytest.raises(N8NAuthError, match="Base URL is required"):
        N8NClient()


@patch.dict("os.environ", {"N8N_API_KEY": "env_key", "N8N_BASE_URL": "https://env.n8n.com"})
def test_client_initialization_from_env():
    """Test client initialization from environment variables."""
    client = N8NClient()

    assert client.api_key == "env_key"
    assert client.base_url == "https://env.n8n.com"


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client can be used as async context manager."""
    async with N8NClient(api_key="test", base_url="https://test.com") as client:
        assert isinstance(client, N8NClient)


@pytest.mark.asyncio
async def test_health_check_success():
    """Test successful health check."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    # Mock the workflows.list method
    client.workflows.list = AsyncMock(return_value=[])

    result = await client.health_check()
    assert result is True

    await client.close()


@pytest.mark.asyncio
async def test_health_check_failure():
    """Test failed health check."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    # Mock the workflows.list method to raise an exception
    client.workflows.list = AsyncMock(side_effect=httpx.ConnectError("Connection failed"))

    with pytest.raises(N8NAPIError, match="Health check failed"):
        await client.health_check()

    await client.close()


def test_client_api_modules_initialized():
    """Test that API modules are properly initialized."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    assert hasattr(client, "workflows")
    assert hasattr(client, "executions")
    assert hasattr(client, "credentials")

    assert client.workflows is not None
    assert client.executions is not None
    assert client.credentials is not None
