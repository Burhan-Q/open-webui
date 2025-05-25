# tasks.py
import asyncio
from typing import Dict
from uuid import uuid4
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from open_webui.models.scheduled_task import ScheduledTasks, ScheduledTaskHistory

# A dictionary to keep track of active tasks
tasks: Dict[str, asyncio.Task] = {}
chat_tasks = {}

# Initialize the scheduler
scheduler = AsyncIOScheduler()
scheduler.start()

def cleanup_task(task_id: str, id=None):
    """
    Remove a completed or canceled task from the global `tasks` dictionary.
    """
    tasks.pop(task_id, None)  # Remove the task if it exists

    # If an ID is provided, remove the task from the chat_tasks dictionary
    if id and task_id in chat_tasks.get(id, []):
        chat_tasks[id].remove(task_id)
        if not chat_tasks[id]:  # If no tasks left for this ID, remove the entry
            chat_tasks.pop(id, None)


def create_task(coroutine, id=None):
    """
    Create a new asyncio task and add it to the global task dictionary.
    """
    task_id = str(uuid4())  # Generate a unique ID for the task
    task = asyncio.create_task(coroutine)  # Create the task

    # Add a done callback for cleanup
    task.add_done_callback(lambda t: cleanup_task(task_id, id))
    tasks[task_id] = task

    # If an ID is provided, associate the task with that ID
    if chat_tasks.get(id):
        chat_tasks[id].append(task_id)
    else:
        chat_tasks[id] = [task_id]

    return task_id, task


def get_task(task_id: str):
    """
    Retrieve a task by its task ID.
    """
    return tasks.get(task_id)


def list_tasks():
    """
    List all currently active task IDs.
    """
    return list(tasks.keys())


def list_task_ids_by_chat_id(id):
    """
    List all tasks associated with a specific ID.
    """
    return chat_tasks.get(id, [])


async def stop_task(task_id: str):
    """
    Cancel a running task and remove it from the global task list.
    """
    task = tasks.get(task_id)
    if not task:
        raise ValueError(f"Task with ID {task_id} not found.")

    task.cancel()  # Request task cancellation
    try:
        await task  # Wait for the task to handle the cancellation
    except asyncio.CancelledError:
        # Task successfully canceled
        tasks.pop(task_id, None)  # Remove it from the dictionary
        return {"status": True, "message": f"Task {task_id} successfully stopped."}

    return {"status": False, "message": f"Failed to stop task {task_id}."}


def job_handler(task_id: str):
    """
    Job handler to execute the scheduled task.
    """
    task = ScheduledTasks.get_scheduled_task_by_id(task_id)
    if not task:
        return

    # Simulate sending the prompt to the selected model
    try:
        # Here you would integrate with the actual model and send the prompt
        response = f"Executed task {task_id} with prompt: {task.content.prompt}"
        status = "success"
        error_message = None
    except Exception as e:
        response = None
        status = "failure"
        error_message = str(e)

    # Log the execution result
    ScheduledTaskHistory.log_execution(
        scheduled_task_id=task_id,
        status=status,
        response=response,
        error_message=error_message,
    )


def schedule_task(task_id: str, schedule: str):
    """
    Schedule a task to be executed at the specified time.
    """
    scheduler.add_job(job_handler, "cron", id=task_id, **schedule, args=[task_id])


def reschedule_task(task_id: str, schedule: str):
    """
    Reschedule an existing task.
    """
    scheduler.reschedule_job(task_id, trigger="cron", **schedule)


def remove_task(task_id: str):
    """
    Remove a scheduled task.
    """
    scheduler.remove_job(task_id)
