import pytest
from datetime import datetime, timedelta

def test_full_appointment_crud(client, auth_headers):
    # 1. CREATE
    new_appt_data = {
        "patient_name": "CRUD Test Patient",
        "patient_phone": "5511999990000",
        "datetime": (datetime.now() + timedelta(days=5)).isoformat(),
        "service": "Clínica Geral",
        "professional": "Dr. Test"
    }
    
    response = client.post("/api/appointments", headers=auth_headers, json=new_appt_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    appt_id = data["id"]
    assert appt_id is not None

    # 1.1 CREATE (Invalid date)
    invalid_appt_data = new_appt_data.copy()
    invalid_appt_data["datetime"] = "invalid-date"
    response = client.post("/api/appointments", headers=auth_headers, json=invalid_appt_data)
    assert response.status_code == 400

    # 2. READ (List)
    response = client.get("/api/appointments", headers=auth_headers)
    assert response.status_code == 200
    appts = response.json()["appointments"]
    # Find our created appointment
    found = [a for a in appts if a["id"] == appt_id]
    assert len(found) == 1
    assert found[0]["patient_name"] == "CRUD Test Patient"
    assert found[0]["professional"] == "Dr. Test"

    # 3. UPDATE
    update_data = {
        "status": "confirmed",
        "professional": "Dr. Updated"
    }
    response = client.put(f"/api/appointments/{appt_id}", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify update
    response = client.get("/api/appointments", headers=auth_headers)
    appts = response.json()["appointments"]
    updated_appt = [a for a in appts if a["id"] == appt_id][0]
    assert updated_appt["status"] == "confirmed"
    assert updated_appt["professional"] == "Dr. Updated"

    # 3.1 UPDATE (Date)
    new_dt = (datetime.now() + timedelta(days=6)).isoformat()
    response = client.put(f"/api/appointments/{appt_id}", headers=auth_headers, json={"datetime": new_dt})
    assert response.status_code == 200
    
    # Verify date update
    response = client.get("/api/appointments", headers=auth_headers)
    appts = response.json()["appointments"]
    updated_appt = [a for a in appts if a["id"] == appt_id][0]
    # Use isoformat() comparison or parse
    assert updated_appt["datetime"].startswith(new_dt[:16]) # Compare up to minutes

    # 3.2 UPDATE (Non-existent)
    response = client.put("/api/appointments/999999", headers=auth_headers, json={"status": "cancelled"})
    assert response.status_code == 404

    # 4. DELETE
    response = client.delete(f"/api/appointments/{appt_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify deletion
    response = client.get("/api/appointments", headers=auth_headers)
    appts = response.json()["appointments"]
    found = [a for a in appts if a["id"] == appt_id]
    assert len(found) == 0

    # 4.1 DELETE (Non-existent)
    response = client.delete("/api/appointments/999999", headers=auth_headers)
    assert response.status_code == 404

def test_appointment_patient_resolution_on_update(client, auth_headers):
    # Create appt - use a different day to avoid conflicts
    new_appt_data = {
        "patient_name": "Original Name",
        "patient_phone": "5511888880000",
        "datetime": (datetime.now() + timedelta(days=10)).isoformat()
    }
    resp = client.post("/api/appointments", headers=auth_headers, json=new_appt_data)
    assert resp.status_code == 200, f"Post failed: {resp.text}"
    appt_id = resp.json()["id"]

    # Update patient name - should resolve/create/update patient
    # In current implementation of resolve_patient_for_contact:
    # If phone is the same but name is different, it creates a NEW patient if no match.
    update_data = {
        "patient_name": "New Name",
        "patient_phone": "5511888880000" # same phone
    }
    resp = client.put(f"/api/appointments/{appt_id}", headers=auth_headers, json=update_data)
    assert resp.status_code == 200

    # Verify appt now linked to "New Name"
    resp = client.get("/api/appointments", headers=auth_headers)
    appts = resp.json()["appointments"]
    updated_appt = [a for a in appts if a["id"] == appt_id][0]
    assert updated_appt["patient_name"] == "New Name"
