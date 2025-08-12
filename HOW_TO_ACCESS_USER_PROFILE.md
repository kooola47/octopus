# 👤 How to Access User Profile Settings

## 🌐 **From the Web UI:**

### **Method 1: Navigation Dropdown**
1. **Login** to the Octopus web interface
2. Look for your **username or "Account"** in the top-right corner of the navigation bar
3. **Click on the dropdown arrow** next to your username
4. Select **"Profile"** from the dropdown menu

### **Method 2: Direct URL**
- Navigate directly to: **`http://your-server:5000/profile`**
- Example: `http://127.0.0.1:5000/profile` (for local development)

### **Method 3: Dashboard Navigation** (if enabled)
- From the main dashboard, look for **"Profile"** in the main navigation menu
- Some layouts may have Profile as a direct menu item

---

## 📍 **Current Navigation Structure:**

```
🐙 Octopus
├── 📊 Dashboard
├── 📋 Tasks  
├── 🖥️ Clients
├── ▶️ Executions
└── 👤 Account (Dropdown)
    ├── 👤 Profile ← **USER SETTINGS HERE**
    ├── ⚙️ Settings
    └── 🚪 Logout
```

---

## 🎯 **What You'll Find in User Profile:**

### **📂 Parameter Categories:**

| Category | Icon | Purpose | Examples |
|----------|------|---------|----------|
| **🔑 API Credentials** | 🔐 | Secure authentication data | ServiceNow API key, Jira token, Slack webhook |
| **🔌 Integrations** | 🔗 | Service configurations | Instance URLs, default priorities |
| **🔔 Notifications** | 📧 | Messaging preferences | Email addresses, notification channels |
| **⚙️ Preferences** | 🎛️ | Personal settings | Timezone, refresh intervals |
| **🔧 Custom** | 🛠️ | User-defined parameters | Project-specific settings |

### **🛠️ Available Actions:**
- ✅ **Add Parameter**: Create new configuration values
- ✅ **Edit Parameter**: Modify existing settings  
- ✅ **Delete Parameter**: Remove unwanted settings
- ✅ **Add Category**: Create custom parameter groups
- ✅ **Export Configuration**: Download your settings
- ✅ **Refresh Cache**: Update plugin access cache

---

## 🔐 **Security Features:**

- **🔒 Encryption**: Sensitive parameters (API keys, passwords) are automatically encrypted
- **👤 User Isolation**: Each user sees only their own parameters
- **🔑 Authentication Required**: Must be logged in to access profile
- **💾 Secure Storage**: Parameters stored in encrypted database tables

---

## 🔌 **How Plugins Use Your Parameters:**

When you create tasks, plugins automatically access your personalized configuration:

```python
# Plugin automatically gets your ServiceNow API key
api_key = get_user_parameter(username, "api_credentials", "servicenow_api_key")

# Plugin uses your preferred ServiceNow instance
instance = get_user_parameter(username, "integrations", "servicenow_instance")
```

This means **the same plugin works differently for each user** based on their personal settings!

---

## 📝 **Quick Setup Guide:**

### **Step 1: Access Profile**
- Login → Account Dropdown → Profile

### **Step 2: Add API Credentials**
```
Category: API Credentials
Parameter: servicenow_api_key
Value: your_actual_api_key_here
Type: String
Sensitive: ✅ Yes (will be encrypted)
```

### **Step 3: Configure Integrations**
```
Category: Integrations  
Parameter: servicenow_instance
Value: https://yourcompany.service-now.com
Type: String
Sensitive: ❌ No
```

### **Step 4: Set Preferences**
```
Category: Preferences
Parameter: timezone
Value: America/New_York
Type: String
```

### **Step 5: Create Tasks**
- Now when you create ServiceNow tasks, they'll automatically use YOUR credentials and instance!

---

## 🎯 **Sample User Profile Setup:**

If you ran the initialization script, you should see sample parameters for user **"admin"**:

- **🔐 API Credentials**: 3 parameters (ServiceNow, Jira, Slack)
- **🔗 Integrations**: 3 parameters (URLs and priorities)  
- **📧 Notifications**: 2 parameters (email and preferences)
- **⚙️ Preferences**: 2 parameters (timezone and intervals)

---

## ⚠️ **Troubleshooting:**

### **Can't see Profile link:**
- Make sure you're logged in
- Check the Account dropdown in top-right corner
- Try direct URL: `/profile`

### **Profile page not loading:**
- Ensure server started with user profile routes
- Check if `user_profile_bp` is registered in `main.py`
- Verify database tables exist (run `init_user_params.py`)

### **Parameters not saving:**
- Check browser console for JavaScript errors
- Verify you have write permissions to database
- Ensure all required fields are filled

---

## 🚀 **Next Steps:**

1. **✅ Access your profile** using the navigation dropdown
2. **🔧 Add your API credentials** for ServiceNow, Jira, etc.
3. **⚙️ Configure your preferences** (timezone, notifications)
4. **📝 Create tasks** that use plugins with your personalized settings
5. **🎯 Enjoy automatic configuration** - no more manual API key entry per task!

**🎉 Your personal settings make every plugin work exactly how YOU need it!**
