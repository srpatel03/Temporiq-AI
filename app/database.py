"""Supabase database configuration and methods."""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from supabase_auth.errors import AuthApiError
import json
import logging
from datetime import datetime
# Force load .env file to ensure credentials are available before client initialization.
# This is crucial because this module is imported and executed at startup.
load_dotenv()
# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
url = os.getenv("SUPABASE_URL", "")
key = os.getenv("SUPABASE_KEY", "")

supabase: Optional[Client] = None

if url and key:
    try:
        supabase = create_client(url, key)
        logger.info("✓ Supabase initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Supabase: {str(e)}")
else:
    logger.warning("✗ Supabase credentials not found. Ensure SUPABASE_URL and SUPABASE_KEY are in your .env file and that it's being loaded correctly.")


def init_db():
    """Initialize database tables if they don't exist."""
    if not supabase:
        return
    
    try:
        # Check if tables exist by trying to query them
        supabase.table("workflows").select("*").limit(1).execute()
    except:
        # Tables will be created via Supabase dashboard
        pass


class AuthDB:
    """Authentication database operations."""

    @staticmethod
    def sign_up(email, password) -> Optional[Dict[str, Any]]:
        """Sign up a new user."""
        if not supabase:
            return None
        try:
            response = supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                # When email confirmation is on, Supabase doesn't error on existing user signup.
                # Instead, it returns a user object with an empty `identities` list to prevent
                # email enumeration. For a completely new user, the `identities` list will
                # contain their newly created identity. We check if this list is empty to 
                # reliably detect if the user already exists.
                if response.user.identities is not None and len(response.user.identities) == 0:
                    raise Exception("User already registered")

                # This is a new user, return their data.
                return response.user.model_dump()
            return None
        except AuthApiError as e:
            raise Exception(f"Signup failed: {e.message}")

    @staticmethod
    def sign_in(email, password) -> Optional[Dict[str, Any]]:
        """Sign in an existing user."""
        if not supabase:
            return None
        try:
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            return response.user.model_dump() if response.user else None
        except AuthApiError as e:
            raise Exception(f"Login failed: {e.message}")

    @staticmethod
    def sign_out():
        """Sign out the current user."""
        if not supabase:
            return
        try:
            supabase.auth.sign_out()
        except AuthApiError as e:
            raise Exception(f"Logout failed: {e.message}")
    
    @staticmethod
    def admin_reset_password(email: str):
        """
        Custom password reset flow using Supabase Admin API and SMTP.
        Requires SUPABASE_SERVICE_ROLE_KEY and SMTP credentials in .env.
        """
        import smtplib
        from email.mime.text import MIMEText
        import string
        import secrets

        if not supabase:
            return
        try:
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if not service_key:
                raise Exception("Server misconfiguration: SUPABASE_SERVICE_ROLE_KEY is missing. Please contact the administrator.")
            
            admin_supabase = create_client(os.getenv("SUPABASE_URL"), service_key)
            
            # Retrieve the user by email using the admin API
            response = admin_supabase.auth.admin.list_users()
            
            # Depending on the supabase-py version, list_users() might return a list directly 
            # or an object with a 'users' attribute.
            users_list = response if isinstance(response, list) else getattr(response, 'users', [])
            
            target_user = next((u for u in users_list if u.email == email), None)
            
            if not target_user:
                return # Silently return if user doesn't exist to prevent email enumeration
                
            # Generate a secure random 12-character temporary password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
            
            admin_supabase.auth.admin.update_user_by_id(target_user.id, {"password": temp_password})
            
            # Send the email with the temporary password
            smtp_server = os.getenv("SMTP_SERVER")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_username = os.getenv("SMTP_USERNAME")
            smtp_password = os.getenv("SMTP_PASSWORD")
            sender_email = os.getenv("SMTP_SENDER_EMAIL")
            
            if not all([smtp_server, smtp_username, smtp_password, sender_email]):
                raise Exception("Server misconfiguration: SMTP credentials are missing. Please contact the administrator.")
                
            msg = MIMEText(f"Your password for Temporiq AI has been reset.\n\nYour new temporary password is: {temp_password}\n\nPlease log in and change your password immediately by navigating to '⚙️ Account & System Status' in the sidebar.")
            msg['Subject'] = 'Temporiq AI - Password Reset'
            msg['From'] = sender_email
            msg['To'] = email
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                
        except Exception as e:
            raise Exception(f"Failed to reset password: {str(e)}")

    @staticmethod
    def set_session(access_token: str, refresh_token: str):
        """Set the session for the client using tokens from a password recovery link."""
        if not supabase:
            return
        try:
            # This authenticates the client for the next action (updating the password)
            supabase.auth.set_session(access_token, refresh_token)
        except AuthApiError as e:
            raise Exception(f"Failed to set session from recovery token: {e.message}")

    @staticmethod
    def exchange_code(code: str):
        """Exchange PKCE code for session."""
        if not supabase:
            return
        try:
            supabase.auth.exchange_code_for_session({"auth_code": code})
        except AuthApiError as e:
            raise Exception(f"Failed to exchange code: {e.message}")

    @staticmethod
    def update_user_password(new_password: str):
        """Update the password for the currently authenticated user."""
        if not supabase:
            return
        try:
            # After set_session is called, the client is authenticated, and we can update the user.
            supabase.auth.update_user({"password": new_password})
        except AuthApiError as e:
            raise Exception(f"Failed to update password: {e.message}")

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get the current authenticated user."""
        if not supabase:
            return None
        user = supabase.auth.get_user()
        return user.user.model_dump() if user and user.user else None


class WorkflowDB:
    """Workflow database operations."""

    @staticmethod
    def create_workflow(name: str, steps: List[str], user_id: str) -> Dict[str, Any]:
        """Create a new workflow."""
        if not supabase:
            return {"id": f"local-{datetime.now().timestamp()}", "name": name, "steps": steps}
        
        data = {
            "name": name,
            "steps": json.dumps(steps),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        try:
            result = supabase.table("workflows").insert(data).execute()
            if result.data and len(result.data) > 0:
                workflow = result.data[0]
                # Parse steps back from JSON if needed
                if isinstance(workflow.get("steps"), str):
                    workflow["steps"] = json.loads(workflow.get("steps", "[]"))
                return workflow
            else:
                raise Exception("No data returned from insert operation")
        except Exception as e:
            raise Exception(f"Failed to create workflow: {str(e)}")
    
    @staticmethod
    def get_workflows(user_id: str) -> List[Dict[str, Any]]:
        """Get all workflows."""
        if not supabase:
            return []
        
        result = supabase.table("workflows").select("*").eq("user_id", user_id).execute()
        for workflow in result.data:
            if isinstance(workflow.get("steps"), str):
                workflow["steps"] = json.loads(workflow["steps"])
        return result.data
    
    @staticmethod
    def get_workflow(workflow_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow by ID."""
        if not supabase:
            return None
        
        result = supabase.table("workflows").select("*").eq("id", workflow_id).eq("user_id", user_id).execute()
        if result.data:
            workflow = result.data[0]
            if isinstance(workflow.get("steps"), str):
                workflow["steps"] = json.loads(workflow.get("steps", "[]"))
            return workflow
        return None

    @staticmethod
    def update_workflow(workflow_id: str, name: str, steps: List[str], user_id: str) -> Dict[str, Any]:
        """Update an existing workflow."""
        if not supabase:
            return {"id": workflow_id, "name": name, "steps": steps, "user_id": user_id}
        
        data = {
            "name": name,
            "steps": json.dumps(steps),
            "updated_at": datetime.now().isoformat()
        }
        try:
            result = supabase.table("workflows").update(data).eq("id", workflow_id).eq("user_id", user_id).execute()
            if result.data and len(result.data) > 0:
                workflow = result.data[0]
                if isinstance(workflow.get("steps"), str):
                    workflow["steps"] = json.loads(workflow.get("steps", "[]"))
                return workflow
            else:
                raise Exception("No data returned from update operation")
        except Exception as e:
            raise Exception(f"Failed to update workflow: {str(e)}")

    @staticmethod
    def delete_workflow(workflow_id: str, user_id: str) -> bool:
        """Delete a workflow and its instances."""
        if not supabase:
            return True
        try:
            # Explicitly delete instances first to prevent foreign key constraint errors
            supabase.table("instances").delete().eq("workflow_id", workflow_id).eq("user_id", user_id).execute()
            supabase.table("workflows").delete().eq("id", workflow_id).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False

class InstanceDB:
    """Instance (patient/observation) database operations."""
    
    @staticmethod
    def create_instance(workflow_id: str, name: str, user_id: str) -> Dict[str, Any]:
        """Create a new instance."""
        if not supabase:
            return {
                "id": f"local-{datetime.now().timestamp()}",
                "workflow_id": workflow_id,
                "name": name,
                "current_step": 0,
                "started_at": None,
                "timestamps": [], # Initialize timestamps as an empty list
                "user_id": user_id,
                "notes": "", # Initialize notes as an empty string
                "created_at": datetime.now().isoformat()
            }
        
        data = {
            "workflow_id": workflow_id,
            "name": name,
            "current_step": 0,
            "started_at": None,
            "timestamps": json.dumps([]), # Store timestamps as JSON string
            "user_id": user_id,
            "notes": "", # Store notes as an empty string
            "created_at": datetime.now().isoformat()
        }
        result = supabase.table("instances").insert(data).execute()
        return result.data[0] if result.data else data
    
    @staticmethod
    def get_instances(workflow_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all instances for a workflow."""
        if not supabase:
            return []
        
        result = (
            supabase.table("instances")
            .select("*") # RLS will filter by user_id
            .eq("user_id", user_id) # Explicitly filter for clarity, though RLS handles it
            .eq("workflow_id", workflow_id)
            .order("created_at", desc=False)
            .execute()
        )
        for instance in result.data:
            if isinstance(instance.get("timestamps"), str):
                # Deserialize timestamps from JSON string to Python list
                instance["timestamps"] = json.loads(instance["timestamps"])
        return result.data
    
    @staticmethod
    def start_instance(instance_id: str, user_id: str) -> Dict[str, Any]:
        """Mark an instance as started."""
        if not supabase:
            return {"id": instance_id, "started_at": datetime.now().isoformat()}
        
        update_data = {
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        result = supabase.table("instances").update(update_data).eq("id", instance_id).eq("user_id", user_id).execute()
        return result.data[0] if result.data else update_data
    
    @staticmethod
    def complete_instance(instance_id: str, total_steps: int, user_id: str) -> Dict[str, Any]:
        """Mark an instance as completed with a stop timestamp."""
        completion_timestamp = datetime.now().isoformat()
        if not supabase:
            return {"id": instance_id, "current_step": total_steps, "timestamps": [{"step": -1, "timestamp": completion_timestamp}]}
        
        result = supabase.table("instances").select("timestamps").eq("id", instance_id).eq("user_id", user_id).execute()
        timestamps = []
        if result.data:
            raw_timestamps = result.data[0].get("timestamps", "[]")
            timestamps = json.loads(raw_timestamps)
            if not isinstance(timestamps, list):
                timestamps = []
        timestamps.append({"step": -1, "timestamp": completion_timestamp})
        update_data = {
            "current_step": total_steps,
            "timestamps": json.dumps(timestamps),
            "updated_at": datetime.now().isoformat()
        }
        result = supabase.table("instances").update(update_data).eq("id", instance_id).eq("user_id", user_id).execute()
        return result.data[0] if result.data else update_data
    
    @staticmethod
    def update_instance_timestamps(instance_id: str, new_timestamps: List[Dict[str, Any]], user_id: str, total_steps: int) -> Dict[str, Any]:
        """Update timestamps for an instance and check for completion."""
        if not supabase:
            num_completed = len({ts.get("step") for ts in new_timestamps if isinstance(ts, dict) and ts.get("step", -1) != -1})
            current_step = total_steps if num_completed >= total_steps else num_completed
            return {"id": instance_id, "timestamps": new_timestamps, "current_step": current_step}

        num_completed_steps = len({ts.get("step") for ts in new_timestamps if isinstance(ts, dict) and ts.get("step", -1) != -1})

        current_step_value = num_completed_steps

        # If all steps are completed, mark the instance as fully complete
        if num_completed_steps >= total_steps:
            current_step_value = total_steps
            # Add a completion timestamp if it doesn't exist
            if not any(ts.get("step") == -1 for ts in new_timestamps if isinstance(ts, dict)):
                new_timestamps.append({"step": -1, "timestamp": datetime.now().isoformat()})

        update_data = {
            "timestamps": json.dumps(new_timestamps),
            "current_step": current_step_value,
            "updated_at": datetime.now().isoformat()
        }
        result = supabase.table("instances").update(update_data).eq("id", instance_id).eq("user_id", user_id).execute()
        return result.data[0] if result.data else update_data
    
    @staticmethod
    def update_instance_notes(instance_id: str, notes: str, user_id: str) -> Dict[str, Any]:
        """Update notes for an instance."""
        if not supabase:
            return {"id": instance_id, "notes": notes, "user_id": user_id}
        
        update_data = {
            "notes": notes,
            "updated_at": datetime.now().isoformat()
        }
        try:
            result = supabase.table("instances").update(update_data).eq("id", instance_id).eq("user_id", user_id).execute()
            return result.data[0] if result.data else {"id": instance_id, "notes": notes, "user_id": user_id}
        except Exception as e:
            raise Exception(f"Failed to update instance notes: {str(e)}")

    
    @staticmethod
    def delete_instance(instance_id: str, user_id: str) -> bool:
        """Delete an instance."""
        if not supabase:
            return True
        result = supabase.table("instances").delete().eq("id", instance_id).eq("user_id", user_id).execute()
        return True

    @staticmethod
    def import_instances(workflow_id: str, instances_data: List[Dict[str, Any]], user_id: str) -> bool:
        """Import multiple instances at once."""
        if not supabase:
            return False
        
        insert_data = []
        for data in instances_data:
            insert_data.append({
                "workflow_id": workflow_id,
                "user_id": user_id,
                "name": data.get("name", "Imported Instance"),
                "notes": data.get("notes", ""),
                "current_step": data.get("current_step", 0),
                "started_at": data.get("started_at"),
                "timestamps": json.dumps(data.get("timestamps", [])),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        
        if insert_data:
            batch_size = 100
            for i in range(0, len(insert_data), batch_size):
                supabase.table("instances").insert(insert_data[i:i+batch_size]).execute()
        return True
