#!/usr/bin/env python3

"""
Post processing script to handle the QA output from trackJetQa i.e. resolution at high pT.
"""

import ROOT
from ROOT import TFile
import argparse
import numpy
import re

from common import Directories, get_directories, canvas_list, canvas, clear_canvaslist, saveCanvasList
from checkTRD import compareTRD
from projection import projectEventProp, projectCorrelationsTo1D, projectCorrelationsTo2D, projectEtaPhiInPt, profile2DProjection
from compareResults import compareDataSets

legends = []

def drawPlots(InputDir="", Mode="", Save=""):
    f = TFile.Open(InputDir, "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    get_directories(f, f"track-jet-qa")
    for dirName in  Directories:
        dir = f.Get(f"track-jet-qa/"+dirName).GetListOfKeys()
        for obj in dir:
            o = f.Get(f"track-jet-qa/"+dirName+"/"+obj.GetName())
            if not o:
                print("Did not get", o, " as object ", obj)
                continue
            if "TH1" in o.ClassName():#Rejectionhisto in EventProp/rejectedCollId
                can = canvas(o.GetTitle())
                o.SetMarkerStyle(21)
                o.SetMarkerColor(4)
                o.GetYaxis().SetTitle("number of entries")
                o.Draw("E")
            if "TH2" in o.ClassName():#Flag bits
                continue
            if "THnSparse" in o.ClassName():
                if "collisionVtxZ" in o.GetName():
                    projectEventProp(o)
                if "MultCorrelations" in o.GetName() and dirName=="EventProp":
                    projectCorrelationsTo1D(o,o.GetNdimensions())
                    projectCorrelationsTo2D(o, [[0,1], [3,4], [5,6], [5,7], [2,7]])
                if "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                    projectCorrelationsTo1D(o,o.GetNdimensions())
                    projectCorrelationsTo2D(o, [[1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0]])
                    projectCorrelationsTo2D(o, [[1,2], [1,3], [1,4], [1,5], [1,6], [1,7], [1,8], [1,9]])
                if "EtaPhiPt" in o.GetName():#pt and pT_TRD for extra check later
                    projectCorrelationsTo1D(o, 4, scaled=False)
                    projectEtaPhiInPt(o, [[1,5], [5,15], [15,30],[30,100], [0,200]], logz=True)
                    profile2DProjection(o, [[0,1], [0,2], [0,3]])
                if "xyz" in o.GetName():
                    projectCorrelationsTo1D(o, 5, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2], [0,3], [0,4]])
                if "alpha" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "signed1Pt" in o.GetName():#add ratio pos neg !
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                    projectCorrelationsTo1D(o, 0, scaled=False)
                if "snp" in o.GetName():#improve binning !
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    profile2DProjection(o, [[0,2]])
                if "tgl" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    profile2DProjection(o, [[0,2]])
                if "dcaXY" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "length" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    profile2DProjection(o, [[0,2]])
                if "dcaZ" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "itsNCls" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "itsChi2NCl" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "itsHits" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=1, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0]])
                    profile2DProjection(o, [[0,2]])
                if "tpcNClsFindable" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "tpcNClsFound" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "tpcNClsShared" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "tpcNClsCrossedRows" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "tpcFractionSharedCls" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "tpcCrossedRowsOverFindableCls" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0]])
                    profile2DProjection(o, [[0,2]])
                if "tpcChi2NCl" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    profile2DProjection(o, [[0,2]])
                if "Sigma1Pt" in o.GetName():
                    if "TRD" in o.GetName():#write extra function in additional script
                        continue
                    else:
                        projectCorrelationsTo1D(o, 1, scaled=False)
                        projectCorrelationsTo2D(o, [[1,0]])
                        profile2DProjection(o, [[0,1]])
            else:
                print(o.GetName())
                print("we miss something..")
            if Save ==False:
                input("Wait and check the histograms !")
    if Save=="True":
        dataSetArr = re.findall(r'\/.*?\/', InputDir)
        dataSet=dataSetArr[0].strip("/")
        print(f"Save/{dataSet}/TrackQA_{dataSet}.pdf")
        saveCanvasList(canvas_list, f"Save/{dataSet}/TrackQA_{dataSet}.pdf", dataSet)
    else:
        print("we don't save this ...")
        clear_canvaslist()


    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Mode", "-m", type=str,
                        default=["Full", "TRD", "COMPARE"], help="Activate 'CompareDataSets', or plots QA AnalysisResults from 'Full' , 'Tree'(derived) results")
    parser.add_argument("--Input", "-in", type=str,
                        default="Results/LHC22s_pass5/AnalysisResults.root", help="Path and File input", nargs="+")
    parser.add_argument("--Save", "-s", type=str,
                        default=["False", "True"], help="If you set this flag, it will save the documents")
    args = parser.parse_args()

    if args.Mode=="FULL":
        drawPlots(args.Input[0], args.Mode, args.Save)
        compareTRD(args.Input, args.Save)
    if args.Mode=="QA":
        drawPlots(args.Input[0], args.Mode, args.Save)
    if args.Mode=="TRD":
        compareTRD(args.Input, args.Save)
    if args.Mode=="COMPARE":
        DataSets = []
        for file in args.Input:
            print(file)
            dataSetArr = re.findall(r'\/.*?\/', file)
            dataSet=dataSetArr[0].strip("/")
            DataSets.append(dataSet)
        #compareDataSets(DataSets=DataSets, Save=args.Save, doRatios="True")
        compareTRD(DataSets, args.Save)
        
    #if args.Mode=="CompareDataSets":# to compare Full results
        #compareDataSets(args.DataSets, args.Save)
        #ratioDataSets(args.DataSets, args.Save)
        #compareTRD(args.DataSets, args.Save)
#./processResults.py --Mode Full --Input Results/LHC23zzh_cpass2/AnalysisResults.root --Save True

main()
    