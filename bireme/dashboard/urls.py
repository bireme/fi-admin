from django.conf.urls import url
from views import *

urlpatterns = [
    # Dashboard widgets
    url(r'^last_actions/$', last_actions, name='last_actions'),
    url(r'^changed_by_other_user/$', changed_by_other_user, name='changed_by_other_user'),
    url(r'^changed_by_other_cc/$', changed_by_other_cc, name='changed_by_other_cc'),

]
