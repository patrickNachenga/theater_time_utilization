import json
import logging

import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from strawberry.fastapi import GraphQLRouter

from src.apis import ApiQuery, ApiMutation
from src.core.config import settings, EnhancedJSONEncoder
from src.core.logger import CustomFormatter
from src.core.rabbit import RabbitMQ
from src.core.security import get_context, permissions


from src.core.security import get_context


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
        self.rabbit_client = RabbitMQ(self.log_incoming_message)

    async def initialize_async(self):
        await self.rabbit_client.setup()
        await self.permissions()


    def log_incoming_message(self, message):
        """Method to do something meaningful with the incoming message"""
        self.logger.info(f"***************** {message} *****************")

    def initialize_graphql(self):
        """Method to initialize graphql"""
        self.log_incoming_message("Initializing GraphQL")
        schema = strawberry.Schema(ApiQuery, mutation=ApiMutation)
        graphql_app = GraphQLRouter(schema, debug=self.debug | False, context_getter=get_context)
        self.include_router(graphql_app, prefix="/graphql", tags=["graphql"])
        gui_app = GraphQL(schema)
        self.add_route("/gui", gui_app, methods=["GET"])

    async def permissions(self):
        self.log_incoming_message("Publishing Permissions")
        await self.rabbit_client.publish(
            "sua-esb-permission-exchange", "sua-esb-permission-routing-key",
            json.dumps(permissions, cls=EnhancedJSONEncoder)
        )