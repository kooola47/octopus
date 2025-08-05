#!/usr/bin/env python3
"""
🐙 OCTOPUS NLP PROCESSOR - Natural Language Task Creation
========================================================

Natural language processing module that converts user input into task definitions.
Uses spaCy for NLP and pattern matching to extract task components.
"""

import spacy
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import threading

# Configure logging
logger = logging.getLogger("octopus_nlp")

class TaskNLPProcessor:
    """
    Natural Language Processor for converting text to task definitions
    Thread-safe singleton implementation for performance
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, static_data_file: Optional[str] = None, plugins_folder: str = "plugins"):
        # Avoid re-initialization in singleton
        if self._initialized:
            return
            
        with self._lock:
            if self._initialized:
                return
                
            """Initialize the NLP processor with spaCy model and optional static data"""
            try:
                # Try to load the English model
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy English model successfully")
            except OSError:
                logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
            
            # Load static data mappings for shortcuts
            self.static_mappings = self._load_static_data(static_data_file)
            
            # Load plugin comments for better understanding
            self.plugin_metadata = self._load_plugin_metadata(plugins_folder)
            
            self._initialized = True
        
        # Define patterns for extracting task components with enhanced coverage
        self.action_patterns = {
            'create_incident': [
                r'create.*incident', r'report.*issue', r'file.*ticket', r'log.*problem',
                r'raise.*alert', r'submit.*bug', r'open.*case', r'incident.*report',
                r'new.*incident', r'issue.*creation', r'problem.*report', r'alert.*creation',
                r'ticket.*creation', r'bug.*report', r'case.*opening'
            ],
            'backup_database': [
                r'backup.*database', r'backup.*db', r'create.*backup', r'dump.*database',
                r'export.*data', r'archive.*database', r'database.*backup', r'db.*backup',
                r'data.*backup', r'backup.*data', r'database.*dump', r'db.*dump'
            ],
            'file_operations': [
                r'create.*file', r'read.*file', r'list.*directory', r'copy.*file', r'delete.*file',
                r'new.*file', r'write.*file', r'make.*file', r'open.*file', r'view.*file',
                r'display.*file', r'show.*files', r'directory.*listing', r'browse.*folder',
                r'ls.*command', r'duplicate.*file', r'backup.*file', r'cp.*command',
                r'remove.*file', r'rm.*command', r'erase.*file', r'file.*operations'
            ],
            'data_processing': [
                r'process.*numbers', r'calculate.*math', r'math.*expression', r'statistics',
                r'data.*analysis', r'json.*data', r'text.*analysis', r'sort.*data',
                r'generate.*data', r'calculate.*numbers', r'sum.*operation', r'average.*numbers',
                r'median.*numbers', r'random.*numbers', r'sample.*data', r'test.*data',
                r'compute.*formula', r'evaluate.*expression', r'mathematical.*calculation'
            ],
            'notifications': [
                r'send.*notification', r'send.*alert', r'notify.*user', r'send.*message',
                r'email.*notification', r'sms.*notification', r'push.*notification',
                r'remind.*user', r'alert.*team', r'notification.*email', r'simple.*notification',
                r'basic.*alert', r'quick.*message', r'async.*notification', r'delayed.*alert',
                r'retry.*notification'
            ],
            'system_info': [
                r'system.*info', r'cpu.*usage', r'memory.*usage', r'disk.*space',
                r'performance.*monitoring', r'server.*stats', r'get.*system.*info',
                r'show.*system.*details', r'server.*information', r'processor.*usage',
                r'cpu.*load', r'system.*performance', r'ram.*usage', r'memory.*stats',
                r'available.*memory', r'run.*command', r'execute.*command', r'system.*command',
                r'shell.*command', r'disk.*usage', r'storage.*usage', r'free.*space'
            ],
            'web_utils': [
                r'fetch.*url', r'http.*request', r'web.*scraping', r'api.*call',
                r'download.*content', r'post.*request', r'get.*request', r'check.*url.*status',
                r'url.*health.*check', r'website.*status', r'ping.*urls', r'monitor.*websites',
                r'url.*encode', r'url.*decode', r'percent.*encoding', r'escape.*url',
                r'unescape.*url', r'parse.*url', r'url.*components', r'break.*down.*url',
                r'analyze.*url', r'generate.*qr.*code', r'create.*qr.*code', r'qr.*code.*url',
                r'barcode', r'validate.*email', r'check.*email', r'email.*validation',
                r'verify.*email.*address'
            ],
            'send_email': [
                r'send.*email', r'email.*to', r'mail.*notification', r'notify.*via.*email',
                r'send.*message', r'alert.*email', r'email.*alert', r'notification.*email',
                r'message.*sending', r'mail.*to', r'email.*notification', r'send.*notification'
            ],
            'cleanup_logs': [
                r'clean.*logs?', r'delete.*logs?', r'remove.*old.*files?', r'purge.*logs?',
                r'cleanup.*logs?', r'clear.*logs?', r'log.*cleanup', r'log.*removal',
                r'delete.*old.*logs?', r'remove.*log.*files?', r'purge.*old.*files?',
                r'cleanup.*files?', r'clear.*logs?'
            ],
            'monitor_system': [
                r'monitor.*system', r'check.*health', r'watch.*performance', r'track.*metrics',
                r'observe.*status', r'surveillance'
            ],
            'generate_report': [
                r'generate.*report', r'create.*report', r'build.*summary', r'compile.*data',
                r'produce.*analysis', r'make.*report'
            ]
        }
        
        # Priority patterns
        self.priority_patterns = {
            'P1': [r'urgent', r'critical', r'emergency', r'asap', r'immediately', r'high priority'],
            'P2': [r'important', r'medium priority', r'moderate'],
            'P3': [r'low priority', r'when possible', r'eventually', r'minor'],
            'P4': [r'lowest', r'trivial', r'cosmetic']
        }
        
        # Time patterns for scheduling
        self.time_patterns = {
            'immediate': [r'now', r'immediately', r'asap', r'right away'],
            'hourly': [r'every hour', r'hourly', r'each hour'],
            'daily': [r'daily', r'every day', r'each day', r'once a day'],
            'weekly': [r'weekly', r'every week', r'each week', r'once a week'],
            'monthly': [r'monthly', r'every month', r'each month', r'once a month']
        }
        
        # Owner/assignee patterns
        self.owner_patterns = {
            'anyone': [r'anyone', r'any client', r'any available', r'whoever'],
            'all': [r'all clients', r'everyone', r'all machines', r'broadcast']
        }

    def is_available(self) -> bool:
        """Check if NLP processor is available"""
        return self.nlp is not None

    def parse_natural_language(self, text: str) -> Dict:
        """
        Parse natural language text into task components
        
        Args:
            text: Natural language description of the task
            
        Returns:
            Dictionary containing parsed task components
        """
        if not self.is_available():
            return {"error": "NLP processor not available. Install spaCy model."}
        
        logger.info(f"Processing natural language input: {text}")
        
        # Expand shortcuts using static data mappings
        expanded_text = self._expand_shortcuts(text)
        if expanded_text != text.lower():
            logger.info(f"Expanded shortcuts: '{text}' → '{expanded_text}'")
        
        # Process text with spaCy
        doc = self.nlp(expanded_text)
        
        # Initialize result structure
        result = {
            "success": True,
            "task": {
                "owner": "Anyone",
                "plugin": None,
                "action": "main",
                "args": [],
                "kwargs": {},
                "type": "Adhoc",
                "priority": "P3"
            },
            "confidence": 0.0,
            "extracted_entities": [],
            "suggestions": [],
            "expanded_text": expanded_text if expanded_text != text.lower() else None
        }
        
        # Extract entities
        entities = self._extract_entities(doc, text)
        result["extracted_entities"] = entities
        
        # Determine action/plugin
        plugin, action, confidence = self._determine_action(expanded_text)
        if plugin:
            result["task"]["plugin"] = plugin
            result["task"]["action"] = action
            
            # Enhance confidence with plugin metadata
            confidence = self._enhance_confidence_with_plugin_metadata(expanded_text, plugin, confidence)
            
            result["confidence"] += confidence * 0.5  # Increased weight for action detection
        
        # Extract priority
        priority = self._extract_priority(text)
        if priority:
            result["task"]["priority"] = priority
            result["confidence"] += 0.15  # Increased from 0.1
        
        # Extract parameters from entities and text
        args, kwargs = self._extract_parameters(entities, text, plugin)
        result["task"]["args"] = args
        result["task"]["kwargs"] = kwargs
        
        # Boost confidence based on parameter completeness
        if kwargs:
            param_score = len(kwargs) * 0.05  # 5% per parameter
            result["confidence"] += min(0.2, param_score)
        
        # Determine owner/assignee
        owner = self._extract_owner(text)
        if owner:
            result["task"]["owner"] = owner
            result["confidence"] += 0.1
        
        # Extract scheduling information
        schedule_info = self._extract_schedule(text)
        if schedule_info:
            result["task"].update(schedule_info)
            result["confidence"] += 0.15  # Increased from 0.2
        
        # Boost confidence for entity recognition
        if entities:
            entity_score = len(entities) * 0.03  # 3% per entity
            result["confidence"] += min(0.15, entity_score)
        
        # Penalty for very short or very long texts
        text_length = len(text.split())
        if text_length < 3:
            result["confidence"] *= 0.8  # 20% penalty for very short text
        elif text_length > 50:
            result["confidence"] *= 0.9  # 10% penalty for very long text
        
        # Generate suggestions
        result["suggestions"] = self._generate_suggestions(text, entities)
        
        # Normalize confidence score
        result["confidence"] = min(1.0, result["confidence"])
        
        logger.info(f"NLP processing complete. Confidence: {result['confidence']:.2f}")
        return result

    def _extract_entities(self, doc, original_text: str) -> List[Dict]:
        """Extract named entities from the text"""
        entities = []
        
        # spaCy named entities
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_),
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, original_text):
            entities.append({
                "text": match.group(),
                "label": "EMAIL",
                "description": "Email address",
                "start": match.start(),
                "end": match.end()
            })
        
        # Extract file paths
        path_pattern = r'[A-Za-z]:\\[^\\/:*?"<>|\r\n]+|/[^\\/:*?"<>|\r\n]+'
        for match in re.finditer(path_pattern, original_text):
            entities.append({
                "text": match.group(),
                "label": "PATH",
                "description": "File or directory path",
                "start": match.start(),
                "end": match.end()
            })
        
        # Extract numbers that might be parameters
        number_pattern = r'\b\d+\b'
        for match in re.finditer(number_pattern, original_text):
            entities.append({
                "text": match.group(),
                "label": "NUMBER",
                "description": "Numeric value",
                "start": match.start(),
                "end": match.end()
            })
        
        return entities

    def _determine_action(self, text: str) -> Tuple[Optional[str], str, float]:
        """Determine the most likely plugin and action from text with improved confidence scoring"""
        text_lower = text.lower()
        best_match = None
        best_score = 0.0
        best_action = "main"  # Default fallback
        match_count = 0
        
        # Plugin-specific action mappings based on common keywords
        plugin_action_mappings = {
            "web_utils": {
                "fetch": "fetch_url",
                "download": "fetch_url", 
                "get": "fetch_url",
                "request": "fetch_url",
                "check": "check_url_status",
                "status": "check_url_status",
                "validate": "validate_email",
                "email": "validate_email",
                "parse": "parse_url",
                "qr": "generate_qr_code",
                "shorten": "shorten_url_info",
                "encode": "encode_decode_url",
                "decode": "encode_decode_url"
            },
            "file_operations": {
                "list": "list_files",
                "copy": "copy_file", 
                "move": "move_file",
                "delete": "delete_file",
                "create": "create_file",
                "read": "read_file",
                "write": "write_file",
                "search": "search_files"
            },
            "notifications": {
                "send": "send_notification",
                "notify": "send_notification",
                "alert": "send_notification",
                "email": "send_email",
                "slack": "send_slack_message"
            },
            "system_info": {
                "info": "get_system_info",
                "status": "get_system_info",
                "disk": "get_disk_usage",
                "memory": "get_memory_usage",
                "cpu": "get_cpu_usage",
                "process": "get_running_processes"
            }
        }
        
        for plugin, patterns in self.action_patterns.items():
            plugin_score = 0.0
            plugin_matches = 0
            
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    plugin_matches += 1
                    match_count += 1
                    
                    # Improved scoring system:
                    # 1. Base score for pattern match
                    base_score = 0.3
                    
                    # 2. Bonus for exact keyword matches
                    if pattern in text_lower:
                        base_score += 0.2
                    
                    # 3. Bonus for pattern specificity (longer patterns are more specific)
                    specificity_bonus = min(0.3, len(pattern) / 20)
                    
                    # 4. Bonus for multiple pattern matches in same plugin
                    multi_match_bonus = min(0.2, plugin_matches * 0.05)
                    
                    current_score = base_score + specificity_bonus + multi_match_bonus
                    plugin_score = max(plugin_score, current_score)
            
            if plugin_score > best_score:
                best_score = plugin_score
                best_match = plugin
                
                # Determine the best action for this plugin
                if plugin in plugin_action_mappings:
                    for keyword, action in plugin_action_mappings[plugin].items():
                        if keyword in text_lower:
                            best_action = action
                            break
        
        # Additional confidence boost for clear action words
        action_words = ['create', 'send', 'backup', 'cleanup', 'generate', 'run', 'execute', 'schedule']
        for word in action_words:
            if word in text_lower:
                best_score += 0.1
                break
        
        if best_match:
            return best_match, best_action, min(1.0, best_score)
        
        return None, "main", 0.0

    def _extract_priority(self, text: str) -> Optional[str]:
        """Extract priority level from text"""
        text_lower = text.lower()
        
        for priority, patterns in self.priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return priority
        
        return None

    def _extract_owner(self, text: str) -> Optional[str]:
        """Extract task owner/assignee from text"""
        text_lower = text.lower()
        
        for owner_type, patterns in self.owner_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return owner_type.upper() if owner_type == 'all' else owner_type.title()
        
        return None

    def _extract_schedule(self, text: str) -> Dict:
        """Extract scheduling information from text"""
        text_lower = text.lower()
        schedule_info = {}
        
        # Check for scheduling patterns
        for schedule_type, patterns in self.time_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if schedule_type == 'immediate':
                        schedule_info["execution_start_time"] = datetime.now().isoformat()
                    elif schedule_type == 'hourly':
                        schedule_info["type"] = "Schedule"
                        schedule_info["interval"] = 3600
                    elif schedule_type == 'daily':
                        schedule_info["type"] = "Schedule"
                        schedule_info["interval"] = 86400
                    elif schedule_type == 'weekly':
                        schedule_info["type"] = "Schedule"
                        schedule_info["interval"] = 604800
                    elif schedule_type == 'monthly':
                        schedule_info["type"] = "Schedule"
                        schedule_info["interval"] = 2592000
                    break
        
        # Extract specific times (basic patterns)
        time_match = re.search(r'at (\d{1,2}):(\d{2})', text_lower)
        if time_match:
            hour, minute = time_match.groups()
            now = datetime.now()
            scheduled_time = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            if scheduled_time < now:
                scheduled_time += timedelta(days=1)
            schedule_info["execution_start_time"] = scheduled_time.isoformat()
        
        return schedule_info

    def _extract_parameters(self, entities: List[Dict], text: str, plugin: str) -> Tuple[List, Dict]:
        """Extract function parameters based on plugin type and entities"""
        args = []
        kwargs = {}
        
        if not plugin:
            return args, kwargs
        
        # Plugin-specific parameter extraction
        if plugin == 'create_incident':
            # Extract priority and description
            priority = None
            description = text
            
            # Look for priority in entities or text
            for entity in entities:
                if entity['label'] in ['PRIORITY', 'CARDINAL']:
                    priority = entity['text']
            
            if not priority:
                priority = self._extract_priority(text) or 'P3'
            
            kwargs = {
                "priority": priority,
                "description": description
            }
        
        elif plugin == 'send_email':
            # Extract recipient and subject
            recipient = None
            subject = "Automated notification"
            message = text
            
            for entity in entities:
                if entity['label'] == 'EMAIL':
                    recipient = entity['text']
                elif entity['label'] == 'PERSON':
                    if not recipient:
                        recipient = entity['text']
            
            # Extract subject from quotes or after "subject:"
            subject_match = re.search(r'subject[:\s]+"([^"]+)"', text, re.IGNORECASE)
            if subject_match:
                subject = subject_match.group(1)
            
            kwargs = {
                "recipient": recipient or "admin@example.com",
                "subject": subject,
                "message": message
            }
        
        elif plugin == 'backup_database':
            # Extract database name and path
            database = "default"
            backup_path = "/tmp/backup"
            
            for entity in entities:
                if entity['label'] == 'PATH':
                    backup_path = entity['text']
                elif entity['label'] in ['ORG', 'PRODUCT']:
                    database = entity['text']
            
            kwargs = {
                "database": database,
                "backup_path": backup_path
            }
        
        elif plugin == 'cleanup_logs':
            # Extract path and age
            log_path = "/var/log"
            days_old = 30
            
            for entity in entities:
                if entity['label'] == 'PATH':
                    log_path = entity['text']
                elif entity['label'] == 'NUMBER':
                    try:
                        days_old = int(entity['text'])
                    except ValueError:
                        pass
            
            kwargs = {
                "log_path": log_path,
                "days_old": days_old
            }
        
        elif plugin == 'generate_report':
            # Extract report type and parameters
            report_type = "system"
            output_format = "pdf"
            
            # Look for report type keywords
            if re.search(r'performance|perf', text, re.IGNORECASE):
                report_type = "performance"
            elif re.search(r'security|sec', text, re.IGNORECASE):
                report_type = "security"
            elif re.search(r'usage|util', text, re.IGNORECASE):
                report_type = "usage"
            
            # Look for format keywords
            if re.search(r'pdf', text, re.IGNORECASE):
                output_format = "pdf"
            elif re.search(r'excel|xlsx', text, re.IGNORECASE):
                output_format = "excel"
            elif re.search(r'csv', text, re.IGNORECASE):
                output_format = "csv"
            
            kwargs = {
                "report_type": report_type,
                "format": output_format
            }
        
        return args, kwargs

    def _generate_suggestions(self, text: str, entities: List[Dict]) -> List[str]:
        """Generate helpful suggestions for the user"""
        suggestions = []
        
        # Suggest improvements based on missing information
        if not any(entity['label'] == 'TIME' for entity in entities):
            suggestions.append("Consider specifying when this task should run (e.g., 'daily', 'at 9 AM', 'every hour')")
        
        if 'urgent' in text.lower() or 'critical' in text.lower():
            suggestions.append("High priority task detected. Consider assigning to specific clients for faster execution.")
        
        if not any(entity['label'] in ['EMAIL', 'PERSON'] for entity in entities):
            if 'email' in text.lower() or 'notify' in text.lower():
                suggestions.append("Specify recipient email address for notifications")
        
        if len(text.split()) < 5:
            suggestions.append("Provide more details to improve task accuracy")
        
        return suggestions

    def _load_static_data(self, static_data_file: Optional[str]) -> Dict:
        """Load static data mappings from JSON file"""
        if not static_data_file:
            # Return default static mappings
            return {
                "database_shortcuts": {
                    "prod db": "production database",
                    "dev db": "development database", 
                    "test db": "testing database",
                    "staging db": "staging database",
                    "orders db": "orders database",
                    "users db": "users database",
                    "logs db": "logs database"
                },
                "server_shortcuts": {
                    "prod server": "production server",
                    "dev server": "development server",
                    "web server": "web application server",
                    "api server": "API gateway server",
                    "db server": "database server",
                    "cache server": "redis cache server"
                },
                "email_shortcuts": {
                    "admin": "admin@company.com",
                    "ops": "ops@company.com", 
                    "devops": "devops@company.com",
                    "security": "security@company.com",
                    "support": "support@company.com"
                },
                "path_shortcuts": {
                    "app logs": "/var/log/app",
                    "system logs": "/var/log/system",
                    "access logs": "/var/log/nginx/access.log",
                    "error logs": "/var/log/nginx/error.log",
                    "backup dir": "/backup",
                    "temp dir": "/tmp"
                },
                "priority_shortcuts": {
                    "asap": "P1",
                    "urgent": "P1", 
                    "high": "P2",
                    "normal": "P3",
                    "low": "P4"
                }
            }
        
        try:
            with open(static_data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Static data file {static_data_file} not found. Using defaults.")
            return self._load_static_data(None)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in static data file {static_data_file}")
            return self._load_static_data(None)

    def _load_plugin_metadata(self, plugins_folder: str) -> Dict:
        """Load plugin metadata from plugin files for better understanding"""
        import os
        import importlib.util
        
        plugin_metadata = {}
        
        if not os.path.exists(plugins_folder):
            logger.warning(f"Plugins folder {plugins_folder} not found")
            return plugin_metadata
        
        for filename in os.listdir(plugins_folder):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]  # Remove .py extension
                plugin_path = os.path.join(plugins_folder, filename)
                
                try:
                    # Read the plugin file to extract comments and docstrings
                    with open(plugin_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    metadata = {
                        'description': '',
                        'keywords': [],
                        'examples': [],
                        'parameters': {}
                    }
                    
                    # Extract module docstring
                    if '"""' in content:
                        start = content.find('"""') + 3
                        end = content.find('"""', start)
                        if end > start:
                            metadata['description'] = content[start:end].strip()
                    
                    # Extract NLP comments (comments starting with # NLP:)
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith('# NLP:'):
                            nlp_info = line[6:].strip()
                            if nlp_info.startswith('keywords:'):
                                keywords = nlp_info[9:].split(',')
                                metadata['keywords'].extend([k.strip() for k in keywords])
                            elif nlp_info.startswith('example:'):
                                metadata['examples'].append(nlp_info[8:].strip())
                    
                    plugin_metadata[plugin_name] = metadata
                    logger.debug(f"Loaded metadata for plugin {plugin_name}")
                    
                except Exception as e:
                    logger.warning(f"Could not load metadata for plugin {plugin_name}: {e}")
        
        return plugin_metadata

    def _expand_shortcuts(self, text: str) -> str:
        """Expand shortcuts in text using static data mappings"""
        expanded_text = text.lower()
        
        # Apply all shortcut mappings
        for category, mappings in self.static_mappings.items():
            for shortcut, full_form in mappings.items():
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(shortcut) + r'\b'
                expanded_text = re.sub(pattern, full_form, expanded_text, flags=re.IGNORECASE)
        
        logger.debug(f"Expanded '{text}' to '{expanded_text}'")
        return expanded_text

    def _enhance_confidence_with_plugin_metadata(self, text: str, plugin: str, confidence: float) -> float:
        """Enhance confidence using plugin metadata"""
        if plugin not in self.plugin_metadata:
            return confidence
        
        metadata = self.plugin_metadata[plugin]
        text_lower = text.lower()
        
        # Boost confidence for keyword matches
        for keyword in metadata.get('keywords', []):
            if keyword.lower() in text_lower:
                confidence += 0.05  # 5% boost per keyword match
        
        # Boost confidence if text matches examples
        for example in metadata.get('examples', []):
            # Simple similarity check
            example_words = set(example.lower().split())
            text_words = set(text_lower.split())
            overlap = len(example_words.intersection(text_words))
            if overlap > 0:
                similarity_boost = min(0.1, overlap * 0.02)  # Up to 10% boost
                confidence += similarity_boost
        
        return min(1.0, confidence)

    def reload_plugin_metadata(self, plugins_folder: str = "plugins"):
        """Reload plugin metadata from files"""
        with self._lock:
            self.plugin_metadata = self._load_plugin_metadata(plugins_folder)
            logger.info("Plugin metadata reloaded successfully")

def get_nlp_processor(static_data_file: Optional[str] = "static_mappings.json", plugins_folder: str = "plugins") -> TaskNLPProcessor:
    """Get a thread-safe singleton instance of the NLP processor"""
    return TaskNLPProcessor(static_data_file, plugins_folder)
