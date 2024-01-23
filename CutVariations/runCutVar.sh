# \author Alice Caluisi <alice.caluisi@cern.ch>
# \since December 2023

#
# This task performs cut variation studies on trees analysis results using the configuration produced by configCutVar.sh
# The produced results are called AnalysisResults_cutName.root and are stored in Results/LHC_Test/CutVariations folder 
#
# To run the task, type: $> bash runCutVar.sh

#!/bin/bash

reset
CfgDir=$(dirname "$0")
Cfg="-b"

#Define an array of all the cuts
cuts=(
    "maxChi2PerClusterITS=30"
    "maxChi2PerClusterITS=40"
    "maxChi2PerClusterTPC=6"
    "maxChi2PerClusterTPC=4"
    "globalTrack=true"
    "minPt=0.2"
)

#Call the configCutVar.sh script to generate the configuration file
bash configCutVar.sh "${cuts[@]}"

#Create subdirectory for cut variation studies in Results/LHC_Test folder
Results="../Results/LHC_Test/"
mkdir -p "${Results}/CutVariations/" 

#Generate the list for the config file
echo "${Results}AnalysisResults.root" > list.txt 

Cfg="--configuration json://Configurations/cutvar_config.json -b" #This is the configuration produced by configCutVar.sh

function runSpec {
    local cutSpec=$1

    #If globalTrack=true, set customTrack=false
    if [[ "$cutSpec" == "globalTracktrue" ]]; then
        sed -i 's/"customTrack": "true"/"customTrack": "false"/' Configurations/cutvar_config.json
    fi

    #If the cutSpec is a float, remove '.' in the file name
    if [[ "$cutSpec" == "minPt0.2" ]]; then
        cutSpec="minPt02"
    fi

    o2-analysis-je-track-jet-qa $Cfg --workflow-suffix $cutSpec
    mv AnalysisResults.root "${Results}/CutVariations/AnalysisResults_${cutSpec}.root"
}

#Loop through the cuts array to run the analysis for each cut
for cut in "${cuts[@]}"; do
    IFS='=' read -r cutName cutValue <<< "$cut"
    runSpec "${cutName}${cutValue}"
done

#Other interesting cut variations:

#runSpec maxChi2PerClusterTPC2
#runSpec maxChi2PerClusterTPC3
#runSpec maxChi2PerClusterTPC5
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

