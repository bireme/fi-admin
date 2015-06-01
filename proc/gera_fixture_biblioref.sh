
# converte para formato JSON intermediário
mx LILACS pft=@fixture_biblioref.pft  lw=8000 from=733515 count=10 now > lilacs_tmp1.json

# aplica sed para ajustar JSON final
iconv -f iso-8859-1 -t utf-8 lilacs_tmp1.json > lilacs_tmp2.json

sed 's@\([\^]\([[:alnum:]]\)\)@\\"_\2\\": \\"@g ; s@\([^{]\)\\"_@\1\\", \\"_@g' lilacs_tmp2.json > lilacs_tmp3.json
# 1o substitui ^ + id do subcampo POR \"_ + id do subcampo + \": \"
# 2o substitui \"_ POR \", \"_  --- resolve os subcampos no meio do campo



# adiciona [ no começo e ] no final do arquivo
sed -e "1s/^/[\n / ; \$a]" lilacs_tmp3.json > lilacs.json

# convert all files to utf8
#iconv -f iso-8859-1 -t utf-8 lilacs_iso.json > lilacs.json


rm *_tmp?.json
