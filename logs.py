from platformdirs import user_data_dir
from datetime import datetime
import re
import os

def get_log_dir():
    APP_NAME = "AI-Grader"

    logs_dir = os.path.join(user_data_dir(APP_NAME), "logs")

    #create directory if nonexistent
    os.makedirs(logs_dir, exist_ok=True)

    return logs_dir

def save_df_as_log(df, tag=None):
    logs_dir = get_log_dir()
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if tag:
        tag = sanitize_filename(tag)
        filename = f"{timestamp}_{tag}.csv"
    else:
        filename = f"{timestamp}.csv"

    path = os.path.join(logs_dir, filename)
    df.to_csv(path, index=False)
    print("Saved to:")
    print(path)
    return path

#Remove unsafe characters for filenames
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)