#!/usr/bin/env python3
import main
import os

app = main.app

# Check if files exist
monaco_dir = 'static/monaco-editor/vs'
files_to_check = [
    'loader.js',
    'editor/editor.main.js', 
    'editor/editor.main.css'
]

print("Checking Monaco Editor files:")
for file_path in files_to_check:
    full_path = os.path.join(monaco_dir, file_path)
    exists = os.path.exists(full_path)
    size = os.path.getsize(full_path) if exists else 0
    print(f"  {file_path}: {'✅' if exists else '❌'} ({size} bytes)")

# Test static routes
with app.test_client() as client:
    print("\nTesting static file routes:")
    for file_path in files_to_check:
        url = f'/static/monaco-editor/vs/{file_path}'
        response = client.get(url)
        print(f"  {url}: {response.status_code}")
