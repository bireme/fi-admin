#!/bin/bash
# -------------------------------------------------------------------------- #
# ComparaIds.sh - Realiza a comparacao entre arquivos ID
# -------------------------------------------------------------------------- #
#    Corrente : ~/proc/compare/wrk
#     Chamada : ./ComparaIds.sh <arquivo1> <arquivo2>
#     Exemplo : ./ComparaIds.sh arquivo_origem.id arquivo_de_comparacao.id
#    Objetivo : Realizar comparacao entre o arquivo ID que sera insumo da
#               importacao no sistema Fi-Admim, e o arquivo criado a partir do
#               processo de exportacao do sistema Fi-Admin.
# Observacao 1: <arquivo1> é o arquivo original, ou seja, nesse processo
#               de importação para o FI-Admin esse <arquivo1> é uma arquivo texto ID
#               resultante da exportação de registro de uma base isis
#               <arquivo2> é o arquivo criado a partir da exportação no sistema FI-Admin,
#               ou seja é o registro que foi importado no FI-Admin.
#
# Observacao 2: A disposicao para funcionamento devera ser a mostrada abaixo,
#               ids - deretorio onde estarao os arquivos Id
#               tpl - diretorio onde esta o shell script ComparaIds.sh
#               wrk - diretorio onde se fara o trabalho de comparacao
#
#               compare
#               +-- ids
#               +-- tpl
#               ¦   +-- ComparaIds.sh
#               +-- wrk
#
# Observacao 3: Eh utilizado sed nesse processo. Em alguns casos existe
#               a utilizacao de ^B, para utilizar ^B deve-se digitar Ctrl+v e Ctrl+b
#
# -------------------------------------------------------------------------- #
#  Centro Latino-Americano e do Caribe de Informação em Ciências da Saúde
#     é um centro especialidado da Organização Pan-Americana da Saúde,
#           escritório regional da Organização Mundial da Saúde
#                      BIREME / OPS / OMS (P)2016
# -------------------------------------------------------------------------- #
#
# Historico
# versao data, Responsavel
#       - Descricao
cat > /dev/null <<HISTORICO
vrs:  1.00 20160715, Fabio Luis de Brito
        - Edicao original
HISTORICO

# -------------------------------------------------------------------------- #

# Verifica passagem de parametro
if [ "$#" != "2" ]
then
  echo "ERRO: Informar nome dos arquivos para comparacao"
  echo "      Use: ./ComparaIds.sh <arquivo1> <arquivo2>"
  echo "      Ex.: ./ComparaIds.sh arquivo_origem.id arquivo_de_comparacao.id"
  exit 1
fi

# -------------------------------------------------------------------------- #
# Variaveis iniciais
ARQ1=$1
ARQ2=$2
RAIZ='/bases/fiadmin/migration/lilacs/compare'
DIR_ID=`echo "$RAIZ/ids"`
DIR_WRK=`echo "$RAIZ/wrk"`

# -------------------------------------------------------------------------- #

# Verifica se existem diretorios para processamento
if [ ! -d $DIR_ID ]; then echo "ERRO! Diretorio $DIR_ID nao existe!"; exit 1; fi
if [ ! -d $DIR_WRK ]; then echo "ERRO! Diretorio $DIR_WRK nao existe!"; exit 1; fi

# Verifica a existencia dos arquivos informados
if [ ! -f $DIR_ID/$ARQ1 ]; then echo "ERRO! Arquivo $DIR_ID/$ARQ1 inexistente!"; exit 1; fi
if [ ! -f $DIR_ID/$ARQ2 ]; then echo "ERRO! Arquivo $DIR_ID/$ARQ2 inexistente!"; exit 1; fi
if [ $DIR_ID/$ARQ1 == $DIR_ID/$ARQ2 ]; then echo "ERRO! Arquivos informados sao o mesmo!"; exit 1; fi

# Acessa area de trabalho
cd $DIR_WRK

clear
rm *.*

echo "#############################################################################################"
echo "                                  COMPARA ARQUIVOS ID"
echo "#############################################################################################"


# Avalia se quantidade de registros eh igual nos arquivos
qtd_arq1=`grep "!ID " $DIR_ID/$ARQ1 | wc -l`
qtd_arq2=`grep "!ID " $DIR_ID/$ARQ2 | wc -l`
if [ $qtd_arq1 -ne $qtd_arq2 ]
then
  echo "ATENCAO! quantidade de registros entre os arquivos $ARQ1 e $ARQ2 nao sao iguais"
  exit 1
fi

# Avalia se sera necessario particionar arquivos
echo
echo "# Arquivo ORIGEM"
if [ $qtd_arq1 -gt 1 ]
then
  echo "--> Particiona arquivos ..."
  echo "    + Arquivo $ARQ1 com $qtd_arq1 registros."
  # copia $ARQ1 para $DIR_WRK
  cp $DIR_ID/$ARQ1 .

  # Coloca tudo em uma so linha por registro
  cat $ARQ1 | tr -d "\012" | sed 's/!ID /!ID /g' | tr "" "\012" > tmp1
  # retirando primeira linha em branco
  sed '1d' tmp1 > tmp2

  # adicionando linha em branco no final
  echo "" > tmp3
  cat tmp2 tmp3 > tmp4

  # Quebra em arquivos
  count=1
  while read line
  do
    echo "$line" > arq1_$count.txt
    count=`expr $count + 1`
  done < tmp4

  [ -f tmp1 ] && rm tmp?

  # coloca os arquivos no formato de cada tag por linha
  for file in $(ls arq1*.txt)
  do
    cat $file | sed 's/!v/!v/g' | tr "" "\012" > wrk1
    mv wrk1 $file
  done

  # renomeia o arquivo com o conteudo do campo v2
  for file in $(ls arq1*.txt)
  do
    # traz o conteudo da tag v2 e garante que nao haverao espacos a direita
    v2=`grep v002 $file | awk -F"\!" '{ print $3 }' | sed 's/ *$//g'`
    mv $file $v2.arq1
  done

else
  echo "--> Arquivo $ARQ1 com apenas 1 registro ..."
  cp $DIR_ID/$ARQ1 .
fi

echo
echo "# Arquivo FI-Admin"
if [ $qtd_arq2 -gt 1 ]
then
  echo "--> Particiona arquivos ..."
  echo "    + Arquivo $ARQ2 com $qtd_arq2 registros."
  # copia $ARQ1 para $DIR_WRK
  cp $DIR_ID/$ARQ2 .

  # apaga eventual linhas em branco no arquivo
  cat $ARQ2 | sed '/^$/d' > tmp1
  mv tmp1 $ARQ2

  # Coloca tudo em uma so linha por registro
  cat $ARQ2 | tr -d "\012" | sed 's/!ID /!ID /g' | tr "" "\012" > tmp1
  # retirando primeira linha em branco
  sed '1d' tmp1 > tmp2

  # adicionando linha em branco no final
  echo "" > tmp3
  cat tmp2 tmp3 > tmp4

  # Quebra em arquivos
  count=1
  while read line
  do
    echo "$line" > arq2_$count.txt
    count=`expr $count + 1`
  done < tmp4

  [ -f tmp1 ] && rm tmp?

  # coloca os arquivos no formato de cada tag por linha
  for file in $(ls arq2*.txt)
  do
    cat $file | sed 's/!v/!v/g' | tr "" "\012" > wrk1
    mv wrk1 $file
  done

  # renomeia o arquivo com o conteudo do campo v778
  for file in $(ls arq2*.txt)
  do
    # traz o conteudo da tag v778 e garante que nao haverao espacos a direita
    v778=`grep v778 $file | awk -F"\!" '{ print $3 }' | sed 's/ *$//g'`
    mv $file $v778.arq2
  done

else
  echo "--> Arquivo $ARQ2 com apenas 1 registro ..."
  cp $DIR_ID/$ARQ2 .
fi

echo
echo "# Verifica se para cada arquivo de ORIGEM existe um igual criado pelo FI-Admin ..."
if [ $qtd_arq1 -gt 1 -a $qtd_arq2 -gt 1 ]
then
  # cria lista de arq1
  ls *.arq1 | awk -F"." '{ print $1 }' > tmp1
  #
  ls *.arq2 | awk -F"." '{ print $1 }' > tmp2
  diff tmp1 tmp2 > /dev/null
  if [ $? == 0 ]
  then
    echo "    + Ok arquivos para comparacao sao parelhos."
  else
    clear
    echo "ERRO! Arquivos para comparacao tem registro diferente."
    diff tmp1 tmp2  
    echo "Arquivos ORIGEM"
    ls *.arq1

    echo "Arquivos FI-Admin"
    ls *.arq2

    [ -f tmp1 ] && rm tmp1
    [ -f tmp2 ] && rm tmp2

    exit 1
  fi
else
  echo "      + OK. Apenas 2 arquivos para comparacao ..."

  # Provendo arquivo ORIGEM no formato para comparacao
  v2=`grep v002 $ARQ1 | awk -F"\!" '{ print $3 }' | sed 's/ *$//g'`
  mv $ARQ1 $v2.arq1

  # Provendo arquivo Fi-Admin no formato para comparacao
  v778=`grep v778 $ARQ2 | awk -F"\!" '{ print $3 }' | sed 's/ *$//g'`
  mv $ARQ2 $v778.arq2

  # Compara se sao mesmo registro
  arq1=`ls *.arq1 | awk -F"." '{ print $1 }'`
  arq2=`ls *.arq2 | awk -F"." '{ print $1 }'`
  if [ $arq1 -ne $arq2 ]
  then
    clear
    echo "ERRO! Arquivos para comparacao tem registro diferente."
    echo "Ver: $arq1.arq1 e $arq2.arq2"
    unset arq1 arq2
    echo
    exit 1
  fi


fi


echo
echo "#############################################################################################"
echo "                             INICIANDO COMPARACAO DE CONTEUDO"

for file in $(ls *.arq1 | awk -F"." '{ print $1 }')
do

# Faz correcao nos arquivos tentando deixar conteudo mais adequado para comparacao
# Apaga campos que nao serao necessario a comparacao
# grep -Ev '!(ID |v002|v091|v092|v093|v776|v778|v899)'
# Apaga espacos em branco no final da linha
# sed 's/ *$//g'
# Apaga linha em branco
# sed '/^$/d'
# Retira acentuacao
# sed 'y/áÁàÀãÃâÂéÉêÊíÍóÓõÕôÔúÚçÇ/aAaAaAaAeEeEiIoOoOoOuUcC/'
# Faz sort no final

echo "#############################################################################################"


ARQ1="$file.arq1"
ARQ2="$file.arq2"


# ARQ1
cat ${ARQ1} | grep -Ev '!(ID |v002|v091|v092|v093|v776|v778|v899)' | sed 's/ *$//g' | sed '/^$/d' | sed 'y/áÁàÀãÃâÂéÉêÊíÍóÓõÕôÔúÚçÇ/aAaAaAaAeEeEiIoOoOoOuUcC/' | sort > tmp_ARQ1.lst
# ARQ2
cat ${ARQ2} | grep -Ev '!(ID |v002|v091|v092|v093|v776|v778|v899)' | sed 's/ *$//g' | sed '/^$/d' | sed 'y/áÁàÀãÃâÂéÉêÊíÍóÓõÕôÔúÚçÇ/aAaAaAaAeEeEiIoOoOoOuUcC/' | sort > tmp_ARQ2.lst

tmpARQ1="tmp_ARQ1.lst"
tmpARQ2="tmp_ARQ2.lst"

echo
echo "--> Realiza a comparacao entre arquivos ${ARQ1}(Origem) e ${ARQ2}(FI-Admin) ..."

existDiff=`diff ${tmpARQ1} ${tmpARQ2} | grep ^\< | wc -l`
if [ $existDiff -gt 0 ]
then 
  echo
  echo "+ Linhas que existem em ${ARQ1} mas nao existem em ${ARQ2} ..."
  diff ${tmpARQ1} ${tmpARQ2} | grep ^\<
  ok1="false"
else
  ok1="true"
fi

existDiff=`diff ${tmpARQ1} ${tmpARQ2} | grep ^\> | wc -l`
if [ $existDiff -gt 0 ] 
then 
  echo
  echo "+ Linhas que existem em ${ARQ2} mas nao existem em ${ARQ1} ..."
  diff ${tmpARQ1} ${tmpARQ2} | grep ^\>
  ok2="false"
else
  ok2="true"
fi

if [ $ok1 = 'true' ] && [ $ok2 = 'true' ]
then
  echo "  OK! Parece bom."
fi

# Limpa area de trabalho - locais
[ -f ${tmpARQ1} ] && rm ${tmpARQ1}
[ -f ${tmpARQ2} ] && rm ${tmpARQ2}

unset ARQ1 ARQ2
unset lARQ1 lARQ2
unset existDiff
unset ok1 ok2

done


# Limpa area de trabalho - globais
[ -f tmp1 ] && rm tmp1
[ -f tmp2 ] && rm tmp2


echo
echo "Fim."
