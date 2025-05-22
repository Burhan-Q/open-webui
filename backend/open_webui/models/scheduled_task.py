import logging
import time
from typing import Optional

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.models.users import Users, UserResponse
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Boolean, Column, String, Text, JSON

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

##############################
# Scheduled Tasks DB Schema
##############################

class ScheduledTask(Base):
    __tablename__ = "scheduled_task"

    id = Column(String, primary_key=True)
    user_id = Column(String)
    name = Column(Text)
    schedule = Column(String)
    """cron string or ISO datetime"""
    enabled = Column(Boolean)
    last_run_at = Column(BigInteger)
    next_run_at = Column(BigInteger)
    content = Column(JSONField)
    meta = Column(JSONField)
    access_control = Column(JSON, nullable=True)
    """
    Controls data access levels.
    - `None`: Public access, available to all users with the "user" role.
    - `{}`: Private access, restricted exclusively to the owner.
    - Custom permissions: Specific access control for reading and writing;
      Can specify group or user-level restrictions:
      {
         "read": {
             "group_ids": ["group_id1", "group_id2"],
             "user_ids":  ["user_id1", "user_id2"]
         },
         "write": {
             "group_ids": ["group_id1", "group_id2"],
             "user_ids":  ["user_id1", "user_id2"]
         }
      }
    """
    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class ScheduledTaskExecution(Base):
    __tablename__ = "scheduled_task_execution"

    id = Column(String, primary_key=True)
    name = Column(Text)
    scheduled_task_id = Column(String)
    content = Column(JSONField)
    run_at = Column(BigInteger, default=lambda: int(time.time()))
    status = Column(String, nullable=False)  # success/failure/queued/running
    response = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(BigInteger)


##############################
# Pydantic Models
##############################

class ScheduledTaskMeta(BaseModel):
    description: Optional[str] = None
    manifest: Optional[dict] = {}


class ScheduledTaskContent(BaseModel):
    model: str
    prompt: str
    tools: list[str]
    """List of Tool IDs"""


class ScheduledTaskModel(BaseModel):
    id: str
    user_id: str
    prompt: str
    last_run_at: Optional[int] = None
    next_run_at: Optional[int] = None
    created_at: int
    updated_at: int
    content: ScheduledTaskContent
    meta: ScheduledTaskMeta
    access_control: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)


class ScheduledTaskExecutionModel(BaseModel):
    id: str
    name: str
    scheduled_task_id: str
    content: ScheduledTaskContent
    run_at: int
    status: str
    response: Optional[str] = None
    error_message: Optional[str] = None
    created_at: int

    model_config = ConfigDict(from_attributes=True)


##############################
# Forms
##############################

class ScheduledTaskUserModel(ScheduledTaskModel):
    user: Optional[UserResponse] = None


class ScheduledTaskResponse(BaseModel):
    id: str
    name: str
    schedule: str
    enabled: bool
    last_run_at: Optional[int] = None
    next_run_at: Optional[int] = None
    created_at: int
    updated_at: int
    content: ScheduledTaskContent
    meta: ScheduledTaskMeta
    access_control: Optional[dict] = None


class ScheduledTaskForm(BaseModel):
    id: str
    name: str
    content: ScheduledTaskContent
    schedule: str
    """cron string or ISO datetime"""
    enabled: Optional[bool] = True
    access_control: Optional[dict] = None


class ScheduledTaskExecutionResponse(BaseModel):
    id: str
    scheduled_task_id: str
    run_at: int
    status: str
    response: Optional[str] = None
    error_message: Optional[str] = None
    created_at: int


##############################
# Table Classes
##############################

# class ScheduledTasksTable:
#     def insert_new_scheduled_task(
#         self, user_id: str, form_data: ScheduledTaskForm
#     ) -> Optional[ScheduledTaskModel]:
#         task_id = str(int(time.time() * 1000))  # simple unique id, replace with uuid if desired
#         now = int(time.time())
#         scheduled_task = ScheduledTaskModel(
#             id=task_id,
#             user_id=user_id,
#             prompt=form_data.prompt,
#             model=form_data.model,
#             schedule=form_data.schedule,
#             enabled=form_data.enabled if form_data.enabled is not None else True,
#             last_run_at=None,
#             next_run_at=None,
#             created_at=now,
#             updated_at=now,
#         )
#         try:
#             with get_db() as db:
#                 task_row = ScheduledTask(**scheduled_task.model_dump())
#                 db.add(task_row)
#                 db.commit()
#                 db.refresh(task_row)
#                 if task_row:
#                     return ScheduledTaskModel.model_validate(task_row)
#                 else:
#                     return None
#         except Exception as e:
#             log.exception(f"Error creating scheduled task: {e}")
#             return None

#     def get_scheduled_task_by_id(self, id: str) -> Optional[ScheduledTaskModel]:
#         try:
#             with get_db() as db:
#                 task = db.get(ScheduledTask, id)
#                 return ScheduledTaskModel.model_validate(task)
#         except Exception:
#             return None

#     def get_scheduled_tasks(self, user_id: Optional[str] = None) -> list[ScheduledTaskModel]:
#         with get_db() as db:
#             query = db.query(ScheduledTask)
#             if user_id:
#                 query = query.filter_by(user_id=user_id)
#             return [
#                 ScheduledTaskModel.model_validate(task)
#                 for task in query.all()
#             ]

#     def update_scheduled_task_by_id(self, id: str, updated: dict) -> Optional[ScheduledTaskModel]:
#         with get_db() as db:
#             try:
#                 db.query(ScheduledTask).filter_by(id=id).update(
#                     {
#                         **updated,
#                         "updated_at": int(time.time()),
#                     }
#                 )
#                 db.commit()
#                 return self.get_scheduled_task_by_id(id)
#             except Exception:
#                 return None

#     def delete_scheduled_task_by_id(self, id: str) -> bool:
#         with get_db() as db:
#             try:
#                 db.query(ScheduledTask).filter_by(id=id).delete()
#                 db.commit()
#                 return True
#             except Exception:
#                 return False

# ScheduledTasks = ScheduledTasksTable()

class ScheduledTasksTable:
    def insert_new_scheduled_task(
        self, user_id: str, form_data: ScheduledTaskForm
    ) -> Optional[ScheduledTaskModel]:
        now = int(time.time())
        enable = (
            str(form_data.enabled).lower() in {"true", "t", "1"}
            if form_data.enabled or form_data.enabled is not None
            else True
        )
        scheduled_task = ScheduledTaskModel(
            user_id=user_id,
            enabled=enable,
            created_at=now,
            updated_at=now,
            **form_data.model_dump(),
        )
        try:
            with get_db() as db:
                result = ScheduledTask(**scheduled_task.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                return ScheduledTaskModel.model_validate(result) if result else None
        except Exception as e:
            log.exception(f"Error creating scheduled task: {e}")
            return None

    def get_scheduled_task_by_id(self, id: str) -> Optional[ScheduledTaskModel]:
        try:
            with get_db() as db:
                task = db.get(ScheduledTask, id)
                return ScheduledTaskModel.model_validate(task) if task else None
        except Exception as e:
            log.exception(f"Error fetching scheduled task by id {id}: {e}")
            return None

    def get_scheduled_tasks(self, user_id: Optional[str] = None) -> list[ScheduledTaskModel]:
        with get_db() as db:
            query = db.query(ScheduledTask).order_by(ScheduledTask.updated_at.desc())
            if user_id:
                query = query.filter_by(user_id=user_id)
            tasks = []
            for task in query.all():
                user = Users.get_user_by_id(task.user_id)
                tasks.append(ScheduledTaskUserModel.model_validate({**task.model_dump(), "user": user.model_dump() if user else None}))
            return tasks

    def update_scheduled_task_by_id(self, id: str, updated: dict) -> Optional[ScheduledTaskModel]:
        with get_db() as db:
            try:
                db.query(ScheduledTask).filter_by(id=id).update({updated | {"updated_at": int(time.time())}})
                db.commit()

                scheduled_task = db.query(ScheduledTask).get(id)
                db.refresh(scheduled_task)
                return ScheduledTaskModel.model_validate(scheduled_task)
            except Exception as e:
                log.exception(f"Error updating scheduled task {id}: {e}")
                return None

    def delete_scheduled_task_by_id(self, id: str) -> bool:
        with get_db() as db:
            try:
                db.query(ScheduledTask).filter_by(id=id).delete()
                db.commit()
                return True
            except Exception as e:
                log.exception(f"Error deleting scheduled task {id}: {e}")
                return False

ScheduledTasks = ScheduledTasksTable()
