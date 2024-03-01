#!/bin/bash

store="/dcache/alice/jlomker/LHC22_pass4_lowIR" # make this your path

mkdir -p $store

IFS=, read -a runs < runs.txt # cp the running list from hyperloop into runs.txt
IFS=, read -a hyperpath < output.txt # cp the output list from hyperloop into output.txt

c=0
for i in "${runs[@]}"
do
  echo "Run [$i]: ${hyperpath["${c}"]}"
  mkdir -p $store/$i/ 
  ./alien_find_jl.sh "${hyperpath["${c}"]}"/AOD/ AO2D.root > files_per_run.txt
  ((c+=1))
  j=0
  while IFS= read -r line
  do
    [[ $line == *'#'* ]] && continue
    mkdir -p $store/$i/$j/
    alien_cp $line file:$store/$i/$j/AO2D.root
    echo "$j/AO2D.root" >> merge_per_run.txt # we don't need the $store and $i (runnumber) here because we enter them before we execute the merging script where we find one  merge_per_run.txt per runnumbe
    ((j+=1))
  done < files_per_run.txt
  echo "$i/AO2D.root" >> merge_runs.txt
  #rm -rf $store/$i/merge_per_run.txt
  #rm -rf $store/$i/files_per_run.txt
  #rm -rf $store/$i/AO2D.root
  mv files_per_run.txt $store/$i/files_per_run.txt
  mv merge_per_run.txt $store/$i/merge_per_run.txt
done

mv merge_runs.txt $store/merge_runs.txt

echo "all files downloaded"

cd $store # go where we find the merge_runs.txt and do it !
