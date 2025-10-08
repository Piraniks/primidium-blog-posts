"""
Dependency Injector is the most popular DI library with features including automatic wiring, overwriting of
dependencies, supporting asynchronous dependencies. The container can be declarative or dynamic (imperative)
and is capable of resource management.

Pros:
- Solid documentation with multiple examples on how to use the most common functionalities.
- Container is aware of and changing behavior based on whether dependencies are synchronous or asynchronous.
- Supports for generator-based dependencies, like resources with cleanup steps.
- Has built-in support for factories, type hints, and automatic wiring.
- Gives great control over what dependencies types are injected - through type hints and providers which can assert on
provided instance types.

Cons:
- Requires more complex setup.

Would suggest for:
- All types of projects, but the simplest scripts or programs that are to be deleted soon after creation.
- All experience levels - experienced engineers will be able to leverage the more advanced functionalities, novices can
learn from the documentation.

Dependency Injector is a great choice and can be considered a solid and capable solution for all types of projects
but the most trivial ones or most basic educational purposes for a newcomer to dependency injection pattern - but only
due to the overhead to learn the tool + it's wide capabilities to understand what's going on. I would probably still
recommend it for newbies, but only wit the assumption that it will be used long-term - e.g., a project to be maintained
in the future, not one-time scripts to be deleted after a few days.
It seems like a default choice for a Python project requiring a dependency injection library.
"""
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide, Provider


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


class EmailNotificationChannel(NotificationChannel):
    def __init__(self, auth_key: str):
        self.auth_key = auth_key


class TypedConfiguration(Protocol):
    email_auth_key: str


class Container(containers.DeclarativeContainer):
    configuration: TypedConfiguration = providers.Configuration(strict=True)
    # The main reason we're using a concrete implementation in the factory here is to show off how to work with such
    # cases. Of course in theory we could have a ContainerBase from which all containers inherit etc... but even with
    # this more complex setup, it's still very easy to follow and work with in testing.
    notification_channel: providers.Provider[NotificationChannel] = providers.Factory(
        instance_of=EmailNotificationChannel,
        auth_key=configuration.email_auth_key,
    )


@inject
def declarative_send_notification(
    *,
    user: User,
    notification: Notification,
    notification_channel: NotificationChannel = Provide[Container.notification_channel],
) -> Confirmation:
    confirmation = notification_channel.send(
        id=notification.id,
        to=user.email,
        subject=notification.name,
        body=notification.message
    )
    return confirmation


@inject
def declarative_send_notification_with_provider_parameters(
    *,
    user: User,
    notification: Notification,
    # Important: Provider here vs Provide in other cases. It will return the provider (e.g., a factory) instead of an
    # instance, so we can pass arguments dynamically, based on the local context.
    notification_channel_provider: providers.Factory[NotificationChannel] = Provider[Container.notification_channel],
    # The only use-case in tests that requires kwargs is parametrization on resolution, in practice it would probably
    # be based on some values from inside the function, but this is the simplest example to show off and test.
    **notification_channel_kwargs
) -> Confirmation:
    notification_channel = notification_channel_provider(**notification_channel_kwargs)
    confirmation = notification_channel.send(
        id=notification.id,
        to=user.email,
        subject=notification.name,
        body=notification.message
    )
    return confirmation


@inject
def dynamic_send_notification(
    *,
    user: User,
    notification: Notification,
    # In theory, we could use the same string approach when using a declarative container. But we cannot use it the
    # other way around, because dynamic container has no attributes to start with, so this is the only sensible option.
    notification_channel: NotificationChannel = Provide['notification_channel'],
) -> Confirmation:
    confirmation = notification_channel.send(
        id=notification.id,
        to=user.email,
        subject=notification.name,
        body=notification.message
    )
    return confirmation
