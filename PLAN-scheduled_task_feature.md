# Scheduled Tasks Feature — End-to-End Implementation Plan

This document outlines a comprehensive, step-by-step plan to implement a "Scheduled Tasks" feature in [open-webui](https://github.com/open-webui/open-webui), enabling users to define prompts that are sent automatically to selected AI models at scheduled times.

---

## 1. Requirements

### 1.1 User Stories

- **Create Scheduled Task:** Users can create prompts, choose a model, and set a schedule (e.g., daily, weekly, custom cron).
- **Manage Tasks:** Users can view, edit, enable/disable, or delete existing scheduled tasks.
- **Execution & History:** Each scheduled execution is logged; users can see the output and status for each run.
- **Security:** Only the task owner can view or manage their scheduled tasks.

---

## 2. Design

### 2.1 Data Model

#### ScheduledTask Table/Model
- `id` (UUID or int, PK)
- `user_id` (FK → Users)
- `prompt` (text)
- `model` (string)
- `schedule` (cron string or datetime)
- `enabled` (boolean)
- `last_run_at` (datetime)
- `next_run_at` (datetime, optional)
- `created_at` (datetime)
- `updated_at` (datetime)

#### ScheduledTaskExecution Table/Model
- `id` (PK)
- `scheduled_task_id` (FK → ScheduledTask)
- `run_at` (datetime)
- `status` (success/failure/queued/running)
- `response` (text, AI model output)
- `error_message` (nullable)
- `created_at` (datetime)

---

## 3. Backend Implementation

### 3.1 ORM Model Definitions

- Add models for `ScheduledTask` and `ScheduledTaskExecution` (e.g., SQLAlchemy, Tortoise ORM).
- Create DB migrations.

### 3.2 REST API Endpoints

#### Scheduled Tasks
- `POST /api/scheduled-tasks` — Create a scheduled task
- `GET /api/scheduled-tasks` — List all scheduled tasks for current user
- `GET /api/scheduled-tasks/{id}` — Get details for a specific task
- `PUT /api/scheduled-tasks/{id}` — Update a scheduled task
- `DELETE /api/scheduled-tasks/{id}` — Delete a scheduled task
- `POST /api/scheduled-tasks/{id}/run` — Manually trigger a task (optional)

#### Scheduled Task Executions
- `GET /api/scheduled-tasks/{id}/executions` — List all executions for a task
- `GET /api/scheduled-tasks/{id}/executions/{exec_id}` — Get details for a specific execution

### 3.3 Scheduling Engine Integration

- Integrate a scheduling library (e.g., APScheduler for Python/FastAPI).
- On startup, load all enabled scheduled tasks from the database and register them as jobs.
- On task creation/update, (re)schedule the corresponding job.
- On task deletion/disable, remove the job from the scheduler.

#### Job Handler
- At scheduled time, send the prompt to the selected model (use existing OpenAI or local model integration).
- Log the request, response, and status in `ScheduledTaskExecution`.
- Handle and log errors gracefully.

### 3.4 Permissions & Security

- Ensure all API endpoints are authenticated.
- Only allow users to manage/view their own scheduled tasks and executions.

### 3.5 Testing (Backend)

- Unit tests for models, API endpoints, and scheduler integration.
- Integration tests for end-to-end flow: create → execute → view history.

---

## 4. Frontend Implementation

### 4.1 UI Components

- **Scheduled Tasks List**: Page to show all tasks, status, next run, last run, model, enabled toggle, and actions (edit, delete, run now).
- **Scheduled Task Editor**: Modal/form for creating/editing a task (fields: prompt, model, schedule, enabled).
- **Execution History**: Detail page/modal for a task, showing all executions (time, status, output, error if any).

### 4.2 New Routes

- `/scheduled-tasks` — list & create
- `/scheduled-tasks/:id` — details & history

### 4.3 API Integration

- Connect UI to new backend endpoints.
- Handle loading, error, and success states.
- Use websocket or polling if live updates are desired (optional).

### 4.4 Validation

- Validate user input for schedule (cron syntax or date/time picker).
- Validate prompt/model selection.
- Show errors returned from backend.

### 4.5 Testing (Frontend)

- Unit tests for new components.
- E2E (Cypress/Playwright) tests for user flows.

---

## 5. Optional Enhancements

- **Notifications:** Email or in-app notification when a scheduled task runs (success/failure).
- **Task Import/Export:** Allow users to backup or share scheduled tasks.
- **Advanced Scheduling:** Support for timezone selection, pause/resume, or dependencies between tasks.

---

## 6. Documentation & DevOps

- Update API and user documentation.
- Add migration scripts for schema changes.
- Ensure scheduler jobs survive backend restarts (persist jobs).
- Add monitoring/alerting for failed scheduled tasks (optional).

---

## 7. Rollout Plan

1. Implement and test backend (API + scheduler).
2. Implement and test frontend (UI + API integration).
3. Perform integration testing.
4. Update documentation.
5. Deploy to staging environment for user testing.
6. Roll out to production.

---

## 8. Example User Flow

1. User navigates to "Scheduled Tasks" page.
2. Clicks "Create Task", fills form (prompt, model, schedule).
3. Task appears in list, next run time shown.
4. At scheduled time, prompt is sent, execution result is saved.
5. User views execution history and result.

---

## 9. References

- [APScheduler Docs](https://apscheduler.readthedocs.io/)
- [Open-WebUI Backend Folder](https://github.com/open-webui/open-webui/tree/main/backend)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

---

**Contact:**  
For questions or to join development, open an issue or a discussion in the open-webui repository.
