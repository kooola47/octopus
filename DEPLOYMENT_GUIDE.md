# 🚀 Octopus Deployment Guide

## Pre-Deployment Checklist

### Server Requirements
- [ ] Python 3.7+ installed
- [ ] Network accessible by client machines
- [ ] Port 8000 available (or configure different port)
- [ ] Sufficient disk space for logs and database
- [ ] (Optional) Web server proxy for production deployment

### Client Requirements
- [ ] Python 3.7+ installed on each target PC
- [ ] Network connectivity to server
- [ ] User permissions for task execution
- [ ] Local disk space for plugins and logs

## Step-by-Step Deployment

### Phase 1: Server Deployment

1. **Prepare Server Environment**
   ```bash
   # Create deployment directory
   mkdir /opt/octopus
   cd /opt/octopus
   
   # Copy server files
   cp -r octopus_server/ .
   cp requirements.txt .
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Server**
   ```bash
   # Edit octopus_server/config.py
   SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
   SERVER_PORT = 8000       # Or your preferred port
   ```

4. **Start Server**
   ```bash
   cd octopus_server
   python main.py
   ```

5. **Verify Server**
   - Access `http://server-ip:8000/dashboard`
   - Check logs in `octopus_server/logs/server.log`

### Phase 2: Client Deployment

1. **Prepare Client Package**
   ```bash
   # Create client deployment package
   mkdir octopus_client_package
   cp -r octopus_client/ octopus_client_package/
   cp requirements.txt octopus_client_package/
   ```

2. **Deploy to User PCs**
   For each target PC:
   ```bash
   # Copy client files
   mkdir C:\octopus_client
   copy octopus_client_package\* C:\octopus_client\
   
   # Install dependencies
   cd C:\octopus_client
   pip install -r requirements.txt
   ```

3. **Configure Each Client**
   Edit `octopus_client/config.py`:
   ```python
   SERVER_URL = "http://YOUR_SERVER_IP:8000"  # ⚠️ Critical!
   ```

4. **Start Clients**
   ```bash
   cd C:\octopus_client
   python main.py
   ```

5. **Verify Client Connection**
   - Check server dashboard for connected clients
   - Verify heartbeat in server logs
   - Check client logs for connection status

### Phase 3: Plugin Deployment

1. **Create Your First Plugin**
   ```python
   # octopus_server/plugins/hello_world.py
   import logging
   
   logger = logging.getLogger("octopus")
   
   def run(*args, **kwargs):
       logger.info("Hello World plugin executed!")
       return "Hello from Octopus!"
   ```

2. **Test Plugin Sync**
   - Plugin should auto-appear in client plugins folder
   - Check client logs for plugin download messages
   - Verify MD5 checksums match

3. **Create Test Task**
   - Use web dashboard to create ad-hoc task
   - Set owner to "Anyone" 
   - Select "hello_world" plugin
   - Monitor execution

### Phase 4: Production Hardening

1. **Security Considerations**
   - Use HTTPS in production
   - Implement authentication if needed
   - Restrict network access with firewalls
   - Regular security updates

2. **Monitoring Setup**
   - Log rotation for server and clients
   - Monitoring dashboard uptime
   - Client connectivity alerts
   - Task execution monitoring

3. **Backup Strategy**
   - Regular database backups
   - Plugin version control
   - Configuration backups

## Troubleshooting

### Common Issues

**Clients Not Connecting**
- Check SERVER_URL in client config
- Verify network connectivity (ping, telnet)
- Check firewall rules
- Review client logs for error messages

**Plugins Not Syncing**
- Check server logs for plugin serving errors
- Verify plugin MD5 checksums
- Check client plugin download permissions
- Review pluginhelper logs

**Tasks Not Executing**
- Verify client heartbeat status
- Check task ownership assignments
- Review execution logs on client side
- Validate plugin syntax and imports

**Performance Issues**
- Monitor database size and performance
- Check network latency between server/clients
- Review memory usage on server
- Optimize plugin execution time

### Log Locations

**Server Logs:**
- `octopus_server/logs/server.log`
- Check for task creation, client connections, plugin serving

**Client Logs:**
- `octopus_client/logs/client.log`
- Check for heartbeat, plugin sync, task execution

### Useful Commands

```bash
# Check server status
curl http://server-ip:8000/clients

# Test plugin endpoint
curl http://server-ip:8000/plugins

# Check database directly
sqlite3 octopus_server/octopus.db "SELECT * FROM tasks;"

# Monitor logs in real-time
tail -f octopus_server/logs/server.log
tail -f octopus_client/logs/client.log
```

## Production Deployment Options

### Option 1: Simple Deployment
- Direct Python execution
- Manual startup on server restart
- Suitable for small environments

### Option 2: Service Deployment
- Register as Windows Service / Linux Daemon
- Auto-start on system boot
- Better for production environments

### Option 3: Containerized Deployment
- Docker containers for server and clients
- Easier scaling and management
- Cloud-ready deployment

### Option 4: Web Server Integration
- Nginx/Apache proxy for server
- SSL termination and load balancing
- Enhanced security and performance
