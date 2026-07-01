"""Chat gateway models — the channel-agnostic identity + thread schema this plugin OWNS.

The chat gateway is the generic side of a chatbot channel (Telegram now, LineOA next). A per-channel
provider Tool (`PiKaOs-Plugin-Tools-Telegram`, …) owns the channel-specific connection; THIS plugin owns
the two channel-agnostic tables that map an inbound identity to a PiKaOs user + conversation thread:

  chat_links       — binds a (channel, channel_user_id) identity to a PiKaOs user
  chat_link_codes  — a short-lived, single-use code a logged-in user redeems to claim a channel identity

They live on this plugin's OWN declarative `Base` (separate metadata from the kernel), created by the
plugin's migration step on install (`migrate.py` / `scripts.migrate_plugins`), never by Core's Alembic.

Cross-plugin refs are logical UUIDs, NOT foreign keys: `user_id` points at `auth.users.id`, `task_id` at
`ai.tasks.id` — bare UUIDs with no DB-level FK across the plugin boundary.

Channel-agnostic on purpose (locked decision 2026-07-01): `channel_user_id` / `channel_chat_id` are
strings (Telegram sends a numeric id, LineOA sends `U…`), so a second channel needs only a new provider
Tool + a `channel` value — no schema change.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """This plugin's declarative base — its metadata is independent of the kernel's `app.core.db.Base`."""


class ChatLink(Base):
    """The trust anchor — binds a channel identity to a PiKaOs user. Every inbound message resolves
    `(channel, channel_user_id)` to this row; all permission/quota checks then run against `user_id`
    (the same RBAC the web app uses). No row → the gateway only handles linking. `task_id` is the
    persistent conversation thread (lazily created so context survives across messages)."""

    __tablename__ = "chat_links"

    # e.g. "telegram", "lineoa" — the provider Tool that owns this identity.
    channel: Mapped[str] = mapped_column(String(32), primary_key=True)
    # the channel's own user id, as a string (Telegram numeric / LineOA `U…`) — supplied by the channel.
    channel_user_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    # where to reply into (Telegram's private chat id, etc.); some channels reuse channel_user_id.
    channel_chat_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # logical ref → auth.users.id (no cross-plugin FK)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    # logical ref → ai.tasks.id (no cross-plugin FK): the conversation thread lives in the ai plugin.
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ChatLinkCode(Base):
    """A short-lived, single-use code a logged-in user generates to claim a channel identity. The user
    sends the code through the channel; redeem checks it's unexpired + unused, writes the ChatLink, and
    stamps `used_at`. Channel-agnostic — a code works for whichever channel redeems it. Random +
    unguessable; expires in minutes (the real auth boundary is the user already being authenticated in
    the app when they minted it)."""

    __tablename__ = "chat_link_codes"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
