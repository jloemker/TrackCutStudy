#!/bin/bash
export cmdTag="#CMD "
if [ $# -eq 1 ]
then
  export cmd=`head -1 ${1}|sed "s/${cmdTag}//"`
  export cmd=${cmd}" "${1}
  exec ${cmd}
elif [ $# -eq 2 ]
then
  echo ${cmdTag}${0} ${@}
  alien_find ${1} ${2} \
  | grep -v "Stage_"\
  | awk '!/files found/ && !/^\s*$/ {print "alien://"$0} /files found/ {print "# "$0}'
elif [ $# -eq 3 ]
then
  [[ ! -f ${3} ]] && exit 4
  alien_find ${1} ${2} \
  | grep -v "Stage_"\
  | awk '!/files found/' \
  | xargs -l1 -IREPLACEME \
    awk -v line=REPLACEME \
    'BEGIN {a=0;} $0 ~ line {a=1;} END {if (a==0) print "alien://"line;}' ${3}
else
  echo "When given 3 arguments the last one is a file to be updated."
  echo "In that case only new entries will be printed"
  echo "for 2 arguments it's like alien_find, only formatted"
  echo "for 1 argument prints the updates to the file (the original find"
  echo "command is stored in the first line of output"
  echo "Usage: `basename $0` path pattern [file to diff to]"
  echo "Usage: `basename $0` path pattern"
  echo "Usage: `basename $0` fileList"
  exit 5
fi

