# app.py
# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# -------------------------------------
import os
import sys

# Add current directory to Python path - crucial for container deployments
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import asyncio
import traceback
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()
# Improved environment variable handling for both local and Azure environments
from config import DefaultConfig

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import TurnContext
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from bot import MyBot
from common.cosmosdb_checkpointer import AsyncCosmosDBSaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

# Create configuration - handles both local and Azure environments
CONFIG = DefaultConfig()

# Create adapter with proper authentication based on environment
AUTH = ConfigurationBotFrameworkAuthentication(CONFIG) if CONFIG.APP_ID else None
ADAPTER = CloudAdapter(AUTH)

# Catch-all for errors
async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)

ADAPTER.on_turn_error = on_error

# Get Cosmos DB connection info from App Service settings
cosmos_endpoint = os.environ.get("AZURE_COSMOSDB_ENDPOINT")
cosmos_key = os.environ.get("AZURE_COSMOSDB_KEY")
cosmos_db_name = os.environ.get("AZURE_COSMOSDB_NAME") 
cosmos_container_name = os.environ.get("AZURE_COSMOSDB_CONTAINER_NAME")

# Simple check for required values
if not all([cosmos_endpoint, cosmos_key, cosmos_db_name, cosmos_container_name]):
    print("Error: Missing Cosmos DB connection information in app settings")
    sys.exit(1)

# Create checkpointer with properly formatted parameters
checkpointer_async = AsyncCosmosDBSaver(
    endpoint=cosmos_endpoint,
    key=cosmos_key.strip() if cosmos_key else None,  # Ensure clean string format
    database_name=cosmos_db_name,
    container_name=cosmos_container_name,
    serde=JsonPlusSerializer(),
)

# Create bot instance
BOT = MyBot(cosmos_checkpointer=checkpointer_async)

# API endpoint for bot messages
async def messages(req: Request) -> Response:
    return await ADAPTER.process(req, BOT)

# Initialize the app with middleware
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)

# Initialize cosmos checkpointer at startup
async def init_app():
    await checkpointer_async.setup()
    return APP

# Entry point that works both locally and in Azure
if __name__ == "__main__":
    
    # web.run_app(init_app(), host="0.0.0.0", port=8000)
    # For local development
    web.run_app(init_app(), host="localhost", port=CONFIG.PORT)