import logging

logger = logging.getLogger("octopus_server")

def run(*args, **kwargs):
    logger.info("Incident COPY created! args=%s kwargs=%s", args, kwargs)



