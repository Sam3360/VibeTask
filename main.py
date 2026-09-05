import time
import vibe as vi
from memobox import Brain

# Persistent local storage.
brain = Brain("tasks.json")

tasks = {}
current_filter = "All"


def load_tasks():
    global tasks
    stored = brain.category("tasks") or {}
    tasks = stored if isinstance(stored, dict) else {}


def save_task(task_id, data):
    brain.remember(task_id, data, category="tasks")


def delete_task(task_id):
    brain.forget(task_id)


def make_id():
    return f"task_{time.time_ns()}"


def get_selected_task_id():
    """Read selection directly from Tkinter because VibeUI's get_selected()
    uses its original _items list, while this app dynamically refreshes rows."""
    indices = task_list.widget.curselection()

    if not indices:
        return None

    index = indices[0]

    try:
        return task_list.visible_ids[index]
    except (IndexError, TypeError):
        return None


def refresh_list():
    task_list.widget.delete(0, "end")
    visible_ids = []

    for task_id, task in tasks.items():
        completed = bool(task.get("completed", False))

        if current_filter == "Active" and completed:
            continue
        if current_filter == "Completed" and not completed:
            continue

        mark = "✓" if completed else "○"
        priority = task.get("priority", "Medium")
        title = task.get("title", "Untitled")

        visible_ids.append(task_id)
        task_list.widget.insert(
            "end",
            f"{mark}  [{priority}]  {title}",
        )

    task_list.visible_ids = visible_ids
    update_progress()


def update_progress():
    total = len(tasks)
    completed = sum(
        1 for task in tasks.values()
        if task.get("completed", False)
    )

    progress.set((completed / total) * 100 if total else 0)
    status.set(f"{completed} of {total} tasks completed")


def add_task():
    title = title_input.get().strip()

    if not title:
        vi.alert("Please enter a task title.")
        return

    task_id = make_id()

    data = {
        "title": title,
        "priority": priority.get(),
        "completed": False,
        "created": time.time(),
    }

    save_task(task_id, data)
    tasks[task_id] = data

    title_input.clear()
    refresh_list()
    vi.toast("Task saved")


def toggle_selected():
    task_id = get_selected_task_id()

    if task_id is None:
        vi.alert("Select a task first.")
        return

    task = tasks.get(task_id)

    if task is None:
        refresh_list()
        return

    task["completed"] = not task.get("completed", False)
    save_task(task_id, task)

    refresh_list()
    vi.toast("Task updated")


def remove_selected():
    task_id = get_selected_task_id()

    if task_id is None:
        vi.alert("Select a task first.")
        return

    if vi.confirm("Delete this task?"):
        delete_task(task_id)
        tasks.pop(task_id, None)

        refresh_list()
        vi.toast("Task deleted")


def clear_completed():
    completed_ids = [
        task_id
        for task_id, task in tasks.items()
        if task.get("completed", False)
    ]

    if not completed_ids:
        vi.alert("There are no completed tasks.")
        return

    if vi.confirm(f"Delete {len(completed_ids)} completed task(s)?"):
        for task_id in completed_ids:
            delete_task(task_id)
            tasks.pop(task_id, None)

        refresh_list()
        vi.toast("Completed tasks cleared")


def set_filter(value):
    global current_filter
    current_filter = value
    refresh_list()


load_tasks()

win = vi.Window(
    "VibeTasks — MemoBox",
    size=(760, 620),
    theme="dark",
    accent="#7c6cf5",
)

win.set_menu({
    "File": {
        "Add Task": add_task,
        "Clear Completed": clear_completed,
        "Exit": win.close,
    },
    "View": {
        "All Tasks": lambda: set_filter("All"),
        "Active Tasks": lambda: set_filter("Active"),
        "Completed Tasks": lambda: set_filter("Completed"),
    },
})

with win.card(title="VibeTasks"):
    win.add_label(
        "A persistent task manager powered by VibeUI + MemoBox",
        size="md",
    )

    with win.row():
        title_input = win.add_input(
            placeholder="What needs to be done?"
        )

        priority = win.add_dropdown(
            ["Low", "Medium", "High"],
            default="Medium",
        )

        win.add_button(
            "Add Task",
            on_click=add_task,
            variant="primary",
        )

with win.card(title="Tasks"):
    task_list = win.add_listbox([], multiple=False)
    task_list.visible_ids = []

    with win.row():
        win.add_button(
            "Complete / Undo",
            on_click=toggle_selected,
            variant="secondary",
        )

        win.add_button(
            "Delete",
            on_click=remove_selected,
            variant="danger",
        )

        win.add_button(
            "Clear Completed",
            on_click=clear_completed,
            variant="ghost",
        )

with win.card(title="Progress"):
    progress = win.add_progressbar(value=0, max_val=100)
    status = win.add_status_bar("Loading...")

refresh_list()
win.run()
