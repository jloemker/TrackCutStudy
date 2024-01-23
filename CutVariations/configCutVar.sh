# \author Alice Caluisi <alice.caluisi@cern.ch>
# \since December 2023

#
# This task creates a configuration file in CutVariations/Configurations called cutvar_config.json used by the runcutvar.sh script
#

#Check if the cuts array is provided. If not, send an error message and exit
use_cuts=("$@")
if [ ${#use_cuts[@]} -eq 0 ]; then
    echo "ERROR: No cuts provided. Please provide cuts in runCutVar.sh script"
    exit 1
fi

#Function to generate the standard configuration
generate_standard_config() {
    local configFile="cutvar_config.json"
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

#Function to append the configuration for each single cut to the standard configuration
append_config_for_cut() {
    local cutName=$1
    local cutValue=$2
    local configFile=$3

    #Check if the cut is 'minPt' and modify its value for the configuration name
    if [ "$cutName" == "minPt" ]; then
        #Delete '.' in cutValue for the configuration section name
        local modifiedCutValue="${cutValue//./}"
        local configSectionName="track-jet-qa${cutName}${modifiedCutValue}"
    else
        local configSectionName="track-jet-qa${cutName}${cutValue}"
    fi

    #Update the configuration
    sed "/\"track-jet-qa\"/,\$!d; s/\"track-jet-qa\"/\"$configSectionName\"/; s/\"$cutName\": \"[^\"]*\"/\"$cutName\": \"$cutValue\"/" "$configFile" >> "cut_config.json"
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

#Move the configuration file into the Configurations folder
mv "$configFile" "Configurations/$configFile"