"""Complete coverage tests for client module."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from n8n_manager import N8NClient
from n8n_manager.exceptions import N8NAPIError, N8NAuthError, N8NRateLimitError


@pytest.mark.asyncio
async def test_handle_response_401_error():
    """Test that 401 errors raise N8NAuthError."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    # Create mock response
    mock_response = MagicMock()
    mock_response.status_code = 401

    # Call the error handler
    with pytest.raises(N8NAuthError, match="Authentication failed"):
        await client._handle_response_errors(mock_response)

    await client.close()


@pytest.mark.asyncio
async def test_handle_response_429_error():
    """Test that 429 errors raise N8NRateLimitError."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    # Create mock response with Retry-After header
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}

    # Call the error handler
    with pytest.raises(N8NRateLimitError) as exc_info:
        await client._handle_response_errors(mock_response)

    assert exc_info.value.retry_after == 60

    await client.close()


@pytest.mark.asyncio
async def test_handle_response_429_without_retry_after():
    """Test 429 error without Retry-After header."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    with pytest.raises(N8NRateLimitError) as exc_info:
        await client._handle_response_errors(mock_response)

    assert exc_info.value.retry_after is None

    await client.close()


@pytest.mark.asyncio
async def test_handle_response_500_error():
    """Test that 500+ errors raise N8NAPIError."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b'{"error": "server error"}'
    mock_response.json.return_value = {"error": "server error"}

    with pytest.raises(N8NAPIError, match="n8n server error: 500"):
        await client._handle_response_errors(mock_response)

    await client.close()


@pytest.mark.asyncio
async def test_handle_response_503_error():
    """Test that 503 errors raise N8NAPIError."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    mock_response = MagicMock()
    mock_response.status_code = 503
    mock_response.content = b""
    mock_response.json.side_effect = Exception("No JSON")

    with pytest.raises(N8NAPIError, match="n8n server error: 503"):
        await client._handle_response_errors(mock_response)

    await client.close()


@pytest.mark.asyncio
async def test_handle_response_no_error():
    """Test that non-error status codes don't raise."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    mock_response = MagicMock()
    mock_response.status_code = 200

    # Should not raise
    await client._handle_response_errors(mock_response)

    await client.close()


def test_client_configuration_options():
    """Test client initialization with all options."""
    client = N8NClient(
        api_key="test_key",
        base_url="https://n8n.test.com",
        timeout=60,
        max_retries=5,
        poll_interval=3,
        max_poll_timeout=600,
    )

    assert client.api_key == "test_key"
    assert client.base_url == "https://n8n.test.com"
    assert "X-N8N-API-KEY" in client.headers
    assert client.headers["X-N8N-API-KEY"] == "test_key"
    assert client.executions.poll_interval == 3
    assert client.executions.max_poll_timeout == 600


@pytest.mark.asyncio
async def test_client_base_url_normalization():
    """Test that base_url trailing slashes are handled."""
    client1 = N8NClient(api_key="test", base_url="https://test.com/")
    client2 = N8NClient(api_key="test", base_url="https://test.com")

    # Both should have same normalized base_url
    assert "/api/v1" in str(client1._client.base_url)
    assert "/api/v1" in str(client2._client.base_url)

    await client1.close()
    await client2.close()


@pytest.mark.asyncio
async def test_client_aenter_aexit():
    """Test async context manager enter and exit."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    entered = await client.__aenter__()
    assert entered is client

    await client.__aexit__(None, None, None)
    # Client should be closed after exit


@pytest.mark.asyncio
async def test_health_check_connection_error():
    """Test health check with connection error."""
    client = N8NClient(api_key="test", base_url="https://test.com")

    # Mock workflows.list to raise connection error
    client.workflows.list = AsyncMock(side_effect=httpx.ConnectError("Failed"))

    with pytest.raises(N8NAPIError, match="Health check failed"):
        await client.health_check()

    await client.close()
