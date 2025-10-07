from uuid import UUID, uuid4

from dependency_injector import containers, providers

from posts.dependency_injection.dependency_injector_examples.python_dependency_injector_example import (
    Container,
    declarative_send_notification,
)
from posts.dependency_injection.notification_sender import NotificationChannel, Confirmation, User, Notification


def test_inject_client_without_any_parameters(
    user: User,
    notification: Notification,
):
    # We're using a declarative approach, so showing off particular cases is quite explicit and long.
    # Given a realistic use-case, it would all or at least mostly live in fixtures per module/functionality.
    # But it also enables per use-case container override while still having automatic wiring in place with code typing.
    class SimpleNotificationChannel(NotificationChannel):
        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id='declarative+in_memory')

    class SimpleContainer(containers.DeclarativeContainer):
        notification_channel = providers.Factory(SimpleNotificationChannel)

    container = Container()
    # Even though we're using a declarative approach and using attributes of this container, we can override a particular
    # container making it easier to test. The new factories do not have to be 1-1 with the ones they override.
    container.override(overriding=SimpleContainer())
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation == Confirmation(notification_id=notification.id, channel_id='declarative+in_memory')


def test_inject_randomized_seed_notification_channel_using_an_instance(
    user: User,
    notification: Notification,
):
    class NotificationChannelWithRandomSeed(NotificationChannel):
        def __init__(self):
            self.seed = uuid4()

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+in_memory+{self.seed}')

    class ObjectContainer(containers.DeclarativeContainer):
        # We could use provider.Singleton here as well, but for the sake of an even more straight forward example,
        # an object is used - it means that the exact same object will be used for all calls, not once per container
        # like in case of a singleton. It's returned as-is, so we can have a truly global single instance, eagerly
        # evaluated.
        notification_channel = providers.Object(NotificationChannelWithRandomSeed())

    first_container = Container()
    first_container.override(overriding=ObjectContainer())
    first_container.wire(modules=['..python_dependency_injector_example'])

    first_confirmation = declarative_send_notification(user=user, notification=notification)

    second_container = Container()
    second_container.override(overriding=ObjectContainer())
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
            return Confirmation(notification_id=id, channel_id=f'declarative+in_memory+{self.seed}')

    class SeededContainer(containers.DeclarativeContainer):
        # For every container instance, the same object is returned. If we want to use the same service, state etc.
        # throughout the whole process/call, we need to use a singleton provider instead of a factory.
        notification_channel = providers.Singleton(NotificationChannelWithRandomSeed)

    first_container = Container()
    first_container.override(overriding=SeededContainer())
    first_container.wire(modules=['..python_dependency_injector_example'])

    first_confirmation = declarative_send_notification(user=user, notification=notification)
    second_confirmation = declarative_send_notification(user=user, notification=notification)
    assert first_confirmation == second_confirmation

    second_container = Container()
    second_container.override(overriding=SeededContainer())
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
            return Confirmation(notification_id=id, channel_id=f'declarative+in_memory+{self.seed}')

    class SeededContainer(containers.DeclarativeContainer):
        # Important to note: factory will return different objects one each call, compared to a singleton where for
        # any container the same object is returned.
        notification_channel = providers.Factory(NotificationChannelWithRandomSeed)

    container = Container()
    container.override(overriding=SeededContainer())
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
            return Confirmation(notification_id=id, channel_id=f'declarative+in_memory+{self.sender}')

    sender = 'parametrized_on_injection'
    class SeededContainer(containers.DeclarativeContainer):
        # This is not the best way to pass parameters on factory creation, but it's a simple example to prove a point.
        # Using a config provider and loading data from a file or passing it directly is the preferred way - then
        # other code should rely on that config.
        notification_channel = providers.Factory(ParametrizedNotificationChannel, sender=sender)

    container = Container()
    container.override(overriding=SeededContainer())
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation.channel_id == f'declarative+in_memory+{sender}'


def test_inject_notification_channel_with_parameters_passed_to_container(
    user: User,
    notification: Notification,
):
    class ParametrizedNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+in_memory+{self.sender}')

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
    container.override(overriding=overriding_container)
    container.wire(modules=['..python_dependency_injector_example'])

    confirmation = declarative_send_notification(user=user, notification=notification)

    assert confirmation.channel_id == f'declarative+in_memory+{sender}'


def test_inject_notification_channel_with_dependency():
    ...


def test_provider_vs_container_overriding():
    ...

...
