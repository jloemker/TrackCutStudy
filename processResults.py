#!/usr/bin/env python3

"""
Post processing script to handle the QA output from trackJetQa i.e. resolution at high pT.
"""

from ROOT import TFile, TLegend, TCanvas, TString, gPad, TH1, TColor, TLatex, gROOT, TH1F, TF1, TArrow, TH2F
from os import path
import os
import configparser
import argparse
import numpy
import json
import pandas
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

canvas_list = {}
#histo_list = {}


#########################

# Alice: add projections and comparison histograms as you have them now in c++
# Johanna: add comparison step for different trackCuts and different data set + prepare standard legends and ratio plots based on what Alice did

#########################


def clear_canvaslist():
    global canvas_list
    l = list(canvas_list.keys())
    for i in l:
        canvas_list[i].Clear()
        del canvas_list[i]
    canvas_list = {}

def canvas(n, x=800, y=800,
           gridx=False, gridy=False,
           tickx=True, ticky=True,
           logx=False, logy=False, logz=True,
           marginx=None):

    global canvas_list
    if canvas_list.setdefault(n, None) is not None:
        can = canvas_list[n]
    else:
        can = TCanvas(f"canvas_{n}", n, x, y)
        can.SetTickx(tickx)
        can.SetTicky(ticky)
        can.SetGridx(gridx)
        can.SetGridy(gridy)
        can.SetLogx(logx)
        can.SetLogy(logy)
        can.SetLogz(logz)
        if x == 800:
            can.SetLeftMargin(0.15)
            can.SetRightMargin(0.13)
        elif x > 1000:
            can.SetLeftMargin(0.12)
            can.SetRightMargin(0.08)
        if marginx is not None:
            can.SetLeftMargin(marginx[0])
            can.SetRightMargin(marginx[1])
        can.SetBottomMargin(0.15)
        can.SetTopMargin(0.1)
        canvas_list[n] = can
    return can

def ProjectThN(histo, NumberOfAxis, dirName):
    title = histo.GetTitle()
    #histo.SetTitle(dirName+" "+title)
    for axis in range(0,NumberOfAxis):
        for next_axis in range(0,NumberOfAxis):
            h = histo.Projection(axis,next_axis)
            #print(h.GetTitle())
            h.SetStats(0)
            can = canvas(dirName+" "+h.GetXaxis().GetTitle()+" vs "+h.GetYaxis().GetTitle())
            can.SetLogz()
            h.SetTitle(" ")
            h.Draw("COLZ")

def drawPlots(InputDir="", Save=True):
    #all available histos
    Kine = {"pt", "pt_TRD", "eta", "phi", "etaVSphi", "EtaPhiPt"}
    TrackPar = {"x", "y", "z", "alpha", "signed1Pt", "snp", "tgl", "flags", "dcaXY", "dcaZ", "length", 
                "Sigma1Pt", "Sigma1Pt_Layer1", "Sigma1Pt_Layer2", "Sigma1Pt_Layers12", "Sigma1Pt_Layer4",
                "Sigma1Pt_Layer5", "Sigma1Pt_Layer6", "Sigma1Pt_Layers45", "Sigma1Pt_Layers56", "Sigma1Pt_Layers46", "Sigma1Pt_Layers456"}
    ITS = {"itsNCls", "itsChi2NCl", "itsHits"}
    TPC = {"tpcNClsFindable", "tpcNClsFound", "tpcNClsShared", "tpcNClsCrossedRows", "tpcFractionSharedCls", "tpcCrossedRowsOverFindableCls", "tpcChi2NCl"}
    EventProp = {"collisionVtxZ", "collisionVtxZnoSel", "collisionVtxZSel8"}
    Centrality = {"FT0M", "FT0A", "FT0C"}
    #Mult = {"NTracksPV", "FT0M", "FT0A", "FT0C", "MultCorrelations"}
    Mult = {"FT0M", "MultCorrelations"}#only these are filled
    #TrackEventPar = {"Sigma1PtFT0Mcent", "Sigma1PtFT0Mmult", "Sigma1PtNTracksPV", "MultCorrelations"}
    TrackEventPar = {"Sigma1PtFT0Mcent", "MultCorrelations"}#only these are filled

   
    Directories = [Kine, TrackPar, ITS, TPC, EventProp, Centrality, Mult, TrackEventPar]
    test = [Mult, TrackEventPar]
    f = TFile.Open(InputDir+"AnalysisResults_FromFull.root", "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    f.ls()
    for dir in test:
        dirName = " "
        for obj in dir:#case switch would be more elegant...
            if dir == Directories[0]:
                dirName = "Kine"
            elif dir == Directories[1]:
                dirName = "TrackPar"
            elif dir == Directories[2]:
                dirName = "ITS"
            elif dir == Directories[3]:
                dirName = "TPC"
            elif dir == Directories[4]:
                dirName = "EventProp"
            elif dir == Directories[5]:
                dirName = "Centrality"
            elif dir == Directories[6]:
                dirName = "Mult"
            elif dir == Directories[7]:
                dirName = "TrackEventPar"
            o = f.Get(f"track-jet-qa/"+dirName+"/"+obj)
            if "TH1" in o.ClassName():
                can = canvas(o.GetTitle())
                o.SetMarkerStyle(21)
                o.SetMarkerColor(4)
                o.GetYaxis().SetTitle("number of entries")
                if "pt" in o.GetName():
                    can.SetLogy()
                elif ("collisionVtxZ" in o.GetName()) or ("Mult"==dirName):
                    o.SetTitle("")# to still display number of events
                else:
                    o.SetTitle("")
                    o.SetStats(0)
                o.Draw("E")
            if "TH2" in o.ClassName():
                can = canvas(o.GetTitle())
                can.SetLogz()
                o.SetStats(0)
                o.Draw("COLZ")
            if "TH3" in o.ClassName():
                print(o.GetXaxis().GetTitle())
                histos = []
                for i in range(1,5):
                    N = o.GetNbinsX()
                    j = i*i
                    can = canvas(o.GetTitle()+str(i))
                    o.SetStats(0)
                    o.GetXaxis().SetRange(i, i*i)
                    h = o.Project3D("yz")
                    h.SetStats(0)
                    h.SetDirectory(0)
                    h.SetTitle("Projection range #it{p}_{T}: "+str(i)+" - "+str(j)+" GeV/#it{c}")
                    h.Draw("COLZ")
                    histos.append(h)
                    o.GetXaxis().SetRange(0, N)
            if "THnSparse" in o.ClassName():
                print("Handling a THnSparse")
                #if dirName == "Mult":
                #    ProjectThN(o,5, dirName)
               # if dirName == "TrackEventPar":
                ProjectThN(o,o.GetNdimensions(), dirName)
                input("Wait2")
            else:
                print("we miss something..")

        n = 0
        if Save==True:
            for i in canvas_list:
                dataSet = InputDir.strip("Results/")
                print(dataSet)
                save_name = f"Save/{dataSet}/{dirName}.pdf"
                save2 = f"Save/{dataSet}/"
                os.makedirs(os.path.dirname(save2), exist_ok=True)
                if n == 0:
                    canvas_list[i].SaveAs(f"{save_name}[")
                    #canvas_list[i].SaveAs(f"{save2}{dataSet}_{i}.png") #to save single images
                canvas_list[i].SaveAs(save_name.replace(".png", f"_{i}.png"))
                n += 1
                if n == len(canvas_list):
                    canvas_list[i].SaveAs(f"{save_name}]")
            input("wait")
            clear_canvaslist()
        else:
            input("Wait")
            clear_canvaslist()
    



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Input", "-in", type=str,
                        default="Results/LHC22s_pass5/", help="Name of the directory where to find the AnalysisResults.root")
    parser.add_argument("--Save", "-s", type=bool,
                        default=False, help="If you set this flag, it will save the documents")
    args = parser.parse_args()

    #get_plots(args.Input, args.Merged, args.Save)
    drawPlots(args.Input, args.Save)

main()
    