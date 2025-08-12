import codecs
import os

def check_detailed_logs():
    log_file = 'logs/server.log'
    if not os.path.exists(log_file):
        print("Server log file not found")
        return
    
    try:
        with codecs.open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for the specific log message from add_execution_result
        if "Adding execution via dashboard" in content:
            print("✅ Found 'Adding execution via dashboard' messages")
            lines = content.split('\n')
            for line in lines:
                if "Adding execution via dashboard" in line:
                    print(f"  {line.strip()}")
        else:
            print("❌ No 'Adding execution via dashboard' messages found")
            
        if "Adding execution result:" in content:
            print("✅ Found 'Adding execution result:' messages")
            lines = content.split('\n')
            for line in lines:
                if "Adding execution result:" in line:
                    print(f"  {line.strip()}")
        else:
            print("❌ No 'Adding execution result:' messages found")
            
        # Count recent dashboard posts
        recent_posts = content.count("POST /dashboard -> 302")
        print(f"\nRecent dashboard POST requests: {recent_posts}")
        
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    check_detailed_logs()
