#!/bin/bash

store="/dcache/alice/jlomker/LHC23_PbPb_pass1" # make this your path

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
    ((j+=1))
    echo "$j/AO2D.root" >> merge_per_run.txt # we don't need the $store and $i (runnumber) here because we enter them before we execute the merging script where we find one  merge_per_run.txt per runnumber
  done < files_per_run.txt
  echo "$i/AO2D.root" >> merge_runs.txt
  mv files_per_run.txt $store/$i/files_per_run.txt
  mv merge_per_run.txt $store/$i/merge_per_run.txt
done

mv merge_runs.txt $store/merge_runs.txt

echo "all files downloaded"

for i in "${runs[@]}"
do
  cd $store/$i/ # entering the location we we store the AO2D's from the download 
  o2-aod-merger --input merge_per_run.txt # execute the merging with the file per run 
  echo "we might have just merged run $i" # and this is just to see where we are.. no guarentee that it works
done

cd $store # go where we find the merge_runs.txt and do it !

o2-aod-merger --input merge_runs.txt # and here we run the final merge - could be that this does not work, but the merger has the --help option too !
mv AO2D.root AnalysisResults_trees.root # renaming into the _trees.root such that we only need to move this into the proper ../Results/LHC_Period/ 

echo "all done and merged into AnalysisResults_trees.root ! (or merging did not work)" # if the merging into one AO2D doesn't work, then look at the ../CutVariations/runCatvar.sh and extent the list.txt
echo "don't mess up moving the results to their location for the cutvariation study !" # good to move all submerged directories into a backup !
