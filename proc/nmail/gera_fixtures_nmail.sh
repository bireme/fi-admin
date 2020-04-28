# set environment variables
export PK_INCREASE_NUMBER=''
export FI_USER_ID='2'
export TABS='/usr/local/bireme/tabs'

rsync -rav transfer@quartzo2:/home/intranet/bases/nmail/nmail.mst .
rsync -rav transfer@quartzo2:/home/intranet/bases/nmail/nmail.xrf .
#rsync -rav transfer@quartzo2:/home/intranet/bases/nmail/nmail.fst .

mxcp nmail create=nmail_clean clean repeat=% period=. tell=100

# normaliza campos 603 e 604 para maiusculo sem acento
mx nmail_clean "gizmo=$TABS/gansna,603,604" "proc=(if p(v603) then '<1603 0>',mpu,v603,mpl'</1603>' fi)" "proc=(if p(v604) then '<1604 0>'mpu,v604,mpl'</1604>' fi)" "proc='d603d604'" create=nmail_norm -all now

# retag 1603, 1604 --> 603, 604
echo "1603 603" > retags.tab
echo "1604 604" >> retags.tab
retag nmail_norm retags.tab

# gera tabelas auxiliares de controle a partir de CSV 
mx seq=nmail_cat_list.csv create=nmail_cat_list -all now
mx nmail_cat_list fst="1 0 if p(v2) then v1/ fi" fullinv=nmail_cat_list -all now

mx seq=nmail_user_list.csv create=nmail_user_list -all now  
mx nmail_user_list fst="1 0 if p(v2) then v1/ fi" fullinv=nmail_user_list -all now


# convert base para fixture json
mx nmail_norm pft=@fixture_nmail.pft gizmo=gizmo_fixture gizmo=g_countries,620 lw=8000 now > institution_iso.json

mx nmail_norm pft=@unit_seq.pft gizmo=gizmo_fixture gizmo=g_countries,620 lw=8000 now > unit_list.seq

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

#rm *_iso.json
rm *_clean.*
