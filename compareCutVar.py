#!/usr/bin/env python3

"""
Comparison script for the cutvariation study - trackJetQa 
"""

import ROOT
from ROOT import TFile
import numpy as np
import argparse
import re
from common import Directories, get_directories, canvas, canvas_list, clear_canvaslist, saveCanvasList, createLegend
from projection import projectEventProp, projectCorrelationsTo1D, profile2DProjection, projectCorrelationsTo2D, projectEtaPhiInPt
from compareResults import compareDataSets

#def compareCutvariation(DataSet, Save="",CutVar=[]): one could add some more cut ralated plots.. but for me its enough rn

def plotResults(DataSet, Save="",CutVar=[]):
    files = {}
    for cut in CutVar:#here some pretty plots
        f = TFile.Open(f"Results/{DataSet}/CutVariations/AnalysisResults_{cut}.root", "READ")
        if not f or not f.IsOpen():
            print("Did not get", f)
            return
        if Directories == []:
            get_directories(f, f"track-jet-qa{cut}")
        files[cut] = f
        for dirName in  Directories:
            dir = f.Get(f"track-jet-qa{cut}/"+dirName).GetListOfKeys()
            for obj in dir:
                o = f.Get(f"track-jet-qa{cut}/"+dirName+"/"+obj.GetName())
                if not o:
                    print("Did not get", o, " as object ", obj)
                elif "TH1" in o.ClassName():#Rejectionhisto in EventProp/rejectedCollId
                    can = canvas(o.GetTitle())
                    o.SetMarkerStyle(21)
                    o.SetMarkerColor(4)
                    o.GetYaxis().SetTitle("number of entries")
                    o.Draw("E")
                elif "TH2" in o.ClassName():#Flag bits
                    continue
                elif "THnSparse" in o.ClassName():
                    if "collisionVtxZ" in o.GetName():
                        projectEventProp(o)
                    elif "MultCorrelations" in o.GetName() and dirName=="EventProp":
                        continue
                        projectCorrelationsTo2D(o, [[0,1], [3,4], [5,6], [5,7], [2,7]])#MultCorrelations_proj_4_3 (Potential memory leak).
                        input("wait")
                    elif "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                        continue
                        projectCorrelationsTo2D(o, [[1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0]])
                        projectCorrelationsTo2D(o, [[1,2], [1,3], [1,4], [1,5], [1,6], [1,7], [1,8], [1,9]])
                    elif "EtaPhiPt" in o.GetName():#pt and pT_TRD for extra check later
                        projectEtaPhiInPt(o, [[1,5], [5,15], [15,30],[30,100], [0,200]], logz=True)#check binning
                    if "xyz" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "alpha" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "signed1Pt" in o.GetName():#add ratio pos neg !
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "dcaXY" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "dcaZ" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "itsNCls" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "itsChi2NCl" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "itsHits" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0]])
                    if "tpcNClsFindable" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "tpcNClsFound" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "tpcNClsShared" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "tpcNClsCrossedRows" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "tpcFractionSharedCls" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "tpcCrossedRowsOverFindableCls" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0]])
                    if "tpcChi2NCl" in o.GetName():
                        projectCorrelationsTo2D(o, [[2,0], [2,1]])
                    if "Sigma1Pt" in o.GetName():
                        if "TRD" in o.GetName():#write extra function in additional script
                            continue
                        else:
                            projectCorrelationsTo2D(o, [[1,0]])
                else:
                    print(o.GetName())
                    print("we miss something..")
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/Compare_{DataSet}_CutVariations/2DTrackQa_{cut}.pdf", f"Compare_{DataSet}_CutVariations")  
            clear_canvaslist()
        else:
            print("we don't save this ...")
            clear_canvaslist()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--CutVar", "-c", type=str,
                        default=["globalTrack", "maxDcaZ1","maxDcaZ3"], help="Activate 'CompareDataSets', or plots 2D QA AnalysisResults from cutvariations", nargs="+")
    parser.add_argument("--DataSet", "-d", type=str,
                        default="", help="Path and File input")
    parser.add_argument("--Save", "-s", type=str,
                        default=["False", "True"], help="If you set this flag, it will save the documents")
    parser.add_argument("--Compare", "-comp", type=str,
                        default=["False", "True"], help="If you set this flag, it will compare the cutvariations in 1D")
    args = parser.parse_args()

    if args.Compare == "True":
        compareDataSets(DataSets=[args.DataSet], Save=args.Save, CutVars=args.CutVar, doRatios=True)
    else:
        for cut in args.CutVar:
            plotResults(DataSet=args.DataSet, Save=args.Save, CutVar=[cut])
main()
