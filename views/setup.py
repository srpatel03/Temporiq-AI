"""Setup page for creating workflows."""
import streamlit as st
import time
from app.database import WorkflowDB # type: ignore
from utils.validators import validate_workflow_name, validate_steps # type: ignore


def clear_workflow_form_state():
    """Resets the state of the workflow form to its defaults."""
    st.session_state.editing_workflow_id = None
    st.session_state["workflow_name"] = ""
    st.session_state["num_steps"] = 3
    for i in range(10):
        if f"step_{i}" in st.session_state:
            st.session_state[f"step_{i}"] = ""

def create_workflow_callback(user_id: str):
    """Callback to handle workflow creation logic."""
    num_steps = int(st.session_state.get("num_steps", 3))
    wf_name = st.session_state.get("workflow_name", "")
    wf_steps = [st.session_state.get(f"step_{i}", "") for i in range(num_steps)]

    valid_name, name_error = validate_workflow_name(wf_name)
    if not valid_name:
        st.session_state.form_message = ("error", f"❌ {name_error}")
        return

    valid_steps, steps_error = validate_steps(wf_steps)
    if not valid_steps:
        st.session_state.form_message = ("error", f"❌ {steps_error}")
        return

    try:
        workflow = WorkflowDB.create_workflow(wf_name, wf_steps, user_id)
        st.session_state.current_workflow_id = workflow.get("id")
        st.session_state.current_workflow = workflow
        st.session_state.form_message = ("success", f"✅ Workflow '{wf_name}' created successfully! Redirecting...")
        st.session_state.redirect_to_tracker = True
        clear_workflow_form_state()
    except Exception as e:
        st.session_state.form_message = ("error", f"❌ Error creating workflow: {str(e)}")

def update_workflow_callback(user_id: str):
    """Callback to handle workflow update logic."""
    num_steps = int(st.session_state.get("num_steps", 3))
    wf_name = st.session_state.get("workflow_name", "")
    wf_steps = [st.session_state.get(f"step_{i}", "") for i in range(num_steps)]

    valid_name, name_error = validate_workflow_name(wf_name)
    if not valid_name:
        st.session_state.form_message = ("error", f"❌ {name_error}")
        return

    valid_steps, steps_error = validate_steps(wf_steps)
    if not valid_steps:
        st.session_state.form_message = ("error", f"❌ {steps_error}")
        return

    try:
        WorkflowDB.update_workflow(st.session_state.editing_workflow_id, wf_name, wf_steps, user_id)
        st.session_state.form_message = ("success", f"✅ Workflow '{wf_name}' updated successfully!")
        clear_workflow_form_state()
    except Exception as e:
        st.session_state.form_message = ("error", f"❌ Error updating workflow: {str(e)}")

def set_edit_workflow_state(workflow):
    """Callback to set up the form for editing an existing workflow."""
    st.session_state.editing_workflow_id = workflow.get('id')
    st.session_state.workflow_name = workflow.get('name')
    steps = workflow.get('steps', [])
    st.session_state.num_steps = len(steps)
    for i in range(10):
        st.session_state[f"step_{i}"] = ""
    for i, step in enumerate(steps):
        st.session_state[f"step_{i}"] = step

def render_workflows_page(user_id: str):
    """Render the workflow management page."""
    # Initialize editing state
    if 'editing_workflow_id' not in st.session_state:
        st.session_state.editing_workflow_id = None

    is_editing = st.session_state.editing_workflow_id is not None

    # Handle redirection which is flagged in a callback
    if st.session_state.get("redirect_to_tracker"):
        del st.session_state.redirect_to_tracker
        time.sleep(1)
        st.session_state.current_page = "Tracker"
        st.rerun()

    st.title("⚙️ Workflows")
    
    # --- Form Section ---
    form_title = "Edit Workflow" if is_editing else "Create New Workflow"
    with st.container(border=True):
        st.subheader(form_title)

        # Display messages set by callbacks
        if 'form_message' in st.session_state:
            msg_type, msg_text = st.session_state.form_message
            st.toast(msg_text, icon="✅" if msg_type == "success" else "❌")
            if msg_type == "error":
                st.error(msg_text)
            del st.session_state.form_message

        if not is_editing:
            st.write("Define a custom workflow with 2-10 steps for your clinical observation.")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.text_input(
                "Workflow Name",
                placeholder="e.g., Patient Intake Process",
                key="workflow_name"
            )

        with col2:
            num_steps_input = st.number_input(
                "Number of Steps",
                min_value=2,
                max_value=10,
                value=st.session_state.get("num_steps", 3),
                key="num_steps"
            )

        st.markdown("---")
        st.subheader("Define Your Steps")
        st.caption("Name each step to mark its completion (e.g., 'Check-in Done', 'Vitals Taken'). The timer measures the duration leading up to each completed step.")

        num_steps = int(num_steps_input)
        cols = st.columns(min(num_steps, 3))

        for i in range(num_steps):
            key = f"step_{i}"
            col = cols[i % len(cols)]
            with col:
                st.text_input(
                    f"Step {i + 1}",
                    placeholder=f"e.g., Step {i + 1}",
                    key=key,
                    value=st.session_state.get(key, "")
                )

        st.markdown("---")

        # --- Action Buttons ---
        if is_editing:
            update_col, _, cancel_col = st.columns([1, 2, 1]) # Ratio for Update, Spacer, Cancel
            with update_col:
                st.button("💾 Update Workflow", key="update_workflow", type="primary", on_click=update_workflow_callback, args=(user_id,), use_container_width=True)
            with cancel_col:
                st.button("❌ Cancel Edit", key="cancel_edit", on_click=clear_workflow_form_state, use_container_width=True)
        else:
            create_col, _, reset_col = st.columns([1, 2, 1]) # Ratio for Create, Spacer, Reset
            with create_col:
                st.button("✅ Create Workflow", key="save_workflow", type="primary", on_click=create_workflow_callback, args=(user_id,), use_container_width=True)
            with reset_col:
                st.button("🔄 Reset Form", key="reset_form", on_click=clear_workflow_form_state, use_container_width=True)
    
    # Display existing workflows
    st.markdown("---")
    st.subheader("📋 Existing Workflows")
    
    try:
        workflows = WorkflowDB.get_workflows(user_id)
        if workflows:
            for workflow in workflows:
                with st.container(border=True):
                    col1, col2, actions_col = st.columns([3, 1, 3])
                    
                    with col1:
                        st.write(f"**{workflow.get('name')}**")
                        steps_list = workflow.get("steps", [])
                        if steps_list:
                            st.caption(f"Steps: {', '.join(steps_list[:3])}{'...' if len(steps_list) > 3 else ''}")
                    with col2:
                        st.caption(f"{len(steps_list)} steps")
                    
                    with actions_col:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("▶️", key=f"select_{workflow.get('id')}", help="Use this workflow", use_container_width=True):
                                st.session_state.current_workflow_id = workflow.get("id")
                                st.session_state.current_workflow = workflow
                                st.session_state.current_page = "Tracker"
                                st.rerun()
                        with c2:
                            st.button("✏️", key=f"edit_{workflow.get('id')}", help="Edit this workflow", use_container_width=True, on_click=set_edit_workflow_state, args=(workflow,))
                        with c3:
                            with st.popover("🗑️", use_container_width=True, key=f"popover_delete_wf_{workflow.get('id')}", help="Delete this workflow"):
                                st.write(f"Are you sure you want to delete workflow **{workflow.get('name')}**?")
                                st.caption("This will also delete all associated instances.")
                                if st.button("Confirm Delete", type="primary", key=f"confirm_delete_wf_{workflow.get('id')}", use_container_width=True):
                                    if WorkflowDB.delete_workflow(workflow.get('id'), user_id):
                                        st.success("Workflow deleted successfully.")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete workflow.")
        else:
            st.info("No workflows created yet. Create one above to get started!")
    except Exception as e:
        st.warning(f"Could not load existing workflows: {str(e)}")
