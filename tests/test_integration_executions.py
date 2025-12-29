"""Integration tests for Execution API."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from n8n_manager.api.executions import ExecutionAPI
from n8n_manager.exceptions import N8NNotFoundError, N8NTimeoutError
from n8n_manager.models.execution import ExecutionMode, ExecutionStatus


@pytest.fixture
def mock_client():
    """Create a mock httpx.AsyncClient."""
    return AsyncMock(spec=httpx.AsyncClient)


@pytest.fixture
def execution_api(mock_client):
    """Create ExecutionAPI instance with mock client."""
    return ExecutionAPI(mock_client, poll_interval=0.1, max_poll_timeout=1)


@pytest.mark.asyncio
async def test_list_executions(execution_api, mock_client):
    """Test listing executions."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "id": "1",
                "finished": True,
                "mode": "manual",
                "workflowId": "w1",
                "status": "success",
            }
        ]
    }
    mock_client.get.return_value = mock_response

    executions = await execution_api.list()

    assert len(executions) == 1
    assert executions[0].id == "1"


@pytest.mark.asyncio
async def test_list_executions_with_filters(execution_api, mock_client):
    """Test listing executions with filters."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []}
    mock_client.get.return_value = mock_response

    await execution_api.list(workflow_id="w1", limit=50, status=ExecutionStatus.SUCCESS)

    call_args = mock_client.get.call_args
    assert call_args[0][0] == "/executions"
    assert call_args[1]["params"]["workflowId"] == "w1"
    assert call_args[1]["params"]["limit"] == 50


@pytest.mark.asyncio
async def test_get_execution(execution_api, mock_client):
    """Test getting a specific execution."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "ex1",
        "finished": True,
        "mode": "manual",
        "workflowId": "w1",
        "status": "success",
    }
    mock_client.get.return_value = mock_response

    execution = await execution_api.get("ex1")

    assert execution.id == "ex1"
    assert execution.status == ExecutionStatus.SUCCESS


@pytest.mark.asyncio
async def test_get_execution_not_found(execution_api, mock_client):
    """Test getting non-existent execution."""
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404, content=b"", json=lambda: {}),
    )

    with pytest.raises(N8NNotFoundError, match="Execution ex999 not found"):
        await execution_api.get("ex999")


@pytest.mark.asyncio
async def test_delete_execution(execution_api, mock_client):
    """Test deleting an execution."""
    mock_response = MagicMock()
    mock_client.delete.return_value = mock_response

    result = await execution_api.delete("ex1")

    assert result is True
    mock_client.delete.assert_called_once_with("/executions/ex1")


@pytest.mark.asyncio
async def test_retry_execution(execution_api, mock_client):
    """Test retrying a failed execution."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "ex2",
        "finished": False,
        "mode": "retry",
        "workflowId": "w1",
        "retryOf": "ex1",
    }
    mock_client.post.return_value = mock_response

    retried = await execution_api.retry("ex1")

    assert retried.id == "ex2"
    assert retried.mode == ExecutionMode.RETRY
    mock_client.post.assert_called_once_with("/executions/ex1/retry")


@pytest.mark.asyncio
async def test_trigger_workflow(execution_api, mock_client):
    """Test triggering a workflow."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "ex1",
        "finished": False,
        "mode": "manual",
        "workflowId": "w1",
    }
    mock_client.post.return_value = mock_response

    execution = await execution_api.trigger_workflow("w1")

    assert execution.id == "ex1"
    assert execution.workflow_id == "w1"


@pytest.mark.asyncio
async def test_trigger_workflow_with_data(execution_api, mock_client):
    """Test triggering workflow with input data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "ex1",
        "finished": False,
        "mode": "manual",
        "workflowId": "w1",
    }
    mock_client.post.return_value = mock_response

    input_data = {"test": "data"}
    await execution_api.trigger_workflow("w1", input_data=input_data)

    call_args = mock_client.post.call_args
    assert call_args[1]["json"] == {"data": input_data}


@pytest.mark.asyncio
async def test_wait_for_execution_completes(execution_api, mock_client):
    """Test waiting for execution to complete."""
    # First call: running, second call: finished
    responses = [
        MagicMock(
            json=lambda: {
                "id": "ex1",
                "finished": False,
                "mode": "manual",
                "workflowId": "w1",
                "status": "running",
            }
        ),
        MagicMock(
            json=lambda: {
                "id": "ex1",
                "finished": True,
                "mode": "manual",
                "workflowId": "w1",
                "status": "success",
            }
        ),
    ]
    mock_client.get.side_effect = responses

    execution = await execution_api.wait_for_execution("ex1", timeout=2)

    assert execution.finished is True
    assert execution.status == ExecutionStatus.SUCCESS
    assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_wait_for_execution_timeout(execution_api, mock_client):
    """Test waiting for execution times out."""
    # Always return running
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "ex1",
        "finished": False,
        "mode": "manual",
        "workflowId": "w1",
        "status": "running",
    }
    mock_client.get.return_value = mock_response

    with pytest.raises(N8NTimeoutError, match="did not complete within"):
        await execution_api.wait_for_execution("ex1", timeout=0.3)


@pytest.mark.asyncio
async def test_run_and_wait(execution_api, mock_client):
    """Test run_and_wait convenience method."""
    # Mock trigger response
    trigger_response = MagicMock()
    trigger_response.json.return_value = {
        "id": "ex1",
        "finished": False,
        "mode": "manual",
        "workflowId": "w1",
    }

    # Mock wait responses
    wait_response = MagicMock()
    wait_response.json.return_value = {
        "id": "ex1",
        "finished": True,
        "mode": "manual",
        "workflowId": "w1",
        "status": "success",
    }

    mock_client.post.return_value = trigger_response
    mock_client.get.return_value = wait_response

    result = await execution_api.run_and_wait("w1", timeout=2)

    assert result.finished is True
    assert result.status == ExecutionStatus.SUCCESS
    mock_client.post.assert_called_once()
