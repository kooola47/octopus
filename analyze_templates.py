#!/usr/bin/env python3
"""
Analyze HTML template usage in the octopus server
"""

import os
import re
import glob

def find_html_files():
    """Find all HTML files in pages directory"""
    pages_dir = "octopus_server/pages"
    html_files = []
    for file in os.listdir(pages_dir):
        if file.endswith('.html'):
            html_files.append(file)
    return sorted(html_files)

def find_template_usage():
    """Find template usage in Python files"""
    used_templates = set()
    
    # Search all Python files in routes directory
    route_files = glob.glob("octopus_server/routes/*.py")
    route_files.append("octopus_server/main.py")
    
    template_pattern = r"render_template\(['\"]([^'\"]+\.html)['\"]"
    
    for file_path in route_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(template_pattern, content)
                used_templates.update(matches)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    return used_templates

def find_extended_templates():
    """Find templates that are extended by other templates"""
    extended_templates = set()
    
    pages_dir = "octopus_server/pages"
    for file in os.listdir(pages_dir):
        if file.endswith('.html'):
            file_path = os.path.join(pages_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for {% extends "template.html" %}
                    extends_match = re.search(r'{%\s*extends\s+["\']([^"\']+)["\']', content)
                    if extends_match:
                        extended_templates.add(extends_match.group(1))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return extended_templates

def main():
    print("🔍 HTML Template Usage Analysis")
    print("=" * 50)
    
    # Find all HTML files
    all_html_files = find_html_files()
    print(f"\n📁 Total HTML files found: {len(all_html_files)}")
    
    # Find directly used templates
    used_templates = find_template_usage()
    print(f"🎯 Directly used templates: {len(used_templates)}")
    for template in sorted(used_templates):
        print(f"   ✅ {template}")
    
    # Find extended templates (base templates)
    extended_templates = find_extended_templates()
    print(f"\n🏗️  Base templates (extended by others): {len(extended_templates)}")
    for template in sorted(extended_templates):
        print(f"   📐 {template}")
    
    # Find all used templates (direct + extended)
    all_used = used_templates.union(extended_templates)
    print(f"\n📊 Total used templates: {len(all_used)}")
    
    # Find unused templates
    unused_templates = set(all_html_files) - all_used
    print(f"\n❌ Potentially unused templates: {len(unused_templates)}")
    for template in sorted(unused_templates):
        print(f"   🗑️  {template}")
    
    # Summary
    print(f"\n📈 Summary:")
    print(f"   Total files: {len(all_html_files)}")
    print(f"   Used files: {len(all_used)}")
    print(f"   Unused files: {len(unused_templates)}")
    print(f"   Usage rate: {len(all_used)/len(all_html_files)*100:.1f}%")

if __name__ == "__main__":
    main()
