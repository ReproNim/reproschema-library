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

def get_activities_with_descriptions():
    """Get list of activities and their descriptions from the activities directory."""
    repo_root = get_repo_root()
    activities_dir = repo_root / "activities"
    
    if not activities_dir.exists():
        raise FileNotFoundError(f"Directory {activities_dir} not found")
    
    # Get all directories and their descriptions
    activities = []
    for activity_dir in sorted(activities_dir.iterdir()):
        if activity_dir.is_dir():
            description = get_activity_description(activity_dir)
            activities.append({
                'name': activity_dir.name,
                'description': description
            })
    
    return activities

def create_markdown_table(activities):
    """Create a markdown table with activity links and descriptions."""
    content = [
        f"*Last updated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC*\n",
        "| *Activity* | *Description* |",
        "|----------|-------------|"
    ]
    
    for activity in activities:
        activity_link = f"[{activity['name']}](activities/{activity['name']})"
        # Escape pipe characters in description
        safe_description = activity['description'].replace('|', '\\|')
        content.append(f"| {activity_link} | {safe_description} |")
    
    return "\n".join(content)

def update_readme(table_content):
    """Update the README.md file with the new table inside the details tag."""
    repo_root = get_repo_root()
    readme_path = repo_root / "README.md"
    
    if not readme_path.exists():
        raise FileNotFoundError("README.md not found")
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the section pattern
    section_pattern = r'(## Available Activities\s*\n\s*<details>\s*\n\s*<summary>.*?</summary>\s*\n).*?(\s*</details>)'
    
    # Create the new section content
    new_section = f"\n{table_content}\n"
    
    if '## Available Activities' not in content:
        # If section doesn't exist, add it at the end
        section_to_add = f"""
## Available Activities

<details>
<summary>Click to expand/collapse the activities list</summary>

{table_content}

</details>
"""
        content = content.rstrip() + "\n" + section_to_add + "\n"
    else:
        # Replace the existing section content
        content = re.sub(
            section_pattern,
            f"\\1{new_section}\\2",
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