"""Complete API coverage tests with proper mocking."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from n8n_manager.api.credentials import CredentialAPI
from n8n_manager.api.executions import ExecutionAPI
from n8n_manager.api.workflows import WorkflowAPI
from n8n_manager.exceptions import (
    N8NAPIError,
    N8NNotFoundError,
    N8NValidationError,
)
from n8n_manager.models.credential import Credential

# ============================================================================
# WORKFLOWS API TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_workflow_list_error_handling():
    """Test workflow list with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to list workflows"):
        await api.list()


@pytest.mark.asyncio
async def test_workflow_get_api_error():
    """Test workflow get with general API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to get workflow"):
        await api.get("123")


@pytest.mark.asyncio
async def test_workflow_delete_api_error():
    """Test workflow delete with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.delete.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to delete workflow"):
        await api.delete("123")


# ============================================================================
# EXECUTIONS API TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_execution_list_api_error():
    """Test execution list with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = ExecutionAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to list executions"):
        await api.list()


@pytest.mark.asyncio
async def test_execution_delete_not_found():
    """Test deleting non-existent execution."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = ExecutionAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.delete.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Execution ex999 not found"):
        await api.delete("ex999")


@pytest.mark.asyncio
async def test_execution_retry_not_found():
    """Test retrying non-existent execution."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = ExecutionAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Execution ex999 not found"):
        await api.retry("ex999")


@pytest.mark.asyncio
async def test_execution_trigger_not_found():
    """Test triggering non-existent workflow."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = ExecutionAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Workflow w999 not found"):
        await api.trigger_workflow("w999")


@pytest.mark.asyncio
async def test_execution_trigger_api_error():
    """Test triggering workflow with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = ExecutionAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to trigger workflow"):
        await api.trigger_workflow("w1")


# ============================================================================
# CREDENTIALS API TESTS
# ============================================================================


@pytest.mark.asyncio
async def test_credential_list_api_error():
    """Test credential list with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = CredentialAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to list credentials"):
        await api.list()


@pytest.mark.asyncio
async def test_credential_create_validation_error():
    """Test creating invalid credential."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = CredentialAPI(client)

    credential = Credential(name="Test", type="httpBasicAuth")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"error": "invalid"}'
    mock_response.json.return_value = {"error": "invalid"}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NValidationError, match="Invalid credential data"):
        await api.create(credential)


@pytest.mark.asyncio
async def test_credential_update_not_found():
    """Test updating non-existent credential."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = CredentialAPI(client)

    credential = Credential(name="Test", type="httpBasicAuth")

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.patch.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Credential c999 not found"):
        await api.update("c999", credential)


@pytest.mark.asyncio
async def test_credential_update_validation_error():
    """Test updating credential with validation error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = CredentialAPI(client)

    credential = Credential(name="Test", type="httpBasicAuth")

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"error": "invalid"}'
    mock_response.json.return_value = {"error": "invalid"}

    client.patch.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NValidationError, match="Invalid credential data"):
        await api.update("c1", credential)


@pytest.mark.asyncio
async def test_credential_delete_not_found():
    """Test deleting non-existent credential."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = CredentialAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.delete.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Credential c999 not found"):
        await api.delete("c999")
