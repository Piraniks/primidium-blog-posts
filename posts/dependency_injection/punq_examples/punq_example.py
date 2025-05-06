"""
Punq is one of the simplest DI libraries available for Python - simpler solution would consist mostly of a context
dictionary being passed around.

Pros:
- Easy to use - you create the container, plug data into it explicitly and pass the container around.
- Light and dead simple, the library is small enough to accidentally implement when working on your project.
- Anything can be a key to register on the container, including classes, raw values like string etc.

Cons:
- No type hinting support - you have to trust that the injected dependency implements the required interface.
- Little documentation on use-cases, only a few cases on how to use in README.
- No automatic wiring, you have to manually resolve, parametrize and pass the container around.
- Lack of support for asynchronous dependencies.
- Lack of support for generator-based dependencies, like resources with clean-up steps.

Would recommend only for:
- Small projects that need a super simple DI support but don't rely on stringer type hints for long-term maintenance.
- Projects that require only a few dependencies to be injected, so the manual wiring is not an issue long-term.
- Learning purposes - to understand how DI works and what are the basic requirements for a DI library.

Anything bigger than smallest of projects would require a more feature rich library. Considering how simple punq is, I
would probably recommend implementing a custom solution instead of using it, as it's not much more work, you can easily
extend it, and you don't have to rely on a third-party library that might not be maintained in the future and is a
security risk.
"""
from punq import Container

from posts.dependency_injection.notification_sender import NotificationChannel, User, Confirmation, Notification


def send_notification(
    *,
    container: Container,
    user: User,
    notification: Notification,
    # The only use-case in tests that requires kwargs is parametrization on resolution.
    **notification_channel_kwargs
) -> Confirmation:
    notification_channel = container.resolve(NotificationChannel, **notification_channel_kwargs)
    # Note: We have no typing suggestions, since the library does not support type hinting - we have to "trust" that
    # injected dependency implements a "send" method
    confirmation = notification_channel.send(
        id=notification.id,
        to=user.email,
        subject=notification.name,
        body=notification.message
    )
    return confirmation
