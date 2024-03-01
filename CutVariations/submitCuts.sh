#!/bin/bash

export cut_var
export runnumber
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

#All from Low IR ! You need to specify the path to the DataSet/Period in runCuts!
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
    "529066"
    "529067"
)
#some runs ended up in error on hyperloop and have no AO2D - eg. problem run 526689, ...
echo "generate config file..."
./generateConfig.sh "${cuts[@]}"

for runnumber in "${runs[@]}"; do
    echo "Runnumber $runnumber"
    for cut in "${cuts[@]}"; do   
        if [[ $cut == *'.'* ]]; then
            tmp="${cut//'.'/_}"
            cut_var="${tmp//'='/}"
            echo "$cut_var"
            qsub -q short -F "${cut_var} ${runnumber}" runCuts.sh
        elif [[ $cut == *'true'* ]]; then
            tmp="${cut//'true'/}"
            cut_var="${tmp//'='/}"
            echo "$cut_var"
            qsub -q short -F "${cut_var} ${runnumber}" runCuts.sh
        else
            cut_var="${cut//'='/}"
            echo "${cut_var}"
            qsub -q short -F "${cut_var} ${runnumber}" runCuts.sh
        fi
    done
done
echo "All submitted !"
