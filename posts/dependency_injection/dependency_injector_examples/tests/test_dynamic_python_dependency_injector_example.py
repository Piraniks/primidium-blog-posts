from uuid import UUID

from dependency_injector import providers
from dependency_injector.containers import DynamicContainer

from posts.dependency_injection.dependency_injector_examples.python_dependency_injector_example import (
    dynamic_send_notification,
)
from posts.dependency_injection.notification_sender import NotificationChannel, Confirmation, User, Notification


def test_inject_client_without_any_parameters(
    user: User,
    notification: Notification,
):
    class InMemoryNotificationChannel(NotificationChannel):
        def send(self, id: UUID, to: str, subject: str, body: str) -> Confirmation:
            return Confirmation(notification_id=id, channel_id='dynamic')

    container = DynamicContainer()
    container.notification_channel = providers.Factory(InMemoryNotificationChannel)
    container.wire(modules=['..python_dependency_injector_example', __name__])

    confirmation = dynamic_send_notification(user=user, notification=notification)

    assert confirmation == Confirmation(notification_id=notification.id, channel_id='dynamic')
