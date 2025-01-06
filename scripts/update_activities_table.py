#!/usr/bin/env python3
import json
import re
from datetime import datetime, UTC
from pathlib import Path

def get_repo_root():
    """Get the root directory of the repository."""
    return Path(__file__).parent.parent

def get_activity_description(activity_dir):
    """Extract the description from the activity's schema file.
    Priority order: description["en"] > prefLabel["en"] > activity name
    """
    try:
        schema_path = activity_dir / f"{activity_dir.name}_schema"
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
                # Add schema validation
                if isinstance(schema, dict):
                    if isinstance(schema.get('description'), dict) and schema['description'].get('en'):
                        return schema['description']['en']
                    if isinstance(schema.get('prefLabel'), dict) and schema['prefLabel'].get('en'):
                        return schema['prefLabel']['en']
                return activity_dir.name
        
        return activity_dir.name
    except Exception as e:
        print(f"Warning: Could not read schema for {activity_dir.name}: {str(e)}")
        return activity_dir.name

def count_items(activity_dir):
    """Count the number of items in the activity's items folder.
    Returns '-' if the items folder doesn't exist."""
    items_dir = activity_dir / "items"
    if not items_dir.exists():
        return "-"
    
    # Count all files in the items directory
    return len([f for f in items_dir.iterdir() if f.is_file()])

def get_activities_with_descriptions():
    """Get list of activities and their descriptions from the activities directory."""
    repo_root = get_repo_root()
    activities_dir = repo_root / "activities"
    
    if not activities_dir.exists():
        raise FileNotFoundError(f"Directory {activities_dir} not found")
    
    # Get all directories and their descriptions
    activities = []
    for idx, activity_dir in enumerate(sorted(activities_dir.iterdir()), 1):
        if activity_dir.is_dir():
            description = get_activity_description(activity_dir)
            item_count = count_items(activity_dir)
            activities.append({
                'id': str(idx),
                'name': activity_dir.name,
                'description': description,
                'item_count': item_count
            })
    
    return activities

def create_markdown_table(activities):
    """Create a markdown table with activity links and descriptions."""
    content = [
        f"*Last updated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC*\n",
        "| **ID** | **Activity** | **# of Items** | **Description** |",
        "|:-----|:-----------|:-----------:|:--------------|"
    ]
    
    for activity in activities:
        activity_link = f"[{activity['name']}](activities/{activity['name']})"
        # Escape pipe characters in description
        safe_description = activity['description'].replace('|', '\\|')
        content.append(f"| {activity['id']} | {activity_link} | {activity['item_count']} | {safe_description} |")
    
    return "\n".join(content)

def update_readme(table_content):
    """Update the README.md file with the new table."""
    repo_root = get_repo_root()
    readme_path = repo_root / "README.md"
    
    if not readme_path.exists():
        raise FileNotFoundError("README.md not found")
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the section pattern (without details/summary tags)
    section_pattern = r'(## Available Activities\s*\n).*?(?=\n##|\Z)'
    
    # Create the new section content
    new_section = f"\\1\n{table_content}\n"
    
    if '## Available Activities' not in content:
        # If section doesn't exist, add it at the end
        section_to_add = f"""## Available Activities
{table_content}"""
        content = content.rstrip() + "\n" + section_to_add + "\n"
    else:
        # Replace the existing section content
        content = re.sub(
            section_pattern,
            new_section,
            content,
            flags=re.DOTALL
        )
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    try:
        activities = get_activities_with_descriptions()
        table = create_markdown_table(activities)
        update_readme(table)
        print("README.md has been successfully updated with the activities table.")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())