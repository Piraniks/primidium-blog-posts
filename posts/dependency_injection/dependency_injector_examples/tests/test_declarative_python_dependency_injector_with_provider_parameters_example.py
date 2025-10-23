from uuid import UUID

from dependency_injector import providers

from posts.dependency_injection.dependency_injector_examples.python_dependency_injector_example import (
    Container,
    declarative_send_notification_with_provider_parameters,
)
from posts.dependency_injection.notification_sender import Confirmation, Notification, NotificationChannel, User


def test_inject_client_with_parameters_on_resolution(
    user: User,
    notification: Notification,
):
    # We're using a declarative approach, so showing off particular cases is quite explicit and long.
    # Given a realistic use-case, it would all or at least mostly live in fixtures per module/functionality.
    # But it also enables per use-case container override while still having automatic wiring in place with code typing.
    class SimpleNotificationChannel(NotificationChannel):
        def __init__(self, sender: str):
            self.sender = sender

        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id=f'declarative+{self.sender}')

    container = Container()
    # Even though we're using a declarative approach and using attributes of this container, we can override a particular
    # container making it easier to test. The new factories do not have to be 1-1 with the ones they override.
    container.notification_channel.override(providers.Factory(SimpleNotificationChannel))
    container.wire(modules=['..python_dependency_injector_example'])

    sender = 'parametrized_on_resolution'
    confirmation = declarative_send_notification_with_provider_parameters(
        user=user, notification=notification, sender=sender
    )

    assert confirmation == Confirmation(notification_id=notification.id, channel_id=f'declarative+{sender}')
