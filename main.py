from starlette.middleware.cors import CORSMiddleware

from src.app import RegistrationApp
from src.core.config import settings
from src.core.redis import redis_dependency
from src.helpers.task_manager import TaskManager
from src.db.session import database
from src.api_routes.program_api import program_router
from src.api_routes.sr2_finance_api import sr2_router

app = RegistrationApp()

app.debug = True

app.add_middleware(
    CORSMiddleware, allow_headers=["*"], allow_origins=["*"], allow_methods=["*"]
)

# Adding REST API route for querying Program Module
app.include_router(program_router)
app.include_router(sr2_router)


async def process_data():
    task_manager = TaskManager(redis_url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    await task_manager.start_processing()
    await task_manager.enqueue_task("create_course_to_moodle")


@app.on_event("startup")
async def startup():
    """
        Startup Event Will be called when the server starts
        Start Database Connection
        Start Redis Connection
    :return:
    """
    await database.connect()

    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    # await redis_dependency.init()

    # background_tasks = BackgroundTasks()
    # background_tasks.add_task(process_data)
    # await background_tasks()


@app.on_event("shutdown")
async def shutdown():
    """
        Shutdown Event Will be called when the server stops
        Close Database Connection
    :return:
    """
    await database.disconnect()


@app.get("/")
def home():
    return {
        "title": "Registration Works",
    }
