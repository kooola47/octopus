import logging
import asyncio

logger = logging.getLogger("octopus_server")

def run(*args, **kwargs):
    # If called synchronously, run the async logic in an event loop and return the result
    async def _run():
        logger.info("Incident created! args=%s kwargs=%s", args, kwargs)
        await asyncio.sleep(1)  # Simulate async work
        logger.info("Incident creation complete.")
        return "Incident created (async complete)"
    return asyncio.run(_run())
