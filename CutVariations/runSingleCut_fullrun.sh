#!/bin/bash

cd $TMPDIR
mkdir yrigrffhra
cd yrigrffhra

source /cvmfs/alice.cern.ch/etc/login.sh
eval $(alienv printenv VO_ALICE@O2Physics::daily-20240214-0100-1)

Results="/dcache/alice/jlomker/LHC23_PbPb_pass1/544091"
Base="/data/alice/jlomker/alice/TrackCutStudy/CutVariations"
Save="${Results}/CutVariations"

mkdir -p $Save

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

cp ${Base}/generated_config.json .

echo "${Results}/AO2D.root" > list.txt # generates the list for the config file
cat list.txt

function runSpec {
        o2-analysis-je-track-jet-qa --configuration json://generated_config.json -b --workflow-suffix $1
        cp AnalysisResults.root ${Save}/AnalysisResults_$1.root
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

rm AnalysisResults.root

cd ..
rm -r yrigrffhra
