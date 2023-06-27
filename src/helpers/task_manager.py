import asyncio
import json

import aioredis
from pydantic import BaseModel
from sqlalchemy import and_, desc
import requests
from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.db.session import session_scope
from src.models import Course
from src.modules.course.service import CourseService


class TaskManager:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.task_queue = asyncio.Queue()
        self.redis_pool = None
        self._queue_interval_seconds: int = 1
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
                    if task_type == "create_course_to_moodle":
                        await self.create_course_to_moodle()
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

    @staticmethod
    async def create_course_to_moodle():
        with session_scope() as session:
            # Get only one at a time
            course = session.query(Course).filter(
                and_(Course.moodle_id.is_(None), Course.deleted_at.is_(None))).first()
            if course:
                """
                Call Department moodle id for uuid
                """
                try:
                    response = requests.get(settings.UAA_URi+f"/department/{course.department_uid}")
                    if response.status_code == 200:
                        responseData = response.json()
                        if not responseData["status"]:
                            raise RuntimeError("Fail to register course to moodle")
                        moodle = MoodleApi()
                        print(course.department_uid)
                        print(responseData)
                        moodle_unit_id = moodle.createCourse(
                            departmentId=responseData["data"]['moodle_id'] or 0,
                            courseFullName=course.name,
                            courseDescription=course.description,
                            courseShortName=course.code,
                        )
                        if moodle_unit_id != 0:
                            course.moodle_id = moodle_unit_id
                            session.add(course)
                            session.commit()
                            print('--- Successfully added course %s to Moodle ---' % course.code)
                            return True
                        else:
                            print()
                            print('--- Failure to create course to Moodle --- ', moodle_unit_id)
                            return False
                    else:
                        raise RuntimeError("Fail to register course to moodle")
                except Exception as e:
                    print('--- Failure to create course to Moodle --- ', course.code)
                    return False

    @staticmethod
    async def create_program_course_to_moodle():
        with session_scope() as session:
            return 0
            # # Get only one at a time
            # course = CourseService.get_unregister_moodle_course()
            # if course:
            #     try:
            #         response = requests.get(settings.UAA_URi+f"department/{course.department_uid}")
            #         if response.status_code == 200:
            #             responseData = response.json()
            #             if responseData["status"]:
            #                 raise RuntimeError("Fail to register course to moodle")
            #             moodle = MoodleApi()
            #             moodle_unit_id = moodle.createCourse(
            #                 departmentId=responseData["moodle_id"],
            #                 courseFullName=course.name,
            #                 courseDescription=course.description,
            #                 courseShortName=course.code,
            #             )
            #
            #             # TODO: add program to moodle
            #             moodle = MoodleApi()
            #             moodle_id = moodle.create_group(
            #                 course_id=4,
            #                 group_name=program_semester.academic_year.name,
            #                 group_description="to be done "
            #             )
            #
            #             if moodle_unit_id != 0:
            #                 course.moodle_id = moodle_unit_id
            #                 session.add(course)
            #                 session.commit()
            #                 print('--- Successfully added course %s to Moodle ---' % course.code)
            #             else:
            #                 print('--- Failure to create course to Moodle --- ', moodle_unit_id)
            #         else:
            #             raise RuntimeError("Fail to register course to moodle")
            #     except Exception as e:
            #         print('--- Failure to create course to Moodle --- ', course.code)
