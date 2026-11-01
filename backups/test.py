import os 
import time, datetime
import threading
import shutil 

# ==============================
# BACKUP SETUP
# ==============================
backup_folder = "backups"
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)
    
# Get the current date and time for the backup filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_filename = f"database_backup_{timestamp}.db"
backup_path = os.path.join(backup_folder, backup_filename)

# # Copy the database file to the backup folder
# try:
#     shutil.copy("database.db", backup_path)
#     print(f"✅ Database backup created: {backup_filename}")
# except Exception as e:
#     print(f"❌ Backup failed: {e}")

def backup_database():
    if not os.path.exists("database.db"):
        print("❌ Error: database.db does not exist! Skipping backup...")
        return  # Stop the function if the database doesn't exist

    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_folder, backup_filename)

        shutil.copy("database.db", backup_path)
        print(f"✅ Database backup created: {backup_filename}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def backup_scheduler():
    """Runs the backup script every 24 hours"""
    while True:
        backup_database()
        time.sleep(5)  # 86400 seconds = 24 hours

# Start the backup scheduler in a separate thread
backup_thread = threading.Thread(target=backup_scheduler, daemon=True)
backup_thread.start()

backup_scheduler()