from django.urls import path, re_path, include
from django.views.generic import TemplateView
from django.conf import settings

from api.resources_api import LinkResource
from api.events_api import EventResource
from api.multimedia_api import MediaResource
from api.title_api import TitleResource, IssueResource
from api.bibliographic import ReferenceResource
from api.legislation import LeisrefResource
from api.oer_api import OERResource
from api.classification_api import *
from api.thesaurus_api_desc import *
from api.thesaurus_api_qualif import *
from api.thesaurus_api import *
from api.thesaurus_solr_api import *
from api.institution_api import *


link_resource = LinkResource()
event_resource = EventResource()
media_resource = MediaResource()
title_resource = TitleResource()
issue_resource = IssueResource()
reference_resource = ReferenceResource()
leisref_resource = LeisrefResource()
oer_resource = OERResource()
collection_resource = CollectionResource()
classification_resource = ClassificationResource()
community_resource = CommunityResource()
institution_resource = InstitutionResource()


# used to render records in ID format
thesaurus_resource_desc = ThesaurusResourceDesc()
thesaurus_resource_qualif = ThesaurusResourceQualif()

# used to render records in JSON format
thesaurus_resource_desc_API = ThesaurusAPIDescResource()
thesaurus_resource_qualif_API = ThesaurusAPIQualifResource()

# used to render records in JSON format for solr index
thesaurus_resource_desc_index_API = ThesaurusAPIDescResourceIndex()
thesaurus_resource_qualif_index_API = ThesaurusAPIQualifResourceIndex()

urlpatterns = [
    # API's
    re_path(r'^$', TemplateView.as_view(template_name="api_doc.html")),
    path('', include(link_resource.urls)),
    path('', include(event_resource.urls)),
    path('', include(media_resource.urls)),
    path('', include(title_resource.urls)),
    path('', include(issue_resource.urls)),
    path('', include(reference_resource.urls)),
    path('', include(leisref_resource.urls)),
    path('', include(oer_resource.urls)),
    path('', include(community_resource.urls)),
    path('', include(collection_resource.urls)),
    path('', include(classification_resource.urls)),
    path('', include(institution_resource.urls)),

    #re_path(r'^api/lis-old/search/', api.lis_old_api.search),
    #re_path(r'^api/users/get_user_id/(?P<username>[a-zA-z0-9\.\-]{0,30})/$', 'api.users.get_user_id'),
    #re_path(r'^api/thematic/get_thematic_id/(?P<thematic_acronym>[a-zA-z0-9\.\-]{0,40})/$', 'api.thematic.get_thematic_id'),

    # used to render records in ID format
    re_path(r'^descriptors/', include(thesaurus_resource_desc.urls)),
    re_path(r'^qualifiers/', include(thesaurus_resource_qualif.urls)),

    # used to render records in JSON format
    re_path(r'^desc/', include(thesaurus_resource_desc_API.urls)),
    re_path(r'^qualif/', include(thesaurus_resource_qualif_API.urls)),

    # used to render records in JSON format for solr index
    re_path(r'^desc/index/', include(thesaurus_resource_desc_index_API.urls)),
    re_path(r'^qualif/index/', include(thesaurus_resource_qualif_index_API.urls)),
]
