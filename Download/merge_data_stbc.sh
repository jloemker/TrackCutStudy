#!/bin/bash

store="/dcache/alice/jlomker/LHC23_PbPb_pass1" # make this your path

mkdir -p $store

IFS=, read -a runs < runs.txt # cp the running list from hyperloop into runs.txt
IFS=, read -a hyperpath < output.txt # cp the output list from hyperloop into output.txt

echo "all files downloaded"

for i in "${runs[@]}"
do
  cd $store/$i/ # entering the location we we store the AO2D's from the download 
  o2-aod-merger --input merge_per_run.txt --skip-parent-files-list --skip-non-existing-files # execute the merging with the file per run 
  echo "we might have just merged run $i" # and this is just to see where we are.. no guarentee that it works
done

cd $store # go where we find the merge_runs.txt and do it !

o2-aod-merger --input merge_runs.txt --skip-parent-files-list # and here we run the final merge - could be that this does not work, but the merger has the --help option too !
mv AO2D.root AO2D_allRuns.root # renaming into the _trees.root such that we only need to move this into the proper ../Results/LHC_Period/ 

echo "all done and merged into AnalysisResults_trees.root ! (or merging did not work)" # if the merging into one AO2D doesn't work, then look at the ../CutVariations/runCatvar.sh and extent the list.txt
echo "don't mess up moving the results to their location for the cutvariation study !" # good to move all submerged directories into a backup !
