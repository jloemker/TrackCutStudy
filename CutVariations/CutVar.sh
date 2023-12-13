# This script is able to produce a configuration file for all the Cut Variations that one wants to apply

#!/bin/bash

reset
Results="$@" # Directory to store the results
CfgDir=$(dirname "$0")

# Create subdirectory for CutVariation in Results folder
mkdir -p "${Results}/CutVariations/"
echo "${Results}/AnalysisResults.root" > list.txt 

# Define an array of cuts
cuts=(
    "maxChi2PerClusterITS=30"
    "maxChi2PerClusterITS=40"
)

# Function to generate the standard configuration
generate_standard_config() {
    local configFile="${CfgDir}/combined_config.json"
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
        "fractionOfEvents": "3",
        "ValVtx": "10",
        "ValCutEta": "0.800000012",
        "minPt": "0.1000000060",
        "maxPt": "9.9999998e+10",
        "fillMultiplicity": "true",
        "globalTrack": "false",
        "globalTrackWoPtEta": "false",
        "globalTrackWoDCA": "false",
        "customTrack": "true",
        "itsPattern": "0",
        "requireITS": "true",
        "requireTPC": "true",
        "requireGoldenChi2": "false",
        "minNCrossedRowsTPC": "60",
        "minNCrossedRowsOverFindableClustersTPC": "0.699999988",
        "maxChi2PerClusterTPC": "7",
        "maxChi2PerClusterITS": "36",
        "maxDcaXYFactor": "1",
        "maxDcaZ": "3",
        "minTPCNClsFound": "0",
        "nBins": "200",
        "binsMultiplicity": {
            "values": [
                "100",
                "0",
                "100"
            ]
        },
        "binsPercentile": {
            "values": [
                "100",
                "0",
                "100"
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
                "200"
            ]
        },
        "processFull": "false",
        "processDerived": "true"
    },
EOF
    echo "$configFile"
}

# Function to append configuration for a given cut
append_config_for_cut() {
    local cutName=$1
    local cutValue=$2
    local configFile=$3

    cat << EOF >> "$configFile"
    "track-jet-qa${cutName}${cutValue}": {
        "fractionOfEvents": "2",
        "ValVtx": "10",
        "ValCutEta": "0.800000012",
        "minPt": "0.150000006",
        "maxPt": "9.9999998e+10",
        "fillMultiplicity": "true",
        "globalTrack": "false",
        "globalTrackWoPtEta": "false",
        "globalTrackWoDCA": "false",
        "customTrack": "true",
        "itsPattern": "1",
        "requireITS": "false",
        "requireTPC": "false",
        "requireGoldenChi2": "false",
        "minNCrossedRowsTPC": "60",
        "minNCrossedRowsOverFindableClustersTPC": "0.699999988",
        "maxChi2PerClusterTPC": "7",
        "maxChi2PerClusterITS": "$cutValue",
        "maxDcaXYFactor": "1",
        "maxDcaZ": "3",
        "minTPCNClsFound": "0",
        "nBins": "200",
        "binsMultiplicity": {
            "values": [
                "100",
                "0",
                "100"
            ]
        },
        "binsPercentile": {
            "values": [
                "100",
                "0",
                "100"
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
                "200"
            ]
        },
        "processFull": "false",
        "processDerived": "true"
    },
EOF
}

# Function to finalize the configuration file
finalize_config_file() {
    local configFile=$1
    cat << EOF >> "$configFile"
    "internal-dpl-aod-global-analysis-file-sink": "",
    "internal-dpl-injected-dummy-sink": ""
}
EOF
}

# Function to run the analysis with the configuration
runSpec() {
    local configPath=$1
    local cutName=$2
    local cutValue=$3
    local suffix="${cutName}${cutValue}"

    Cfg="--configuration json://${configPath} -b"
    
    o2-analysis-je-track-jet-qa $Cfg --workflow-suffix "$suffix"
    mv AnalysisResults.root "${Results}/CutVariations/AnalysisResults_${suffix}.root"
}


# Generate the standard configuration
configFile=$(generate_standard_config)

# Append each cut variation to the configuration
for cut in "${cuts[@]}"; do
    IFS='=' read -r cutName cutValue <<< "$cut"
    append_config_for_cut "$cutName" "$cutValue" "$configFile"
done

# Finalize the configuration file
finalize_config_file "$configFile"

# Run analysis with the final configuration for each cut
for cut in "${cuts[@]}"; do
    IFS='=' read -r cutName cutValue <<< "$cut"
    runSpec "$configFile" "$cutName" "$cutValue"
done

