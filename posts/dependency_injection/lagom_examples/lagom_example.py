"""

"""
from posts.dependency_injection.notification_sender import User, Notification, Confirmation, NotificationChannel


def send_notification_as_lagom(
    *,
    notification_channel: NotificationChannel,
    user: User,
    notification: Notification,
) -> Confirmation:
    # Note: We have no typing suggestions, since the library does not support type hinting - we have to "trust" that
    # injected dependency implements a "send" method
    confirmation = notification_channel.send(
        id=notification.id, to=user.email, subject=notification.name, body=notification.message
    )
    return confirmation
