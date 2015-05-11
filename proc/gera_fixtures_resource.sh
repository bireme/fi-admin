# set environment variables
export PK_INCREASE_NUMBER='99999'
export FI_USER_ID='1'            # admin
export CC_CODE='BRXX'
export FI_CONTENT_TYPE_ID='15'   # Resource (prod)
export FI_THEMATIC_AREA_ID='99'  # thematic-area

rm lis_process.*
rm lis_clean.*

mxcp lis create=lis_clean clean
retag lis_clean unlock

mx lis_clean "proc=if v399 <> '1' then 'd*d.' fi" append=lis_process -all now tell=100

mxcp lis_process create=lis_clean clean

mx lis_clean pft=@fixture_resources.pft gizmo=gansna,318 gizmo=gizmo_fixture gizmo=g_record_source,305 gizmo=g_originator_location,314 gizmo=countries,314  gizmo=g_source_language,317 gizmo=g_source_type,318  lw=8000 now > resources_iso.json

mx1660 lis_clean pft=@fixture_descriptors.pft gizmo=gizmo_fixture lw=8000 now > descriptors_iso.json

mx lis_clean pft=@fixture_keywords.pft gizmo=gizmo_fixture lw=8000 now > keywords_iso.json

mx1660 lis_clean pft=@fixture_resource_thematic.pft gizmo=gizmo_fixture gizmo=g_thematic_area,302 lw=8000 now > resource_thematic_iso.json

sed 's@, \]@\]@g' resources_iso.json > resources_iso_ok.json
mv resources_iso_ok.json resources_iso.json

# convert to utf8

iconv -f iso-8859-1 -t utf-8 resources_iso.json > resources.json
iconv -f iso-8859-1 -t utf-8 descriptors_iso.json > descriptors.json
iconv -f iso-8859-1 -t utf-8 keywords_iso.json > keywords.json
iconv -f iso-8859-1 -t utf-8 resource_thematic_iso.json > resource_thematic.json

rm *_iso*.json
