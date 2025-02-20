import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    """Load data from a JSON file, reinitialize if empty or invalid."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                data = json.load(file)
        except (json.JSONDecodeError, ValueError):
            print("Data file is empty or invalid. Reinitializing...")
            data = initialize_data()
            save_data(data)
    else:
        data = initialize_data()
        save_data(data)
    return data

def initialize_data():
    """Return the default data structure."""
    return {
        "weekly_outings": [0, 0, 0, 0],
        "weekly_spending": [0.0, 0.0, 0.0, 0.0],
        "charges": [[], [], [], []],
        "monthly_budget": 300.0
    }

def save_data(data):
    """Save data to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def calculate_remaining_budget(data):
    """Calculate the remaining monthly budget."""
    total_spent = sum(data["weekly_spending"])
    return data["monthly_budget"] - total_spent



