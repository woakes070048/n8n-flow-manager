"""
Workflow templating example for n8n-flow-manager.

This example demonstrates:
- Creating workflow templates with Jinja2
- Loading templates with variables
- Deploying templated workflows
"""

import asyncio

from n8n_manager import N8NClient
from n8n_manager.utils.templating import render_workflow_template


async def main():
    print("=== Workflow Templating Example ===\n")

    # 1. Create a workflow template with Jinja2 variables
    workflow_template = """
    {
        "name": "{{ workflow_name }} - {{ environment }}",
        "active": {{ "true" if environment == "production" else "false" }},
        "nodes": [
            {
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "parameters": {
                    "path": "{{ webhook_path }}",
                    "httpMethod": "POST",
                    "responseMode": "onReceived"
                },
                "webhookId": "{{ webhook_id }}"
            },
            {
                "name": "HTTP Request",
                "type": "n8n-nodes-base.httpRequest",
                "position": [450, 300],
                "parameters": {
                    "url": "{{ api_endpoint }}",
                    "method": "POST",
                    "options": {
                        "timeout": {{ request_timeout }}
                    }
                }
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "HTTP Request",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
    }
    """

    # 2. Define variables for different environments
    environments = {
        "dev": {
            "workflow_name": "Data Sync",
            "environment": "development",
            "webhook_path": "sync-dev",
            "webhook_id": "dev-webhook-123",
            "api_endpoint": "https://dev.api.example.com/sync",
            "request_timeout": 10000,
        },
        "prod": {
            "workflow_name": "Data Sync",
            "environment": "production",
            "webhook_path": "sync",
            "webhook_id": "prod-webhook-456",
            "api_endpoint": "https://api.example.com/sync",
            "request_timeout": 30000,
        },
    }

    # 3. Render templates for each environment
    print("Rendering workflow templates...\n")

    for env_name, variables in environments.items():
        print(f"Environment: {env_name}")
        workflow_data = render_workflow_template(workflow_template, variables)

        print(f"  Workflow Name: {workflow_data['name']}")
        print(f"  Active: {workflow_data['active']}")
        print(f"  Webhook Path: {workflow_data['nodes'][0]['parameters']['path']}")
        print(f"  API Endpoint: {workflow_data['nodes'][1]['parameters']['url']}")
        print()

    # 4. Deploy to n8n (optional - requires valid credentials)
    deploy = input("Deploy workflows to n8n? (y/n): ").lower() == "y"

    if deploy:
        async with N8NClient() as client:
            print("\nDeploying workflows...\n")

            for env_name, variables in environments.items():
                workflow_data = render_workflow_template(workflow_template, variables)

                # Import the Workflow model
                from n8n_manager.models.workflow import Workflow

                workflow = Workflow(**workflow_data)

                created = await client.workflows.create(workflow)
                print(f"✓ {env_name}: Deployed '{created.name}' (ID: {created.id})")

            print("\n✓ All workflows deployed successfully!")
    else:
        print("\nSkipping deployment (dry run only)")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
