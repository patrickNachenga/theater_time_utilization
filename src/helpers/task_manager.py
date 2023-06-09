import asyncio
import json

import aioredis
from pydantic import BaseModel
from sqlalchemy import and_

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.db.session import session_scope


class TaskManager:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.task_queue = asyncio.Queue()
        self.redis_pool = None
        self._queue_interval_seconds: int = 60 * 1
        self.task_type_mapping = {}
        self.moodle = MoodleApi()

    def register_task_type(self, task_type, processing_logic):
        self.task_type_mapping[task_type] = processing_logic

    async def get_redis_pool(self):
        if self.redis_pool is None:
            self.redis_pool = await aioredis.from_url(self.redis_url)
        return self.redis_pool

    async def enqueue_task(self, task_type, task_params=None):
        task = {"type": task_type, "params": task_params}
        await self.task_queue.put(task)
        # serialized_task = json.dumps(task)  # Serialize task dictionary to JSON
        # redis_pool = await self.get_redis_pool()
        # await redis_pool.lpush('tasks', serialized_task)

    async def process_tasks(self):
        redis_pool = await self.get_redis_pool()
        while True:
            await asyncio.sleep(self._queue_interval_seconds)
            if self.task_queue.empty():
                pass
                # serialized_task = await redis_pool.brpop('tasks')
                # task = json.loads(serialized_task[1])  # Deserialize task JSON
                # if task:
                #     await self.task_queue.put(task)
                #     # Remove processed task from Redis
                #     await redis_pool.lrem('tasks', 1, serialized_task[1])
            else:
                task = await self.task_queue.get()
                try:
                    task_type = task.get("type")
                    params = task.get("params")
                    if task_type == "ldap_account":
                        await self.send_ldap_account_task(params)
                    elif task_type == "create_moodle_unit":
                        await self.create_units_to_moodle()
                    elif task_type == "create_moodle_department":
                        await self.create_departments_to_moodle()
                    elif task_type == "create_moodle_user":
                        await self.create_users_to_moodle()
                    else:
                        print(f"Unknown task type: {task_type}")
                finally:
                    self.task_queue.task_done()

    async def start_processing(self):
        await self.get_redis_pool()
        asyncio.create_task(self.process_tasks())

    async def stop_processing(self):
        if self.redis_pool is not None:
            self.redis_pool.close()
            await self.redis_pool.wait_closed()

    # @staticmethod
    # async def send_ldap_account_task(params):
    #     staff_uid = params.get('staff_uid')
    #     random_password = params.get('random_password')
    #     generated_username = params.get('generated_username')
    #     with session_scope() as session:
    #         staff = session.query(Staff).filter(and_(Staff.uid == staff_uid, Staff.deleted_at.is_(None))).first()
    #         if staff:
    #             ldap_result = create_ldap_account(staff.user, random_password)
    #             if ldap_result['status']:
    #                 print('--- Successfully added staff to LDAP ---')
    #                 await email_process.send_staff_account_confirmation_email(client_name=staff.user.first_name,
    #                                                                           username=generated_username,
    #                                                                           password=random_password,
    #                                                                           recipient_email=staff.user.email,
    #                                                                           verification_link=
    #                                                                           settings.LOGIN_SERVICE_URL)
    #             else:
    #                 print('--- Failure to add staff to LDAP ---', ldap_result['exception'])
    #                 FailedNotification(user=staff.user, exception=ldap_result['exception'])
    #                 session.commit()
    #
    # @staticmethod
    # async def create_units_to_moodle():
    #     with session_scope() as session:
    #         # Get only one at a time
    #         unit = session.query(Unit).filter(
    #             and_(Unit.moodle_id.is_(None), Unit.deleted_at.is_(None))).first()
    #         if unit:
    #             moodle = MoodleApi()
    #             moodle_unit_id = moodle.createFalcuty(shortname=unit.code, fullname=unit.name,
    #                                                   description=unit.description)
    #             if moodle_unit_id != 0:
    #                 unit.moodle_id = moodle_unit_id
    #                 session.add(unit)
    #                 session.commit()
    #                 print('--- Successfully added Unit %s to Moodle ---' % unit.code)
    #             else:
    #                 print('--- Failure to create units to Moodle --- ', moodle_unit_id)
    #
    # async def create_departments_to_moodle(self):
    #     with session_scope() as session:
    #         # Get only one at a time
    #         department = session.query(Department).filter(
    #             and_(Department.moodle_id.is_(None), Department.deleted_at.is_(None))).first()
    #         if department and department.unit.moodle_id:
    #             moodle_department_id = self.moodle.createDepartment(facultyId=department.unit.moodle_id,
    #                                                                 departmentName=department.name,
    #                                                                 departmentDescription=department.description)
    #             if moodle_department_id != 0:
    #                 department.moodle_id = moodle_department_id
    #                 session.add(department)
    #                 session.commit()
    #                 print('--- Successfully added Department %s to Moodle ---' % department.code)
    #             else:
    #                 print('--- Failure to create Departments to Moodle --- ', moodle_department_id)
    #
    # async def create_users_to_moodle(self):
    #     with session_scope() as session:
    #         # Get only one at a time
    #         user = session.query(User).filter(
    #             and_(User.moodle_id.is_(None), User.deleted_at.is_(None))).first()
    #         if user and (user.staff or user.student):
    #             moodle_user_id = self.moodle.createUser(username=user.username, firstname=user.first_name,
    #                                                     lastname=user.last_name, email=user.email,
    #                                                     password=generate_strong_string())
    #             print(generate_strong_string())
    #             if moodle_user_id != 0:
    #                 user.moodle_id = moodle_user_id
    #                 session.add(user)
    #                 session.commit()
    #                 print('--- Successfully added User %s to Moodle ---' % user.username)
    #             else:
    #                 print('--- Failure to create Users to Moodle --- ', moodle_user_id)
