# set environment variables
export PK_INCREASE_NUMBER=''
export FI_USER_ID=''
export CC_CODE=''
export FI_CONTENT_TYPE_ID=''
export FI_THEMATIC_AREA_ID=''

mxcp online create=online_clean clean repeat=% period=. tell=1

mx online_clean pft=@fixture_events.pft gizmo=gizmo_fixture gizmo=g_invalid_date,507,509 gizmo=g_countries,740 gizmo=g_event_language,503 giz
mo=g_event_type,513 lw=8000 now > events_iso.json

./mx1660 online_clean gizmo=gizmo_fixture pft=@fixture_event_descriptors.pft lw=8000 now > event_descriptors_iso.json
./mx1660 online_clean gizmo=gizmo_fixture pft=@fixture_event_keywords.pft lw=8000 now > event_keywords_iso.json
./mx1660 online_clean gizmo=gizmo_fixture pft=@fixture_event_thematic_area.pft lw=8000 now > event_thematic_area_iso.json

for file in events event_descriptors event_keywords event_thematic_area;
do
      echo $file ...
      # clean control characters
      sed -i 's/\x93/\\"/g ; s/\x94/\\"/g ; s/\x91/`/g ; s/\x92/`/g ; s/\x99//g ; s/\x96/-/g ; s/\x97/-/g; ; s/\x8b/</g' ${file}_iso.json

      # convert to utf8
      iconv -f iso-8859-1 -t utf-8 -c ${file}_iso.json > ${file}_utf8.json

      # fix last 2 lines of file to valid JSON
      head -n -2 ${file}_utf8.json > ${file}.json
      echo -e "\n}\n]" >> ${file}.json

done

# validate json files

jsonlint -v events.json
jsonlint -v event_descriptors.json
jsonlint -v event_keywords.json
jsonlint -v event_thematic_area.json

rm *_iso.json
rm *_utf8.json
rm *_clean.*
