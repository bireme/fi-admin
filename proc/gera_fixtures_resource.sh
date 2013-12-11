
mxcp lis create=lis_clean clean

mx lis_clean pft=@fixture_resources.pft gizmo=gansna,318 gizmo=gizmo_fixture gizmo=g_source_language,317 gizmo=g_source_type,318  lw=8000 now > resources_iso.json

mx1660 lis_clean pft=@fixture_descriptors.pft gizmo=gizmo_fixture lw=8000 now > descriptors_iso.json

mx lis_clean pft=@fixture_keywords.pft gizmo=gizmo_fixture lw=8000 now > keywords_iso.json

mx1660 lis_clean pft=@fixture_resource_thematic.pft gizmo=gizmo_fixture gizmo=g_thematic_area,302 lw=8000 now > resource_thematic_iso.json

# convert to utf8

iconv -f iso-8859-1 -t utf-8 resources_iso.json > resources.json
iconv -f iso-8859-1 -t utf-8 descriptors_iso.json > descriptors.json
iconv -f iso-8859-1 -t utf-8 keywords_iso.json > keywords.json
iconv -f iso-8859-1 -t utf-8 resource_thematic_iso.json > resource_thematic.json

rm *_iso.json
