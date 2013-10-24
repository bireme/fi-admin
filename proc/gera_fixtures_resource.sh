
mx lis pft=@fixture_resources.pft gizmo=gansna,318 gizmo=gizmo_fixture gizmo=g_source_language,317 gizmo=g_source_type,318  lw=8000 from=1 count=50 now > sample_resources_iso.json

mx1660 lis pft=@fixture_descriptors.pft gizmo=gizmo_fixture lw=8000 from=1 count=50 now > sample_descriptors_iso.json

mx lis pft=@fixture_keywords.pft gizmo=gizmo_fixture lw=8000 from=1 count=50 now > sample_keywords_iso.json

mx lis pft=@fixture_resource_thematic.pft gizmo=gizmo_fixture gizmo=g_thematic_area,302 lw=8000 from=1 count=50 now > sample_resource_thematic_iso.json

# convert to utf8

iconv -f iso-8859-1 -t utf-8 sample_resources_iso.json > sample_resources.json
iconv -f iso-8859-1 -t utf-8 sample_descriptors_iso.json > sample_descriptors.json
iconv -f iso-8859-1 -t utf-8 sample_keywords_iso.json > sample_keywords.json
iconv -f iso-8859-1 -t utf-8 sample_resource_thematic_iso.json > sample_resource_thematic.json

rm *_iso.json
