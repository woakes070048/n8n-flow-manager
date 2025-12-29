"""
Backup and restore workflows example.

This example demonstrates:
- Backing up all workflows to local files
- Restoring workflows from backup files
- Useful for version control and disaster recovery
"""

import asyncio
from pathlib import Path

from n8n_manager import N8NClient
from n8n_manager.utils.templating import load_workflow_from_file, save_workflow_to_file


async def backup_workflows(client: N8NClient, backup_dir: Path):
    """Backup all workflows to a directory."""
    print("=== Backing up workflows ===\n")

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Get all workflows
    workflows = await client.workflows.list()
    print(f"Found {len(workflows)} workflows to backup\n")

    # Save each workflow
    for workflow in workflows:
        # Create safe filename
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in workflow.name)
        filename = f"{workflow.id}_{safe_name}.json"
        filepath = backup_dir / filename

        save_workflow_to_file(workflow, filepath)
        print(f"✓ Backed up: {workflow.name} → {filename}")

    print(f"\n✓ All workflows backed up to {backup_dir}\n")
    return len(workflows)


async def restore_workflows(client: N8NClient, backup_dir: Path):
    """Restore workflows from backup directory."""
    print("=== Restoring workflows ===\n")

    if not backup_dir.exists():
        print(f"✗ Backup directory not found: {backup_dir}")
        return 0

    # Get all JSON files
    backup_files = list(backup_dir.glob("*.json"))
    print(f"Found {len(backup_files)} backup files\n")

    restored = 0
    for filepath in backup_files:
        try:
            # Load workflow from file
            workflow = load_workflow_from_file(filepath)

            # Remove ID to create as new workflow
            workflow.id = None

            # Create workflow
            created = await client.workflows.create(workflow)
            print(f"✓ Restored: {created.name} (New ID: {created.id})")
            restored += 1

        except Exception as e:
            print(f"✗ Failed to restore {filepath.name}: {e}")

    print(f"\n✓ Restored {restored}/{len(backup_files)} workflows\n")
    return restored


async def sync_workflows(source_client: N8NClient, target_client: N8NClient):
    """
    Sync workflows from source to target instance.
    Useful for Dev -> Prod deployments.
    """
    print("=== Syncing workflows between instances ===\n")

    # Get workflows from source
    source_workflows = await source_client.workflows.list()
    print(f"Source: {len(source_workflows)} workflows")

    # Get workflows from target
    target_workflows = await target_client.workflows.list()
    target_names = {wf.name: wf for wf in target_workflows}
    print(f"Target: {len(target_workflows)} workflows\n")

    created = 0
    updated = 0

    for workflow in source_workflows:
        workflow.id = None  # Remove ID for creation

        if workflow.name in target_names:
            # Update existing workflow
            target_wf = target_names[workflow.name]
            await target_client.workflows.update(target_wf.id, workflow)
            print(f"↻ Updated: {workflow.name}")
            updated += 1
        else:
            # Create new workflow
            await target_client.workflows.create(workflow)
            print(f"✓ Created: {workflow.name}")
            created += 1

    print(f"\n✓ Sync complete: {created} created, {updated} updated\n")


async def main():
    print("=== n8n Backup & Restore Example ===\n")

    # Configuration
    backup_directory = Path("./n8n_backups")

    async with N8NClient() as client:
        print("Choose an operation:")
        print("1. Backup all workflows")
        print("2. Restore workflows from backup")
        print("3. List backup files")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            count = await backup_workflows(client, backup_directory)
            print(f"Backup complete: {count} workflows saved")

        elif choice == "2":
            confirm = input("⚠️  This will create new workflows. Continue? (y/n): ").lower()

            if confirm == "y":
                count = await restore_workflows(client, backup_directory)
                print(f"Restore complete: {count} workflows restored")
            else:
                print("Restore cancelled")

        elif choice == "3":
            if backup_directory.exists():
                files = list(backup_directory.glob("*.json"))
                print(f"\nBackup files in {backup_directory}:")
                for f in files:
                    print(f"  - {f.name}")
                print(f"\nTotal: {len(files)} files")
            else:
                print(f"No backup directory found at {backup_directory}")

        else:
            print("Invalid choice")

    print("\n=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
