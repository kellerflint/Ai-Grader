from platformdirs import user_data_dir
from datetime import datetime
import re
import os

def get_log_dir(folder):
    APP_NAME = "AI-Grader"

    logs_dir = os.path.join(user_data_dir(APP_NAME), "logs")
    logs_dir = os.path.join(logs_dir, folder)

    #create directory if nonexistent
    os.makedirs(logs_dir, exist_ok=True)

    return logs_dir

def save_df_as_log(df, tag=None):
    logs_dir = get_log_dir("individual")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if tag:
        tag = sanitize_filename(tag)
        filename = f"{tag}_{timestamp}.csv"
    else:
        filename = f"{timestamp}.csv"

    path = os.path.join(logs_dir, filename)
    df.to_csv(path, index=False)
    print("Saved to:")
    print(path)
    return timestamp

def save_text_as_log(text, timestamp, tag=None):
    logs_dir = get_log_dir("aggregate")

    if tag:
        tag = sanitize_filename(tag)
        filename = f"{tag}_{timestamp}.txt"
    else:
        filename = f"{timestamp}.txt"
    
    path = os.path.join(logs_dir, filename)
    with open(path, "w") as file:
        file.write(text)
    print("Saved to:")
    print(path)

#Remove unsafe characters for filenames
def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)