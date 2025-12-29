"""
Basic usage example for n8n-flow-manager.

This example demonstrates:
- Creating a client
- Listing workflows
- Getting a specific workflow
- Creating a new workflow
- Executing a workflow
"""

import asyncio

from n8n_manager import N8NClient
from n8n_manager.models.workflow import Node, Workflow


async def main():
    # Initialize client (uses N8N_API_KEY and N8N_BASE_URL from environment)
    async with N8NClient() as client:

        print("=== n8n-flow-manager Basic Usage Example ===\n")

        # 1. Health Check
        print("1. Checking connection...")
        healthy = await client.health_check()
        print(f"   ✓ Connection is {'healthy' if healthy else 'failed'}\n")

        # 2. List all active workflows
        print("2. Listing active workflows...")
        workflows = await client.workflows.list(active=True)
        print(f"   Found {len(workflows)} active workflows:")
        for wf in workflows[:5]:  # Show first 5
            print(f"   - {wf.name} (ID: {wf.id})")
        print()

        # 3. Get a specific workflow (if any exist)
        if workflows:
            print("3. Getting details of first workflow...")
            workflow = await client.workflows.get(workflows[0].id)
            print(f"   Name: {workflow.name}")
            print(f"   Active: {workflow.active}")
            print(f"   Nodes: {len(workflow.nodes)}")
            print()

        # 4. Create a simple workflow
        print("4. Creating a new workflow...")
        new_workflow = Workflow(
            name="Example Workflow from Python",
            active=False,
            nodes=[
                Node(
                    name="Start",
                    type="n8n-nodes-base.start",
                    position=[250, 300],
                    parameters={},
                ),
                Node(
                    name="Set",
                    type="n8n-nodes-base.set",
                    position=[450, 300],
                    parameters={
                        "values": {
                            "string": [
                                {
                                    "name": "message",
                                    "value": "Hello from Python!",
                                }
                            ]
                        }
                    },
                ),
            ],
            connections={
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Set",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                }
            },
        )

        created = await client.workflows.create(new_workflow)
        print(f"   ✓ Workflow created with ID: {created.id}\n")

        # 5. Activate the workflow
        print("5. Activating workflow...")
        activated = await client.workflows.activate(created.id)
        print(f"   ✓ Workflow '{activated.name}' is now active\n")

        # 6. Execute the workflow (for manual workflows)
        # Note: This will only work if the workflow can be manually triggered
        print("6. Triggering workflow execution...")
        try:
            execution = await client.executions.trigger_workflow(created.id)
            print(f"   ✓ Execution started with ID: {execution.id}")
            print(f"   Status: {execution.status}\n")

            # Wait for execution to complete
            print("7. Waiting for execution to complete...")
            completed = await client.executions.wait_for_execution(execution.id, timeout=60)
            print("   ✓ Execution finished!")
            print(f"   Status: {completed.status}")
            print(f"   Success: {completed.is_successful}\n")
        except Exception as e:
            print("   Note: Execution might not be available for this workflow type")
            print(f"   Error: {e}\n")

        # 7. Deactivate the workflow
        print("8. Deactivating workflow...")
        deactivated = await client.workflows.deactivate(created.id)
        print("   ✓ Workflow deactivated\n")

        # 8. Delete the test workflow
        print("9. Cleaning up (deleting test workflow)...")
        await client.workflows.delete(created.id)
        print("   ✓ Test workflow deleted\n")

        print("=== Example Complete ===")


if __name__ == "__main__":
    # Make sure to set N8N_API_KEY and N8N_BASE_URL environment variables
    # or create a .env file with these values
    asyncio.run(main())
