# 🐙 Octopus Installation Guide

## Project Structure
- `octopus_server/` - Task orchestration server
- `octopus_client/` - Task execution client

## Installation

### Server Installation
```bash
cd octopus_server
pip install -r requirements.txt

# Install spaCy language model for NLP features
python -m spacy download en_core_web_sm

# Start the server
python main.py
```

### Client Installation
```bash
cd octopus_client
pip install -r requirements.txt

# Start the client
python main.py
```

## Dependencies Summary

### Server Dependencies
- **Flask**: Web framework for API and dashboard
- **Requests**: HTTP client for external communications
- **spaCy**: Natural language processing for task creation
- **psutil**: System monitoring and performance metrics
- **PyYAML**: Configuration file support
- **sqlite-web**: Optional database web interface

### Client Dependencies
- **Flask**: Web framework for status server
- **Requests**: HTTP client for server communication
- **psutil**: System monitoring and heartbeat data
- **PyYAML**: Configuration file support

## Optional Setup
- Use virtual environments for isolation
- Configure environment variables in `.env` files
- Adjust configuration files for your environment
