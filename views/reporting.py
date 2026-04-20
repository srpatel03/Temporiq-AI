"""Reporting page for workflow analysis."""
import streamlit as st
import pandas as pd
from app.database import WorkflowDB, InstanceDB
from utils.timer import TimestampLogger
from typing import List, Dict, Any
import io
import os
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, date
from app.gcp import GEMINI_MODEL, IS_CONFIGURED, CONFIG_ERROR

def generate_ai_analysis(df: pd.DataFrame, workflow_name: str):
    """Generates AI analysis of the workflow data using the Vertex AI Gemini API."""
    if not IS_CONFIGURED or not GEMINI_MODEL:
        return f"Vertex AI is not configured correctly. Please check the System Status page for details. Error: {CONFIG_ERROR}"
    try:
        data_summary = df.to_markdown(index=False)

        prompt = f"""
        As an expert in clinical operations and process optimization, please analyze the following performance data for the "{workflow_name}" workflow.

        The data shows the duration for each step and the total duration for several instances. All durations are in a "Xm Ys" or "Xh Ym Zs" format.

        **Workflow Performance Data:**
        ```
        {data_summary}
        ```

        **Your Task:**
        Based on the data provided, please provide a concise analysis in markdown format that includes:
        1.  **Overall Performance Summary:** A brief overview of the workflow's efficiency.
        2.  **Potential Bottlenecks:** Identify which step(s) take the longest on average or have the most variability. These are likely bottlenecks.
        3.  **Actionable Recommendations:** Suggest 2-3 specific, practical improvements to address the identified bottlenecks and improve the overall workflow.

        Present your analysis in a clear, easy-to-read markdown format.
        """

        response = GEMINI_MODEL.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the AI analysis: {str(e)}"
def prepare_report_data(instances: List[Dict[str, Any]], steps: List[str], duration_formatter=TimestampLogger.calculate_elapsed_time) -> pd.DataFrame:
    """Process instance data into a structured DataFrame for reporting."""
    report_data = []
    step_duration_columns = [f"{step} (duration)" for step in steps]

    for instance in instances:
        row = {"Instance Name": instance.get("name")}
        row["Notes"] = instance.get("notes", "")
        
        timestamps = instance.get("timestamps", [])
        if not isinstance(timestamps, list):
            timestamps = []

        started_at = instance.get("started_at")
        row["Start Time"] = TimestampLogger.format_timestamp_full(started_at) if started_at else "N/A"

        # Find completion time and calculate total duration
        completion_ts_entry = next((ts for ts in timestamps if ts.get("step") == -1), None)
        completion_time = completion_ts_entry.get("timestamp") if completion_ts_entry else None
        row["Completion Time"] = TimestampLogger.format_timestamp_full(completion_time) if completion_time else "N/A"
        
        if started_at and completion_time:
            row["Total Duration"] = duration_formatter(started_at, completion_time)
        else:
            row["Total Duration"] = "In Progress"

        # Initialize step duration columns
        for col in step_duration_columns:
            row[col] = "N/A"

        # Create a map of step index to its timestamp
        step_ts_map = {ts.get("step"): ts.get("timestamp") for ts in timestamps if "step" in ts and "timestamp" in ts}

        # Calculate duration for each step
        for i, step_name in enumerate(steps):
            step_end_time = step_ts_map.get(i)
            if step_end_time:
                # Find the start time for this step
                if i == 0:
                    step_start_time = started_at
                else:
                    step_start_time = step_ts_map.get(i - 1)
                
                if step_start_time:
                    duration = duration_formatter(step_start_time, step_end_time)
                    row[f"{step_name} (duration)"] = duration
        
        report_data.append(row)

    # Define column order
    columns = ["Instance Name", "Notes", "Start Time", "Completion Time", "Total Duration"] + step_duration_columns
    df = pd.DataFrame(report_data, columns=columns)
    return df

def render_reporting_page(user_id: str):
    """Renders the reporting page."""
    st.title("📈 Reporting")
    st.write("Analyze performance by exporting workflow instance data.")

    workflows = WorkflowDB.get_workflows(user_id)
    if not workflows:
        st.info("No workflows found. Please create a workflow on the Setup page first.")
        return

    workflow_map = {wf["name"]: wf["id"] for wf in workflows}
    selected_workflow_name = st.selectbox("Select a workflow to review:", options=list(workflow_map.keys()))

    if selected_workflow_name:
        workflow_id = workflow_map[selected_workflow_name]
        selected_workflow = next((wf for wf in workflows if wf["id"] == workflow_id), None)
        
        if selected_workflow:
            st.markdown("---")
            st.subheader(f"Report for: {selected_workflow_name}")
            
            instances = InstanceDB.get_instances(workflow_id, user_id)
            
            if not instances:
                st.info("No instances have been recorded for this workflow yet.")
                return

            # --- Date Filter Logic ---
            all_started_dates = []
            for instance in instances:
                if instance.get("started_at"):
                    try:
                        all_started_dates.append(datetime.fromisoformat(instance["started_at"].replace('Z', '+00:00')).date())
                    except (ValueError, TypeError):
                        pass

            if not all_started_dates:
                min_date = max_date = date.today()
            else:
                min_date = min(all_started_dates)
                max_date = max(all_started_dates)
            date_range = st.date_input(
                "Filter by date range (based on instance start time):",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                format="YYYY/MM/DD"
            )

            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
            elif date_range and len(date_range) == 1:
                start_date = end_date = date_range[0]
            else: # Handle case where date_range might be empty
                start_date, end_date = None, None

            filtered_instances = []
            if start_date and end_date:
                for instance in instances:
                    started_at_str = instance.get("started_at")
                    if started_at_str:
                        try:
                            started_at_date = datetime.fromisoformat(started_at_str.replace('Z', '+00:00')).date()
                            if start_date <= started_at_date <= end_date:
                                filtered_instances.append(instance)
                        except (ValueError, TypeError):
                            continue
            
            if not filtered_instances:
                st.info("No instances found for the selected date range.")
                return
            # --- End Date Filter ---

            steps = selected_workflow.get("steps", [])

            # --- Full Data Table at the top ---
            st.markdown("---")
            st.subheader(" Full Data Report")
            st.caption("This table contains the detailed data for the selected date range. Use the export button to download it as an Excel file.")
            
            report_df = prepare_report_data(filtered_instances, steps)
            st.dataframe(report_df)
            
            # Create a version of the dataframe for visuals/export with hh:mm:ss format
            export_df = prepare_report_data(filtered_instances, steps, duration_formatter=TimestampLogger.calculate_elapsed_time_hms)

            # Export to Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, index=False, sheet_name='Workflow Report')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Export to Excel",
                data=excel_data,
                file_name=f"{selected_workflow_name}_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.caption("💡 **Tip:** You can use the exported Excel file to import this data back into the app or share it with other users via the **Import Data** page.")

            st.markdown("---")
            st.subheader("📊 Visual Analysis")

            # 5) Add filters for instance names
            all_instance_names = export_df['Instance Name'].tolist()
            selected_instances = st.multiselect(
                "Filter instances for visual analysis:",
                options=all_instance_names,
                default=all_instance_names,
                key=f"filter_{workflow_id}"
            )

            if not selected_instances:
                st.warning("Please select at least one instance to display visuals.")
                st.stop()

            # Filter the dataframe used for visuals
            visual_df = export_df[export_df['Instance Name'].isin(selected_instances)].copy()

            # Helper to convert hh:mm:ss to seconds
            def hms_to_seconds(t):
                if t == "N/A" or pd.isna(t):
                    return None
                try:
                    h, m, s = map(int, t.split(':'))
                    return h * 3600 + m * 60 + s
                except:
                    return None

            # Helper to convert seconds to hh:mm:ss string
            def seconds_to_hms_str(s):
                s = int(s)
                h, m, ss = s // 3600, (s % 3600) // 60, s % 60
                return f"{h:02d}:{m:02d}:{ss:02d}"

            # --- Key Metrics Table ---
            st.markdown("---")
            st.write("#### Key Performance Metrics")
            st.caption("This table shows the fastest, slowest, and average time for the total workflow and each individual step.")

            metrics_rows = []
            step_duration_cols = [col for col in visual_df.columns if '(duration)' in col and 'Total' not in col]
            duration_cols_for_metrics = ['Total Duration'] + [col.replace(' (duration)', '') for col in step_duration_cols]

            metrics_df = visual_df.copy()

            for col_name in duration_cols_for_metrics:
                duration_col = f"{col_name} (duration)" if col_name != 'Total Duration' else 'Total Duration'
                
                seconds_series = metrics_df[duration_col].apply(hms_to_seconds).dropna()
                
                if not seconds_series.empty:
                    min_idx = seconds_series.idxmin()
                    max_idx = seconds_series.idxmax()

                    fastest_instance = metrics_df.loc[min_idx, 'Instance Name']
                    slowest_instance = metrics_df.loc[max_idx, 'Instance Name']
                    
                    avg_duration = seconds_to_hms_str(seconds_series.mean())
                    fastest_duration = seconds_to_hms_str(seconds_series.min())
                    slowest_duration = seconds_to_hms_str(seconds_series.max())
                    
                    metrics_rows.append({
                        "Metric": col_name,
                        "Average": avg_duration,
                        "Fastest": f"{fastest_duration} ({fastest_instance})",
                        "Slowest": f"{slowest_duration} ({slowest_instance})",
                    })

            if metrics_rows:
                summary_df = pd.DataFrame(metrics_rows)
                st.dataframe(summary_df.set_index('Metric'), use_container_width=True)
            else:
                st.info("Not enough data to calculate key metrics.")

            # --- Top/Bottom Performers ---
            st.markdown("---")
            st.write("#### Outlier Instances")
            st.caption("These tables highlight the 5 fastest and 5 slowest instances, allowing you to quickly identify best-case scenarios and significant delays.")

            outlier_df = visual_df[['Instance Name', 'Total Duration']].copy()
            outlier_df['Total Duration (seconds)'] = outlier_df['Total Duration'].apply(hms_to_seconds)
            outlier_df.dropna(subset=['Total Duration (seconds)'], inplace=True)
            outlier_df.sort_values('Total Duration (seconds)', ascending=True, inplace=True)

            if len(outlier_df) >= 1:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**🚀 Top 5 Fastest**")
                    fastest_df = outlier_df.head(5)[['Instance Name', 'Total Duration']]
                    st.dataframe(fastest_df.set_index('Instance Name'), use_container_width=True)
                with col2:
                    st.write("**🐢 Top 5 Slowest**")
                    # Make sure to sort descending for slowest
                    slowest_df = outlier_df.tail(5).sort_values('Total Duration (seconds)', ascending=False)[['Instance Name', 'Total Duration']]
                    st.dataframe(slowest_df.set_index('Instance Name'), use_container_width=True)
            else:
                st.info("Not enough data to identify outlier instances.")

            st.markdown("---")
            st.write("#### Distribution of Total Durations")
            st.caption("This histogram shows the frequency of different total completion times, helping you understand the overall consistency and spread of your workflow performance.")

            duration_seconds = visual_df['Total Duration'].apply(hms_to_seconds).dropna()
            if not duration_seconds.empty:
                duration_minutes = duration_seconds / 60
                hist_fig = go.Figure(data=[go.Histogram(x=duration_minutes, nbinsx=20)])
                hist_fig.update_layout(
                    xaxis_title="Total Duration (minutes)",
                    yaxis_title="Number of Instances",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(hist_fig, use_container_width=True)
            else:
                st.info("Not enough data to generate a duration histogram.")

            st.markdown("---")
            st.write("#### Average Percentage of Time Per Step")
            st.caption("This pie chart shows the proportion of total average time that each step consumes.")
            step_duration_cols = [col for col in visual_df.columns if '(duration)' in col and 'Total' not in col]
            if step_duration_cols:
                avg_durations = {}
                for col in step_duration_cols:
                    seconds = visual_df[col].apply(hms_to_seconds).dropna()
                    if not seconds.empty:
                        avg_seconds = seconds.mean()
                        avg_durations[col.replace(' (duration)', '')] = avg_seconds

                # Ensure chart columns are in the correct order
                ordered_avg_durations = []
                for step in steps:
                    duration_seconds = avg_durations.get(step)
                    if duration_seconds is not None:
                        ordered_avg_durations.append((step, duration_seconds))

                if ordered_avg_durations:
                    pie_labels = [item[0] for item in ordered_avg_durations]
                    pie_values = [item[1] for item in ordered_avg_durations]
                    
                    if pie_values and sum(pie_values) > 0:
                        pie_fig = go.Figure(data=[go.Pie(labels=pie_labels, values=pie_values, textinfo='percent+label', hole=.3)])
                        pie_fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=20, b=20))
                        st.plotly_chart(pie_fig, use_container_width=True)

            st.markdown("---")
            st.write("#### Distribution of Time Per Step")
            st.caption("Use this box plot to identify steps with high variability and outliers. A wider box means a less predictable step.")
            if step_duration_cols:
                box_fig = go.Figure()
                for step in steps:
                    col = f"{step} (duration)"
                    if col in visual_df.columns:
                        durations_in_minutes = visual_df[col].apply(hms_to_seconds).dropna() / 60
                        if not durations_in_minutes.empty:
                            box_fig.add_trace(go.Box(y=durations_in_minutes, name=step, boxpoints='outliers'))
                
                box_fig.update_layout(yaxis_title="Duration (minutes)", xaxis_title="Workflow Step", showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(box_fig, use_container_width=True)

            st.markdown("---")
            st.write("#### Total Duration Per Instance (by Step)")
            st.caption("This stacked bar chart shows the total time for each instance and how that time was divided among the steps.")
            stacked_bar_data = visual_df.copy()
            
            # Convert all step durations to seconds for plotting
            for col in step_duration_cols:
                if col in stacked_bar_data.columns:
                    stacked_bar_data[f"{col}_seconds"] = stacked_bar_data[col].apply(hms_to_seconds)

            # Also convert total duration for y-axis scaling
            stacked_bar_data['Total Duration (seconds)'] = stacked_bar_data['Total Duration'].apply(hms_to_seconds)
            stacked_bar_data.dropna(subset=['Total Duration (seconds)'], inplace=True)

            if not stacked_bar_data.empty:
                
                bar_fig = go.Figure()

                # Add a bar for each step
                for step in steps:
                    duration_col_seconds = f"{step} (duration)_seconds"
                    if duration_col_seconds in stacked_bar_data.columns:
                        bar_fig.add_trace(go.Bar(
                            x=stacked_bar_data['Instance Name'],
                            y=stacked_bar_data[duration_col_seconds],
                            name=step
                        ))

                # Update layout for stacked bars and formatted Y-axis
                bar_fig.update_layout(
                    barmode='stack',
                    xaxis=dict(title='Instance Name'),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=40, b=20)
                )

                # Format Y-axis as hh:mm:ss
                max_seconds = stacked_bar_data['Total Duration (seconds)'].max()
                if pd.notna(max_seconds) and max_seconds > 0:
                    tick_interval = max(60, (max_seconds // 6))
                    tickvals = [i for i in range(0, int(max_seconds) + 1, int(tick_interval))]
                    ticktext = [seconds_to_hms_str(s) for s in tickvals]
                    bar_fig.update_layout(yaxis=dict(title='Total Duration (hh:mm:ss)', tickmode='array', tickvals=tickvals, ticktext=ticktext))
                
                st.plotly_chart(bar_fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🤖 AI-Powered Analysis")

            if not IS_CONFIGURED:
                st.warning(f"Vertex AI is not configured, so AI analysis is disabled. Please check the System Status page for details. Error: {CONFIG_ERROR}")
            else:
                session_key = f"ai_analysis_{workflow_id}"

                # Clear old analysis if workflow changes
                if 'last_workflow_id_for_ai' not in st.session_state or st.session_state.last_workflow_id_for_ai != workflow_id:
                    if session_key in st.session_state:
                        del st.session_state[session_key]
                st.session_state.last_workflow_id_for_ai = workflow_id

                if st.button("Generate Analysis", key=f"gen_ai_{workflow_id}"):
                    with st.spinner("🧠 The AI is analyzing your data..."):
                        # Use visual_df for AI analysis as it's already filtered
                        analysis = generate_ai_analysis(visual_df, selected_workflow_name)
                        st.session_state[session_key] = analysis
                
                if session_key in st.session_state:
                    analysis_text = st.session_state[session_key]
                    st.markdown(analysis_text)

                    st.download_button(
                        label="📥 Export Analysis as Markdown",
                        data=analysis_text,
                        file_name=f"{selected_workflow_name}_ai_analysis.md",
                        mime="text/markdown",
                        key=f"download_ai_{workflow_id}"
                    )