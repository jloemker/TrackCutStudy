#!/bin/bash

mergeRuns=merge_runs.txt
touch $mergeRuns

IFS=, read -a runs < runs.txt # cp the running list from hyperloop into runs.txt
IFS=, read -a hyperpath < output.txt # cp the output list from hyperloop into output.txt

c=0
for i in "${runs[@]}"
do
  echo "Run [$i]: ${hyperpath["${c}"]}"
  mkdir -p $i/
  mkdir -p $i/merged/
  input=$i/files_per_run.list
  merge=$i/merge_per_run.txt
  touch $input
  ./alien_find_jl.sh "${hyperpath["${c}"]}"/AOD/ AO2D.root > $input
  ((c+=1))
  j=0
  while IFS= read -r line
  do
    [[ “$line” =~ ^#.*$ ]] && continue
    mkdir -p $i/$j/
    alien_cp $line file:$i/$j/AO2D.root
    ((j+=1))
    echo $j/AO2D.root >> $merge
  done < $input

  cd $i/
  o2-aod-merger --input merge_per_run.txt
  cd ../
  echo $i/AO2D.root >> $mergeRuns
done
o2-aod-merger --input merge_runs.txt # could be that this does not work, but the merger has the --help option too !
mv AO2D.root AnalysisResults_trees.root # renaming into the _trees.root such that we only need to move this into the proper ../Results/LHC_Period/ 

echo "all done and merged into AnalysisResults_trees.root ! " # if the merging into one AO2D doesn't work, then look at the ../CutVariations/runCatvar.sh and extent the list.txt
echo "don't mess up moving the results to their location for the cutvariation study !" # good to move all submerged directories into a backup !
