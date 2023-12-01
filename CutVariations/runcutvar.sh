#!/bin/bash

#set the values of the trackCuts to some standard deviation and manipulate one at a time
#(these are examples; before duplicating the lines in derived_multi.sh we should define standard values)
#therefore we should keep track of the mother file (tree) in this directory
# once the cutvars are done the ,other file should move to the same diectory!
reset
ResDir="LHC_Test" #one can make it a command line argument ..that would be nice... and that it creates the paths !! uff yeah !
CfgDir=$(dirname "$0")
Cfg="-b"
Cfg="--configuration json://configs/derived_multi.json -b --aod-file ../Results/LHC_Test/AnalysisResultsMother.root"

function runSpec {
    #o2-analysis-lf-spectra-tof
    o2-analysis-je-track-jet-qa $Cfg --workflow-suffix $1
    mv AnalysisResults.root AnalysisResults_$1.root
}

runSpec maxChi2PerClusterITS30
runSpec maxChi2PerClusterITS40

#I only list some examples; you can in principle check all the configurables (on track level) that we find in the config file

#runSpec maxChi2PerClusterTPC2
#runSpec maxChi2PerClusterTPC3
#runSpec maxChi2PerClusterTPC5
#runSpec maxChi2PerClusterTPC6
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

#move the mother file to same directory as specified in the beginning
#mv *.root ../Results/LHC_Test/CutVariations/*.root

