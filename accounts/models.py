import uuid

from django.db import models


class User(models.Model):
    email = models.EmailField(primary_key=True)

    """
    for a class to be a valid custom User class it must implement the
    following:

    attributes
    ----------
    - REQUIRED_FIELDS : a list of the field names that will be prompted
        for when creating a user via the `createsuperuser` command. It has
        has no effect in other parts of Django.
        It must include every field in the model where `blank` is False.
        It may include any fields you want to be prompted for when a user
        is created with `createsuperuser`.
        It should not include `USERNAME_FIELD` or `password` as these will
        always be prompted for.
    - USERNAME_FIELD : a string describing the name of the field that is
        used as the unique identifier. This field _must_ be unique (have
        `unique=True` in its definition) unless the custom auth backend
        supports non-unique usernames.
    - is_anonymous : boolean. A read-only attribute that is always set to
        False (cf `AnonymousUser.is_anonymous` which is always True)
    - is_authenticated : boolean. A read-only attribute that is always set
        to True (cf `AnonymousUser.is_authenticated` which is always False).
        This is a way to tell if the user has been authenticated but does
        not imply any permissions nor check if the user is active or has a
        valid session. This is the preferred attribute for distinguishing
        between Users and AnonymousUsers.
    """
    REQUIRED_FIELDS = [] # this is empty because our only required field is
                         # email which is one of the always-prompted fields
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = True


class Token(models.Model):
    email = models.EmailField()
    """
    uuid4 generates RFC 4122 v4 UUIDs. These are guaranteed to be unique.
    str(uuid) returns a 36 character (32 data characters and 4 separators)
    string of the form:
    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (8-4-4-4-12) where each x
    represents a hexadecimal digit
    """
    uid = models.CharField(default=uuid.uuid4,
                           max_length=40)

