"""Timer and timestamp utilities."""
from datetime import datetime
from typing import List, Dict, Any
import json


class TimestampLogger:
    """Logs timestamps for workflow steps."""
    
    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()
    
    @staticmethod
    def format_timestamp(timestamp_str: str) -> str:
        """Format timestamp for display."""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%H:%M:%S")
        except:
            return timestamp_str
    
    @staticmethod
    def format_timestamp_full(timestamp_str: str) -> str:
        """Format timestamp with date for display."""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str
    
    @staticmethod
    def calculate_elapsed_time(start_timestamp: str, end_timestamp: str) -> str:
        """Calculate elapsed time between two timestamps."""
        try: # Ensure timestamps are correctly parsed, handling 'Z' for UTC
            start = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_timestamp.replace('Z', '+00:00'))
            elapsed = end - start
            
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}s"
        except:
            return "N/A"
    
    @staticmethod
    def calculate_elapsed_time_hms(start_timestamp: str, end_timestamp: str) -> str:
        """Calculate elapsed time and return in hh:mm:ss format."""
        try:
            start = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_timestamp.replace('Z', '+00:00'))
            elapsed = end - start
            
            total_seconds = int(elapsed.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except:
            return "N/A"
    
