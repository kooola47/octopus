#!/usr/bin/env python3
"""
File Operations Plugin
======================
Plugin for file and directory operations
"""

import os
import shutil
import json
from typing import Optional, List

def create_file(filename: str, content: str = "", overwrite: bool = False):
    """
    Create a new file with the specified content.
    
    Args:
        filename: Name of the file to create
        content: Content to write to the file (default: empty)
        overwrite: Whether to overwrite if file exists (default: False)
    
    Returns:
        str: Success message or error details
    """
    try:
        if os.path.exists(filename) and not overwrite:
            return f"Error: File '{filename}' already exists. Set overwrite=True to replace it."
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully created file '{filename}' with {len(content)} characters"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def read_file(filename: str, max_lines: int = 100):
    """
    Read content from a file.
    
    Args:
        filename: Name of the file to read
        max_lines: Maximum number of lines to read (default: 100)
    
    Returns:
        str: File content or error message
    """
    try:
        if not os.path.exists(filename):
            return f"Error: File '{filename}' does not exist"
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) > max_lines:
            content = ''.join(lines[:max_lines])
            content += f"\n... (showing first {max_lines} lines of {len(lines)} total)"
        else:
            content = ''.join(lines)
        
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_directory(path: str = ".", include_hidden: bool = False, file_types: Optional[List[str]] = None):
    """
    List files and directories in the specified path.
    
    Args:
        path: Directory path to list (default: current directory)
        include_hidden: Include hidden files/directories (default: False)
        file_types: List of file extensions to filter (e.g., ['.txt', '.py'])
    
    Returns:
        str: Directory listing or error message
    """
    try:
        if not os.path.exists(path):
            return f"Error: Directory '{path}' does not exist"
        
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory"
        
        items = os.listdir(path)
        
        # Filter hidden files
        if not include_hidden:
            items = [item for item in items if not item.startswith('.')]
        
        # Filter by file types
        if file_types:
            filtered_items = []
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    filtered_items.append(item)  # Include directories
                else:
                    # Check file extension
                    _, ext = os.path.splitext(item)
                    if ext.lower() in [ft.lower() for ft in file_types]:
                        filtered_items.append(item)
            items = filtered_items
        
        # Sort and format
        items.sort()
        result = f"Directory listing for '{path}':\n"
        
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                result += f"  [DIR]  {item}/\n"
            else:
                size = os.path.getsize(item_path)
                result += f"  [FILE] {item} ({size} bytes)\n"
        
        return result if items else f"Directory '{path}' is empty"
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def copy_file(source: str, destination: str, overwrite: bool = False):
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite destination if it exists
    
    Returns:
        str: Success message or error details
    """
    try:
        if not os.path.exists(source):
            return f"Error: Source file '{source}' does not exist"
        
        if os.path.exists(destination) and not overwrite:
            return f"Error: Destination '{destination}' already exists. Set overwrite=True to replace it."
        
        shutil.copy2(source, destination)
        return f"Successfully copied '{source}' to '{destination}'"
        
    except Exception as e:
        return f"Error copying file: {str(e)}"

def delete_file(filename: str, confirm: bool = False):
    """
    Delete a file (requires confirmation).
    
    Args:
        filename: Name of the file to delete
        confirm: Confirmation flag (must be True to actually delete)
    
    Returns:
        str: Success message or error details
    """
    try:
        if not confirm:
            return f"Deletion cancelled. Set confirm=True to actually delete '{filename}'"
        
        if not os.path.exists(filename):
            return f"Error: File '{filename}' does not exist"
        
        os.remove(filename)
        return f"Successfully deleted file '{filename}'"
        
    except Exception as e:
        return f"Error deleting file: {str(e)}"
