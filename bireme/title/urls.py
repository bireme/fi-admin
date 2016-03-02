from django.conf.urls import url

from views import *

urlpatterns = [

    # Title
    url(r'^/?$', TitleListView.as_view(), name='list_title'),
    url(r'^new/?$', TitleCreateView.as_view(), name='create_title'),
    url(r'^edit/(?P<pk>\d+)/?$', TitleUpdateView.as_view(), name='edit_title'),
    url(r'^delete/(?P<pk>\d+)/?$', TitleDeleteView.as_view(), name='delete_title'),
    url(r'^preview/(?P<pk>\d+)/?$', TitlePreview.as_view(), name='preview_title'),

    # Issue
    #url(r'^issues/?$', IssueListView.as_view(), name='list_issue'),
    #url(r'^issues/new/?$', IssueCreateView.as_view(), name='create_issue'),
    #url(r'^issues/edit/(?P<pk>\d+)/?$', IssueUpdateView.as_view(), name='edit_issue'),
    #url(r'^issues/delete/(?P<pk>\d+)/?$', IssueDeleteView.as_view(), name='delete_issue'),

]
