"""Configuration constants for the app."""

# App constants
APP_NAME = "Aegis Time AI"
APP_VERSION = "1.0.0"
APP_ICON = "⏱️"

# Workflow constraints
MIN_STEPS = 2
MAX_STEPS = 10
MAX_WORKFLOW_NAME_LENGTH = 100
MAX_STEP_NAME_LENGTH = 50
MAX_INSTANCE_NAME_LENGTH = 100

# UI configuration
SIDEBAR_STATE = "collapsed"
LAYOUT_MODE = "wide"

# Color scheme (high-contrast)
PRIMARY_COLOR = "#1F77B4"
SUCCESS_COLOR = "#2CA02C"
WARNING_COLOR = "#FF7F0E"
DANGER_COLOR = "#D62728"
BG_COLOR = "#FFFFFF"
TEXT_COLOR = "#262730"

# Time format
TIME_FORMAT = "%H:%M:%S"
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Database tables
WORKFLOWS_TABLE = "workflows"
INSTANCES_TABLE = "instances"
