from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class User:
    email: str


@dataclass(frozen=True)
class Notification:
    id: UUID
    name: str
    message: str


@dataclass(frozen=True)
class Confirmation:
    notification_id: UUID
    channel_id: str


class NotificationChannel(Protocol):
    def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
        raise NotImplementedError()
