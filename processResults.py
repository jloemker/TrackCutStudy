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

def project(h):
    h1 = h.Projection(1) # pT
    h2 = h.Projection(2) # sigma
    h3 = h.Projection(0) # multiplicity measures
    h1.SetStats(0)
    h2.SetStats(0)
    h3.SetStats(0)
    h1.SetTitle("")
    h2.SetTitle("")
    h3.SetTitle("")
    h1.GetYaxis().SetTitle("Number of entries")
    h2.GetYaxis().SetTitle("Number of entries")
    h3.GetYaxis().SetTitle("Number of entries")
    h1.GetXaxis().SetTitle("#it{p}_{T} [GeV/#it{c}]")
    h2.GetXaxis().SetTitle("#sigma(1/#it{p}_{T})")
    if "Track" in h.GetTitle():
        h3.GetXaxis().SetTitle("Number of tracks PV")
    elif "mult" in h.GetTitle():
        h3.GetXaxis().SetTitle("Multiplicity FT0M")
    return h1,h2,h3

def project2D(h):
    h12 = h.Projection(1,2)#PtVsSigmaPtViaTracks
    h13 = h.Projection(2,0)#SigmaVsTracksPV
    h10 = h.Projection(1,0)#PtVsTrackPV
    h12.SetStats(0)
    h13.SetStats(0)
    h10.SetStats(0)
    h12.SetTitle("")
    h13.SetTitle("")
    h10.SetTitle("")
    h12.GetXaxis().SetTitle("#sigma(1/#it{p}_{T})")
    h12.GetYaxis().SetTitle("#it{p}_{T} [GeV/#it{c}]")
    h13.GetYaxis().SetTitle("#sigma(1/#it{p}_{T})")
    h10.GetYaxis().SetTitle("#it{p}_{T}")
    if "Track" in h.GetTitle():
        h13.GetXaxis().SetTitle("Number of tracks PV")
        h10.GetXaxis().SetTitle("Number of tracks PV")
    elif "mult" in h.GetTitle():
        h13.GetXaxis().SetTitle("Multiplicity FT0M")
        h10.GetXaxis().SetTitle("Multiplicity FT0M")
    return h12, h13, h10

def product(pt, sigmapT):#pT / sigmaPt
    result = sigmapT.Clone("sigmapT")
    result.Reset()
    for i in range(0,sigmapT.GetNbinsX()):
        if sigmapT.GetBinContent(i) > 0:
            result.SetBinContent(i, pt.GetBinContent(i)/sigmapT.GetBinContent(i))
            err = pow(pow(pt.GetBinError(i)/sigmapT.GetBinContent(i), 2) + pow(sigmapT.GetBinContent(i)*pt.GetBinError(i)/(sigmapT.GetBinContent(i)*sigmapT.GetBinContent(i)),2), 1/2)
            result.SetBinError(i, err )
        else:
            result.SetBinError(i, 0 )
    result.GetYaxis().SetTitle("#it{p}_{T}/#sigma(1/#it{p}_{T})")
    return result


def get_plots(InputDir="", Merged=True, Save=""):# old stuff.. 
    histoList = {"Sigma1PtFT0Mcent", "Sigma1PtFT0Mmult", "Sigma1PtNTracksPV"}
    if Merged:
        f = TFile.Open(InputDir+"AnalysisResults.root", "READ")
        if not f or not f.IsOpen():
            print("Did not get", f)
            return
        f.ls()
        FT0M = f.Get("track-jet-qa/TrackEventPar/Sigma1PtFT0Mmult")
        Tracks = f.Get("track-jet-qa/TrackEventPar/Sigma1PtNTracksPV")
        #correlation(FT0M, Tracks)
        input("Wait")
        clear_canvaslist()
        for obj in histoList:
            h = f.Get("track-jet-qa/TrackEventPar/"+obj)
            if "THnSparse" in h.ClassName():
                print("Handling a THnSparse")
                sigma_axis = None
                cent_axis = None
                pt_axis = None
                mult_axis = None
                track_axis = None
                if "multiplicity" in h.GetTitle():
                    print("multiplicity")
                    #inclusive
                    h1, h2, h3 = project(h)
                    h12, h13, h10 = project2D(h)
                    hsigma = product(h1, h2)
                    #in ranges
                    cMult= canvas("Mult")
                    h3.Draw("E")
                    cPt = canvas("InclusivePtViaMult")
                    cPt.SetLogy()
                    h1.Draw("E")
                    cSigma = canvas("InlcusiveSigmaViaMult")
                    cSigma.SetLogy()
                    h2.Draw("E")
                    corrSigma = canvas("CorrectedSigmaPtViaMult")
                    corrSigma.SetLogy()
                    hsigma.Draw("E")
                    cSigmaPt = canvas("PtVsSigmaPtViaMult")
                    cSigmaPt.SetLogz()
                    h12.Draw("COLZ")
                    cSigmaTrack = canvas("SigmaVsMult")
                    cSigmaTrack.SetLogz()
                    h13.Draw("COLZ")
                    cSigmaPt = canvas("PtVsMult")
                    cSigmaPt.SetLogz()
                    h10.Draw("COLZ")
                    if Save=="False":
                        input("Wait")
 
                if "NTracksPV" in h.GetTitle(): #THnSparse::GetAxis(12)->SetRange(from_bin, to_bin);
                    #projectionInRange(h,10)
                    #clear_canvaslist()
                    print("NTracksPV")
                    #inclusive
                    h1, h2, h3 = project(h)
                    h12, h13, h10 = project2D(h)
                    #hsigma = product(h1, h2)
                    #make array of histos for projections in NTracks ranges
                    hT={}
                    #in ranges
                    cTrack = canvas("NTrackPV")
                    h3.Draw("E")
                    #cPt = canvas("InclusivePtViaTracks")
                    #cPt.SetLogy()
                    #h1.Draw("E")
                    #cSigma = canvas("InlcusiveSigmaViaTracks")
                    #cSigma.SetLogy()
                    #h2.Draw("E")
                    #corrSigma = canvas("CorrectedSigmaPtViaTracks")
                    #corrSigma.SetLogy()
                    #hsigma.Draw("E")
                    cSigmaPt = canvas("PtVsSigmaPtViaTracks")
                    cSigmaPt.SetLogz()
                    h12.Draw("COLZ")
                    cSigmaTrack = canvas("SigmaVsTracksPV")
                    cSigmaTrack.SetLogz()
                    h13.Draw("COLZ")
                    cSigmaPt = canvas("PtVsTrackPV")
                    cSigmaPt.SetLogz()
                    h10.Draw("COLZ")
                    if Save=="False":
                        input("Wait")
                if "centrality" in h.GetTitle(): #Not Yet Calibrated
                    print("centrality")

                if Save=="True":
                    n = 0
                    for i in canvas_list:
                        dataSet = InputDir.strip("Results/")
                        print(dataSet)
                        save_name = f"Save/{dataSet}.pdf"
                        save2 = f"Save/{dataSet}/"
                        os.makedirs(os.path.dirname(save2), exist_ok=True)
                        if n == 0:
                            canvas_list[i].SaveAs(f"{save_name}[")
                        #canvas_list[i].SaveAs(f"{save2}{dataSet}_{i}.png") #to save single images
                        canvas_list[i].SaveAs(save_name.replace(".png", f"_{i}.png"))
                        n += 1
                        if n == len(canvas_list):
                            canvas_list[i].SaveAs(f"{save_name}]")



#########################

# ALICE FUnctions for projetions

#########################


def drawPlots(InputDir="", Save=True):
    Kine = {"pt", "pt_TRD", "eta", "phi", "etaVSphi", "EtaPhiPt"}
    TrackPar = {"x", "y", "z", "alpha", "signed1Pt", "snp", "tgl", "flags", "dcaXY", "dcaZ", "length", 
                "Sigma1Pt", "Sigma1Pt_Layer1", "Sigma1Pt_Layer2", "Sigma1Pt_Layers12", "Sigma1Pt_Layer4",
                "Sigma1Pt_Layer5", "Sigma1Pt_Layer6", "Sigma1Pt_Layers45", "Sigma1Pt_Layers56", "Sigma1Pt_Layers46", "Sigma1Pt_Layers456"}
    ITS = {"itsNCls", "itsChi2NCl", "itsHits"}
    TPC = {"tpcNClsFindable", "tpcNClsFound", "tpcNClsShared", "tpcNClsCrossedRows", "tpcFractionSharedCls", "tpcCrossedRowsOverFindableCls", "tpcChi2NCl"}
    EventProp = {"collisionVtxZ", "collisionVtxZnoSel", "collisionVtxZSel8"}
    Centrality = {"FT0M", "FT0A", "FT0C"}
    Mult = {"NTracksPV", "FT0M", "FT0A", "FT0C", "MultCorrelations"}
    TrackEventPar = {"Sigma1PtFT0Mcent", "Sigma1PtFT0Mmult", "Sigma1PtNTracksPV", "MultCorrelations"}

    #histos.add("Mult/MultCorrelations", "MultCorrelations", HistType::kTHnSparseD, {axisPercentileFT0A, axisPercentileFT0C, axisMultiplicityFT0A, axisMultiplicityFT0C, axisMultiplicityPV});

    #histos.add("TrackEventPar/Sigma1PtFT0Mcent", "Sigma1Pt vs pT vs FT0M centrality", HistType::kTHnSparseD, {axisPercentileFT0M, axisPt, axisSigma1OverPt});
    #histos.add("TrackEventPar/Sigma1PtFT0Mmult", "Sigma1Pt vs pT vs FT0A,C multiplicity", HistType::kTHnSparseD, {axisMultiplicityFT0M, axisPt, axisSigma1OverPt});
    #histos.add("TrackEventPar/Sigma1PtNTracksPV", "Sigma1Pt vs pT vs NTracksPV", HistType::kTHnSparseD, {axisMultiplicityPV, axisPt, axisSigma1OverPt});
    #histos.add("TrackEventPar/MultCorrelations", "Sigma1Pt vs pT vs MultCorrelations", HistType::kTHnSparseD, {axisSigma1OverPt, axisPt, axisPercentileFT0A, axisPercentileFT0C, axisMultiplicityFT0A, axisMultiplicityFT0C, axisMultiplicityPV});

    Directories = [Kine, TrackPar, ITS, TPC, EventProp, Centrality, Mult, TrackEventPar]
    f = TFile.Open(InputDir+"AnalysisResults.root", "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    f.ls()
    for dir in Directories:
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
            #input("Wait")
            if "THnSparse" in o.ClassName():
                print("Handling a THnSparse")
                sigma_axis = None
                cent_axis = None
                pt_axis = None
                mult_axis = None
                track_axis = None
                if "multiplicity" in o.GetTitle():
                    print("multiplicity")
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
            clear_canvaslist()
    input("Wait")
    



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
    