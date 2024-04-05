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

def drawPlots(InputDir="", Mode="", Save="", dataSet=None):
    eventMult=0
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
                    if ("no" in o.GetName()) or ("Sel8" in o.GetName()):
                        projectEventProp(o)
                    else:
                        eventMult=projectEventProp(o, extractScale=True)                    
                    print(eventMult)
                elif "EtaPhiPt" in o.GetName():#pt and pT_TRD for extra check later
                    projectCorrelationsTo1D(o, 4, scaled=True, scaleFactor=eventMult)
                    projectEtaPhiInPt(o, [[1,5], [5,15], [15,30],[30,100], [0,200]], logz=True)
                    profile2DProjection(o, [[0,1], [0,2], [0,3]])
                else:
                    continue
            else:
                print(o.GetName())
                print("we miss something..")
            if Save ==False:
                input("Wait and check the histograms !")
    if Save=="True":
        if dataSet == None:
            dataSetArr = re.findall(r'\/.*?\/', InputDir)
            dataSet=dataSetArr[0].strip("/")
        print(f"Save/{dataSet}/TrackQA_{dataSet}.pdf")
        saveCanvasList(canvas_list, f"Save/{dataSet}/TrackQA_{dataSet}.pdf", dataSet)
        clear_canvaslist()
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
        drawPlots(args.Input[0], args.Mode, args.Save, dataSet="LHC23y_pass1")
        compareTRD(args.Input, args.Save, dataSet="LHC23y_pass1")
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
        compareDataSets(DataSets=DataSets, Save=args.Save, doRatios="True")#needs a fix for division by 0 !
        compareTRD(DataSets, args.Save)
main()

#./gijsQA.py --Mode FULL --Input /dcache/alice/jlomker/LHC23y_pass1/AnalysisResults.root --Save True
    
