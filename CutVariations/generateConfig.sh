#!/bin/bash

use_cuts=("$@")
if [ ${#use_cuts[@]} -eq 0 ]; then
    echo "ERROR: No cuts provided. Please provide cuts in runCutVar.sh script"
    exit 1
fi

#Function to generate the standard configuration
generate_standard_config() {
    local configFile="generated_config.json"
    cat << EOF > "$configFile"
{
    "internal-dpl-clock": "",
    "internal-dpl-aod-reader": {
        "time-limit": "0",
        "orbit-offset-enumeration": "0",
        "orbit-multiplier-enumeration": "0",
        "start-value-enumeration": "0",
        "end-value-enumeration": "-1",
        "step-value-enumeration": "1",
        "aod-file": "@list.txt"
    },
    "track-jet-qa": {
        "ValVtx": "10",
        "ValCutEta": "0.8000000",
        "minPt": "0.1000000",
        "maxPt": "1e+10",
        "fillMultiplicity": "true",
        "globalTrack": "false",
        "globalTrackWoPtEta": "false",
        "globalTrackWoDCA": "false",
        "customTrack": "true",
        "itsPattern": "1",
        "requireITS": "false",
        "requireTPC": "false",
        "requireGoldenChi2": "false",
        "minNCrossedRowsTPC": "110",
        "minNCrossedRowsOverFindableClustersTPC": "1.0",
        "maxChi2PerClusterTPC": "2",
        "maxChi2PerClusterITS": "24",
        "maxDcaXY": "0.5",
        "maxDcaZ": "2",
        "minTPCNClsFound": "4",
        "binsMultiplicity": {
            "values": [
                "10",
                "0",
                "5000"
            ]
        },
        "binsMultNTracksPV": {
            "values": [
                "10",
                "0",
                "100"
            ]
        },
        "binsPercentile": {
            "values": [
                "10",
                "0",
                "100"
            ]
        },
        "binsVtx": {
            "values": [
                "40",
                "-20",
                "20"
            ]
        },
        "binsPt": {
            "values": [
                "200",
                "0",
                "200"
            ]
        },
        "binsSigma1OverPt": {
            "values": [
                "200",
                "0",
                "1"
            ]
        },
        "binsPhi": {
            "values": [
                "180",
                "0",
                "6.2831853071795862"
            ]
        },
        "binsEta": {
            "values": [
                "50",
                "-1",
                "1"
            ]
        },
        "binsTrackXY": {
            "values": [
                "50",
                "-0.5",
                "0.5"
            ]
        },
        "binsTrackZ": {
            "values": [
                "50",
                "-11",
                "11"
            ]
        },
        "binsRot": {
            "values": [
                "36",
                "-3.1415926535897931",
                "3.1415926535897931"
            ]
        },
        "binsSignedPt": {
            "values": [
                "100",
                "-8",
                "8"
            ]
        },
        "binsDcaXY": {
            "values": [
                "50",
                "-4",
                "4"
            ]
        },
        "binsDcaZ": {
            "values": [
                "50",
                "-6",
                "6"
            ]
        },
        "binsLength": {
            "values": [
                "50",
                "0",
                "1000"
            ]
        },
        "processFull": "false",
        "processDerived": "true"
    },
EOF
    echo "$configFile"
}

#Function to append to the standard configuration the configuration for each single cut
append_config_for_cut() {
    local cutName=$1
    local cutValue=$2
    local configFile=$3
    if [[ $cutValue = *'.'* ]]; then
        echo 'found a . ' 
        #make '.' in cutValue to '_' for the configuration section name
        local modifiedCutValue="${cutValue//./_}" 
        local configSectionName="track-jet-qa${cutName}${modifiedCutValue}"
        sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"$configSectionName\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/" "$configFile" >> "cut_config.json"
    elif [[ $cutName = *'Track'* ]]; then
        echo 'found a Track bool'
        local modifiedCutValue="${cutValue//*'true'*/}" 
        local configSectionName="track-jet-qa${cutName}${modifiedCutValue}"
        local c="customTrack"
        local f="false"
        #Set costum tracks to false and the specific cutname to true
        sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"$configSectionName\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/; s/\"$c\": \"[^\"]*\"/\"$c\": \"$f\"/" "$configFile" >> "cut_config.json"
    elif [[ $cutName = *'require'* ]]; then
        echo 'found a require bool'
        local modifiedCutValue="${cutValue//*'false'*/}" 
        local configSectionName="track-jet-qa${cutName}${modifiedCutValue}"
        sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"$configSectionName\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/" "$configFile" >> "cut_config.json"
    else
        echo 'no special value'
        local configSectionName="track-jet-qa${cutName}${cutValue}"
        sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"$configSectionName\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/" "$configFile" >> "cut_config.json"
    fi
}

#Function to finalize the overall configuration
finalize_config_file() {
    local configFile=$1
    cat "cut_config.json" >> "$configFile"
    rm "cut_config.json"
    cat << EOF >> "$configFile"
    "internal-dpl-aod-global-analysis-file-sink": "",
    "internal-dpl-injected-dummy-sink": ""
}
EOF
}

#Generate the standard configuration
configFile=$(generate_standard_config)

#Append each cut variation to the configuration
for cut in "${use_cuts[@]}"; do
    IFS='=' read -r cutName cutValue <<< "$cut"
    append_config_for_cut "$cutName" "$cutValue" "$configFile"
done

#Finalize the configuration file
finalize_config_file "$configFile"

#mv "$configFile" "configs/$configFile"
