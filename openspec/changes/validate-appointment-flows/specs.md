# Specs: Verification Implementation Details

## File Structure

### `verify_flows.py`
Located in root, this script will be executed to run the validation.

```python
import os
import requests
import logging
from sqlmodel import Session, select, create_engine
from src.database import Appointment, Patient
from src.config import DATA_DIR
import sys

# Configuration
BASE_URL = "http://localhost:8000"
DB_PATH = os.path.join(DATA_DIR, "post_clinics.db")
sqlite_url = f"sqlite:///{DB_PATH}"
engine = create_engine(sqlite_url)

class WorkflowTester:
    def __init__(self):
        self.phone = "5511999999999"
        self.patient_name = "Test User"
    
    def reset_db(self):
        """Clears relevant tables for a clean slate."""
        # Logic to delete appointments/patients for test phone
        pass

    def send_message(self, text):
        """Sends a Z-API webhook payload."""
        payload = {
            "phone": self.phone,
            "text": {"message": text},
            "messageId": "test_id_123"
        }
        return requests.post(f"{BASE_URL}/webhook/zapi", json=payload)

    def verify_appointment_status(self, expected_status):
        """Checks DB for appointment status."""
        pass
    
    # Scenarios
    def run_scenario_scheduling(self): pass
    def run_scenario_reschedule(self): pass
    def run_scenario_cancel(self): pass
    def run_dashboard_check(self): pass
```

## Dependencies
*   `requests`: To be installed (`pip install requests`) or present in env.
*   `sqlmodel`: Already in env.

## Success Conditions
The script should output `SUCCESS` at the end if all steps pass, or `FAILURE` with a reason.
