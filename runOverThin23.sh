#!/bin/bash

datasets=(
    "Thinner_LHC23"
    "Thinner_LHC23f"
    "Thinner_LHC23g"
    "Thinner_LHC23h"
    "Thinner_LHC23j"
    "Thinner_LHC23k"
    "Thinner_LHC23l"
    "Thinner_LHC23m"
    "Thinner_LHC23n"
    "Thinner_LHC23o"
    "Thinner_LHC23q"
    "Thinner_LHC23r"
    "Thinner_LHC23s"
    "Thinner_LHC23t"
    "Thinner_LHC23u"
    "Thinner_LHC23v"
    "Thinner_LHC23y"
    "Thinner_LHC23z"
    "Thinner_LHC23za"
    "Thinner_LHC23zb"
    "Thinner_LHC23zc"
    "Thinner_LHC23zd"
    "Thinner_LHC23ze"
    "Thinner_LHC23zf"
    "Thinner_LHC23zg"
    "Thinner_LHC23zh"
    "Thinner_LHC23zi"
    "Thinner_LHC23zj"
    "Thinner_LHC23zk"
    "Thinner_LHC23zm"
    "Thinner_LHC23zn"
    "Thinner_LHC23zq"
    "Thinner_LHC23zr"
    "Thinner_LHC23zs"
    "Thinner_LHC23zt"
)

for dataset in "${datasets[@]}"; do
    echo "Dataset: $dataset"
    #./processResults.py --Mode FULL --Input Results/$dataset/AnalysisResults.root --Save True --Suffix WoPtEta --DataSet $dataset --Scaled INT
    #./processResults.py --Mode FULL --Input Results/$dataset/AnalysisResults.root --Save True --Suffix WoPtEta --DataSet $dataset --Scaled LOG
    ./processResults.py --Mode FULL --Input Results/$dataset/AnalysisResults.root --Save True --DataSet $dataset --Scaled INT
    ./processResults.py --Mode FULL --Input Results/$dataset/AnalysisResults.root --Save True --DataSet $dataset --Scaled LOG

done