from starlette.middleware.cors import CORSMiddleware

from src.app import RegistrationApp
from src.core.redis import redis_dependency
from src.db.session import database

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
    await redis_dependency.init()


@app.on_event("shutdown")
async def shutdown():
    """
        Shutdown Event Will be called when the server stops
        Close Database Connection
    :return:
    """
    await database.disconnect()


@app.get("/health")
async def health():
    """
        Health Check For APP
    :return:
    """
    return {"status": "ok"}


@app.get("/")
def home():
    return {
        "title": "Registration Works",
    }
