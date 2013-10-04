
mx config from=1 count=1 pft=@fixture_thematic_area.pft -all now > thematic_area_iso.json

mx config from=2 count=1 pft=@fixture_source_language.pft -all now > source_language_iso.json

mx config from=3 count=1 pft=@fixture_source_type.pft -all now > source_type_iso.json

# convert to utf8

iconv -f iso-8859-1 -t utf-8 thematic_area_iso.json > thematic_area.json

iconv -f iso-8859-1 -t utf-8 source_language_iso.json > source_language.json

iconv -f iso-8859-1 -t utf-8 source_type_iso.json > source_type.json

rm *_iso.json
