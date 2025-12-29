"""Complete coverage tests for templating module."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from n8n_manager.exceptions import N8NValidationError
from n8n_manager.models.workflow import Node, Workflow
from n8n_manager.utils.templating import (
    load_workflow_from_directory,
    load_workflow_from_file,
    render_workflow_template,
    save_workflow_to_file,
)


def test_render_template_with_exception():
    """Test rendering template with Jinja2 error."""
    template = "{% for i in range(undefined) %}"  # Will cause error

    # This should raise N8NValidationError
    try:
        render_workflow_template(template, {})
        assert False, "Should have raised N8NValidationError"
    except N8NValidationError:
        pass  # Expected


def test_load_workflow_from_directory_success():
    """Test loading workflow from directory with FileSystemLoader."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create template file
        template_content = {"name": "{{ name }}", "active": False, "nodes": [], "connections": {}}

        template_file = tmp_path / "workflow.json"
        with open(template_file, "w") as f:
            json.dump(template_content, f)

        # Load using directory loader
        workflow = load_workflow_from_directory(
            tmp_path, "workflow.json", variables={"name": "Test Workflow"}
        )

        assert workflow.name == "Test Workflow"


def test_load_workflow_from_directory_template_not_found():
    """Test loading non-existent template."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        with pytest.raises(N8NValidationError, match="Template not found"):
            load_workflow_from_directory(tmp_path, "nonexistent.json", variables={})


def test_load_workflow_from_directory_invalid_json():
    """Test loading template with invalid JSON."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create invalid JSON template
        template_file = tmp_path / "invalid.json"
        with open(template_file, "w") as f:
            f.write("{{ name }}")  # Not valid JSON after rendering

        with pytest.raises(N8NValidationError, match="Invalid JSON"):
            load_workflow_from_directory(
                tmp_path, "invalid.json", variables={"name": "{incomplete"}
            )


def test_load_workflow_from_file_invalid_json():
    """Test loading file with invalid JSON."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        invalid_file = tmp_path / "invalid.json"

        with open(invalid_file, "w") as f:
            f.write("{invalid json}")

        with pytest.raises(N8NValidationError, match="Invalid JSON in workflow file"):
            load_workflow_from_file(invalid_file)


def test_load_workflow_from_file_general_error():
    """Test loading file with permission error or validation."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        bad_file = tmp_path / "bad.json"

        # Create file with invalid workflow data
        with open(bad_file, "w") as f:
            json.dump({"name": "Test"}, f)  # Missing required fields

        with pytest.raises(N8NValidationError, match="Failed to load workflow from file"):
            load_workflow_from_file(bad_file)


def test_save_workflow_to_file_creates_parents():
    """Test that saving creates parent directories."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        nested_path = tmp_path / "level1" / "level2" / "workflow.json"

        workflow = Workflow(
            name="Test",
            active=False,
            nodes=[Node(name="Start", type="n8n-nodes-base.start", position=[0, 0], parameters={})],
            connections={},
        )

        save_workflow_to_file(workflow, nested_path)

        assert nested_path.exists()
        assert nested_path.parent.exists()


def test_render_template_complex_jinja():
    """Test rendering with complex Jinja2 features."""
    template = """
    {
        "name": "{{ name | upper }}",
        "active": {{ "true" if env == "prod" else "false" }},
        "nodes": [
            {% for i in range(count) %}
            {
                "name": "Node{{ i }}",
                "type": "n8n-nodes-base.set",
                "position": [{{ i * 100 }}, 0],
                "parameters": {}
            }{{ "," if not loop.last else "" }}
            {% endfor %}
        ],
        "connections": {}
    }
    """

    variables = {"name": "test", "env": "prod", "count": 2}
    result = render_workflow_template(template, variables)

    assert result["name"] == "TEST"
    assert result["active"] is True
    assert len(result["nodes"]) == 2


def test_load_workflow_with_variables_none():
    """Test loading workflow without variables."""
    with TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        workflow_file = tmp_path / "simple.json"

        workflow_data = {"name": "Simple", "active": False, "nodes": [], "connections": {}}

        with open(workflow_file, "w") as f:
            json.dump(workflow_data, f)

        workflow = load_workflow_from_file(workflow_file, variables=None)

        assert workflow.name == "Simple"
