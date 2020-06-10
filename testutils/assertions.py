# -*- coding: utf-8 -*-
from django.core import mail


class EmailAssertionsMixin(object):
    """Assertions related to sending emails.
    """
    def assertEmailsInMailbox(self, count):
        self.assertEqual(
            len(mail.outbox),
            count,
            'There is {0} e-mails in mailbox, expected {1}'.format(
                len(mail.outbox),
                count,
            )
        )

    def _is_email_matching_criteria(self, email, **kwargs):
        for key, value in kwargs.items():
            if getattr(email, key) != value:
                return False
        return True

    def assertEmail(self, email, **kwargs):
        for key, value in kwargs.items():
            self.assertEqual(
                getattr(email, key),
                value,
                'Email does not match criteria, expected {0} to be {1} but it is {2}'.format(
                    key,
                    value,
                    getattr(email, key),
                )
            )

    def assertEmailExists(self, **kwargs):
        for email in mail.outbox:
            if self._is_email_matching_criteria(email, **kwargs):
                return
        raise AssertionError('Email matching criteria was not sent')

    def assertEmailDoesNotExists(self, **kwargs):
        for email in mail.outbox:
            if self._is_email_matching_criteria(email, **kwargs):
                raise AssertionError('Email matching criteria was sent')


class _InstanceContext(object):
    """Context manager returned by assert_instance_created/deleted.
    """
    def __init__(self, enter_assertion, exit_assertion, model_class, **kwargs):
        self.enter_assertion = enter_assertion
        self.exit_assertion = exit_assertion
        self.model_class = model_class
        self.kwargs = kwargs

    def __enter__(self):
        self.enter_assertion(self.model_class, **self.kwargs)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit_assertion(self.model_class, **self.kwargs)
        return True


class InstanceAssertionsMixin(object):
    """ORM-related assertions for testing instance creation and deletion.
    """
    def assertInstanceExists(self, model_class, **kwargs):
        try:
            obj = model_class._default_manager.get(**kwargs)
            self.assertIsNotNone(obj)
        except model_class.DoesNotExist:
            raise AssertionError('No {0} found matching the criteria.'.format(
                model_class.__name__,
            ))

    def assertInstanceDoesNotExist(self, model_class, **kwargs):
        try:
            instance = model_class._default_manager.get(**kwargs)
            raise AssertionError('A {0} was found matching the criteria. ({1})'.format(
                model_class.__name__,
                instance,
            ))
        except model_class.DoesNotExist:
            pass

    def assertInstanceCreated(self, model_class, **kwargs):
        """
        Checks if a model instance was created in the database.

        For example::

        >>> with self.assert_instance_created(Article, slug='lorem-ipsum'):
        ...     Article.objects.create(slug='lorem-ipsum')
        """
        return _InstanceContext(
            self.assertInstanceDoesNotExist,
            self.assertInstanceExists,
            model_class,
            **kwargs
        )

    def assertInstanceDeleted(self, model_class, **kwargs):
        """
        Checks if the model instance was deleted from the database.

        For example::

        >>> with self.assert_instance_deleted(Article, slug='lorem-ipsum'):
        ...     Article.objects.get(slug='lorem-ipsum').delete()
        """
        return _InstanceContext(
            self.assertInstanceExists,
            self.assertInstanceDoesNotExist,
            model_class,
            **kwargs
        )

    def assertInstanceUpdated(self, instance, **kwargs):
        """
        Checks if the model instance has been updated.
        """
        instance.refresh_from_db()
        for name, attribute in instance.__dict__.items():
            if name in kwargs:
                msg = '%s does not equal %s' % (attribute, kwargs[name])
                if isinstance(attribute, (list, set,)):
                    self.assertEqual(set(attribute), set(kwargs[name]), msg)
                else:
                    self.assertEqual(attribute, kwargs[name], msg)

    def assertInstanceNotUpdated(self, instance, **kwargs):
        """
        Checks if the model instance has been updated.
        """
        instance.refresh_from_db()
        for name, attribute in instance.__dict__.items():
            if name in kwargs:
                msg = '%s equals %s' % (attribute, kwargs[name])
                if isinstance(attribute, (list, set,)):
                    self.assertNotEqual(set(attribute), set(kwargs[name]), msg)
                else:
                    self.assertNotEqual(attribute, kwargs[name], msg)
