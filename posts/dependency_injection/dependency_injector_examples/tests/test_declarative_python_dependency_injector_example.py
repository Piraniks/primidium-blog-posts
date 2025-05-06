from uuid import UUID

import pytest
from dependency_injector import containers, providers

from posts.dependency_injection.dependency_injector_examples.python_dependency_injector_example import (
    Container,
    declarative_send_notification,
)
from posts.dependency_injection.notification_sender import NotificationChannel, Confirmation, User, Notification


class InMemoryNotificationChannel(NotificationChannel):
    def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
        return Confirmation(notification_id=id, channel_id='declarative+in_memory')


class OverrideContainer(containers.DeclarativeContainer):
    notification_channel = providers.Factory(InMemoryNotificationChannel)


@pytest.fixture(autouse=True)
def container() -> Container:
    container = Container()
    override_container = OverrideContainer()

    container.override(override_container)
    container.wire(modules=['..python_dependency_injector_example'])

    return container


def test_inject_client_without_any_parameters(
    container: Container,
    user: User,
    notification: Notification,
):
    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation == Confirmation(notification_id=notification.id, channel_id='declarative+in_memory')


def test_inject_randomized_seed_notification_channel_using_an_instance(
    container: Container,
    user: User,
    notification: Notification,
):
    ...


def test_inject_randomized_seed_notification_channel_using_a_factory(
    container: Container,
    user: User,
    notification: Notification,
):
    ...


def test_inject_notification_channel_with_parameters_on_injection(
    container: Container,
    user: User,
    notification: Notification,
):
    ...


def test_inject_notification_channel_with_parameters_on_resolution(
    container: Container,
    user: User,
    notification: Notification,
):
    ...
