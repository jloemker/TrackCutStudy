#!/bin/bash

#enter the O2physics env manually before going into screen mode by executing this script !

#source /cvmfs/alice.cern.ch/bin/alienv enter VO_ALICE@O2Physics::daily-20231108-0200-1

screen -S download -d -m bash download_data_stbc.sh
