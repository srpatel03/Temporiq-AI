# Temporiq AI

Clinical operations observation tool for tracking patient workflows in real-time with timestamp logging and progress visualization.

## Features 

✅ **Workflow Setup**
- Create custom workflows with 2-10 steps
- Personalize step names for your clinical process
- Multiple workflow templates support

📊 **Observation Tracker**
- Track multiple instances (patients, rooms, etc.) simultaneously
- Real-time progress bars and step indicators
- Visual status badges (In Progress / Completed)

📈 **Reporting & Export**
- Generate summary reports for any workflow
- Calculate total duration and per-step duration for all instances
- Export reports to Excel (.xlsx) for further analysis
- AI-powered analysis to identify bottlenecks and suggest improvements
- Export AI analysis to a markdown file

📥 **Data Import**
- Import previously exported observation data from Excel
- Merge records from multiple users or devices
- Automatic step duration validation

⚙️ **System Monitoring**
- Built-in status check for Supabase and Vertex AI connections
- Admin-specific detailed diagnostic views

⏱️ **Timer & Timestamps**
- Large, tablet-optimized "Next Step" button
- Automatic timestamp logging for each step transition
- Duration tracking per step and total workflow time
- Timeline view with detailed timestamps

🎨 **User Interface**
- Minimalist, high-contrast design optimized for clinical environments
- Tablet-responsive layout with large touch targets
- Card-based instance view for quick scanning
- Mobile-first responsive design

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: Supabase (PostgreSQL)
- **UI Framework**: CSS3 with responsive design

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/srpatel03/Temporiq-AI.git
cd Temporiq-AI
```

### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate the virtual environment. Choose the command for your shell:

# On macOS/Linux (bash/zsh):
source .venv/bin/activate

# On Windows (Command Prompt):
.\.venv\Scripts\activate.bat

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```.env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GCP_PROJECT=your-gcp-project-id
GCP_LOCATION=your-gcp-location
ADMIN_EMAIL=your_admin_email@example.com # Email for the user who sees the detailed System Status page
GCP_MODEL_NAME=gemini-2.5-pro # Optional: Defaults to gemini-2.5-pro

# SMTP Configuration for Password Resets (e.g., via Resend)
SMTP_SERVER=smtp.resend.com
SMTP_PORT=587
SMTP_USERNAME=resend
SMTP_PASSWORD=re_your_resend_api_key
SMTP_SENDER_EMAIL=onboarding@resend.dev
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

#### Getting Supabase Credentials:

1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. In Project Settings, copy:
   - **Project URL** → `SUPABASE_URL`
   - **Anon Public** → `SUPABASE_KEY`

#### Getting Google Cloud Credentials (for AI Analysis):

1.  Go to the Google Cloud Console and create a new project or select an existing one. Copy the **Project ID**.
2.  Enable the **Vertex AI API** for your project. You can use this direct link.
3.  Create a service account to allow the application to authenticate.
    -   Go to **IAM & Admin > Service Accounts** and click **Create Service Account**.
    -   Give it a name (e.g., "temporiq-ai-runner") and grant it the **Vertex AI User** role.
    -   After creating the account, click on it, go to the **Keys** tab, click **Add Key > Create new key**, select **JSON**, and download the key file.
4.  Update your `.env` file with your Project ID and a valid location:
    ```.env
    GCP_PROJECT=your-gcp-project-id
    GCP_LOCATION=us-central1
    ```
5.  **Set an environment variable** in your terminal that points to the key file you downloaded. This command must be run in every new terminal session before you start the app.
    -   **macOS/Linux:** `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"`
    -   **Windows (Command Prompt):** `set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\key.json"`
    -   **Windows (PowerShell):** `$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\key.json"`

4. Create these tables in Supabase SQL Editor:

```sql
-- Workflows table
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  name VARCHAR(100) NOT NULL,
  steps JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Instances table
CREATE TABLE instances (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  name VARCHAR(100) NOT NULL,
  notes TEXT,
  current_step INTEGER DEFAULT 0,
  started_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  timestamps JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_instances_workflow ON instances(workflow_id);
CREATE INDEX idx_workflows_user ON workflows(user_id);
CREATE INDEX idx_instances_user ON instances(user_id);
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment

This application is ready to be deployed to Streamlit Community Cloud.

For a complete step-by-step guide, please see the **Deployment Guide**.


## Usage Guide

### Workflows Screen (⚙️)
1. Enter a **Workflow Name** (e.g., "Patient Intake")
2. Select the **Number of Steps** (2-10)
3. Define each step name (e.g., Check-in, Triage, Consult)
4. Click **Create Workflow** 
5. Select a workflow to start tracking

### Tracker (📊)
1. On the tracker page, view workflow progress and active instances.
2. Click **➕ Add Instance** to start tracking a new case.
3. Enter an instance name (e.g., "Patient #101").
4. Use the step buttons to advance through the workflow.
5. Expand the **Notes** or **Timeline** sections for more detail.

### Reporting (📈)
1. Navigate to the Reporting page from the sidebar.
2. Select a workflow from the dropdown menu.
3. View the summary table of all instances.
4. Click **Export to Excel** to download the data.
5. Click **Generate Analysis** to get AI-powered insights on your workflow's performance.
6. Click **Export Analysis** to save the AI insights as a markdown file.

## Features in Detail

### Progress Tracking
- **Progress Bar**: Visual indicator of workflow completion percentage
- **Step Indicators**: Color-coded timeline (Completed = Green, Current = Blue, Pending = Gray)
- **Status Badges**: Quick status at a glance (In Progress / Completed)

### Timer Features
- Automatic timestamp logging on each step
- Total elapsed time display
- Per-step duration calculation
- Full timeline with timestamps in MM:SS format

### Mobile Optimization
- Tablet-sized touch targets (60px+ buttons)
- Responsive grid layout
- Collapsible navigation
- Large, readable typography

## Project Structure

```
Temporiq-AI/
├── app.py                          # Main application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
│
├── app/
│   ├── __init__.py               # Package initialization
│   ├── database.py               # Supabase connections & queries
│   └── styles.py                 # Custom CSS styling
│
├── pages/
│   ├── workflows.py              # Workflow creation view
│   └── tracker.py              # Main observation tracker view
│
├── utils/
│   ├── timer.py                  # Timestamp & duration utilities
│   └── validators.py             # Input validation functions
│
└── .streamlit/
    └── config.toml               # Streamlit configuration
```

## API Reference

### Database Methods

#### WorkflowDB
```python
WorkflowDB.create_workflow(name: str, steps: List[str]) -> Dict
WorkflowDB.get_workflows() -> List[Dict]
WorkflowDB.get_workflow(workflow_id: str) -> Optional[Dict]
WorkflowDB.update_workflow(workflow_id: str, name: str, steps: List[str], user_id: str) -> Dict
WorkflowDB.delete_workflow(workflow_id: str, user_id: str) -> bool
```

#### InstanceDB
```python
InstanceDB.create_instance(workflow_id: str, name: str) -> Dict
InstanceDB.get_instances(workflow_id: str) -> List[Dict]
InstanceDB.update_instance_step(instance_id: str, new_step: int) -> Dict
InstanceDB.delete_instance(instance_id: str) -> bool
```

### Timer Utilities
```python
TimestampLogger.get_current_timestamp() -> str
TimestampLogger.format_timestamp(timestamp_str: str) -> str
TimestampLogger.calculate_elapsed_time(start: str, end: str) -> str
TimestampLogger.get_total_duration(timestamps: List[Dict]) -> str
```

## Keyboard Shortcuts

- **W** → Go to Workflows
- **T** → Go to Tracker
- **R** → Go to Reporting

## Performance Tips

- **For 50+ instances**: Use the filter checkboxes to hide completed instances
- **For faster navigation**: Use keyboard shortcuts
- **Database**: Supabase free tier supports 500K rows (plenty for daily usage)

## Troubleshooting

### App won't start
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache_*
streamlit run app.py
```

### Supabase connection errors
- Verify `.env` file has correct credentials
- Check Supabase tables are created with proper schema
- Ensure RLS (Row-Level Security) is disabled or properly configured

### Timestamps not recording
- Check browser console for errors
- Verify `timestamps` column exists in instances table
- Clear browser cache and reload

## Contributing

We welcome contributions! If you've made changes locally and want to save them to your GitHub repository, follow these steps. This is the standard process for committing and pushing code.

### Standard Git Workflow

1.  **Check Status**: Open your terminal in the project directory and run this command to see which files have been changed or are new:
    ```bash
    git status
    ```

2.  **Stage Changes**: Add all the new and modified files to be included in your next commit. The `.` stands for all files in the current directory.
    ```bash
    git add .
    ```

3.  **Commit Changes**: Save your changes to your local repository history. Write a clear, descriptive message about what you've changed.
    ```bash
    git commit -m "feat: Add initial application files and project structure"
    ```

4.  **Push to GitHub**: Upload your local commits to the remote repository on GitHub.
    ```bash
    git push
    ```

After pushing, you should see all your project files appear in your repository on GitHub.com. For collaborative projects, it's best practice to work in a feature branch and open a Pull Request, but for your own project, pushing directly to `main` is fine to get started.

## License

MIT License - See LICENSE file for details