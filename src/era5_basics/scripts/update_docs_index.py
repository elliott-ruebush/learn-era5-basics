#!/usr/bin/env python3
import os
from pathlib import Path

def extract_h1(file_path: Path) -> str | None:
    """Extracts the first H1 header from a markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception:
        pass
    return None

def generate_toc(project_root: Path) -> str:
    docs_dir = project_root / "docs"
    lines = ["<!-- START_TOC -->", ""]
    
    if not docs_dir.exists():
        lines.append("No documentation found.")
        lines.extend(["", "<!-- END_TOC -->"])
        return "\n".join(lines)

    # Filter out README.md in docs if it exists
    items = sorted([item for item in docs_dir.iterdir() if item.name != "README.md"], 
                  key=lambda x: (not x.is_file(), x.name.lower()))
    
    for item in items:
        if item.is_file() and item.suffix == ".md":
            title = extract_h1(item) or item.stem.replace("-", " ").replace("_", " ").title()
            rel_path = item.relative_to(project_root)
            lines.append(f"* [{title}]({rel_path})")
            
        elif item.is_dir():
            dir_name = item.name.replace("-", " ").replace("_", " ").title()
            lines.append(f"* **{dir_name}**")
            sub_items = sorted(item.glob("*.md"))
            for sub_item in sub_items:
                sub_title = extract_h1(sub_item) or sub_item.stem.replace("-", " ").replace("_", " ").title()
                sub_rel_path = sub_item.relative_to(project_root)
                lines.append(f"    * [{sub_title}]({sub_rel_path})")
    
    lines.extend(["", "<!-- END_TOC -->"])
    return "\n".join(lines)

def update_readme(project_root: Path):
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        print(f"Error: {readme_path} not found.")
        return
    
    content = readme_path.read_text()
    toc = generate_toc(project_root)
    
    start_marker = "<!-- START_TOC -->"
    end_marker = "<!-- END_TOC -->"
    
    if start_marker in content and end_marker in content:
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker) + len(end_marker)
        new_content = content[:start_idx] + toc + content[end_idx:]
        readme_path.write_text(new_content)
        print(f"Updated {readme_path}")
    else:
        # If markers aren't there, append them under a Documentation header if it exists
        if "## Documentation" in content:
            print(f"Markers not found in {readme_path}, but Documentation header exists. Inserting TOC...")
            new_content = content.replace("## Documentation", f"## Documentation\n\n{toc}")
            readme_path.write_text(new_content)
        else:
            print(f"Markers not found in {readme_path}. Please add <!-- START_TOC --> and <!-- END_TOC -->.")

def main():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    update_readme(project_root)

if __name__ == "__main__":
    main()
