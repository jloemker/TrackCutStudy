#!/bin/bash

# This script is able to produce a configuration file for all the Cut Variations that one wants to apply

reset
Results="$@" # Directory to store results
CfgDir=$(dirname "$0")

# Create subdirectory for CutVariation in Results folder
mkdir -p "${Results}/CutVariations/"
echo "${Results}/AnalysisResults.root" > list.txt 

# Function to generate configuration sections for cut variations on the maximum value of Chi2 per ITS clusters
generate_config_section() {
    local chi2Value=$1
    cat << EOF
    "track-jet-qamaxChi2PerClusterITS${chi2Value}": {
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
        "maxChi2PerClusterITS": "${chi2Value}",
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

# Generate the whole configuration file
generate_config_file() {
    local configFile="${CfgDir}/generated_config.json"

    # Start of the configuration file
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

    # Append specific configurations
    generate_config_section 30 >> "$configFile"
    generate_config_section 40 >> "$configFile"

    # End of the configuration file
    cat << EOF >> "$configFile"
    "internal-dpl-aod-global-analysis-file-sink": "",
    "internal-dpl-injected-dummy-sink": ""
}
EOF

    echo "$configFile"
}

# Function to run the analysis with a specific configuration
runSpec() {
    local suffix=$1
    local configPath=$(generate_config_file)

    Cfg="--configuration json://${configPath} -b"
    
    o2-analysis-je-track-jet-qa $Cfg --workflow-suffix "$suffix"
    mv AnalysisResults.root "${Results}/CutVariations/AnalysisResults_${suffix}.root"
}

# Run analysis for each specification
runSpec maxChi2PerClusterITS30
runSpec maxChi2PerClusterITS40
