#!/bin/bash

#set the values of the trackCuts to some standard deviation and manipulate one at a time
#(these are examples; before duplicating the lines in derived_multi.sh we should define standard values)
#therefore we should keep track of the mother file (tree) in this directory
# once the cutvars are done the ,other file should move to the same diectory!
# to run: bash CutVar.sh ../Results/LHC_Test
reset
Results="$@" #directory to tress as command line argument
CfgDir=$(dirname "$0")
Cfg="-b"

mkdir -p "${Results}/CutVariations/" #creates subdirectory for CutVariation in Results section where you keep your data
echo "${Results}AnalysisResults_trees.root" > list.txt # generates the list for the config file

#Cfg="--configuration json://configs/derived_multi.json -b" # this was a dummy configuration
Cfg="--configuration json://configs/combined_config.json -b" # this is produced with CutVar.sh

function runSpec {
    o2-analysis-je-track-jet-qa $Cfg --workflow-suffix $1
    mv AnalysisResults.root ${Results}/CutVariations/AnalysisResults_$1.root
}

runSpec maxChi2PerClusterITS30
runSpec maxChi2PerClusterITS40
runSpec maxChi2PerClusterTPC6

#I only list some examples; you can in principle check all the configurables (on track level) that we find in the config file

#runSpec maxChi2PerClusterTPC2
#runSpec maxChi2PerClusterTPC3
#runSpec maxChi2PerClusterTPC5
#
#runSpec maxDcaZ1
#runSpec maxDcaZ3
#runSpec minNCrossedRowsOverFindableClustersTPC075
#runSpec minNCrossedRowsOverFindableClustersTPC085
#runSpec minNCrossedRowsOverFindableClustersTPC105
#runSpec minNCrossedRowsTPC110
#runSpec minNCrossedRowsTPC60
#runSpec minNCrossedRowsTPC80
#runSpec globalTrack
#runspec globalTrackWoPtEta
#runspec globalTrackWoPtEta
#runspec requireITSrefit
#runspec requireTPCrefit

