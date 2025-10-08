from uuid import UUID, uuid4

import pytest
from dependency_injector import containers, providers

from posts.dependency_injection.dependency_injector_examples.python_dependency_injector_example import (
    Container,
    declarative_send_notification,
)
from posts.dependency_injection.notification_sender import NotificationChannel, Confirmation, User, Notification


# In the rest of the tests, both overrides are used, depending on the need, but both are equivalent.
# In some cases it might be easier to override only the one thing we want to test with on the container directly.
# In other cases, it might be more convenient to provide a whole container that encapsulates e.g., Object provider state,
# so we don't have to worry about it.
def test_provider_vs_container_overriding(
    user: User,
    notification: Notification,
):
    class OverridingNotificationChannel(NotificationChannel):
        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id='dummy')

    class OverridingContainer(containers.DeclarativeContainer):
        notification_channel = providers.Factory(OverridingNotificationChannel)

    # The 2 overrides below are equivalent. Because we're overriding the whole provider, and it's the provider that
    # defines parameters into the notification channel, we are free to use any interface we please. We're not tied to
    # the Container implementations.
    container_for_container_override = Container()
    container_for_container_override.override(OverridingContainer)
    container_for_container_override.wire(modules=['..python_dependency_injector_example'])
    confirmation_with_container_override = declarative_send_notification(user=user, notification=notification)

    container_for_provider_override = Container()
    container_for_provider_override.notification_channel.override(providers.Factory(OverridingNotificationChannel))
    container_for_provider_override.wire(modules=['..python_dependency_injector_example'])
    confirmation_with_provider_override = declarative_send_notification(user=user, notification=notification)

    assert confirmation_with_container_override == confirmation_with_provider_override


def test_inject_client_without_any_parameters(
    user: User,
    notification: Notification,
):
    # We're using a declarative approach, so showing off particular cases is quite explicit and long.
    # Given a realistic use-case, it would all or at least mostly live in fixtures per module/functionality.
    # But it also enables per use-case container override while still having automatic wiring in place with code typing.
    class SimpleNotificationChannel(NotificationChannel):
        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id='declarative')

    container = Container()
    # Even though we're using a declarative approach and using attributes of this container, we can override a
    # particular container making it easier to test. The new factories do not have to be 1-1 with the ones they override.
    container.notification_channel.override(providers.Factory(SimpleNotificationChannel))
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation == Confirmation(notification_id=notification.id, channel_id='declarative')


def test_inject_randomized_seed_notification_channel_using_an_instance(
    user: User,
    notification: Notification,
):
    class NotificationChannelWithRandomSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+{self.seed}')

    class ObjectContainer(containers.DeclarativeContainer):
        # We could use provider.Singleton here as well, but for the sake of an even more straight forward example,
        # an object is used - it means that the exact same object will be used for all calls, not once per container
        # like in a case of a singleton. It's returned as-is, so we can have a truly global single instance, eagerly
        # evaluated.
        notification_channel = providers.Object(NotificationChannelWithRandomSeed())

    first_container = Container()
    first_container.override(ObjectContainer())
    first_container.wire(modules=['..python_dependency_injector_example'])

    first_confirmation = declarative_send_notification(user=user, notification=notification)

    second_container = Container()
    second_container.override(ObjectContainer())
    second_container.wire(modules=['..python_dependency_injector_example'])
    second_confirmation = declarative_send_notification(user=user, notification=notification)

    assert first_confirmation == second_confirmation


def test_inject_randomized_seed_notification_channel_using_a_singleton_factory(
    user: User,
    notification: Notification,
):
    class NotificationChannelWithRandomSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+{self.seed}')

    first_container = Container()
    # For every container instance, the Singleton provider will return the same object. If we want to use the same
    # service, state etc. throughout the whole process/call, we need to use a singleton provider instead of a factory.
    first_container.notification_channel.override(providers.Singleton(NotificationChannelWithRandomSeed))
    first_container.wire(modules=['..python_dependency_injector_example'])

    first_confirmation = declarative_send_notification(user=user, notification=notification)
    second_confirmation = declarative_send_notification(user=user, notification=notification)
    assert first_confirmation == second_confirmation

    second_container = Container()
    second_container.notification_channel.override(providers.Singleton(NotificationChannelWithRandomSeed))
    second_container.wire(modules=['..python_dependency_injector_example'])

    third_confirmation = declarative_send_notification(user=user, notification=notification)
    assert first_confirmation != third_confirmation


def test_inject_randomized_seed_notification_channel_using_a_factory(
    user: User,
    notification: Notification,
):
    class NotificationChannelWithRandomSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+{self.seed}')

    container = Container()
    # Important to note: the Factory provider will return different objects one each call, compared to a singleton
    # where for any container the same object is returned.
    container.notification_channel.override(providers.Factory(NotificationChannelWithRandomSeed))
    container.wire(modules=['..python_dependency_injector_example'])

    first_confirmation = declarative_send_notification(user=user, notification=notification)
    second_confirmation = declarative_send_notification(user=user, notification=notification)

    # Factories produce new objects on each call - useful for stateless or configurable services.
    assert first_confirmation.notification_id == second_confirmation.notification_id
    assert first_confirmation.channel_id != second_confirmation.channel_id


def test_inject_notification_channel_with_parameters_on_injection(
    user: User,
    notification: Notification,
):
    class ParametrizedNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+{self.sender}')

    sender = 'parametrized_on_injection'
    class SeededContainer(containers.DeclarativeContainer):
        # This is not the best way to pass parameters on factory creation, but it's a simple example to prove a point.
        # Using a config provider and loading data from a file or passing it directly is the preferred way - then
        # other code should rely on that config.
        notification_channel = providers.Factory(ParametrizedNotificationChannel, sender=sender)

    container = Container()
    container.override(SeededContainer())
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation.channel_id == f'declarative+{sender}'


def test_inject_notification_channel_with_parameters_passed_to_container(
    user: User,
    notification: Notification,
):
    class ParametrizedNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'parametrized+{self.sender}')

    # Overriding can happen on a particular provider level as well as overriding the whole container - by providing an
    # alternative container object to override with.
    class SeededContainer(containers.DeclarativeContainer):
        # Config allows passing parameters on factory creation in a structured way with support for many sources.
        config = providers.Configuration()
        # Automatically injects the "sender" parameter from the config. It doesn't matter if the container being
        # overridden has the same parameter name or not - which is convenient for testing or different factory
        # arguments.
        notification_channel = providers.Factory(ParametrizedNotificationChannel, sender=config.sender)

    container = Container()
    sender = 'parametrized_on_container_instance'
    overriding_container = SeededContainer(config=dict(sender=sender))
    container.override(overriding_container)
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation.channel_id == f'parametrized+{sender}'


@pytest.fixture
def different_user() -> User:
    return User(email='different.user@email.com')


@pytest.fixture
def different_notification() -> Notification:
    return Notification(
        id=UUID(int=1),
        name='Different Notification Name',
        message='DifferentMessage',
    )


def test_inject_notification_channel_with_dependency(
    user: User,
    notification: Notification,
    different_user: User,
    different_notification: Notification,
):
    # We could simplify this test greatly by using fixtures, so most of this setup noise is delegated to fixtures, and
    # we're provided with actual objects/services to work with. Pytest fixture system is a dependency injection library
    # of its own, we can get it working with dependency injector quite easily.

    class DatabaseEmailRecorderService:
        def __init__(self):
            self.sent_emails: dict[UUID, tuple[str, str, str]] = dict()

        def send(self, id: UUID, to: str, subject: str, body: str) -> None:
            # Imagine API calls here in a production-ready implementation.
            # In the case of test implementation - collecting the data for ensuring emails were sent is most likely more
            # than enough. Notification example is maybe not the best example of a real-world use-case, but think about
            # this being a database shared across many stateless services - handling connection pools etc.
            self.sent_emails[id] = (to, subject, body)

    class ExternalServiceNotificationChannel(NotificationChannel):
        def __init__(self, email_service: DatabaseEmailRecorderService):
            self.email_service = email_service

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            self.email_service.send(id=id, to=to, subject=subject, body=body)
            return Confirmation(notification_id=id, channel_id=f'parametrized')

    # Overriding can happen on a particular provider level as well as overriding the whole container - by providing an
    # alternative container object to override with.
    class DependencyContainer(containers.DeclarativeContainer):
        email_recorder_service = providers.Singleton(DatabaseEmailRecorderService)
        notification_channel = providers.Factory(ExternalServiceNotificationChannel, email_service=email_recorder_service)

    container = Container()
    overriding_container = DependencyContainer()
    container.override(overriding_container)
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)
    different_confirmation = declarative_send_notification(user=different_user, notification=different_notification)
    assert confirmation != different_confirmation

    # The recorder dependency is a singleton, so we can easily get the same object with the recorded emails.
    email_recorder_service = overriding_container.email_recorder_service()
    assert len(email_recorder_service.sent_emails) == 2

    expected_sent_email_for_confirmation = (user.email, notification.name, notification.message)
    assert email_recorder_service.sent_emails[confirmation.notification_id] == expected_sent_email_for_confirmation
    expected_sent_email_for_different_confirmation = (different_user.email, different_notification.name, different_notification.message)
    assert email_recorder_service.sent_emails[different_confirmation.notification_id] == expected_sent_email_for_different_confirmation
