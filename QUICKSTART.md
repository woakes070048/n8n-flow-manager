# Quick Start Guide

Get started with n8n-flow-manager in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- An n8n instance (cloud or self-hosted)
- n8n API key

## Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/n8n-flow-manager.git
cd n8n-flow-manager

# Install with Poetry (recommended)
poetry install

# Or with pip
pip install -e .
```

## Step 2: Activate Environment (Poetry 2.0+)

```bash
# Para Poetry 2.0+, usa uno de estos métodos:

# Opción 1: Activar el entorno (recomendado)
source $(poetry env info --path)/bin/activate

# Opción 2: Usar poetry run antes de cada comando
# (no necesitas activar el entorno)
```

## Step 3: Configuration

Create a `.env` file in the project root:

```bash
N8N_API_KEY=your_api_key_here
N8N_BASE_URL=https://n8n.example.com
```

### Getting Your API Key

1. Open your n8n instance
2. Click on your user menu (bottom left)
3. Go to **Settings** → **API**
4. Click **Create API Key**
5. Copy the key and save it in your `.env` file

## Step 4: Verify Connection

Test your connection using the CLI:

```bash
# Con poetry run (funciona siempre)
poetry run n8n-py health

# O si activaste el entorno:
n8n-py health
```

You should see:

```
✓ Connection healthy!
  API URL: https://n8n.example.com/api/v1/
```

## Step 5: Your First Command

List all your workflows:

```bash
poetry run n8n-py list-workflows
```

## Step 6: Try the Python SDK

Create a file `test.py`:

```python
import asyncio
from n8n_manager import N8NClient

async def main():
    async with N8NClient() as client:
        # List workflows
        workflows = await client.workflows.list(active=True)

        print(f"Found {len(workflows)} active workflows:")
        for wf in workflows:
            print(f"  - {wf.name} (ID: {wf.id})")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
poetry run python test.py
```

## Common Use Cases

### 1. Backup All Workflows

```bash
poetry run n8n-py backup --output ./my-backups
```

### 2. Deploy a Workflow

```bash
poetry run n8n-py deploy path/to/workflow.json --activate
```

### 3. Execute a Workflow

```bash
poetry run n8n-py execute <workflow_id>
```

### 4. Get Workflow Details

```bash
poetry run n8n-py get-workflow <workflow_id> --output workflow.json
```

## Python SDK Examples

### Create a Simple Workflow

```python
import asyncio
from n8n_manager import N8NClient
from n8n_manager.models.workflow import Workflow, Node

async def create_workflow():
    async with N8NClient() as client:
        workflow = Workflow(
            name="Hello World",
            active=False,
            nodes=[
                Node(
                    name="Start",
                    type="n8n-nodes-base.start",
                    position=[250, 300],
                    parameters={}
                )
            ],
            connections={}
        )

        created = await client.workflows.create(workflow)
        print(f"Created workflow: {created.id}")

asyncio.run(create_workflow())
```

### Execute and Wait for Result

```python
import asyncio
from n8n_manager import N8NClient

async def execute_workflow(workflow_id: str):
    async with N8NClient() as client:
        # Execute and wait for completion
        execution = await client.executions.run_and_wait(
            workflow_id=workflow_id,
            timeout=60
        )

        print(f"Status: {execution.status}")
        print(f"Success: {execution.is_successful}")

asyncio.run(execute_workflow("your_workflow_id"))
```

### Use Workflow Templates

```python
import asyncio
from n8n_manager import N8NClient
from n8n_manager.utils.templating import load_workflow_from_file

async def deploy_templated_workflow():
    # Load workflow with variables
    workflow = load_workflow_from_file(
        "templates/my_workflow.json",
        variables={
            "environment": "production",
            "api_endpoint": "https://api.example.com",
            "timeout": 30
        }
    )

    async with N8NClient() as client:
        created = await client.workflows.create(workflow)
        print(f"Deployed: {created.name} (ID: {created.id})")

asyncio.run(deploy_templated_workflow())
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/](examples/) for more usage patterns
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Join the [n8n Community Forum](https://community.n8n.io/)

## Troubleshooting

### "Authentication failed"

- Check your API key is correct in `.env`
- Verify the API key is active in n8n settings
- Ensure your n8n instance allows API access

### "Connection refused"

- Verify `N8N_BASE_URL` is correct
- Check if n8n instance is accessible from your network
- For self-hosted: ensure n8n is running

### "Module not found"

- Make sure you're in the project directory
- If using Poetry: run `poetry shell` first
- If using pip: ensure virtual environment is activated

## Support

Need help?

- Check the [README.md](README.md) for full documentation
- Search [existing issues](https://github.com/yourusername/n8n-flow-manager/issues)
- Ask in [GitHub Discussions](https://github.com/yourusername/n8n-flow-manager/discussions)
- Visit [n8n Community](https://community.n8n.io/)

---

Happy automating! 🚀
