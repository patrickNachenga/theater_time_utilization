from starlette.middleware.cors import CORSMiddleware

from src.app import RegistrationApp
from src.db.session import database
from src.api import program_api
from src.modules.programs.service import ProgramService

app = RegistrationApp()

app.debug = True

app.add_middleware(
    CORSMiddleware, allow_headers=["*"], allow_origins=["*"], allow_methods=["*"]
)


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


@app.on_event("shutdown")
async def shutdown():
    """
        Shutdown Event Will be called when the server stops
        Close Database Connection
    :return:
    """
    await database.disconnect()


@app.get("/program")
async def get_program_data(code: str | None = None):
    return await ProgramService().api_get_program_by_code(code=code)


@app.get("/")
def home():
    return {
        "title": "Registration Works",
    }
