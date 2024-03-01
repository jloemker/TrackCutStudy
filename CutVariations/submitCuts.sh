#!/bin/bash

export cut_var
export runnumber

# specify the cutvariations you would like to perform
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

# specify the runs you want to analyse
runs=(
    "520259"
    "520294" 
    "520471"
    "520472"
    "520473"
    "523897"
    "527799"
    "528991"  
    "528997"
    "529003"  
    "529005"
    "529006"
    "529009"
    "529015"
    "529037"
    "529038"
    "529039"
    "529043"
)
# Error runs lowIR (removed from /dcache/): 526689, 529066, 529066

echo "generating the config file according to your needs (cuts in submitCuts.sh )..."
./generateConfig.sh "${cuts[@]}"

for runnumber in "${runs[@]}"; do
    echo "Runnumber $runnumber"
    export Results="/dcache/alice/jlomker/LHC22_pass4_lowIR/${runnumber}"  # specify your /dcache path
    cp ${Results}/merge_per_run.txt .
    export subId
    subId=0
    while IFS= read -r line
    do
        for cut in "${cuts[@]}"; do   
            if [[ $cut == *'.'* ]]; then
                tmp="${cut//'.'/_}"
                cut_var="${tmp//'='/}"
                echo "$cut_var"
                qsub -q short -F "${cut_var} ${runnumber} ${subId} ${Results}" runCuts.sh
            elif [[ $cut == *'true'* ]]; then
                tmp="${cut//'true'/}"
                cut_var="${tmp//'='/}"
                echo "$cut_var"
                qsub -q short -F "${cut_var} ${runnumber} ${subId} ${Results}" runCuts.sh
            else
                cut_var="${cut//'='/}"
                echo "${cut_var}"
                qsub -q short -F "${cut_var} ${runnumber} ${subId} ${Results}" runCuts.sh
            fi
        done
        echo "${subId}"
        ((subId+=1))
    done < merge_per_run.txt
done
echo "All submitted !"
