"""Custom CSS styles for Aegis Time AI."""

CUSTOM_CSS = """
<style>
    /* Tablet-optimized styles */
    html, body {
        margin: 0;
        padding: 0;
        font-size: 16px;
        -webkit-user-select: none;
        user-select: none;
    }
    
    /* High contrast colors */
    :root {
        --primary: #1F77B4;
        --success: #2CA02C;
        --warning: #FF7F0E;
        --danger: #D62728;
        --dark-bg: #FFFFFF;
        --light-bg: #F0F2F6;
        --text-dark: #262730;
        --text-light: #666666;
        --border: #CCCCCC;
    }
    
    /* Main container */
    .main {
        max-width: 1400px;
        padding: 1rem;
    }
    
    /* Cards with high contrast */
    .card {
        background-color: var(--dark-bg);
        border: 2px solid var(--text-dark);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Instance cards - larger for tablet */
    .instance-card {
        background-color: var(--dark-bg);
        border: 3px solid var(--primary);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .instance-card.active {
        border-color: var(--success);
        box-shadow: 0 0 0 4px rgba(44, 160, 44, 0.2);
    }
    
    .instance-card.completed {
        background-color: var(--light-bg);
        border-color: var(--success);
        opacity: 0.8;
    }
    
    /* Progress bar */
    .progress-bar {
        height: 24px;
        background-color: var(--light-bg);
        border: 2px solid var(--border);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--success));
        transition: width 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Large buttons for tablet */
    .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
        border: 2px solid var(--text-dark);
        min-height: 60px;
        height: auto;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: normal;
        word-wrap: break-word;
    }
    
    /* Next Step button - primary action */
    .next-step-btn {
        background-color: var(--primary) !important;
        color: white !important;
        border: 3px solid var(--primary) !important;
        font-size: 24px !important;
        font-weight: bold !important;
        min-height: 80px !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
    }
    
    .next-step-btn:hover {
        background-color: #1557A0 !important;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.4);
    }
    
    .next-step-btn:active {
        transform: scale(0.98);
    }
    
    /* Reset button */
    .reset-btn {
        background-color: var(--danger) !important;
        color: white !important;
        border: 2px solid var(--danger) !important;
        font-size: 16px !important;
        min-height: 50px !important;
    }
    
    .reset-btn:hover {
        background-color: #B81F25 !important;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: var(--text-dark);
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    h2 {
        font-size: 2rem;
        border-bottom: 3px solid var(--primary);
        padding-bottom: 0.5rem;
    }
    
    h3 {
        font-size: 1.5rem;
        color: var(--primary);
    }
    
    /* Input fields */
    .stTextInput input,
    .stSelectbox select {
        font-size: 16px;
        padding: 12px;
        border-radius: 6px;
        border: 2px solid var(--border);
    }
    
    .stTextInput input:focus,
    .stSelectbox select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.1);
    }
    
    /* Form sections */
    .form-section {
        background-color: var(--light-bg);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary);
    }
    
    /* Info message */
    .info-box {
        background-color: #E8F4F8;
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: var(--text-dark);
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin: 1.5rem 0;
        gap: 0.5rem;
    }
    
    .step {
        flex: 1;
        height: 8px;
        background-color: var(--light-bg);
        border-radius: 4px;
        border: 1px solid var(--border);
    }
    
    .step.active {
        background-color: var(--primary);
    }
    
    .step.completed {
        background-color: var(--success);
    }
    
    /* Responsive grid */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        .stButton > button {
            font-size: 16px;
            padding: 0.8rem 1.5rem;
        }
    }
    
    /* Timestamp display */
    .timestamp {
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: var(--text-light);
        margin-top: 0.5rem;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .badge.pending {
        background-color: #FFF3CD;
        color: #856404;
        border: 2px solid #FFC107;
    }
    
    .badge.active {
        background-color: #D4EDDA;
        color: #155724;
        border: 2px solid #28A745;
    }
    
    .badge.completed {
        background-color: #E2E3E5;
        color: #383D41;
        border: 2px solid #6C757D;
    }
</style>
"""

def inject_custom_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
