"""Validation utilities."""
from typing import Tuple, List


def validate_workflow_name(name: str) -> Tuple[bool, str]:
    """Validate workflow name."""
    if not name or not name.strip():
        return False, "Workflow name cannot be empty"
    if len(name) > 100:
        return False, "Workflow name must be less than 100 characters"
    return True, ""


def validate_steps(steps: List[str]) -> Tuple[bool, str]:
    """Validate workflow steps."""
    if len(steps) < 2:
        return False, "Workflow must have at least 2 steps"
    if len(steps) > 10:
        return False, "Workflow cannot have more than 10 steps"
    
    for i, step in enumerate(steps):
        if not step or not step.strip():
            return False, f"Step {i+1} name cannot be empty"
        if len(step) > 25:
            return False, f"Step {i+1} name must be 25 characters or less"
    
    return True, ""


def validate_instance_name(name: str) -> Tuple[bool, str]:
    """Validate instance name."""
    if not name or not name.strip():
        return False, "Instance name cannot be empty"
    if len(name) > 100:
        return False, "Instance name must be less than 100 characters"
    return True, ""
