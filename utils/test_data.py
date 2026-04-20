"""Test utilities for local development."""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock database for local testing (when Supabase is not connected)
_mock_workflows: Dict[str, Any] = {}
_mock_instances: Dict[str, Any] = {}


def get_mock_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get mock workflow data."""
    return _mock_workflows.get(
        workflow_id,
        {
            "id": workflow_id,
            "name": "Sample Patient Intake",
            "steps": ["Check-in", "Triage", "Assessment", "Treatment", "Discharge"]
        }
    )


def get_mock_instances(workflow_id: str) -> List[Dict[str, Any]]:
    """Get mock instances data."""
    instances = []
    now = datetime.now()
    
    # Generate demo instances
    for i in range(1, 4):
        timestamps = []
        for step in range(min(i + 1, 5)):
            timestamps.append({
                "step": step,
                "timestamp": (now - timedelta(minutes=(5-step)*10)).isoformat()
            })
        
        instances.append({
            "id": f"mock-instance-{i}",
            "workflow_id": workflow_id,
            "name": f"Patient #{i+100}",
            "current_step": min(i, 4),
            "started_at": (now - timedelta(minutes=60)).isoformat(),
            "timestamps": timestamps,
            "created_at": now.isoformat()
        })
    
    return instances


# Example workflows for testing
EXAMPLE_WORKFLOWS = [
    {
        "name": "Patient Intake Process",
        "steps": ["Check-in", "Insurance Verification", "Triage", "Initial Assessment", "Doctor Consult"]
    },
    {
        "name": "Surgical Procedure",
        "steps": ["Pre-op Assessment", "Anesthesia", "Surgery", "Recovery", "Discharge Planning"]
    },
    {
        "name": "Emergency Response",
        "steps": ["Triage", "Initial Assessment", "Stabilization", "Testing", "Treatment", "Monitoring"]
    }
]
