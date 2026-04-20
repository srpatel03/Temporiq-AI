import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
num_patients = 50
start_time_base = datetime(2023, 10, 27, 8, 0, 0) # Starts at 8:00 AM

# Helper function to format seconds into hh:mm:ss
def format_seconds_to_hms(total_seconds):
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

data = []
# A realistic mix of common clinic notes
notes_options = [
    "Smooth check-in", 
    "Forgot ID card, took longer", 
    "Extremely quick", 
    "Long wait in line", 
    "Normal flow", 
    "System glitch during registration", 
    "Patient needed extra assistance",
    "", "", "" # Added blanks so some patients intentionally have no notes
]

current_start = start_time_base

for i in range(1, num_patients + 1):
    instance_name = f"Patient {i:03d}"
    notes = random.choice(notes_options)
    
    # Stagger patient arrivals by 2 to 8 minutes
    current_start += timedelta(minutes=random.randint(2, 8))
    start_time_str = current_start.strftime("%Y-%m-%d %H:%M:%S")
    
    # Randomize durations (in seconds) to be realistic
    # Gets in Line: 1 to 15 mins
    step1_sec = random.randint(60, 900)
    # Called to Register: 2 to 20 mins
    step2_sec = random.randint(120, 1200)
    # Finishes Registration: 2 to 8 mins
    step3_sec = random.randint(120, 480)
    
    total_sec = step1_sec + step2_sec + step3_sec
    completion_time = current_start + timedelta(seconds=total_sec)
    completion_time_str = completion_time.strftime("%Y-%m-%d %H:%M:%S")
    
    row = {
        "Instance Name": instance_name,
        "Notes": notes,
        "Start Time": start_time_str,
        "Completion Time": completion_time_str,
        "Total Duration": format_seconds_to_hms(total_sec),
        "Gets in Line (duration)": format_seconds_to_hms(step1_sec),
        "Called to Register (duration)": format_seconds_to_hms(step2_sec),
        "Finishes Registration (duration)": format_seconds_to_hms(step3_sec)
    }
    data.append(row)

# Convert to a DataFrame and export to Excel
df = pd.DataFrame(data)
df.to_excel("cardiology_50_test_patients.xlsx", index=False)

print("✅ Successfully created cardiology_50_test_patients.xlsx!")