REadme on CutVariations:

cd in /Download (stbc):

1. create a file "runs.txt" and paste the run list from hyperloop in there (as done in the example file) 
2. create a file "output.txt" and paste the corresponding output list from hyperloop in there 
3. adjust the store (line 3) in download_data_stbc.sh to the path where you want to store the derived data; please choose a /dcache directory.
4. enter the o2-physics environment (you can use your own installations, or load the latest tag via ./load-alien-tag-thx-gijs )

source /cvmfs/alice.cern.ch/etc/login.sh
alienv enter VO_ALICE@O2Physics::daily-20240214-0100-1

5. execute the ./download_data_stbc.sh
when the download started you should see this per Run: 

Run [528531]: /alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436
jobID: 1/1 >>> Start
jobID: 1/1 >>> STATUS OK >>> SPEED 86.11 MiB/s
Succesful jobs (1st try): 1/1
jobID: 1/1 >>> Start
jobID: 1/1 >>> STATUS OK >>> SPEED 91.59 MiB/s
Succesful jobs (1st try): 1/1

6. checkout if all your data is stored where you wanted it to be (step 3)

You should find a directory per Runnumber + a .txt file 

eg. cd $YourStorePath
ls
528461  528531 ... merge_runs.txt

The merge_runs.txt will allow us to easily merge the AnalysisResults.root from the CutVariations over all runs of a given dataset

cat merge_runs.txt 
528461/AO2D.root
528531/AO2D.root
...

Each Runnumber can be entered and should contain several enumerated subdirectories + a .txt file

eg cd $YourStorePath/528531
ls
0  1  2  3  4  5  files_per_run.txt  merge_per_run.txt

Each subdirectory contains one AO2D.root file which will be the input for the /CutVariations. For now, all these .txt files are used for bookkeeping. They will be utalized to merge the AnalysisResults.root per Run (and if you like even for all runs of a given period or dataset) once the /CutVariations are perfomed.

files_per_run.txt contains the path used to download the data (in case smth goes wrong)
cat files_per_run.txt 
#CMD ./alien_find_jl.sh /alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/ AO2D.root
alien:///alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/001/AO2D.root
alien:///alice/cern.ch/user/a/alihyperloop/jobs/0039/hy_391436/AOD/002/AO2D.root

and merge_per_run.txt contains the list of subdirectories that you can now easily merge (next step)

cat merge_per_run.txt 
0/AO2D.root
1/AO2D.root
2/AO2D.root
3/AO2D.root
4/AO2D.root
5/AO2D.root



