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

def drawPlots(InputDir="", Mode="", Save="", scale="",dataSet=None, suffix=None):
    log=False
    integral=False
    if scale == "LOG":
        log=True
    elif scale == "INT":
        integral=True
    f = TFile.Open(InputDir, "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    if suffix!=None:
        Id=f"track-jet-qa_{suffix}"
    else:
        Id=f"track-jet-qa"
    get_directories(f,Id)
    eventMult=0
    for dirName in  Directories:
        Dir = f.Get(Id+"/"+dirName).GetListOfKeys()
        for obj in Dir:
            o = f.Get(Id+"/"+dirName+"/"+obj.GetName())
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
                    if ("no" in o.GetName()) or ("Sel8" in o.GetName()):
                        projectEventProp(o)
                    else:
                        eventMult=projectEventProp(o, extractScale=integral)
                    print(eventMult)
                elif "MultCorrelations" in o.GetName() and dirName=="EventProp":
                    continue
                    projectCorrelationsTo1D(o,o.GetNdimensions())
                    projectCorrelationsTo2D(o, [[0,1], [3,4], [5,6], [5,7], [2,7]], logz=log)
                elif "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                    continue
                    projectCorrelationsTo1D(o,o.GetNdimensions())
                    projectCorrelationsTo2D(o, [[1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0]], logz=log)
                    projectCorrelationsTo2D(o, [[1,2], [1,3], [1,4], [1,5], [1,6], [1,7], [1,8], [1,9]], logz=log)
                elif "EtaPhiPt" in o.GetName():
                    projectCorrelationsTo1D(o, 4, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectEtaPhiInPt(o, [[2,10], [10,60], [60,100], [100,199], [2,199]], logz=log)
                    profile2DProjection(o, [[0,1], [0,2], [0,3]])
                elif "xyz" in o.GetName():
                    projectCorrelationsTo1D(o, 5, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]], logz=log)
                    profile2DProjection(o, [[0,2], [0,3], [0,4]])
                elif "tpcCrossedRowsOverFindableCls" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectCorrelationsTo2D(o, [[2,0]], logz=log)
                    profile2DProjection(o, [[0,2]])
                elif "Sigma1Pt" in o.GetName():
                    if "TRD" in o.GetName():#extra function in additional script
                        continue
                    else:
                        projectCorrelationsTo1D(o, 1, logy=log, scaled=integral)
                        projectCorrelationsTo2D(o, [[1,0]], logz=log)
                        profile2DProjection(o, [[0,1]])
                elif "alpha" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]], logz=log)
                    profile2DProjection(o, [[0,2]])
                elif "signed1Pt" in o.GetName():#add ratio pos neg !
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]], logz=log)
                    profile2DProjection(o, [[0,2]])
                    projectCorrelationsTo1D(o, 0, logy=log, scaled=integral, scaleFactor=eventMult)
                elif "snp" in o.GetName():#improve binning !
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    profile2DProjection(o, [[0,2]])
                elif "tgl" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    profile2DProjection(o, [[0,2]])
                elif "length" in o.GetName():
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    profile2DProjection(o, [[0,2]])
                else:
                    projectCorrelationsTo1D(o, 2, dim_min=2, logy=log, scaled=integral, scaleFactor=eventMult)
                    projectCorrelationsTo2D(o, [[2,0], [2,1]], logz=log)
                    profile2DProjection(o, [[0,2]])
            else:
                print(o.GetName())
                print("we miss something..")
            if Save ==False:
                input("Wait and check the histograms !")
    if Save=="True":
        if dataSet==None :
            dataSetArr = re.findall(r'\/.*?\/', InputDir)
            dataSet=dataSetArr[0].strip("/")
        print(f"Save/{dataSet}/TrackQA_{dataSet}_{scale}.pdf")
        if suffix!=None:
            saveCanvasList(canvas_list, f"Save/{dataSet}/TrackQA_{suffix}_{scale}.pdf", dataSet)
        else:
            saveCanvasList(canvas_list, f"Save/{dataSet}/TrackQA_{dataSet}_{scale}.pdf", dataSet)
        clear_canvaslist()
    else:
        print("we don't save this ...")
        clear_canvaslist()


    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Mode", "-m", type=str,
                        default=["FULL", "TRD", "COMPARE"], help="Activate 'CompareDataSets', or plots QA AnalysisResults from 'Full' , 'Tree'(derived) results")
    parser.add_argument("--Input", "-in", type=str,
                        default="Results/LHC22s_pass5/AnalysisResults.root", help="Path and File input", nargs="+")
    parser.add_argument("--Save", "-s", type=str,
                        default=["False", "True"], help="If you set this flag, it will save the documents")
    parser.add_argument("--DataSets", "-d", type=str,
                        default="LHC23y_pass1", help="To specify the name for saving", nargs="+")
    parser.add_argument("--Suffix", "-x", type=str,
                        default=None, help="Suffix for subwagon output")
    parser.add_argument("--Scaled", "-sc", type=str,
                        default=["LOG", "INT","NONE"])
    args = parser.parse_args()

    if args.Mode=="FULL":
        if args.Suffix!=None:
            drawPlots(args.Input[0], args.Mode, args.Save, args.Scaled, dataSet=args.DataSets[0], suffix=args.Suffix)
            compareTRD(args.Input, args.Save, dataSet=args.DataSets[0], suffix=args.Suffix)
#./processResults.py --Mode FULL --Input Results/LHC23_pass4_Thin_small/AnalysisResults.root --DataSet LHC23 --Save True --Scaled LOG --Suffix WoPtEta
        else:
            print("no suffix")
            drawPlots(args.Input[0], args.Mode, args.Save, args.Scaled, dataSet=args.DataSets[0])
            compareTRD(args.Input, args.Save, dataSet=args.DataSets[0])
# ./processResults.py --Mode FULL --Input /dcache/alice/jlomker/LHC23k4b/AnalysisResults.root --DataSet LHC23k4b --Save True
    if args.Mode=="QA":
        drawPlots(args.Input[0], args.Mode, args.Save, args.Scaled, dataSet=args.DataSets[0])
    if args.Mode=="TRD":
        compareTRD(args.Input, args.Save)
    if args.Mode=="COMPARE":
        DataSets = []
        for file in args.Input:
            print(file)
            dataSetArr = re.findall(r'\/.*?\/', file)
            dataSet=dataSetArr[0].strip("/")
            DataSets.append(dataSet)
        compareDataSets(DataSets=DataSets, Save=args.Save, doRatios="True")#needs a fix for division by 0 !
        compareTRD(DataSets, args.Save)
main()
    
