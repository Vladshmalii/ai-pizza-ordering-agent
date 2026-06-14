import asyncio
import logging
from dotenv import load_dotenv

from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, AgentSession
from livekit.agents.voice import Agent
from livekit.plugins import openai

from src.agent.tools import get_menu, get_item_details, create_order, get_order_status
from src.agent.prompts import SYSTEM_PROMPT

load_dotenv()
logging.getLogger().setLevel(logging.DEBUG)

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = Agent(
        llm=openai.realtime.RealtimeModel(
            model="gpt-realtime-mini",
        ),
        instructions=SYSTEM_PROMPT,
        tools=[get_menu, get_item_details, create_order, get_order_status],
    )


    session = AgentSession()
    await session.start(agent=agent, room=ctx.room)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
