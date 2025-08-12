#!/usr/bin/env python3
"""
Plugin Discovery System
=======================
Dynamically discovers plugins and extracts their function signatures and parameters
"""

import os
import ast
import inspect
import importlib.util
import sys
from typing import Dict, List, Any, Optional
import logging

class PluginDiscovery:
    """Dynamically discover and analyze plugins"""
    
    def __init__(self, plugins_folder: str):
        self.plugins_folder = plugins_folder
        self.logger = logging.getLogger(__name__)
        
    def get_plugins_with_metadata(self) -> Dict[str, Any]:
        """
        Get all plugins with their functions and parameter metadata
        
        Returns:
            Dict: {
                'plugin_name': {
                    'file': 'plugin_file.py',
                    'description': 'Plugin description',
                    'functions': {
                        'function_name': {
                            'description': 'Function description',
                            'parameters': [
                                {
                                    'name': 'param_name',
                                    'type': 'str',
                                    'default': 'default_value',
                                    'required': True,
                                    'description': 'Parameter description'
                                }
                            ],
                            'nlp_keywords': ['keyword1', 'keyword2'],
                            'nlp_examples': ['example1', 'example2']
                        }
                    }
                }
            }
        """
        plugins = {}
        
        if not os.path.exists(self.plugins_folder):
            self.logger.warning(f"Plugins folder not found: {self.plugins_folder}")
            return plugins
            
        for filename in os.listdir(self.plugins_folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                plugin_name = filename[:-3]  # Remove .py extension
                plugin_path = os.path.join(self.plugins_folder, filename)
                
                try:
                    plugin_info = self._analyze_plugin_file(plugin_path, plugin_name)
                    if plugin_info:
                        plugins[plugin_name] = plugin_info
                except Exception as e:
                    self.logger.error(f"Error analyzing plugin {filename}: {e}")
                    
        return plugins
    
    def _analyze_plugin_file(self, plugin_path: str, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Analyze a single plugin file to extract metadata"""
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the AST
            tree = ast.parse(content)
            
            plugin_info = {
                'file': os.path.basename(plugin_path),
                'description': self._extract_module_docstring(tree),
                'functions': {}
            }
            
            # Extract function information
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node, content)
                    if func_info:
                        plugin_info['functions'][node.name] = func_info
                        
            return plugin_info if plugin_info['functions'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing {plugin_path}: {e}")
            return None
    
    def _extract_module_docstring(self, tree: ast.AST) -> str:
        """Extract module-level docstring"""
        if (isinstance(tree, ast.Module) and 
            tree.body and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Constant)):
            return tree.body[0].value.value
        return ""
    
    def _analyze_function(self, func_node: ast.FunctionDef, content: str) -> Optional[Dict[str, Any]]:
        """Analyze a function to extract its metadata"""
        # Skip private functions (starting with _)
        if func_node.name.startswith('_'):
            return None
            
        func_info = {
            'description': self._extract_function_docstring(func_node),
            'parameters': [],
            'nlp_keywords': [],
            'nlp_examples': []
        }
        
        # Extract parameters
        for arg in func_node.args.args:
            param_info = self._extract_parameter_info(arg, func_node)
            if param_info:
                func_info['parameters'].append(param_info)
        
        # Extract NLP metadata from docstring and comments
        nlp_data = self._extract_nlp_metadata(func_node, content)
        func_info.update(nlp_data)
        
        return func_info
    
    def _extract_function_docstring(self, func_node: ast.FunctionDef) -> str:
        """Extract function docstring"""
        if (func_node.body and 
            isinstance(func_node.body[0], ast.Expr) and 
            isinstance(func_node.body[0].value, ast.Constant)):
            return func_node.body[0].value.value
        return ""
    
    def _extract_parameter_info(self, arg: ast.arg, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract parameter information including type hints and defaults"""
        param_info = {
            'name': arg.arg,
            'type': 'Any',
            'default': None,
            'required': True,
            'description': ''
        }
        
        # Extract type annotation
        if arg.annotation:
            param_info['type'] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else 'Any'
        
        # Extract default values
        defaults = func_node.args.defaults
        args_count = len(func_node.args.args)
        defaults_count = len(defaults)
        
        if defaults_count > 0:
            # Calculate if this parameter has a default
            param_index = func_node.args.args.index(arg)
            default_index = param_index - (args_count - defaults_count)
            
            if default_index >= 0:
                default_value = defaults[default_index]
                if isinstance(default_value, ast.Constant):
                    param_info['default'] = default_value.value
                    param_info['required'] = False
                elif hasattr(ast, 'unparse'):
                    param_info['default'] = ast.unparse(default_value)
                    param_info['required'] = False
        
        return param_info
    
    def _extract_nlp_metadata(self, func_node: ast.FunctionDef, content: str) -> Dict[str, List[str]]:
        """Extract NLP keywords and examples from function docstring and comments"""
        nlp_data = {
            'nlp_keywords': [],
            'nlp_examples': []
        }
        
        # Get function docstring
        docstring = self._extract_function_docstring(func_node)
        
        # Parse NLP metadata from docstring
        lines = docstring.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# NLP: keywords:'):
                keywords = line.replace('# NLP: keywords:', '').strip()
                nlp_data['nlp_keywords'].extend([k.strip() for k in keywords.split(',')])
            elif line.startswith('# NLP: example:'):
                example = line.replace('# NLP: example:', '').strip()
                nlp_data['nlp_examples'].append(example)
        
        return nlp_data
    
    def get_plugin_functions(self, plugin_name: str) -> List[str]:
        """Get list of function names for a specific plugin"""
        plugins = self.get_plugins_with_metadata()
        if plugin_name in plugins:
            return list(plugins[plugin_name]['functions'].keys())
        return []
    
    def get_function_parameters(self, plugin_name: str, function_name: str) -> List[Dict[str, Any]]:
        """Get parameters for a specific plugin function"""
        plugins = self.get_plugins_with_metadata()
        if (plugin_name in plugins and 
            function_name in plugins[plugin_name]['functions']):
            return plugins[plugin_name]['functions'][function_name]['parameters']
        return []

# Example usage and testing
if __name__ == "__main__":
    # Test the plugin discovery
    plugins_folder = "plugins"
    discovery = PluginDiscovery(plugins_folder)
    plugins = discovery.get_plugins_with_metadata()
    
    print("Discovered plugins:")
    for plugin_name, plugin_info in plugins.items():
        print(f"\n{plugin_name}:")
        print(f"  Description: {plugin_info['description'][:100]}...")
        print(f"  Functions: {list(plugin_info['functions'].keys())}")
        
        for func_name, func_info in plugin_info['functions'].items():
            print(f"    {func_name}:")
            print(f"      Params: {[p['name'] for p in func_info['parameters']]}")
