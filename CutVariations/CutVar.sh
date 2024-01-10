# \author Alice Caluisi <alice.caluisi@cern.ch>
# \since December 2023

#
# Task performing cut variations on trees analysis results - No here you just want to create a config file for the running script
# The produced results are called AnalysisResults_cutName.root and are stored in Results/LHC_Test/CutVariations folder 
# To run the task, type: $> bash CutVar.sh ../Results/LHC_Test
#

#!/bin/bash
#Define an array of all the cuts I want to apply
cuts=(
    "maxChi2PerClusterITS=30"
    "maxChi2PerClusterITS=40"
    "maxChi2PerClusterTPC=6"
)

#Function to generate the standard configuration
generate_standard_config() {
    local configFile="combined_config.json"
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

#Function to append to the standard configuration the configuration for each single cut
append_config_for_cut() {
    local cutName=$1
    local cutValue=$2
    local configFile=$3

    #Copy the standard track-jet-qa configuration and perform the cut variation
    sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"track-jet-qa${cutName}${cutValue}\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/" "$configFile" >> "cut_config.json"
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
for cut in "${cuts[@]}"; do
    IFS='=' read -r cutName cutValue <<< "$cut"
    append_config_for_cut "$cutName" "$cutValue" "$configFile"
done

#Finalize the configuration file
finalize_config_file "$configFile"

mv "$configFile" "configs/$configFile"
#Run analysis with the final configuration for each cut -> Use runcutvar.sh for the running; simply change the file name.