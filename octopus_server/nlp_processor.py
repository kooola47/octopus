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

# Configure logging
logger = logging.getLogger("octopus_nlp")

class TaskNLPProcessor:
    """
    Natural Language Processor for converting text to task definitions
    """
    
    def __init__(self):
        """Initialize the NLP processor with spaCy model"""
        try:
            # Try to load the English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy English model successfully")
        except OSError:
            logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Define patterns for extracting task components
        self.action_patterns = {
            'create_incident': [
                r'create.*incident', r'report.*issue', r'file.*ticket', r'log.*problem',
                r'raise.*alert', r'submit.*bug', r'open.*case'
            ],
            'send_email': [
                r'send.*email', r'email.*to', r'mail.*notification', r'notify.*via.*email',
                r'send.*message', r'alert.*email'
            ],
            'backup_database': [
                r'backup.*database', r'backup.*db', r'create.*backup', r'dump.*database',
                r'export.*data', r'archive.*database'
            ],
            'cleanup_logs': [
                r'clean.*logs?', r'delete.*logs?', r'remove.*old.*files?', r'purge.*logs?',
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
        
        # Process text with spaCy
        doc = self.nlp(text.lower())
        
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
            "suggestions": []
        }
        
        # Extract entities
        entities = self._extract_entities(doc, text)
        result["extracted_entities"] = entities
        
        # Determine action/plugin
        plugin, action, confidence = self._determine_action(text)
        if plugin:
            result["task"]["plugin"] = plugin
            result["task"]["action"] = action
            result["confidence"] += confidence * 0.4
        
        # Extract priority
        priority = self._extract_priority(text)
        if priority:
            result["task"]["priority"] = priority
            result["confidence"] += 0.1
        
        # Extract parameters from entities and text
        args, kwargs = self._extract_parameters(entities, text, plugin)
        result["task"]["args"] = args
        result["task"]["kwargs"] = kwargs
        
        # Determine owner/assignee
        owner = self._extract_owner(text)
        if owner:
            result["task"]["owner"] = owner
            result["confidence"] += 0.1
        
        # Extract scheduling information
        schedule_info = self._extract_schedule(text)
        if schedule_info:
            result["task"].update(schedule_info)
            result["confidence"] += 0.2
        
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
        """Determine the most likely plugin and action from text"""
        text_lower = text.lower()
        best_match = None
        best_score = 0.0
        
        for plugin, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Score based on pattern specificity and length
                    score = len(pattern) / len(text_lower) + 0.5
                    if score > best_score:
                        best_score = score
                        best_match = plugin
        
        if best_match:
            return best_match, "main", min(1.0, best_score)
        
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


def get_nlp_processor() -> TaskNLPProcessor:
    """Get a singleton instance of the NLP processor"""
    if not hasattr(get_nlp_processor, '_instance'):
        get_nlp_processor._instance = TaskNLPProcessor()
    return get_nlp_processor._instance
