"""Tests for templating utilities."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from n8n_manager.exceptions import N8NValidationError
from n8n_manager.models.workflow import Node, Workflow
from n8n_manager.utils.templating import (
    load_workflow_from_file,
    render_workflow_template,
    save_workflow_to_file,
)


def test_render_workflow_template_simple():
    """Test rendering a simple template."""
    template = '{"name": "{{ workflow_name }}", "active": {{ active }}}'
    variables = {"workflow_name": "Test Workflow", "active": "true"}

    result = render_workflow_template(template, variables)

    assert result["name"] == "Test Workflow"
    assert result["active"] is True


def test_render_workflow_template_complex():
    """Test rendering a complex template with nested values."""
    template = """
    {
        "name": "{{ name }}",
        "active": false,
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "position": [0, 0],
                "parameters": {
                    "env": "{{ environment }}"
                }
            }
        ],
        "connections": {}
    }
    """
    variables = {"name": "Production Flow", "environment": "prod"}

    result = render_workflow_template(template, variables)

    assert result["name"] == "Production Flow"
    assert result["nodes"][0]["parameters"]["env"] == "prod"


def test_render_workflow_template_invalid_json():
    """Test that invalid JSON after rendering raises error."""
    template = '{"name": "{{ name }}"'  # Missing closing brace
    variables = {"name": "Test"}

    with pytest.raises(N8NValidationError, match="Invalid JSON"):
        render_workflow_template(template, variables)


def test_load_workflow_from_file_without_template():
    """Test loading a workflow from a plain JSON file."""
    workflow_data = {
        "name": "Test Workflow",
        "active": False,
        "nodes": [
            {
                "name": "Start",
                "type": "n8n-nodes-base.start",
                "position": [0, 0],
                "parameters": {},
            }
        ],
        "connections": {},
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(workflow_data, f)
        temp_path = Path(f.name)

    try:
        workflow = load_workflow_from_file(temp_path)

        assert isinstance(workflow, Workflow)
        assert workflow.name == "Test Workflow"
        assert len(workflow.nodes) == 1
    finally:
        temp_path.unlink()


def test_load_workflow_from_file_with_template():
    """Test loading a workflow from a template file."""
    template_data = {
        "name": "{{ workflow_name }}",
        "active": False,
        "nodes": [],
        "connections": {},
    }

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(template_data, f)
        temp_path = Path(f.name)

    try:
        workflow = load_workflow_from_file(
            temp_path, variables={"workflow_name": "Dynamic Workflow"}
        )

        assert workflow.name == "Dynamic Workflow"
    finally:
        temp_path.unlink()


def test_load_workflow_from_file_not_found():
    """Test that loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_workflow_from_file("/nonexistent/file.json")


def test_save_workflow_to_file():
    """Test saving a workflow to a file."""
    workflow = Workflow(
        name="Test Workflow",
        active=True,
        nodes=[
            Node(
                name="Start",
                type="n8n-nodes-base.start",
                position=[0, 0],
                parameters={},
            )
        ],
        connections={},
    )

    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

    try:
        save_workflow_to_file(workflow, temp_path)

        # Verify file was created and contains valid JSON
        assert temp_path.exists()

        with open(temp_path) as f:
            data = json.load(f)

        assert data["name"] == "Test Workflow"
        assert data["active"] is True
        assert len(data["nodes"]) == 1
    finally:
        temp_path.unlink()


def test_save_workflow_creates_parent_dirs():
    """Test that saving workflow creates parent directories if needed."""
    import shutil
    import tempfile

    temp_dir = Path(tempfile.mkdtemp())

    try:
        workflow = Workflow(
            name="Test",
            active=False,
            nodes=[],
            connections={},
        )

        nested_path = temp_dir / "subdir" / "another" / "workflow.json"
        save_workflow_to_file(workflow, nested_path)

        assert nested_path.exists()
    finally:
        shutil.rmtree(temp_dir)
