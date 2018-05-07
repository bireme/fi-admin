# set environment variables
export PK_INCREASE_NUMBER=''
export FI_USER_ID='2'

mxcp nmail create=nmail_clean clean repeat=% period=. tell=100

mx nmail_clean pft=@fixture_nmail.pft gizmo=gizmo_fixture gizmo=g_countries,620 lw=8000 now > institution_iso.json

mx nmail_clean pft=@unit_seq.pft gizmo=gizmo_fixture gizmo=g_countries,620 lw=8000 now > unit_list.seq

mx seq=unit_list.seq create=unit_list -all now

mx unit_list pft=@fixture_units.pft lw=8000 now > units_iso.json

# remove initial blank lines of notes field
sed -e 's/"\\r\\n\\r\\n/"/' institution_iso.json > institution_iso_fix1.json

# convert to utf8
iconv -f iso-8859-1 -t utf-8 -c institution_iso_fix1.json > institution_utf8.json
iconv -f iso-8859-1 -t utf-8 -c units_iso.json > units_utf8.json

# fix last 2 lines of file to valid JSON
head -n -2 institution_utf8.json > institution.json
echo -e "\n}\n]" >> institution.json

head -n -2 units_utf8.json > units.json
echo -e "\n}\n]" >> units.json


# validate json file
jsonlint -v institution.json
jsonlint -v units.json

rm *_iso*.json
rm *_clean.*
