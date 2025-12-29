# Workflow Templates

This directory contains workflow templates that can be used with n8n-flow-manager's templating system.

## What are Workflow Templates?

Workflow templates are JSON files with Jinja2 variables that allow you to create environment-specific workflows without duplicating code.

## Using Templates

### From Python

```python
from n8n_manager.utils.templating import load_workflow_from_file

workflow = load_workflow_from_file(
    "templates/example_workflow.json",
    variables={
        "workflow_name": "My Workflow",
        "environment": "production",
        "webhook_path": "my-webhook",
        "webhook_id": "unique-id-123",
        "api_endpoint": "https://api.example.com/webhook",
        "request_timeout": 30000
    }
)
```

### From CLI

```bash
n8n-py deploy templates/example_workflow.json \
    --var workflow_name="My Workflow" \
    --var environment="production" \
    --var webhook_path="my-webhook" \
    --var webhook_id="unique-id-123" \
    --var api_endpoint="https://api.example.com/webhook" \
    --var request_timeout=30000 \
    --activate
```

## Available Templates

### example_workflow.json

A webhook-triggered workflow that:
1. Receives HTTP POST requests
2. Sets environment metadata
3. Forwards data to an external API

**Required variables:**
- `workflow_name` - Name of the workflow
- `environment` - Deployment environment (dev/staging/production)
- `webhook_path` - Webhook URL path
- `webhook_id` - Unique webhook identifier
- `api_endpoint` - External API URL
- `request_timeout` - HTTP request timeout in milliseconds

**Optional variables:**
- `execution_timeout` - Workflow execution timeout in seconds (default: 300)

## Creating Your Own Templates

1. Export an existing workflow from n8n
2. Replace values with Jinja2 variables: `{{ variable_name }}`
3. Add conditional logic if needed: `{{ "true" if condition else "false" }}`
4. Test with different variable sets

### Tips

- Use descriptive variable names
- Add defaults for optional values: `{{ timeout | default(60) }}`
- Group related variables in configuration files
- Document required and optional variables
- Test templates before deployment

## Example Configuration

Create a `config.py` for your environments:

```python
ENVIRONMENTS = {
    "dev": {
        "workflow_name": "Data Sync",
        "environment": "development",
        "webhook_path": "sync-dev",
        "webhook_id": "dev-webhook-001",
        "api_endpoint": "https://dev.api.example.com/sync",
        "request_timeout": 10000,
        "execution_timeout": 120
    },
    "prod": {
        "workflow_name": "Data Sync",
        "environment": "production",
        "webhook_path": "sync",
        "webhook_id": "prod-webhook-001",
        "api_endpoint": "https://api.example.com/sync",
        "request_timeout": 30000,
        "execution_timeout": 300
    }
}
```

Then deploy to any environment:

```python
from n8n_manager import N8NClient
from n8n_manager.utils.templating import load_workflow_from_file
from config import ENVIRONMENTS

async def deploy(env: str):
    workflow = load_workflow_from_file(
        "templates/example_workflow.json",
        variables=ENVIRONMENTS[env]
    )

    async with N8NClient() as client:
        created = await client.workflows.create(workflow)
        print(f"Deployed to {env}: {created.id}")
```

## Best Practices

1. **Version Control**: Keep templates in Git
2. **Environment Files**: Use separate config files for each environment
3. **Validation**: Test templates with n8n-flow-manager before deploying
4. **Documentation**: Document all required and optional variables
5. **Security**: Never commit sensitive values; use environment variables

## Advanced Jinja2 Features

### Conditionals

```json
"active": {{ "true" if environment == "production" else "false" }}
```

### Loops

```json
"values": {
  "string": [
    {% for item in items %}
    {
      "name": "{{ item.name }}",
      "value": "{{ item.value }}"
    }{{ "," if not loop.last else "" }}
    {% endfor %}
  ]
}
```

### Filters

```json
"timeout": {{ timeout | default(60) }},
"name": "{{ name | upper }}"
```

## Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [n8n Node Reference](https://docs.n8n.io/integrations/)
- [n8n Workflow Examples](https://n8n.io/workflows)
