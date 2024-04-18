README for /CutVariations:

**Submit CutVariations (stbc):**

1. modify the generateConfig.sh to specify the "standard configuration" around which you want to vary certain cuts; here you can also change the binning.
The script will produce the generated_config.json file which is used as input for the o2Physics workflow (line 25 runCuts.sh).

2. modify the submitCuts.sh:
- cuts specify the cuts and values you want to change wrt to th "standard configuration" from step 1.
- runs specify the runnumbers that you want to analyse 
  you can use the tool printRunNumbers to print out all runnumbers in a handy format; simply change line 3 in that script to your data and copy the output from the terminal:
  ./printRunNumbers 
 '528531' 
 '528461' 
 '528292' 
 '527899' 
 '527895'
  
- export the correct path to your data (export Results line 67)

3. adjust runCuts.sh:
- change the Base (line 12) to your repository
- at some point you might need to update the version in the eval command 

4. do ./submit cuts and see how you spam stbc !

- first you see how the cutvalues are translated into input variables 

found a . 
no special value
no special value
found a Track bool
found a Track bool
found a Track bool
no special value
no special value

Then you start submitting per subdirectory of each runnumber (that can take some time)

Runnumber 528531
maxChi2PerClusterITS46
17669259.burrell.nikhef.nl
maxChi2PerClusterITS42
17669260.burrell.nikhef.nl
maxChi2PerClusterITS30
...
0 ->Subdirectory with AO2D.root file
maxChi2PerClusterITS46
17669259.burrell.nikhef.nl
maxChi2PerClusterITS42
17669260.burrell.nikhef.nl
maxChi2PerClusterITS30
...
1 ->Subdirectory with AO2D.root file
(...)
All submitted !

Then you have to wait ... Be aware that we use mainly THnSpare and thus the binning might slow down the analysis drastically ! Please double check centrality and multiplicity bins carefully in the generated_config.sh in case you run into trouble.

You can find the AnalysisResults_CutVariation.root files from the completed jobs in the new directory $Results (from step2)/Runnumber/CutVariations/ 
!! if jobs crush and corrupted AnalysisResults are produced, then you need to delete them manually (or with the help of cleanSubMerge - but be careful !! Don't delete what you need) before re-submitting the failed job -> No overwriting on /dcache !

eg.
528531]$ ls
0  1  2  3  4  5  CutVariations  files_per_run.txt  merge_per_run.txt
528531]$ cd CutVariations/
CutVariations]$ ls
0  1  2  3  4  5
CutVariations]$ cd 5/
5]$ ls
AnalysisResults_globalTrack.root
AnalysisResults_globalTrackWoDCA.root
AnalysisResults_globalTrackWoPtEta.root
AnalysisResults_itsPattern0.root
AnalysisResults_itsPattern1.root


**Merge AnalysisResults** (per run and/or period):

1. Per Runnumber
update haddAnalysisFile to merge the AnalysisResults_*.root for a given run
- you may, or may not, change the o2physics version (line 4) 
- change the Results path (line 10)
- choose for which cuts you want to perform the merge (usually the ones specified in submit.sh , line 12++)

./haddAnalysisFiles

output in terminal:

1
2
3
4
5
6
maxChi2PerClusterITS46
hadd Target file: AnalysisResults_maxChi2PerClusterITS46.root
hadd compression setting for all output: 1
hadd Source file 1: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/0/AnalysisResults_maxChi2PerClusterITS46.root
hadd Source file 2: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/1/AnalysisResults_maxChi2PerClusterITS46.root
hadd Source file 3: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/2/AnalysisResults_maxChi2PerClusterITS46.root
hadd Source file 4: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/3/AnalysisResults_maxChi2PerClusterITS46.root
hadd Source file 5: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/4/AnalysisResults_maxChi2PerClusterITS46.root
hadd Source file 6: /dcache/alice/jlomker/LHC22o_pass6_QC1_sampling/528531/CutVariations/5/AnalysisResults_maxChi2PerClusterITS46.root
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/EventProp
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/TrackEventPar
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/Kine
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/TrackPar
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/ITS
hadd Target path: AnalysisResults_maxChi2PerClusterITS46.root:/track-jet-qamaxChi2PerClusterITS46/TPC

...

(then it will take 'some' time before all subjobs are merged... prepare for a run ;) )





2. Per Period (requires previous step !)
update haddPeriods to merge the AnalysisResults_*.root from different runs into defined period
- (write a list merge_LHC22o_apass4.txt into your Results directory if you like to ex/include certain runs in the period merge:
eg.
Results=/dcache/.../LHC22_pass4_lowIR]$ cat merge_LHC22o_apass4.txt
526689/AO2D.root
527799/AO2D.root

else the script will read only the auto-generated full merge_runs.txt.)

- you may, or may not, change the o2physics version (line 4) 
- change the Results path (line 10)
- choose for which cuts you want to perform the merge (usually all, line 12++)







