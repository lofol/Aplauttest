import asyncio
from bot.bot import run_bot
from pars.loggs import ParserLogger

if __name__ == "__main__":
    ParserLogger()
    asyncio.run(run_bot())
