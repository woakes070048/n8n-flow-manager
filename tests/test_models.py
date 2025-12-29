"""Tests for Pydantic models."""

from datetime import datetime

import pytest
from n8n_manager.models.credential import Credential
from n8n_manager.models.execution import Execution, ExecutionMode, ExecutionStatus
from n8n_manager.models.workflow import Node, Settings, Workflow
from pydantic import ValidationError


def test_node_creation():
    """Test creating a Node model."""
    node = Node(
        name="Start",
        type="n8n-nodes-base.start",
        position=[100, 200],
        parameters={"test": "value"},
    )

    assert node.name == "Start"
    assert node.type == "n8n-nodes-base.start"
    assert node.position == [100, 200]
    assert node.parameters["test"] == "value"


def test_node_with_credentials():
    """Test Node with credentials."""
    node = Node(
        name="HTTP Request",
        type="n8n-nodes-base.httpRequest",
        position=[200, 300],
        parameters={},
        credentials={"httpAuth": {"id": "1", "name": "My Auth"}},
    )

    assert node.credentials is not None
    assert "httpAuth" in node.credentials


def test_workflow_creation():
    """Test creating a Workflow model."""
    workflow = Workflow(
        name="Test Workflow",
        active=True,
        nodes=[
            Node(
                name="Start",
                type="n8n-nodes-base.start",
                position=[100, 200],
                parameters={},
            )
        ],
        connections={},
    )

    assert workflow.name == "Test Workflow"
    assert workflow.active is True
    assert len(workflow.nodes) == 1
    assert workflow.id is None


def test_workflow_with_settings():
    """Test Workflow with settings."""
    workflow = Workflow(
        name="Test",
        active=False,
        nodes=[],
        connections={},
        settings=Settings(
            timezone="America/New_York",
            executionTimeout=300,
        ),
    )

    assert workflow.settings is not None
    assert workflow.settings.timezone == "America/New_York"
    assert workflow.settings.execution_timeout == 300


def test_workflow_to_json_dict():
    """Test Workflow conversion to JSON dict."""
    workflow = Workflow(
        name="Test",
        active=True,
        nodes=[Node(name="Start", type="n8n-nodes-base.start", position=[0, 0], parameters={})],
        connections={},
    )

    json_dict = workflow.to_json_dict()

    assert "name" in json_dict
    assert "nodes" in json_dict
    assert "connections" in json_dict
    assert "settings" in json_dict
    # 'active' should NOT be in json_dict (it's read-only, use activate/deactivate methods)
    assert "active" not in json_dict
    assert "id" not in json_dict  # Should be excluded
    assert "tags" not in json_dict  # Should be excluded (read-only)


def test_execution_status_enum():
    """Test ExecutionStatus enum values."""
    assert ExecutionStatus.SUCCESS.value == "success"
    assert ExecutionStatus.ERROR.value == "error"
    assert ExecutionStatus.RUNNING.value == "running"


def test_execution_creation():
    """Test creating an Execution model."""
    execution = Execution(
        id="123",
        finished=True,
        mode=ExecutionMode.MANUAL,
        startedAt=datetime.now(),
        workflowId="workflow_123",
        status=ExecutionStatus.SUCCESS,
    )

    assert execution.id == "123"
    assert execution.finished is True
    assert execution.mode == ExecutionMode.MANUAL
    assert execution.workflow_id == "workflow_123"


def test_execution_is_running():
    """Test execution running status check."""
    execution = Execution(
        id="123",
        finished=False,
        mode=ExecutionMode.MANUAL,
        startedAt=datetime.now(),
        workflowId="workflow_123",
        status=ExecutionStatus.RUNNING,
    )

    assert execution.is_running is True
    assert execution.is_successful is False
    assert execution.is_failed is False


def test_execution_is_successful():
    """Test execution success status check."""
    execution = Execution(
        id="123",
        finished=True,
        mode=ExecutionMode.MANUAL,
        startedAt=datetime.now(),
        workflowId="workflow_123",
        status=ExecutionStatus.SUCCESS,
    )

    assert execution.is_running is False
    assert execution.is_successful is True
    assert execution.is_failed is False


def test_execution_is_failed():
    """Test execution failure status check."""
    execution = Execution(
        id="123",
        finished=True,
        mode=ExecutionMode.MANUAL,
        startedAt=datetime.now(),
        workflowId="workflow_123",
        status=ExecutionStatus.ERROR,
    )

    assert execution.is_running is False
    assert execution.is_successful is False
    assert execution.is_failed is True


def test_credential_creation():
    """Test creating a Credential model."""
    credential = Credential(
        name="My Credential",
        type="httpBasicAuth",
        data={"username": "user", "password": "pass"},
    )

    assert credential.name == "My Credential"
    assert credential.type == "httpBasicAuth"
    assert credential.data is not None


def test_credential_to_json_dict():
    """Test Credential conversion to JSON dict."""
    credential = Credential(
        name="Test",
        type="httpBasicAuth",
        data={"username": "test"},
    )

    json_dict = credential.to_json_dict()

    assert "name" in json_dict
    assert "type" in json_dict
    assert "id" not in json_dict  # Should be excluded


def test_workflow_validation_missing_required_field():
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        Workflow(
            # Missing 'name' and 'nodes'
            active=True,
            connections={},
        )
