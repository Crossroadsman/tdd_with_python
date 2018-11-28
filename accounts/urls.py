from django.urls import re_path
from . import views

# Note that with our URLs we are using the following convention:
# - urls that modify the database ('action' urls): no trailing slash
# - urls that do not modify the DB: trailing slash
urlpatterns = [
    re_path(r'^send_login_email',
        views.send_login_email,
        name='send_login_email'),
    re_path(r'^login$',
        views.login,
        name='login'),
]
