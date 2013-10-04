
mx lis pft=@fixture_resources.pft gizmo=gizmo_fixture lw=8000 from=1 count=50 now > sample_resources_iso.json

mx lis pft=@fixture_descriptors.pft gizmo=gizmo_fixture lw=8000 from=1 count=50 now > sample_descriptors_iso.json

mx lis pft=@fixture_keywords.pft gizmo=gizmo_fixture lw=8000 from=1 count=50 now > sample_keywords_iso.json

# convert to utf8

iconv -f iso-8859-1 -t utf-8 sample_resources_iso.json > sample_resources.json
iconv -f iso-8859-1 -t utf-8 sample_descriptors_iso.json > sample_descriptors.json
iconv -f iso-8859-1 -t utf-8 sample_keywords_iso.json > sample_keywords.json

rm *_iso.json
