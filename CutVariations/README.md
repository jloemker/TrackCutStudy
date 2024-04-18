# Perfrom CutVariations
After following the instruction in [../Download/](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/README.md), you can process the tables from [jettrackderived.cxx](https://github.com/AliceO2Group/O2Physics/blob/master/PWGJE/TableProducer/jettrackderived.cxx) with the derived process of the [trackJetqa.cxx](https://github.com/AliceO2Group/O2Physics/blob/master/PWGJE/Tasks/trackJetqa.cxx). The following instructions can be used to obtain the ```AnalysisResults_cutvar.root``` per run and to further merge them into Results per periods or datasets.

**I) Setup scripts for CutVariations (stbc):**

**1.** modify the [generateConfig.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/generateConfig.sh) to 
  - specify the *'standard configuration'* around which you want to vary certain cuts; here you can also change the binning.
  - produce the ```generated_config.json``` file which is used as input for the O2Physics workflow (line 25 [runCuts.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/runCuts.sh)).

**2.** modify the [submitCuts.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/submitCuts.sh)
  - *cuts=(...)* specify the cuts and values you want to change wrt to th *'standard configuration') from **1.**.
  - *runs=(...)* specify the runnumbers that you want to analyse 
  you can use the tool [printRunNumbers](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/printRunNumbers) to print out all runnumbers in a handy format; simply change line 3 in that script to your data and copy the output from the terminal into *runs=(...)*:
  ```
    ./printRunNumbers 
   '528531' 
   '528461' 
   '528292' 
   '527899' 
   '527895'
  ```
  - set the correct path to your derived data (*'export Results=/dcache/alice/YourUserName/DataSet'* line 67)

**3.** modify [runCuts.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/runCuts.sh):
- change the *'Base='* (line 12) to **your repository**
- (at some point you might need to update the version in the eval command)


**II) Submit CutVariations (stbc-short):**

After downloading and preparing all your scripts, simply type: ```./submitCuts.sh``` and see how you spam stbc !

- first you see how the cutvalues are translated into input variables:
```
found a . 
no special value
no special value
found a Track bool
found a Track bool
found a Track bool
no special value
no special value
```
- then you start submitting jobs per subdirectory of each runnumber for every cut (that can take some time)
```
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
```

- you have to wait ... Be aware that we use mainly [THnSpare](https://root.cern.ch/doc/master/classTHnSparse.html) and thus the binning might slow down the analysis drastically ! Please double check centrality and multiplicity bins carefully in the ```generated_config.sh``` in case you run into trouble.

- find the ```AnalysisResults_CutVariation.root``` files from the completed jobs in the new directory *'/dcache/alice/YourUserName/DataSet'* + *'/Runnumber/CutVariations/'* 
```
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
```

**III) Merge AnalysisResults** (per run and/or period):

**1. merge per runnumber**

first update the script [haddAnalysisFile](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/haddAnalysisFiles) to merge the each ```AnalysisResults_cutvar.root``` on per runnumber:
- you may, or may not, change the o2physics version (line 4) 
- change the *Results='/dcache/alice/YourUserName/DataSet'* path (line 10)
- choose for which cuts you want to perform the merge (usually the ones specified in [submitCuts.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/submitCuts.sh) , line 12++),

then execute the script ```./haddAnalysisFiles``` .

you can expect the following output in your terminal:
```
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
```
(then it will take 'some' time before all subjobs are merged... prepare for a run ;) )


**2. Merge per period** (requires previous step !)

first update [haddPeriods](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/haddPeriods) to merge the ```AnalysisResults_cutvar.root``` from different runs into defined periods (or datasets)
  - you can write a list *merge_LHC22o_apass4.txt* into your *Results='/dcache/alice/YourUserName/DataSet'* directory inorder to ex/include certain runs in the period merge:
    ```
    Results=/dcache/.../LHC22_pass4_lowIR]$ cat merge_LHC22o_apass4.txt
    526689/AO2D.root
    527799/AO2D.root
    ```
    else the script will read only the auto-generated full merge_runs.txt.)

  - you may, or may not, change the o2physics version (line 4) 
  - change the *Results='/dcache/alice/YourUserName/DataSet'* path (line 10)
  - choose for which cuts you want to perform the merge (usually all, line 12++)


## Caution
**!! if jobs crush and corrupted AnalysisResults_cutvar.root are produced, then you need to delete them manually** (or with the help of [cleanSubMerge](https://github.com/jloemker/TrackCutStudy/blob/johanna/CutVariations/cleanSubMerge) - but be careful !! Don't delete what you need) before re-submitting the failed job **-> No overwriting on /dcache !**





