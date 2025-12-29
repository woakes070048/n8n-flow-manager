"""Complete coverage tests for workflows API."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from n8n_manager.api.workflows import WorkflowAPI
from n8n_manager.exceptions import N8NAPIError, N8NNotFoundError, N8NValidationError
from n8n_manager.models.workflow import Workflow


@pytest.mark.asyncio
async def test_list_workflows_404_error():
    """Test list workflows with 404 error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}
    mock_response.request = MagicMock()
    mock_response.request.url = "http://test/workflows"

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=mock_response.request, response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Workflows endpoint not found"):
        await api.list()


@pytest.mark.asyncio
async def test_list_workflows_general_error():
    """Test list workflows with general HTTP error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.content = b'{"error": "forbidden"}'
    mock_response.json.return_value = {"error": "forbidden"}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Forbidden", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to list workflows"):
        await api.list()


@pytest.mark.asyncio
async def test_get_workflow_not_found():
    """Test get workflow returns 404."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.get.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Workflow w999 not found"):
        await api.get("w999")


@pytest.mark.asyncio
async def test_get_workflow_api_error():
    """Test get workflow with API error."""
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
        await api.get("w1")


@pytest.mark.asyncio
async def test_create_workflow_api_error():
    """Test create workflow with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    workflow = Workflow(name="Test", active=False, nodes=[], connections={})

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to create workflow"):
        await api.create(workflow)


@pytest.mark.asyncio
async def test_update_workflow_validation_error():
    """Test update workflow with validation error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    workflow = Workflow(name="Test", active=False, nodes=[], connections={})

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"error": "invalid"}'
    mock_response.json.return_value = {"error": "invalid"}

    client.patch.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NValidationError, match="Invalid workflow data"):
        await api.update("w1", workflow)


@pytest.mark.asyncio
async def test_update_workflow_api_error():
    """Test update workflow with API error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    workflow = Workflow(name="Test", active=False, nodes=[], connections={})

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.patch.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server Error", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NAPIError, match="Failed to update workflow"):
        await api.update("w1", workflow)


@pytest.mark.asyncio
async def test_create_workflow_validation_error():
    """Test create workflow with validation error."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    workflow = Workflow(name="Test", active=False, nodes=[], connections={})

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.content = b'{"error": "validation failed"}'
    mock_response.json.return_value = {"error": "validation failed"}

    client.post.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NValidationError, match="Invalid workflow data"):
        await api.create(workflow)


@pytest.mark.asyncio
async def test_delete_workflow_not_found():
    """Test delete workflow with 404."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.delete.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Workflow w999 not found"):
        await api.delete("w999")


@pytest.mark.asyncio
async def test_delete_workflow_api_error():
    """Test delete workflow with API error."""
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
        await api.delete("w1")


@pytest.mark.asyncio
async def test_update_workflow_not_found():
    """Test update workflow with 404."""
    client = AsyncMock(spec=httpx.AsyncClient)
    api = WorkflowAPI(client)

    workflow = Workflow(name="Test", active=False, nodes=[], connections={})

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.content = b""
    mock_response.json.return_value = {}

    client.patch.return_value = mock_response
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=mock_response
    )

    with pytest.raises(N8NNotFoundError, match="Workflow w999 not found"):
        await api.update("w999", workflow)
