# QUICK START Guide - Temporiq AI

## 30-Second Setup

### Option 1: Automated Setup (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Automated Setup (Windows)
```bash
setup.bat
```

### Option 3: Manual Setup
```bash
# 1. Create virtual environment
python -m venv .venv

# Activate the virtual environment. Choose the command for your shell:
# On macOS/Linux (bash/zsh):
source .venv/bin/activate
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

> **Note for PowerShell users:** If you get an error about "running scripts is disabled," run this command once in PowerShell, then try activating again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
echo "Edit the new .env file with your credentials:"
echo "SUPABASE_URL=your_supabase_url"
echo "SUPABASE_KEY=your_supabase_anon_key"
echo "GCP_PROJECT=your-gcp-project-id"
echo "GCP_LOCATION=us-central1  # Or another valid Vertex AI region"
echo "ADMIN_EMAIL=your_admin_email@example.com # Email for the admin user"
echo "GCP_MODEL_NAME=gemini-2.5-pro # Optional: Defaults to gemini-2.5-pro"
echo ""
echo "Then, enable the Vertex AI API for your project:"
echo "Visit: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com"
echo "And click 'Enable'."
echo ""
echo "Then, set the path to your Google Cloud service account key:"
echo "# On macOS/Linux:"
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/key.json"'
echo "# On Windows (in Command Prompt): set GOOGLE_APPLICATION_CREDENTIALS=\\"C:\\path\\to\\your\\key.json\\""

# 4. Run the app
streamlit run app.py
```

## Getting Supabase Credentials (2 minutes)

1. Visit https://supabase.com and sign up free
2. Create a new project
3. Wait for project to initialize (~1-2 min)
4. In left sidebar, click "Project Settings" → "API"
5. Copy **Project URL** and **Anon Key** into `.env`:
   ```
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_KEY=eyJxxx...
   ```
6. Go back to "SQL Editor" and run the SQL setup script from README.md

## Run the App

```bash
streamlit run app.py
```

Visit: http://localhost:8501

## Testing Without Supabase

For quick testing without Supabase:
1. Leave `.env` empty or use dummy values
2. App will work locally but won't persist data
3. Data resets on page refresh

## Common Issues

**Port 8501 already in use?**
```bash
streamlit run app.py --server.port 8502
```

**Module not found?**
```bash
pip install -r requirements.txt --upgrade
```

**Slow performance?**
- Close other browser tabs
- Clear cache: `rm -rf ~/.streamlit/cache_*`

## Next: Create Your First Workflow

1. Open http://localhost:8501
2. Go to "Setup" tab
3. Enter workflow name: "Patient Intake"
4. Set 4 steps: Check-in, Triage, Assessment, Discharge
5. Click "Create Workflow"
6. Go to "Dashboard" and start tracking!

---

For full documentation, see README.md
