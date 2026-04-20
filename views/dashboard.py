"""Dashboard page for tracking instances."""
import streamlit as st
from app.database import WorkflowDB, InstanceDB # type: ignore
from utils.timer import TimestampLogger # type: ignore
from utils.validators import validate_instance_name # type: ignore
import time
import json
from datetime import datetime


def render_tracker_page(user_id: str):
    """Render the observation tracker."""
    
    # Get current workflow
    if "current_workflow_id" not in st.session_state or not st.session_state.current_workflow_id:
        st.title("⏱️ Observation Tracker")
        st.markdown("---")
        
        workflows = WorkflowDB.get_workflows(user_id)
        if not workflows:
            st.warning("No workflows found. Please create a workflow on the Workflows page first.")
            if st.button("Go to Workflows"):
                st.session_state.current_page = "Workflows"
                st.rerun()
            return
        
        st.info("Please select a workflow to begin tracking.")
        
        workflow_map = {wf["name"]: wf for wf in workflows}
        workflow_names = ["-- Select a workflow --"] + list(workflow_map.keys())
        
        selected_workflow_name = st.selectbox(
            "Available Workflows",
            options=workflow_names,
            index=0
        )
        
        if selected_workflow_name != "-- Select a workflow --":
            selected_workflow = workflow_map[selected_workflow_name]
            st.session_state.current_workflow_id = selected_workflow.get("id")
            st.session_state.current_workflow = selected_workflow
            st.rerun()
        return
    
    workflow_id = st.session_state.get("current_workflow_id")
    workflow = WorkflowDB.get_workflow(workflow_id, user_id)
    
    if not workflow:
        st.error("Workflow not found. Please create a workflow in Setup first.")
        if st.button("Go to Workflows"):
            st.session_state.current_page = "Workflows"
            st.rerun()
        return
    
    steps = workflow.get("steps", [])
    total_steps = len(steps)
    
    # Header
    st.title("⏱️ Observation Tracker")
    st.write(f"**{workflow.get('name')}** • {total_steps} steps")
    
    st.markdown("---")
    
    # Create new instance section
    if "clear_new_instance" not in st.session_state:
        st.session_state["clear_new_instance"] = False

    # Initialize auto-start toggle state if it doesn't exist
    if "auto_start_instances" not in st.session_state:
        st.session_state.auto_start_instances = False

    if st.session_state["clear_new_instance"]:
        st.session_state["new_instance_name"] = ""
        st.session_state["clear_new_instance"] = False

    with st.form("add_instance_form"):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            new_instance_name = st.text_input(
                "Add new instance:",
                placeholder="e.g., Patient #101, Room 203",
                key="new_instance_name",
                label_visibility="collapsed"
            )
        with col2:
            st.toggle("Auto-start on add", key="auto_start_instances", help="If enabled, new instances will be started immediately upon creation.")
        with col3:
            add_pressed = st.form_submit_button("➕ Add", width='stretch')

    if add_pressed:
        valid, error = validate_instance_name(new_instance_name)
        if not valid:
            st.error(error)
        else:
            try:
                new_instance = InstanceDB.create_instance(workflow_id, new_instance_name, user_id)
                st.success("Instance created!")
                if st.session_state.auto_start_instances and new_instance.get("id"):
                    InstanceDB.start_instance(new_instance["id"], user_id)
                    st.toast("Instance started automatically.")
                st.session_state["clear_new_instance"] = True
                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Display instances
    try:
        instances = InstanceDB.get_instances(workflow_id, user_id)
        
        if not instances:
            st.info("No instances tracked yet. Add one above!")
            return
        
        active_instances = []
        completed_instances = []
        
        for instance in instances:
            current_step = instance.get("current_step", 0)
            if current_step >= total_steps:
                completed_instances.append(instance)
            else:
                active_instances.append(instance)
        
        if active_instances:
            st.subheader("▶️ Active Instances")
            for instance in active_instances: # type: ignore
                render_instance_card(instance=instance, steps=steps, workflow_id=workflow_id, user_id=user_id)
        
        if completed_instances:
            st.markdown("---")
            st.subheader("✅ Completed Instances")

            # Initialize session state for expand/collapse all
            if 'completed_expansion_state' not in st.session_state:
                st.session_state.completed_expansion_state = False # False for collapsed, True for expanded

            c1, c2, _ = st.columns([1, 1, 5])
            with c1:
                if st.button("Expand all", width='stretch', key="expand_all"):
                    st.session_state.completed_expansion_state = True
            with c2:
                if st.button("Collapse all", width='stretch', key="collapse_all"):
                    st.session_state.completed_expansion_state = False

            for instance in completed_instances: # type: ignore
                with st.expander(f"**{instance.get('name')}**", expanded=st.session_state.completed_expansion_state):
                    render_instance_card(instance=instance, steps=steps, workflow_id=workflow_id, user_id=user_id)
    
    except Exception as e:
        st.error(f"Error loading instances: {str(e)}")
    
    # Navigation
    st.markdown("---")
    if st.button("⚙️ Change Workflow"):
        st.session_state.current_workflow_id = None
        st.session_state.current_workflow = None
        st.session_state.current_page = "Workflows" # type: ignore
        st.rerun()


def render_instance_card(instance, steps, workflow_id, user_id: str):
    """Render a compact instance card with individual step buttons."""
    
    instance_id = instance.get("id")
    name = instance.get("name")
    timestamps = instance.get("timestamps", [])
    started_at = instance.get("started_at", "") or ""
    current_notes = instance.get("notes", "")
    
    if isinstance(timestamps, str):
        try:
            timestamps = json.loads(timestamps)
        except:
            timestamps = []
    
    total_steps = len(steps)
    completed_steps = {int(ts.get("step", -1)) for ts in timestamps if isinstance(ts, dict) and 0 <= int(ts.get("step", -1)) < total_steps}
    completion_ts = next((ts for ts in timestamps if isinstance(ts, dict) and int(ts.get("step", -1)) == -1), None)
    is_started = bool(started_at)
    is_completed = instance.get("current_step", 0) >= total_steps
    progress_percent = len(completed_steps) / total_steps if total_steps > 0 else 0
    
    with st.container(border=True, key=f"instance_{instance_id}"):
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            if not is_started:
                status_text = "Not started"
                status_icon = "🟡"
            elif is_completed:
                status_text = "Completed"
                status_icon = "✅"
            else:
                status_text = "In progress"
                status_icon = "🔄"
            st.write(f"**{status_icon} {name}**")
            st.caption(status_text)
            if not is_started:
                st.caption("Press ▶️ to begin.")
        with col2:
            st.write(f"{len(completed_steps)}/{total_steps} steps • {int(progress_percent*100)}%")
            if is_started and started_at:
                st.caption(f"Started: {TimestampLogger.format_timestamp(started_at)}")
            if is_completed and completion_ts:
                st.caption(f"Completed: {TimestampLogger.format_timestamp(completion_ts.get('timestamp', ''))}")
        with col3:
            c1, c2 = st.columns(2)
            with c1:
                if not is_started:
                    if st.button("▶️", key=f"start_{instance_id}", width='stretch', help="Start"):
                        InstanceDB.start_instance(instance_id, user_id)
                        st.rerun()
                elif not is_completed:
                    if st.button("⏹️", key=f"stop_{instance_id}", width='stretch', help="Stop"):
                        InstanceDB.complete_instance(instance_id, total_steps, user_id)
                        st.rerun()
                else:
                    st.button("✅", key=f"done_{instance_id}", width='stretch', disabled=True, help="Completed")
            with c2:
                with st.popover("🗑️", width='stretch', help="Delete Instance"):
                    st.write(f"Are you sure you want to delete **{name}**?")
                    if st.button("Confirm Delete", type="primary", key=f"confirm_delete_{instance_id}", width='stretch'):
                        InstanceDB.delete_instance(instance_id, user_id)
                        st.rerun()
        
        st.markdown("---")
        
        step_cols = st.columns(min(total_steps, 5))
        for step_idx in range(total_steps):
            col = step_cols[step_idx % len(step_cols)]
            with col:
                is_done = step_idx in completed_steps
                step_name = steps[step_idx]
                
                display_label = step_name
                button_label = f"✓ {display_label}" if is_done else display_label
                
                if st.button(
                    button_label,
                    key=f"step_{instance_id}_{step_idx}",
                    width='stretch',
                    disabled=not is_started or is_completed,
                    help=step_name  # Show full step name on hover
                ):
                    if is_done:
                        new_timestamps = [ts for ts in timestamps if int(ts.get("step", -1)) != step_idx]
                    else:
                        new_ts = {
                            "step": step_idx,
                            "timestamp": datetime.now().isoformat()
                        }
                        new_timestamps = timestamps + [new_ts] if isinstance(timestamps, list) else [new_ts] # type: ignore
                    InstanceDB.update_instance_timestamps(instance_id, new_timestamps, user_id, total_steps)
                    st.rerun()
        
        # Notes section
        st.markdown("---")
        with st.expander("📝 Notes"):
            # Use a unique key for the text_area to prevent issues with multiple cards
            # and set a callback to save notes when the text area changes
            edited_notes = st.text_area(
                "Add or edit notes for this instance:",
                value=current_notes,
                key=f"notes_editor_{instance_id}",
                on_change=lambda: InstanceDB.update_instance_notes(instance_id, st.session_state[f"notes_editor_{instance_id}"], user_id)
            )
            # No explicit save button needed if using on_change, but you could add one if preferred.
            # If you prefer a button, remove on_change and add a button that calls InstanceDB.update_instance_notes

        if completed_steps or is_completed:
            st.divider()
            st.write("**⏱️ Step Timeline**")
            sorted_ts = sorted(
                [ts for ts in timestamps if isinstance(ts, dict)],
                key=lambda x: x.get("timestamp", "")
            )
            
            for idx, ts_entry in enumerate(sorted_ts, start=1):
                step_idx = int(ts_entry.get("step", -1))
                ts_time = ts_entry.get("timestamp", "")
                if step_idx == -1:
                    step_name = "Completed"
                elif 0 <= step_idx < total_steps:
                    step_name = steps[step_idx]
                else:
                    continue
                if idx == 1:
                    duration = TimestampLogger.calculate_elapsed_time(started_at, ts_time) if started_at else "N/A"
                else:
                    prev_time = sorted_ts[idx - 2].get("timestamp", "") if idx > 1 else started_at # Corrected index for previous timestamp
                    duration = TimestampLogger.calculate_elapsed_time(prev_time, ts_time)
                st.caption(f"{idx}. {step_name} • {duration}")
            
            if is_completed and completion_ts:
                total_time = TimestampLogger.calculate_elapsed_time(started_at, completion_ts.get("timestamp", ""))
                st.write(f"**Total time:** {total_time}")
