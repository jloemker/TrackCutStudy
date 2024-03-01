#!/bin/bash

run(){
export cut=$1
export runnumber=$2

cd $TMPDIR
mkdir yikes_$cut
cd yikes_$cut

Results="/dcache/alice/jlomker/LHC22_pass4_lowIR/${runnumber}"
Base="/data/alice/jlomker/alice/TrackCutStudy/CutVariations"
Save="${Results}/CutVariations"
mkdir -p ${Save}

cp ${Base}/generated_config.json .
cp ${Results}/merge_per_run.txt .
cp ${Base}/runSpec .
cat merge_per_run.txt

echo "${Results}/0/AO2D.root" >> list.txt

subId=1
while IFS= read -r line
do
  echo "reading line.."
  echo "${Results}/${subId}/AO2D.root" >> list.txt
  subId=+1
done > merge_per_run.txt

cat list.txt
echo $cut

source /cvmfs/alice.cern.ch/etc/login.sh
eval $(alienv printenv VO_ALICE@O2Physics::daily-20240214-0100-1)
#./runSpec $cut
o2-analysis-je-track-jet-qa --configuration json://generated_config.json -b --workflow-suffix $cut
cp AnalysisResults.root ${Save}/AnalysisResults_$cut.root
rm AnalysisResults.root

cd ..
pwd
rm -r yikes_$cut
}

export cut=$1
export runnumber=$2
run $cut $runnumber
