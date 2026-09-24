# ```python
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

from datetime import date

# Page Configuration
st.set_page_config(
    page_title="Todo Manager",
    page_icon="✅",
    layout="centered"
) 

st.caption("Built & deployed by Niraj Gupta")
st.title("✅ Task Management Dashboard")
st.markdown("""
<style>

.task-card {
    background: #ffffff;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 8px;
    color: #222222;
}

.task-title {
    font-size: 16px;
    font-weight: 600;
    color: #222222;
    margin-bottom: 6px;
    word-wrap: break-word;
}

.priority-high {
    color: #d32f2f;
    font-weight: bold;
}

.priority-medium {
    color: #f57c00;
    font-weight: bold;
}

.priority-low {
    color: #388e3c;
    font-weight: bold;
}

/* Buttons */
div.stButton > button {
    width: 100%;
}

/* Statistics */
.stats-container {
    display: flex;
    width: 100%;
    gap: 8px;
    margin: 15px 0;
}

.stat-box {
    flex: 1;
    background: #FFEBCD;
    border: 1px solid #444;
    border-radius: 10px;
    padding: 10px 5px;
    text-align: center;
}

.stat-label {
    font-size: 13px;
    white-space: nowrap;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
}

/* Mobile */
@media (max-width: 640px) {

    .task-card {
        padding: 12px;
        margin-bottom: 6px;
        border-radius: 10px;
    }

    .task-title {
        font-size: 15px;
    }

    .stats-container {
        gap: 5px;
    }

    .stat-box {
        padding: 8px 2px;
    }

    .stat-label {
        font-size: 10px;
    }

    .stat-value {
        font-size: 20px;
    }
}

</style>
""", unsafe_allow_html=True)



st.caption("Manage your daily tasks with Supabase")

# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        st.error("Supabase URL or Key not found.")
        st.stop()

supabase: Client = create_client(url, key)


# Get todos
def get_todos():
    response = (
        supabase
        .table("todos")
        .select("*")
        .order("id")
        .execute()
    )
    return response.data


# Add todo
def add_todo(task, priority, due_date):
    supabase.table("todos").insert({
        "task": task,
        "completed": False,
        "priority":priority,
        "due_date": str(due_date) if due_date else None

    }).execute()


# Update todo status
def update_todo(todo_id, completed):
    supabase.table("todos").update({
        "completed": completed
    }).eq("id", todo_id).execute()

def delete_todo(todo_id):
    supabase.table("todos").delete().eq("id", todo_id).execute()

def clear_completed_tasks():
    supabase.table("todos").delete().eq(
        "completed", True
    ).execute()

def delete_all_tasks():
    supabase.table("todos").delete().neq("id", 0).execute()

def update_task(todo_id, new_task, priority):
    supabase.table("todos").update({
        "task": new_task,
        "priority":priority
    }).eq("id", todo_id).execute()


# UI

st.subheader("➕ Add New Task")

col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])

with col1:
    task = st.text_input(
        "Task",
        placeholder="Enter your task...",
        label_visibility="collapsed"
    )

with col2:
    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"],
        label_visibility="collapsed"
    )

with col3:
    due_date = st.date_input(
        "Due Date",
        value = None,
        label_visibility="collapsed"
    )

with col4:
    add_button = st.button(
        "➕ Add",
        use_container_width=True
    )

if add_button:
    if task.strip():
        add_todo(task.strip(), priority, due_date)
        st.success("Task added successfully! 🎉")
        st.rerun()
    else:
        st.warning("Please enter a task.")
        
st.write("### Todo List:")

todos = get_todos()

st.subheader("🔍 Search & Filter")

search_text = st.text_input(
    "Search",
    placeholder="Search your tasks...",
    label_visibility="collapsed"
)

filter_option = st.selectbox(
    "Filter tasks",
    ["All", "Pending", "Completed"]
)

sort_option = st.selectbox(
    "Sort tasks",
    [
        "Newest First",
        "Oldest First",
        "Priority: High → Low",
        "Priority: Low → High",
        "Due Date"
    ]
)


filtered_todos = todos

if search_text:
    filtered_todos = [
        todo for todo in filtered_todos
        if search_text.lower() in todo["task"].lower()
    ]

if filter_option == "Pending":
    filtered_todos = [
        todo for todo in filtered_todos
        if not todo.get("completed", False)
    ]

elif filter_option == "Completed":
    filtered_todos = [
        todo for todo in filtered_todos
        if todo.get("completed", False)
    ]

# Sorting
if sort_option == "Newest First":
    filtered_todos = sorted(
        filtered_todos,
        key=lambda x: x["id"],
        reverse=True
    )

elif sort_option == "Oldest First":
    filtered_todos = sorted(
        filtered_todos,
        key=lambda x: x["id"]
    )

elif sort_option == "Priority: High → Low":
    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    filtered_todos = sorted(
        filtered_todos,
        key=lambda x: priority_order.get(
            x.get("priority", "Medium"), 2
        )
    )

elif sort_option == "Priority: Low → High":
    priority_order = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    filtered_todos = sorted(
        filtered_todos,
        key=lambda x: priority_order.get(
            x.get("priority", "Medium"), 2
        )
    )

elif sort_option == "Due Date":
    filtered_todos = sorted(
        filtered_todos,
        key=lambda x: x.get("due_date") or "9999-12-31"
    )


# Todo Statistics
total_tasks = len(todos)

completed_tasks = sum(
    1 for todo in todos if todo.get("completed", False)
)

pending_tasks = total_tasks - completed_tasks

# Statistics
st.markdown(
    f"""<div class="stats-container"><div class="stat-box"><div class="stat-label">📋 Total</div><div class="stat-value">{total_tasks}</div></div><div class="stat-box"><div class="stat-label">✅ Completed</div><div class="stat-value">{completed_tasks}</div></div><div class="stat-box"><div class="stat-label">⏳ Pending</div><div class="stat-value">{pending_tasks}</div></div></div>""",
    unsafe_allow_html=True
)

# Progress
if total_tasks > 0:
    progress = completed_tasks / total_tasks
    st.write(f"📊 Progress: {completed_tasks}/{total_tasks} tasks completed")
    st.progress(progress)
else:
    st.write("📊 Progress: 0/0 tasks completed")
    st.progress(0)


st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "🧹 Clear Completed",
        use_container_width=True
    ):
        clear_completed_tasks()
        st.success("Completed tasks cleared! 🧹")
        st.rerun()

with col2:
    if st.button(
        "🗑️ Delete All",
        use_container_width=True
    ):
        st.session_state["confirm_delete_all"] = True


if st.session_state.get("confirm_delete_all", False):
    
    st.warning("⚠️ Are you sure you want to delete ALL tasks?")

    confirm_col1, confirm_col2 = st.columns(2)

    with confirm_col1:
        if st.button("✅ Yes, Delete All"):
            delete_all_tasks()
            st.session_state["confirm_delete_all"] = False
            st.success("All tasks deleted!")
            st.rerun()

    with confirm_col2:
        if st.button("❌ Cancel"):
            st.session_state["confirm_delete_all"] = False
            st.rerun()


if filtered_todos:
    
    for todo in filtered_todos:

        # Checkbox
        completed = st.checkbox(
            "",
            value=todo.get("completed", False),
            key=f"todo_{todo['id']}"
        )

        # Task name
        task_text = todo["task"]

        if completed:
            task_text = f"<s>{task_text}</s>"

        # Priority
        priority = todo.get("priority", "Medium")

        if priority == "High":
            priority_class = "priority-high"
            priority_text = "🔴 High"

        elif priority == "Medium":
            priority_class = "priority-medium"
            priority_text = "🟡 Medium"

        else:
            priority_class = "priority-low"
            priority_text = "🟢 Low"

        # TASK CARD
        st.markdown(
            f"""<div class="task-card">
<div class="task-title">{task_text}</div>
<div class="{priority_class}">{priority_text}</div>
</div>""",
            unsafe_allow_html=True
        )

        # Database update
        if completed != todo.get("completed", False):
            update_todo(todo["id"], completed)
            st.rerun()

        # Due date
        due_date = todo.get("due_date")

        if due_date:
            due_date_obj = date.fromisoformat(str(due_date))

            if not completed and due_date_obj < date.today():
                st.caption("⚠️ Overdue")
            else:
                st.caption(f"📅 Due: {due_date}")

        # Buttons
        edit_col, delete_col = st.columns(2)

        with edit_col:
            if st.button(
                "✏️ Edit",
                key=f"edit_{todo['id']}"
            ):
                st.session_state[f"editing_{todo['id']}"] = True

        with delete_col:
            if st.button(
                "🗑️ Delete",
                key=f"delete_{todo['id']}"
            ):
                delete_todo(todo["id"])
                st.rerun()

        # Edit mode
        if st.session_state.get(
            f"editing_{todo['id']}",
            False
        ):

            new_task = st.text_input(
                "Edit task:",
                value=todo["task"],
                key=f"input_{todo['id']}"
            )

            current_priority = todo.get(
                "priority",
                "Medium"
            )

            new_priority = st.selectbox(
                "Priority:",
                ["Low", "Medium", "High"],
                index=[
                    "Low",
                    "Medium",
                    "High"
                ].index(current_priority),
                key=f"priority_{todo['id']}"
            )

            if st.button(
                "💾 Save",
                key=f"save_{todo['id']}"
            ):

                if new_task.strip():

                    update_task(
                        todo["id"],
                        new_task.strip(),
                        new_priority
                    )

                    st.session_state[
                        f"editing_{todo['id']}"
                    ] = False

                    st.rerun()

                else:
                    st.error("Task cannot be empty.")

        st.divider()

else:
    st.info("No matching tasks found.") 