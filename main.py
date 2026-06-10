from sched import scheduler

from src.core.config import Settings
from src.helpers.apscheduler import scheduler
from starlette.middleware.cors import CORSMiddleware

from src.app import MainServiceApp
from src.core.redis import redis_dependency
from src.db.session import database
from src.api_routes.program_api import program_router
from src.api_routes.sr2_finance_api import sr2_router

app = MainServiceApp()

# app.debug = True
app.debug = Settings().SYSTEM_DEBUG_MODE

app.add_middleware(
    CORSMiddleware, allow_headers=["*"], allow_origins=["*"], allow_methods=["*"]
)

# Adding REST API route for querying Program Module
app.include_router(program_router)
app.include_router(sr2_router)


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
    await redis_dependency.init()
    if not app.debug:
        await app.initialize_async()
        scheduler.start()


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
        "title": "Theatre Utilization Works",
    }
