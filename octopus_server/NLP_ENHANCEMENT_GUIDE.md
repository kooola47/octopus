# 🐙 Octopus NLP Enhancement Guide

## 📁 Static Data Mapping

### Where to Place Static Data

1. **Main Configuration File**: `octopus_server/static_mappings.json`
   - This is the primary location for all shortcut mappings
   - The NLP processor automatically loads this file

2. **Custom Location**: You can specify a different file by updating the server initialization

### Static Data Structure

The static mappings JSON file contains several categories:

```json
{
  "database_shortcuts": {
    "prod db": "production database",
    "dev db": "development database"
  },
  "server_shortcuts": {
    "prod server": "production server",
    "api server": "API gateway server"
  },
  "email_shortcuts": {
    "admin": "admin@company.com",
    "ops": "ops@company.com"
  },
  "path_shortcuts": {
    "app logs": "/var/log/app",
    "backup dir": "/backup"
  },
  "priority_shortcuts": {
    "asap": "P1",
    "urgent": "P1",
    "high": "P2"
  },
  "time_shortcuts": {
    "now": "immediately",
    "tonight": "at 11 PM",
    "morning": "at 9 AM"
  }
}
```

### How Shortcuts Work

When a user types: **"backup prod db tonight"**
- `prod db` → `production database`
- `tonight` → `at 11 PM`
- Result: **"backup production database at 11 PM"**

## 🔧 Plugin Comments for Better NLP

### NLP Comment Format

Add these special comments to your plugin files to improve confidence:

```python
# NLP: keywords: keyword1, keyword2, keyword3
# NLP: example: example natural language input
```

### Example Plugin with NLP Comments

```python
#!/usr/bin/env python3
"""
Email Notification Plugin

Sends email notifications to specified recipients.
"""

# NLP: keywords: email, send, notify, mail, message, alert
# NLP: example: send email to admin about server maintenance
# NLP: example: notify ops team about database backup completion
# NLP: example: mail alert to security team about suspicious activity

def run(recipient, subject, message, *args, **kwargs):
    # Plugin implementation
    pass
```

### Confidence Boost Calculation

1. **Keywords Match**: +5% per keyword found in user input
2. **Example Similarity**: Up to +10% based on similarity to examples
3. **Combined Effect**: Can add up to +25% total confidence boost

### Best Practices for Plugin Comments

1. **Use Relevant Keywords**:
   ```python
   # NLP: keywords: backup, database, export, dump, archive, save
   ```

2. **Provide Varied Examples**:
   ```python
   # NLP: example: backup production database daily
   # NLP: example: create backup of orders db  
   # NLP: example: export customer data to backup dir
   ```

3. **Include Common Variations**:
   ```python
   # NLP: keywords: incident, issue, problem, alert, ticket, bug, case
   ```

4. **Add Action-Specific Terms**:
   ```python
   # NLP: keywords: cleanup, clean, delete, remove, purge, clear
   ```

## 📈 Confidence Improvement Examples

### Before Enhancements
- Input: "backup prod db"
- Confidence: ~40%
- Issues: Unknown shortcuts, limited context

### After Enhancements
- Input: "backup prod db" 
- Expanded: "backup production database"
- Plugin keywords matched: "backup", "database"
- Final Confidence: ~75%

## 🚀 Advanced Usage

### Custom Static Data Categories

You can add your own categories to the static mappings:

```json
{
  "your_custom_shortcuts": {
    "shortcut": "full expansion",
    "k8s": "Kubernetes cluster",
    "vpc": "Virtual Private Cloud"
  }
}
```

### Multi-Level Expansions

Shortcuts can chain together:
- "backup prod db to backup dir tonight"
- Becomes: "backup production database to /backup at 11 PM"

### Plugin-Specific Keywords

Each plugin should have keywords that match its functionality:

- **Incident Plugin**: incident, issue, problem, alert, ticket, bug, case, outage
- **Backup Plugin**: backup, database, dump, export, archive, save, copy
- **Email Plugin**: email, send, notify, mail, message, alert, notification
- **Cleanup Plugin**: cleanup, clean, delete, remove, purge, clear, logs

## 📊 Monitoring Confidence Levels

You can check confidence improvements by:

1. Using the NLP test page to try different inputs
2. Checking server logs for confidence scores
3. Comparing before/after confidence levels

## 🔄 Updating Static Data

To update static mappings:

1. Edit `static_mappings.json`
2. Restart the Octopus server
3. Test with the NLP test page

## 💡 Tips for Maximum Confidence

1. **Use specific terms**: "prod db" instead of "database"
2. **Include time references**: "daily", "at 9 AM", "immediately"
3. **Add priority indicators**: "urgent", "P1", "critical"
4. **Specify targets**: "admin@company.com", "/var/log/app"
5. **Combine shortcuts**: "backup prod db to backup dir tonight"

---

**Need Help?** Visit the [Confidence Guide](/confidence-guide) for detailed examples and scoring explanations.
