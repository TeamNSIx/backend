"""Bootstrap RBAC roles, permissions and admin user.

Run after migrations:

    uv run python -m scripts.bootstrap_rbac
"""

import asyncio
import sys

from src.app.db.database import AsyncSessionLocal
from src.app.internal.bootstrap import run_bootstrap


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await run_bootstrap(session)
    print('RBAC bootstrap completed successfully')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception:
        print('RBAC bootstrap failed', file=sys.stderr)
        raise
