import logging

import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter

from src.apis import ApiQuery, ApiMutation
from src.core.config import settings
from src.core.logger import CustomFormatter
#from src.core.security import get_context


class RegistrationApp(FastAPI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(settings.PROJECT_TITLE)
        self.logger.setLevel(logging.DEBUG)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        ch.setFormatter(CustomFormatter())

        self.logger.addHandler(ch)
        self.initialize_graphql()

    def log_incoming_message(self, message):
        """Method to do something meaningful with the incoming message"""
        self.logger.info(f"***************** {message} *****************")

    def initialize_graphql(self):
        """Method to initialize graphql"""
        self.log_incoming_message("Initializing GraphQL")
        schema = strawberry.Schema(ApiQuery, mutation=ApiMutation)
        graphql_app = GraphQLRouter(schema, debug=self.debug | False)
        self.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
        gui_app = GraphQL(schema)
        self.add_route("/gui", gui_app, methods=["GET"])