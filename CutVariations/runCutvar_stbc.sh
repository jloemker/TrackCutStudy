#!/bin/bash

reset
#Results="$@" #directory to tress as command line argument: bash CutVar.sh ../Results/LHC_Test
# submit to the grid via: qsub runCutvar_stbc.sh

Results="/dcache/alice/jlomker/LHC23_PbPb_pass1/544510"
Base="/data/alice/jlomker/alice/TrackCutStudy/CutVariations"
eval $(/data/alice/jlomker/alice/TrackCutStudy/Download/./load-alien-tag-thx-gijs)  

# these cuts will be automatically converted to a) generate the config file and b) run the function runSpec
cuts=(
    "maxChi2PerClusterITS=30"
    "maxChi2PerClusterITS=42"
    "maxChi2PerClusterTPC=2"
    "maxChi2PerClusterTPC=3"
    "maxChi2PerClusterTPC=5"
    "maxChi2PerClusterTPC=6"
    "maxDcaZ=1"
    "maxDcaZ=3"
    "maxDcaXY=0.5"
    "maxDcaXY=1"
    "maxDcaXY=1.5"
    "maxDcaXY=2.5"
    "maxDcaXY=3"
    "minNCrossedRowsOverFindableClustersTPC=0.6"
    "minNCrossedRowsOverFindableClustersTPC=0.7"
    "minNCrossedRowsOverFindableClustersTPC=0.9"
    "minNCrossedRowsOverFindableClustersTPC=1.0"
    "minNCrossedRowsTPC=110"
    "minNCrossedRowsTPC=60"
    "minNCrossedRowsTPC=80"
    "globalTrackWoPtEta=true"
    "globalTrackWoDCA=true"
    "globalTrack=true"
    "itsPattern=0"
    "itsPattern=1"
    "itsPattern=3"
    "minTPCNClsFound=1"
    "minTPCNClsFound=2"
    "minTPCNClsFound=3"
)

${Base}/configs/./generateConfig.sh "${cuts[@]}"

#configs/./generateConfig.sh "${cuts[@]}"
mv ${Base}/configs/generated_config.json ${Base}/generated_config.json

mkdir -p "${Results}/CutVariations/" #creates subdirectory for CutVariation in Results section where you keep your data
echo "${Results}/AO2D.root" > list.txt # generates the list for the config file

Cfg="--configuration json://generated_config.json -b" # this is produced with generateConfig.sh

function runSpec {
        o2-analysis-je-track-jet-qa --configuration json://${Base}/generated_config.json -b --workflow-suffix $1
        mv AnalysisResults.root ${Results}/CutVariations/AnalysisResults_$1.root
    }

for cut in "${cuts[@]}"; do
    if [[ $cut == *'.'* ]]; then
        tmp="${cut//'.'/_}"
        spec_cut="${tmp//'='/}"
        echo $spec_cut
        runSpec $spec_cut
    elif [[ $cut == *'true'* ]]; then
        tmp="${cut//'true'/}"
        spec_cut="${tmp//'='/}"
        echo $spec_cut
        runSpec $spec_cut
    else
        spec_cut="${cut//'='/}"  
        runSpec $spec_cut
    fi
done


