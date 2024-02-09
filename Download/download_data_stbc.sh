#!/bin/bash

store=/dcache/alice/jlomker/LHC23_PbPb_pass1
mkdir -p $store
mergeRuns=$store/merge_runs.txt
rm -rf $mergeRuns
touch $mergeRuns

IFS=, read -a runs < runs.txt # cp the running list from hyperloop into runs.txt
IFS=, read -a hyperpath < output.txt # cp the output list from hyperloop into output.txt

c=0
for i in "${runs[@]}"
do
  echo "Run [$i]: ${hyperpath["${c}"]}"
  mkdir -p $store/$i/
  #mkdir -p $store/$i/merged/
  input=$store/$i/files_per_run.list
  merge=$store/$i/merge_per_run.txt
  touch $input
  touch $merge
  ./alien_find_jl.sh "${hyperpath["${c}"]}"/AOD/ AO2D.root > $input
  ((c+=1))
  j=0
  while IFS= read -r line
  do
    [[ “$line” =~ ^#.*$ ]] && continue
    mkdir -p $store/$i/$j/
    alien_cp $line file:$store/$i/$j/AO2D.root
    ((j+=1))
    echo $store/$j/AO2D.root >> $merge
  done < $input
done
echo "all files downloaded"

for i in "${runs[@]}"
do
  cd $store/$i/
  o2-aod-merger --input merge_per_run.txt
  cd ../
  echo $store/$i/AO2D.root >> $mergeRuns
  echo "merged run $i"
done

o2-aod-merger --input merge_runs.txt # could be that this does not work, but the merger has the --help option too !
mv AO2D.root AnalysisResults_trees.root # renaming into the _trees.root such that we only need to move this into the proper ../Results/LHC_Period/ 

echo "all done and merged into AnalysisResults_trees.root ! " # if the merging into one AO2D doesn't work, then look at the ../CutVariations/runCatvar.sh and extent the list.txt
echo "don't mess up moving the results to their location for the cutvariation study !" # good to move all submerged directories into a backup !
