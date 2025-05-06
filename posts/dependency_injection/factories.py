from uuid import UUID

import factory

from posts.dependency_injection.punq_examples.punq_example import User, Notification


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda sequence_number: f'email{sequence_number}@example.com')


class NotificationFactory(factory.Factory):
    class Meta:
        model = Notification

    id = factory.Sequence(lambda sequence_number: UUID(int=sequence_number))
    name = factory.Sequence(lambda sequence_number: f'Notification Name {sequence_number}')
    message = factory.Sequence(lambda sequence_number: f'Notification Message {sequence_number}')
