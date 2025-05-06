import pytest

from posts.dependency_injection.notification_sender import User, Notification
from posts.dependency_injection.factories import UserFactory, NotificationFactory


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def notification() -> Notification:
    return NotificationFactory()
