from django.conf.urls import url
from views import *

urlpatterns = [
    # Dashboard widgets
    url(r'^last_actions/$', last_actions, name='last_actions'),
    url(r'^changed_by_others/(?P<review_type>\w{0,15})/$', changed_by_others, name='changed_by_others'),

]
