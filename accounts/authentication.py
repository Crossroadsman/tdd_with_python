from accounts.models import ListUser, Token


# Note, the book's version of PasswordlessAuthenticationBackend explicitly
# inherits from `object`. However, it seems that there is no reason to do
# this in Python 3. See this detailed discussion:
# https://stackoverflow.com/a/45062077
class PasswordlessAuthenticationBackend:
    """An authentication backend is a class that implements two required
    methods (and optionally can implement certain other permission-related
    methods). These are:

    authenticate(request, **credentials) -> `user object` | None

    get_user(user_id) -> `user object`

    where:
    - `request` is an HttpRequest (which might be None),
    - `credentials` are whatever is being used to authenticate (e.g., a
      username and pasword, or a token, etc),
    - `user_id` is whatever type the primary_key of the user object is
    """

    def authenticate(self, request, uid):
        """This implementation of `authenticate` takes `uid` as the
        required credential. This represents a token (issued in the
        send_email process).

        If uid doesn't match a token, it returns None.

        If uid does match a token, it looks up the email address associated
        with that token and checks for a User with the same email address.

        If a matching user is found, it returns that user; if not found, it
        creates a new user, then returns that user.

        (Note: in the book, the authenticate method lacks a `request`
        parameter, even though this is required (even in Django 1.11,
        which the book is based on). Leaving off this method causes Django
        not to call this authenticate() method. We can isolate the point at
        which Django's behaviour diverges from expectations (at least as per
        the book) by loading a Django shell, then importing and calling
        `django.contrib.auth.authenticate`. This will trigger this method
        (which indicates that when the Django server is running it is
        looking at the parameter lists of the proposed
        AUTHENTICATION_BACKENDS and refusing to launch any that don't have
        valid signatures (i.e, including the request parameter)).
        It's not clear how the book was able to get the authentication to
        work in the absence of this parameter, but it definitely doesn't
        work without adding `request` in Django 2.1).
        """
        try:
            token = Token.objects.get(uid=uid)
        except Token.DoesNotExist:
            return None

        user, created = ListUser.objects.get_or_create(email=token.email)
        return user

    def get_user(self, email):
        """This takes an email (the PK of the user) and returns the
        corresponding user
        The section of the docs dealing with customising Auth doesn't
        mention how to handle the case where the provided argument doesn't
        match a pk. However, the `django.contrib.auth`  section of the docs
        suggests that it expects None from custom backends:
        https://docs.djangoproject.com/en/2.1/ref/contrib/auth/#django.contrib.auth.get_user
        """
        # Note that because get_user takes the object's pk (in this case
        # email) there can only ever be 1 or 0 matches. We can implement
        # a simple get or None behaviour by combining filter() on the pk
        # with first() (which returns None if no matches)
        return ListUser.objects.filter(email=email).first()

