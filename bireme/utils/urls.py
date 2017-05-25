from django.conf.urls import url
from views import *

urlpatterns = [
    url(r'^field_assist/(?P<field_name>\w+)/', field_assist, name='field_assist'),
]
