
# config fixtures
mx config from=1 count=1 pft=@fixture_thematic_area.pft -all now > thematic_area_iso.json
mx config from=2 count=1 pft=@fixture_source_language.pft -all now > source_language_iso.json
mx config from=3 count=1 pft=@fixture_source_type.pft -all now > source_type_iso.json

# gizmo for source language
mx config from=2 count=1 "pft=(if p(v317) then v317^c,'|',f(iocc,1,0) fi/)" now > g_source_language.seq
mx seq=g_source_language.seq create=g_source_language -all now

# gizmo for source type
mx config from=3 count=1 "pft=(if p(v318) then v318^e,'|',f(iocc,1,0) fi/)" now > g_source_type.seq
mx seq=g_source_type.seq create=g_source_type -all now


# convert to utf8

iconv -f iso-8859-1 -t utf-8 thematic_area_iso.json > thematic_area.json

iconv -f iso-8859-1 -t utf-8 source_language_iso.json > source_language.json

iconv -f iso-8859-1 -t utf-8 source_type_iso.json > source_type.json

rm *_iso.json
rm *.seq
