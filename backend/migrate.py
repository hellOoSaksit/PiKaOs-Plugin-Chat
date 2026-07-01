"""Install-time schema step for the chat gateway plugin.

The kernel migration runner (`scripts.migrate_plugins`) calls `migrate(engine, session_factory)` for each
enabled plugin after Core's Alembic baseline. Chat owns its tables on its own `Base` metadata (models.py),
so here we just create them. No seed — the `chat.read` / `chat.use` permissions are declared in the
manifest and (until the auth permission-catalog seam lands) still seeded centrally by the auth plugin.

Functional/fresh-DB model (locked decision): plain `create_all` on the plugin's metadata, not a versioned
Alembic history yet — per-plugin Alembic is a later hardening step.
"""
from __future__ import annotations

from .models import Base


async def migrate(engine, session_factory) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
