from uuid import UUID

import pytest

from posts.dependency_injection.notification_sender import User, Notification


@pytest.fixture
def user() -> User:
    return User(email='user@email.com')


@pytest.fixture
def notification() -> Notification:
    return Notification(
        id=UUID(int=0),
        name='Notification Name',
        message='Message',
    )
