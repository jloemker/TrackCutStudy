#!/usr/bin/env python3

"""
Comparison script for the cutvariation study - trackJetQa 
"""

import ROOT
from ROOT import TFile
import numpy as np
import re
from common import Directories, get_directories, canvas, canvas_list, clear_canvaslist, saveCanvasList, createLegend
from projection import projectEventProp, projectCorrelationsTo1D, profile2DProjection

def plotResults(InputDir):
    f = TFile.Open(InputDir, "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    get_directories(f, f"track-jet-qa")

def getCutvariation(DataSet="", CutVar=[]):
    for cut in CutVar:
        f = TFile.Open(f"Results/{DataSet}/CutVariations/AnalysisResults_{cut}.root", "READ")
        print(cut)

def main():
    getCutvariation("LHC_Test1", ["maxDcaZ1", "maxDcaZ3"])

main()
