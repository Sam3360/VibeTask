# VibeTasks + MemoBox

A persistent desktop task manager built with VibeUI and MemoBox.

## Install

```bash
pip install vibeUI MemoBox
```

## Run

```bash
python main.py
```

## Features

- Persistent tasks
- Add tasks
- Priority selection
- Complete / undo
- Delete tasks
- Clear completed tasks
- All / Active / Completed filters
- Progress bar
- VibeUI dark theme
- Menus, cards, dialogs and toasts
- Local JSON persistence through MemoBox

## Important implementation detail

The app does **not** call `task_list.get_selected()` after dynamically
replacing Listbox rows.

VibeUI's `ListBox.get_selected()` maps Tkinter selection indices through the
wrapper's original `_items` list. Since this app dynamically rebuilds the
visual rows, that wrapper list would become stale.

Instead, the app reads the selected Tkinter index through:

```python
task_list.widget.curselection()
```

and maps that index to `task_list.visible_ids`.

This keeps the UI dynamic while using the actual VibeUI widget underneath.
