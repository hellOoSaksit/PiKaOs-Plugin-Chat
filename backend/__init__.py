"""Chat gateway plugin — the channel-agnostic side of a chatbot channel (Telegram now, LineOA next).

Owns the two channel-agnostic tables (`chat_links`, `chat_link_codes`) that map an inbound channel
identity to a PiKaOs user + conversation thread, on its own declarative `Base` (models.py). The tables
are created by `migrate.migrate()`, run per enabled plugin by the kernel's `scripts.migrate_plugins`.

This is a THIN schema-only extraction (2026-07-01 spec): the gateway logic — inbound→agent routing, the
`chat.Gateway` contract, the command dispatcher — is a later feature build, so there is no router,
service, or bound contract yet and `register()` is a placeholder. `dependencies: ["ai"]` states the
target (inbound messages route to the ai agent runtime); a per-channel provider Tool
(`PiKaOs-Plugin-Tools-Telegram`) depends on THIS plugin.

Package surface the Loader looks for (plugin-architecture.md §5/§10):
  migrate — install-time schema step (create_all), run by scripts.migrate_plugins
"""
from __future__ import annotations


def register(ctx) -> None:
    """No-op for now — the chat gateway ships no DI contract or router yet (schema-only slice). The
    future `chat.Gateway` binding (resolve a channel identity → user, route inbound → agent) lands with
    the gateway feature build."""


__all__ = ["register"]
