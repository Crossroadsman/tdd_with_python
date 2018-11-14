from django.urls import re_path
from . import views

# Note that with our URLs we are using the following convention:
# - urls that modify the database ('action' urls): no trailing slash
# - urls that do not modify the DB: trailing slash
urlpatterns = [
    re_path(r'^new$', views.new_list, name='new_list'),
    re_path(r'^(\d+)/$', views.view_list, name='view_list'),
]
