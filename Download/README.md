# Download derived data

here is a collection of small scripts that can be used to download derived data per run from hyperloop.
The derived data from [jettrackderived.cxx](https://github.com/AliceO2Group/O2Physics/blob/master/PWGJE/TableProducer/jettrackderived.cxx) contains collision and track tables, produced with a loose set of track cuts.

**Download derived data per run to /dcache**
(make sure you are in the ```/Download``` directory)
```cd TrackCutStudy/Download/ ```

**1.** create a file [runs.txt](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/runs.txt) and paste the run list of your train output from hyperloop in there 

**2.** create a file [output.txt](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/output.txt) and paste the corresponding output list from hyperloop in there 

**3.** adjust the ```store="/dcache/alice/YourUserName/DataSet"``` (line 3) in [download_data_stbc.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/download_data_stbc.sh) to the path where you want to store the derived data.

**4.** enter the O2Physics environment
   - you can load your own installations,
   - or load the latest tag via [./load-alien-tag-thx-gijs](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/load-alien-tag-thx-gijs)
   - or load a working tag via
     ```
      source /cvmfs/alice.cern.ch/etc/login.sh
      alienv enter VO_ALICE@O2Physics::daily-20240214-0100-1
     ```
**5.** execute the script: [./download_data_stbc.sh](https://github.com/jloemker/TrackCutStudy/blob/johanna/Download/download_data_stbc.sh)

after some time you should expect to see something similar per Run: 
```
Run [528531]: /alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436
jobID: 1/1 >>> Start
jobID: 1/1 >>> STATUS OK >>> SPEED 86.11 MiB/s
Succesful jobs (1st try): 1/1
jobID: 1/1 >>> Start
jobID: 1/1 >>> STATUS OK >>> SPEED 91.59 MiB/s
Succesful jobs (1st try): 1/1
```

**6.** checkout if all your data is stored where you wanted it to be (step 3)

  You should find a newly created directory per Runnumber + a .txt file:
  ```
  cd /dcache/alice/YourUserName/DataSet
  ls
  528461  528531 ... merge_runs.txt
  ```
  The ```merge_runs.txt``` will allows to easily merge the AnalysisResults.root from the CutVariations over all runs of a given dataset:  
  ```
  cat merge_runs.txt 
  528461/AO2D.root
  528531/AO2D.root
  ...
  ```

  Each runnumber-directory should contain several enumerated subdirectories + a .txt file
  ```
  cd /dcache/alice/YourUserName/DataSet/528531
  ls
  0  1  2  3  4  5  files_per_run.txt  merge_per_run.txt
  ```

  Each subdirectory contains one AO2D.root file which will be the input for the [../CutVariations](https://github.com/jloemker/TrackCutStudy/tree/johanna/CutVariations). For now, all these .txt files are used for bookkeeping. They will be utilized to merge the AnalysisResults_cut.root per run (and if you like even for all runs of a given period or dataset) once the ../CutVariations are perfomed.

  ```files_per_run.txt``` contains the path used to download the data (in case smth goes wrong)
  ```
  cat files_per_run.txt 
  #CMD ./alien_find_jl.sh /alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/ AO2D.root  
  alien:///alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/001/AO2D.root
  alien:///alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/002/AO2D.root
  ```
  ```merge_per_run.txt``` contains the list of subdirectories that serves as input for the input list of our O2Physics workflow [(derived process of trackjetqa.cxx)](https://github.com/AliceO2Group/O2Physics/blob/master/PWGJE/Tasks/trackJetqa.cxx). The file is also used to easily merge the AnalysisResults.root files in the next steps.
  ```
  cat merge_per_run.txt 
  0/AO2D.root
  1/AO2D.root
  2/AO2D.root
  3/AO2D.root
  4/AO2D.root
  5/AO2D.root
  ```

## Caution !
**You cannot overwirte files on /dcache - delete corrupted files before repeating a download**



