
# converte para formato JSON intermediário
mx LILACS pft=@fixture_biblioref.pft  lw=8000 from=733515 count=10 now > lilacs_tmp.json

# aplica sed para ajustar JSON final

sed 's@\([\^]\([[:alnum:]]\)\)@\\"_\2\\": \\"@g ; s@\([^{]\)\\"_@\1\\", \\"_@g' lilacs_tmp.json > lilacs_tmp2.json
# 1o substitui ^ + id do subcampo POR \"_ + id do subcampo + \": \"
# 2o substitui \"_ POR \", \"_  --- resolve os subcampos no meio do campo



# adiciona [ no começo e ] no final do arquivo
sed -e "1s/^/[\n / ; \$a]" lilacs_tmp2.json > lilacs_iso.json

# convert all files to utf8
iconv -f iso-8859-1 -t utf-8 lilacs_iso.json > lilacs.json


rm *_tmp.json
