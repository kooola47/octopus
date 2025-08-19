import sqlite3

def check_user_idents():
    conn = sqlite3.connect('octopus_server/octopus.db')
    cursor = conn.cursor()
    
    print("=== CHECKING USER IDENTS ===")
    
    # Check all users and their user_ident values
    cursor.execute('SELECT id, username, user_ident, email, role, status FROM users')
    users = cursor.fetchall()
    
    print("Existing users with user_ident:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, UserIdent: {user[2]}, Email: {user[3]}, Role: {user[4]}")
    
    # Check heartbeats for aries-7044
    cursor.execute('SELECT username, COUNT(*) FROM heartbeats GROUP BY username')
    heartbeat_users = cursor.fetchall()
    
    print(f"\nHeartbeat users:")
    for hb_user in heartbeat_users:
        print(f"  Username: {hb_user[0]}, Heartbeats: {hb_user[1]}")
    
    conn.close()

if __name__ == "__main__":
    check_user_idents()
