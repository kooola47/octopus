import codecs
import os

def check_logs():
    log_file = 'logs/server.log'
    if not os.path.exists(log_file):
        print("Server log file not found")
        return
    
    try:
        with codecs.open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        print("=== Recent Execution-Related Log Entries ===")
        execution_lines = [line.strip() for line in lines[-100:] 
                          if any(keyword in line.lower() for keyword in ['execution', 'adding', 'error', 'dashboard'])]
        
        if execution_lines:
            for line in execution_lines[-20:]:  # Last 20 relevant entries
                print(line)
        else:
            print("No execution-related entries found in recent logs")
            
        print(f"\nTotal log lines: {len(lines)}")
        
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    check_logs()
