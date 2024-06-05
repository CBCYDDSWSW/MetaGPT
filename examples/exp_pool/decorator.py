"""Decorator example of experience pool."""

import asyncio
import uuid

from metagpt.exp_pool import exp_cache, exp_manager
from metagpt.logs import logger


@exp_cache(pass_exps_to_func=True)
async def produce(req, exps=None):
    logger.info(f"Previous experiences: {exps}")
    return f"{req} {uuid.uuid4().hex}"


async def main():
    req = "Water"

    resp = await produce(req)
    logger.info(f"The resp of `produce{req}` is: {resp}")

    exps = await exp_manager.query_exps(req)
    logger.info(f"Find experiences: {exps}")


if __name__ == "__main__":
    asyncio.run(main())
