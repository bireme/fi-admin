from django.conf.urls import url

from views import * 

urlpatterns = [

    # Bibliographic References
    url(r'^/?$', BiblioRefListView.as_view(), name='list_biblioref'),
    url(r'^type/?$', SelectDocumentTypeView.as_view(), name='create_biblioref_step_1'),
    url(r'^new/?$', BiblioRefCreateView.as_view(), name='create_biblioref'),
    url(r'^edit/(?P<pk>\d+)/?$', BiblioRefUpdateView.as_view(), name='edit_biblioref'),
    url(r'^delete/(?P<pk>\d+)/?$', BiblioRefDeleteView.as_view(), name='delete_biblioref'),
    
    url(r'^field_assist/(?P<field_name>\w+)/', field_assist, name='field_assist'),

]

