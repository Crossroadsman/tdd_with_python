from django.urls import re_path
from django.contrib.auth.views import LogoutView

from . import views

# Note that with our URLs we are using the following convention:
# - urls that modify the database ('action' urls): no trailing slash
# - urls that do not modify the DB: trailing slash
urlpatterns = [
    re_path(r'^send_login_email',
        views.send_login_email,
        name='send_login_email'),
    re_path(r'^login$', views.login, name='login'),
    # note that with class-based views we pass arguments that we want
    # to go to the view into the as_view() method. Cf function views
    # where we pass a dictionary of the form {'next_page': '/'} as
    # the third argument to re_path (i.e., between the reference to the
    # view and the name= kwarg.
    re_path(r'^logout$', LogoutView.as_view(next_page='/'), name='logout'),
]
