from uuid import UUID, uuid4

import pytest
from punq import Container

from posts.dependency_injection.notification_sender import NotificationChannel, User, Confirmation, Notification
from posts.dependency_injection.punq_examples.punq_example import send_notification


@pytest.fixture
def container():
    return Container()


def test_inject_client_without_any_parameters(
    container: Container,
    user: User,
    notification: Notification,
):
    class BasicInMemoryHandler(NotificationChannel):
        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id='in_memory')

    container.register(NotificationChannel, BasicInMemoryHandler)

    confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )

    assert confirmation == Confirmation(notification_id=notification.id, channel_id='in_memory')


def test_inject_randomized_seed_notification_channel_using_an_instance(
    container: Container,
    user: User,
    notification: Notification,
):
    class NotificationHandlerWithRandomizedSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'in_memory+{self.seed}')

    # Useful when sharing resources like a database connection or sharing the same object between multiple container
    # resole calls - when requesting the same dependency in different parts of depending code, for example user
    # requesting changes inserted without need to pass it everywhere.
    instance = NotificationHandlerWithRandomizedSeed()
    container.register(NotificationChannel, instance=instance)

    first_confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )
    second_confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )

    assert first_confirmation == second_confirmation


def test_inject_randomized_seed_notification_channel_using_a_factory(
    container: Container,
    user: User,
    notification: Notification,
):
    class NotificationHandlerWithRandomizedSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'in_memory+{self.seed}')

    container.register(NotificationChannel, NotificationHandlerWithRandomizedSeed)

    first_confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )
    second_confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )

    assert first_confirmation.notification_id == second_confirmation.notification_id
    assert first_confirmation.channel_id != second_confirmation.channel_id


def test_inject_notification_channel_with_parameters_on_injection(
    container: Container,
    user: User,
    notification: Notification,
):
    class ParametrizedNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'in_memory+{self.sender}')

    # Useful when passing parameters that are required to build the instance of the dependency and don't change
    # between the instances - configuration, possibly other dependencies. It's a fancy shortcut over manually creating
    # a callable without any parameters, but instead storing those in the callable passed into the container on
    # registration..
    sender = 'parametrized_on_injection'
    container.register(NotificationChannel, ParametrizedNotificationChannel, sender=sender)

    confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
    )

    assert confirmation.notification_id == notification.id
    assert confirmation.channel_id == f'in_memory+{sender}'


def test_inject_notification_channel_with_parameters_on_resolution(
    container: Container,
    user: User,
    notification: Notification,
):
    class ParametrizedNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'in_memory+{self.sender}')

    # Useful when passing call-specific parameters that are required to build the instance of the dependency and change
    # between the instances - request id, user context, personalized configuration, feature flags and more.
    # The only way to simulate this behavior is to pass the parameters as kwargs to the depending code directly, using
    # some context variables and skipping the resolver. At that point it's stateful, so we're back to the reason we
    # introduced a dependency injection tooling in the first place. Another alternative would be to instead of passing
    # the parameters as kwargs to resolver. Instead of returning an instance, return a callable that will create the
    # instance with the parameters passed in the call. Very similar to how functional paradigm resolves similar issues.
    sender = 'parametrized_on_resolution'
    container.register(NotificationChannel, ParametrizedNotificationChannel)

    confirmation = send_notification(
        container=container,
        user=user,
        notification=notification,
        sender=sender,
    )

    assert confirmation.notification_id == notification.id
    assert confirmation.channel_id == f'in_memory+{sender}'
