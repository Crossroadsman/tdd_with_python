from django.conf import settings
from django.contrib.auth import (BACKEND_SESSION_KEY,
                                 SESSION_KEY,
                                 get_user_model)
User = get_user_model()
from django.contrib.sessions.backends.db import SessionStore
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    # for more discussion of BaseCommand and more examples, see:
    # https://django.readthedocs.io/en/2.1.x/howto/custom-management-commands.html
    def add_arguments(self, parser):
        parser.add_argument('email')

    def handle(self, *args, **options):
        session_key = create_pre_authenticated_session(options['email'])
        self.stdout.write(session_key)


def create_pre_authenticated_session(email):

    # first, create a user
    user = User.objects.create(email=email)

    # second, create a session object in the database (by default, Django
    # stores its sessions in the DB). The session's SESSION_KEY is the
    # user object's pk (in this case email).
    # The session also stores information to lookup which authentication
    # backend was used to authenticate the user. Hence the 
    # BACKEND_SESSION_KEY
    # (Note, if this function stops working and needs a hash session key,
    # check the following gist:
    # https://gist.github.com/dbrgn/bae5329e17d2801a041e
    # )
    session = SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    return session.session_key

