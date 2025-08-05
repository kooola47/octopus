#!/usr/bin/env python3
"""
Data Processing Plugin
======================
Plugin for data manipulation and processing tasks

# NLP: keywords: process numbers, calculate, math, statistics, data analysis, json, text analysis, sort data, generate data
# NLP: example: Process numbers 1,2,3,4,5 with operation sum
# NLP: example: Calculate math expression 2 + 3 * 4
# NLP: example: Generate 10 random numbers between 1 and 100
# NLP: example: Analyze text content for word frequency
# NLP: example: Sort data items by length
# NLP: example: Validate and pretty print JSON data
"""

import json
import csv
import math
import statistics
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

def process_numbers(numbers: str, operation: str = "sum"):
    """
    Process a list of numbers with various operations.
    
    # NLP: keywords: process numbers, calculate numbers, sum, average, median, statistics
    # NLP: example: Process numbers 10,20,30,40,50 with sum operation
    # NLP: example: Calculate average of numbers 5,15,25,35
    
    Args:
        numbers: Comma-separated list of numbers (e.g., "1,2,3,4,5")
        operation: Operation to perform (sum, avg, min, max, median)
    
    Returns:
        str: Result of the operation
    """
    try:
        # Parse numbers
        num_list = [float(x.strip()) for x in numbers.split(',')]
        
        if not num_list:
            return "Error: No numbers provided"
        
        operation = operation.lower()
        
        if operation == "sum":
            result = sum(num_list)
        elif operation == "avg" or operation == "average":
            result = statistics.mean(num_list)
        elif operation == "min":
            result = min(num_list)
        elif operation == "max":
            result = max(num_list)
        elif operation == "median":
            result = statistics.median(num_list)
        elif operation == "std" or operation == "stdev":
            result = statistics.stdev(num_list) if len(num_list) > 1 else 0
        else:
            return f"Error: Unknown operation '{operation}'. Available: sum, avg, min, max, median, std"
        
        return f"Operation '{operation}' on {len(num_list)} numbers: {result}"
        
    except ValueError as e:
        return f"Error: Invalid number format - {str(e)}"
    except Exception as e:
        return f"Error processing numbers: {str(e)}"

def generate_data(data_type: str = "numbers", count: int = 10, min_val: int = 1, max_val: int = 100):
    """
    Generate sample data for testing.
    
    # NLP: keywords: generate data, create numbers, random data, sample data, test data
    # NLP: example: Generate 20 random numbers between 1 and 100
    # NLP: example: Create 15 random dates for testing
    # NLP: example: Generate 5 random names
    
    Args:
        data_type: Type of data to generate (numbers, dates, names)
        count: Number of items to generate (default: 10)
        min_val: Minimum value for numbers (default: 1)
        max_val: Maximum value for numbers (default: 100)
    
    Returns:
        str: Generated data
    """
    try:
        import random
        
        data_type = data_type.lower()
        
        if data_type == "numbers":
            data = [random.randint(min_val, max_val) for _ in range(count)]
            return f"Generated {count} random numbers: {', '.join(map(str, data))}"
        
        elif data_type == "dates":
            start_date = datetime.now() - timedelta(days=365)
            data = []
            for _ in range(count):
                random_days = random.randint(0, 365)
                date = start_date + timedelta(days=random_days)
                data.append(date.strftime("%Y-%m-%d"))
            return f"Generated {count} random dates: {', '.join(data)}"
        
        elif data_type == "names":
            first_names = ["Alice", "Bob", "Charlie", "Diana", "Edward", "Fiona", "George", "Helen"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            data = []
            for _ in range(count):
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                data.append(name)
            return f"Generated {count} random names: {', '.join(data)}"
        
        else:
            return f"Error: Unknown data type '{data_type}'. Available: numbers, dates, names"
        
    except Exception as e:
        return f"Error generating data: {str(e)}"

def convert_json(data: str, operation: str = "validate"):
    """
    Perform operations on JSON data.
    
    Args:
        data: JSON string to process
        operation: Operation to perform (validate, pretty, minify, keys)
    
    Returns:
        str: Result of the operation
    """
    try:
        # Parse JSON
        parsed_data = json.loads(data)
        
        operation = operation.lower()
        
        if operation == "validate":
            return f"JSON is valid. Type: {type(parsed_data).__name__}"
        
        elif operation == "pretty":
            return json.dumps(parsed_data, indent=2, ensure_ascii=False)
        
        elif operation == "minify":
            return json.dumps(parsed_data, separators=(',', ':'))
        
        elif operation == "keys":
            if isinstance(parsed_data, dict):
                keys = list(parsed_data.keys())
                return f"JSON keys ({len(keys)}): {', '.join(keys)}"
            else:
                return f"JSON is not an object. Type: {type(parsed_data).__name__}"
        
        elif operation == "size":
            if isinstance(parsed_data, (list, dict, str)):
                return f"JSON size: {len(parsed_data)} items"
            else:
                return f"JSON value: {parsed_data}"
        
        else:
            return f"Error: Unknown operation '{operation}'. Available: validate, pretty, minify, keys, size"
        
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON - {str(e)}"
    except Exception as e:
        return f"Error processing JSON: {str(e)}"

def text_analysis(text: str, analysis_type: str = "basic"):
    """
    Analyze text content.
    
    Args:
        text: Text content to analyze
        analysis_type: Type of analysis (basic, words, chars, lines)
    
    Returns:
        str: Analysis results
    """
    try:
        analysis_type = analysis_type.lower()
        
        if analysis_type == "basic":
            char_count = len(text)
            word_count = len(text.split())
            line_count = len(text.split('\n'))
            
            result = f"Text Analysis:\n"
            result += f"  Characters: {char_count}\n"
            result += f"  Words: {word_count}\n"
            result += f"  Lines: {line_count}\n"
            
            return result
        
        elif analysis_type == "words":
            words = text.split()
            word_freq = {}
            for word in words:
                word = word.lower().strip('.,!?;:"()[]{}')
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top 10 most frequent words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            result = f"Word Frequency Analysis (Top 10):\n"
            for word, count in top_words:
                result += f"  '{word}': {count}\n"
            
            return result
        
        elif analysis_type == "chars":
            char_freq = {}
            for char in text.lower():
                if char.isalpha():
                    char_freq[char] = char_freq.get(char, 0) + 1
            
            # Get top 10 most frequent characters
            top_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            result = f"Character Frequency Analysis (Top 10):\n"
            for char, count in top_chars:
                result += f"  '{char}': {count}\n"
            
            return result
        
        elif analysis_type == "lines":
            lines = text.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            result = f"Line Analysis:\n"
            result += f"  Total lines: {len(lines)}\n"
            result += f"  Non-empty lines: {len(non_empty_lines)}\n"
            result += f"  Empty lines: {len(lines) - len(non_empty_lines)}\n"
            
            if non_empty_lines:
                line_lengths = [len(line) for line in non_empty_lines]
                result += f"  Average line length: {statistics.mean(line_lengths):.1f} chars\n"
                result += f"  Longest line: {max(line_lengths)} chars\n"
                result += f"  Shortest line: {min(line_lengths)} chars\n"
            
            return result
        
        else:
            return f"Error: Unknown analysis type '{analysis_type}'. Available: basic, words, chars, lines"
        
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def calculate_math(expression: str, precision: int = 2):
    """
    Evaluate mathematical expressions safely.
    
    # NLP: keywords: calculate math, evaluate expression, mathematical calculation, compute formula
    # NLP: example: Calculate math expression 2 + 3 * sqrt(16)
    # NLP: example: Compute formula sin(pi/4) + cos(pi/3)
    
    Args:
        expression: Mathematical expression to evaluate
        precision: Number of decimal places for result (default: 2)
    
    Returns:
        str: Calculation result
    """
    try:
        # Only allow safe mathematical operations
        allowed_names = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sum': sum, 'pow': pow,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'log': math.log, 'log10': math.log10, 'exp': math.exp,
            'pi': math.pi, 'e': math.e
        }
        
        # Evaluate expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        if isinstance(result, float):
            result = round(result, precision)
        
        return f"Expression: {expression}\nResult: {result}"
        
    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError:
        return f"Error: Invalid expression syntax - {expression}"
    except NameError as e:
        return f"Error: Unknown function or variable - {str(e)}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

def sort_data(data: str, sort_type: str = "text", reverse: bool = False):
    """
    Sort data in various ways.
    
    Args:
        data: Comma-separated data to sort
        sort_type: Type of sort (text, numeric, length)
        reverse: Sort in descending order (default: False)
    
    Returns:
        str: Sorted data
    """
    try:
        items = [item.strip() for item in data.split(',')]
        
        sort_type = sort_type.lower()
        
        if sort_type == "text":
            sorted_items = sorted(items, reverse=reverse)
        elif sort_type == "numeric":
            try:
                numeric_items = [(float(item), item) for item in items]
                sorted_items = [item[1] for item in sorted(numeric_items, reverse=reverse)]
            except ValueError:
                return "Error: Cannot convert all items to numbers for numeric sort"
        elif sort_type == "length":
            sorted_items = sorted(items, key=len, reverse=reverse)
        else:
            return f"Error: Unknown sort type '{sort_type}'. Available: text, numeric, length"
        
        order = "descending" if reverse else "ascending"
        return f"Sorted {len(items)} items ({sort_type}, {order}): {', '.join(sorted_items)}"
        
    except Exception as e:
        return f"Error sorting data: {str(e)}"
