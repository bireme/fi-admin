#!/bin/bash
# -------------------------------------------------------------------------- #
# import2FIAdmin_LIST.sh
# -------------------------------------------------------------------------- #
#    Corrente :
#     Chamada :
#     Exemplo :
#
# -------------------------------------------------------------------------- #
#  Centro Latino-Americano e do Caribe de Informação em Ciências da Saúde
#     é um centro especialidado da Organização Pan-Americana da Saúde,
#           escritório regional da Organização Mundial da Saúde
#                      BIREME / OPS / OMS (P)2016
# -------------------------------------------------------------------------- #

# Historico
# versao data, Responsavel
#       - Descricao
cat > /dev/null <<HISTORICO
vrs:  1.00 20160815, Ana Katia Camilo
                     Fabio Luis de Brito
        - Edicao original
HISTORICO

# -------------------------------------------------------------------------- #

INSUMO="import"
echo
echo "ATENCAO! Esse processo fara a inclusao de conteudo no FI-Admin"
echo "Esta lendo o insumo de fixtures/$INSUMO/"
echo
echo "Se houver duvida digite CTRL+c, ou Enter para continuar."
# read #pausa até que o ENTER seja pressionado

# read -p "Este procedimento irá IMPORTAR os dados. Confirma (S/N)? " -n 1 -r


# -------------------------------------------------------------------------- #

# Anota hora de inicio de processamento
export HORA_INICIO=`date '+ %s'`
export HI="`date '+%Y.%m.%d %H:%M:%S'`"

echo "[TIME-STAMP] `date '+%Y.%m.%d %H:%M:%S'` [:INI:] Processa ${0} ${1} ${3} ${4} ${5}"
echo ""
# ------------------------------------------------------------------------- #

INSUMO="import"

# Acessando diretorio dos arquivos json
cd fixtures/$INSUMO

# criando lista de diretorios
ls -l | grep "^d" | awk {' print $9 '} > json_dir.lst

for json_dir in $(cat json_dir.lst)
do

  # Acessa diretorio do range de jsons
  cd $json_dir
  echo "#------------------------------------------------#"
  echo " --> Realizando leitura do diretorio $json_dir ..."

  # cria lista de jsons
  ls slice*json > json_list.lst
  numero_arquivos=`cat json_list.lst | wc -l`

  contador=1
  for json_arq in $(cat json_list.lst)
  do

    echo "Importando: $json_dir/$json_arq ( $contador de $numero_arquivos )"

    python ../manage.py loaddata $json_arq
    if [ "$?" -ne 0 ]
    then
      echo "Houve erro na importacao! - ver arquivo: $json_dir/fix_import_$json_arq"
      mv $json_arq fix_import_$json_arq
    fi

    contador=`expr $contador + 1`

  done

  # apaga lista de arquivos json do range em questao
  [ -f json_list.lst ] && rm json_list.lst

  # volta no diretorio imediatamente acima para proximo loop
  cd ..

done

echo
echo "Analisando arquivos que nao foram convertidos em json ..."
# Verifica se existe o arquivo
if [ $(ls */fix_* 2> /dev/null | wc -l) -eq 0 ]
then
  echo " Conversao OK!!!"
else
  ls */fix_* > fix.txt
  echo " ** Ocorreu problema em alguns arquivos"
  echo "    Checar fixtures/$INSUMO/fix.txt"
  echo
fi


# Prepara resumo
[ -f resumo.txt ] && rm resumo.txt
[ -f total_arqs.txt ] && rm total_arqs.txt
[ -f total_ids.txt ] && rm total_ids.txt
[ -f total_fix.txt ] && rm total_fix.txt
[ -f excel.txt ] && rm excel.txt

for dir_json in $(cat json_dir.lst)
do
  cd $dir_json

  total_ids=`grep "LILACS_original_id" slice*json | wc -l`

  total_arqs=`ls slice*json | wc -l`

  if [ $(grep LILACS_original_id fix_import* 2> /dev/null | wc -l) -ne 0 ]
  then
    total_fix=`grep LILACS_original_id fix_import* | awk -F":" '{ print $3 }' | sed 's/\"//g' | sed 's/\,//g' | sed 's/ //g' | wc -l`
  else
    total_fix="0"
  fi

  echo "- $DIR_WRK/$dir_json"             >> ../resumo.txt
  echo "  Total de imports : $total_arqs" >> ../resumo.txt
  echo "  Total de id´s    : $total_ids"  >> ../resumo.txt
  echo "  Total de fix     : $total_fix"  >> ../resumo.txt

  echo "$total_arqs"                       >> ../total_arqs.txt
  echo "$total_ids"                        >> ../total_ids.txt
  echo "$total_fix"                        >> ../total_fix.txt

  # prepara excel
  echo "$dir_json - $total_arqs - $total_ids - $total_fix" >> ../excel.txt


  # volta acima
  cd ..

done


# Faz a soma total de valores
vlr_arq=0
for t_arqs in $(cat total_arqs.txt)
do
  # echo $t_arqs
  t_vlr=`echo $t_arqs`
  vlr_arq=`expr $t_vlr + $vlr_arq`
done

# Faz a soma total de id´s
vlr_ids=0
for t_ids in $(cat total_ids.txt)
do
  # echo $t_ids
  t_vlr=`echo $t_ids`
  vlr_ids=`expr $t_vlr + $vlr_ids`
done

# Faz a soma total de fix
vlr_fix=0
for t_fix in $(cat total_fix.txt)
do
  # echo $t_ids
  t_fix=`echo $t_fix`
  vlr_fix=`expr $t_fix + $vlr_fix`
done


echo "---------------------------------------------------------------------------------------------------" >> resumo.txt
echo "   Total de imports : $vlr_arq" >> resumo.txt
echo "   Total de id´s    : $vlr_ids" >> resumo.txt
echo "   Total de fix´s   : $vlr_fix" >> resumo.txt


# Limpa area de trabalho
[ -f total_arqs.txt ] && rm total_arqs.txt
[ -f total_ids.txt ] && rm total_ids.txt
unset dir_json
unset total_ids
unset total_arqs
unset vlr_arq
unset t_arqs
unset t_vlr
unset vlr_arq
unset vlr_ids
unset t_ids

# limpa area de trabalho
#[ -f json_dir.lst ] && rm json_dir.lst

HORA_FIM=`date '+ %s'`
DURACAO=`expr ${HORA_FIM} - ${HORA_INICIO}`
HORAS=`expr ${DURACAO} / 60 / 60`
MINUTOS=`expr ${DURACAO} / 60 % 60`
SEGUNDOS=`expr ${DURACAO} % 60`

echo " " >> resumo.txt
echo "DURACAO DE PROCESSAMENTO" >> resumo.txt
echo "-------------------------------------------------------------------------" >> resumo.txt
echo " - Inicio:  ${HI}" >> resumo.txt
echo " - Termino: `date '+%Y.%m.%d %H:%M:%S'`" >> resumo.txt
echo " " >> resumo.txt
echo " Tempo de execucao: ${DURACAO} [s]" >> resumo.txt
echo " Ou ${HORAS}h ${MINUTOS}m ${SEGUNDOS}s" >> resumo.txt
echo " " >> resumo.txt

# ------------------------------------------------------------------------- #
echo "[TIME-STAMP] `date '+%Y.%m.%d %H:%M:%S'` [:FIM:] Processa  ${0} ${1} ${3} ${4} ${5}" >> resumo.txt
# ------------------------------------------------------------------------- #
echo " " >> resumo.txt
echo " " >> resumo.txt

cat resumo.txt
exit
