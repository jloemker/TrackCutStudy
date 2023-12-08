#!/usr/bin/env python3

"""
Post processing script to handle the QA output from trackJetQa i.e. resolution at high pT.
"""

import ROOT
from ROOT import TFile, TLegend, TCanvas, TString, gPad, TH1, TColor, TLatex, gROOT, TH1F, TF1, TArrow, TH2F, TProfile, kAzure, kRainbow
from os import path
import os
import configparser
import argparse
import numpy
import json
import pandas
import warnings

ROOT.gStyle.SetPalette(kRainbow)

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

Directories = ['Kine', 'TrackPar', 'ITS', 'TPC', 'EventProp', 'Mult', 'TrackEventPar', 'Centrality'] 
canvas_list = {}
nice_frames = {}
legends = []
#histo_list = {}


#########################
# Johanna: 
#   - fix TRD (this is very lengthly and should be improved)
#   - add user specification
#   - add comparison step for cutvariations
#   - improve general comparison script - make axis pretty pipapo - correct the task on o2physics for the sigma1pt stuff; also add sigmaPt*pT to THnSparse !
#   - add multBinning for projections of ThNSparses uncertainty in ranges (needed once multiplicites are calibrated)
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
        can.SetTopMargin(0.15)
        canvas_list[n] = can
    return can

def createLegend(x=[0.7, 0.92], y=[0.8, 0.95], title="",
                     columns=1, objects=None, linecolor=0):
    global legends
    leg = TLegend(x[0], y[0], x[1], y[1], title)
    leg.SetLineColor(linecolor)
    leg.SetNColumns(columns)
    if objects is not None:
        if type(objects) is list:
            for o in objects:
                leg.AddEntry(o, f"{o.GetName()}", "lp")
        elif type(objects) is dict:
            for o in objects:
                leg.AddEntry(objects[o], "", "lp")
    legends.append(leg)
    return leg


def saveCanvasList(canvas_list, save_name, dataSet=None):
    n = 0
    for i in canvas_list:
        if dataSet:
            print(dataSet)
            save2 = f"Save/{dataSet}/"
            os.makedirs(os.path.dirname(save2), exist_ok=True)
        if n == 0:
            canvas_list[i].SaveAs(f"{save_name}[")
            #canvas_list[i].SaveAs(f"{save2}{dataSet}_{i}.png") #to save single images
        canvas_list[i].SaveAs(save_name.replace(".png", f"_{i}.png"))
        n += 1
        if n == len(canvas_list):
            canvas_list[i].SaveAs(f"{save_name}]")
    clear_canvaslist()

# TH2 histograms X profile
def profileTH2X(histo, dirName):
    h_profileX = histo.ProfileX()
    h_profileX.SetTitle(histo.GetTitle() + " X Profile")
    h_profileX.GetYaxis().SetTitle("mean value")
    h_profileX.SetLineColor(kAzure+7)
    h_profileX.SetLineWidth(3)
    canX = canvas(dirName+" "+h_profileX.GetTitle())
    h_profileX.Draw("E")

def projectTH2(o, dirName):
    hx = o.ProjectionX()
    hx.SetLineColor(kAzure+7)
    hx.SetLineWidth(3)
    hx.SetStats(0)
    hx.SetTitle("Eta vs Phi projection x")
    canx = canvas(dirName+hx.GetTitle())
    hx.GetYaxis().SetTitle("number of entires")
    hx.Draw("E")
    canx.SetLogx()
    hy = o.ProjectionY()
    hy.SetLineColor(kAzure+7)
    hy.SetLineWidth(3)
    hy.SetStats(0)
    hy.SetTitle("Eta vs Phi projection y")
    cany = canvas(dirName+hy.GetTitle())
    hy.GetYaxis().SetTitle("number of entires")
    hy.Draw("E")
    cany.SetLogy()  

def ProjectTHnSparse(hist, NumberOfAxis, dirName=None):
    hlist = []
    for axis in range(0,NumberOfAxis):
        histo = hist.Projection(axis)
        histo.SetTitle(hist.GetAxis(axis).GetTitle())
        #hlist.append(histo)
        if "Centrality" in (hist.GetAxis(axis).GetTitle()):
            continue
        for next_axis in range(0,NumberOfAxis):
            if "Centrality" in (hist.GetAxis(next_axis).GetTitle()):
                continue
            if hist.GetAxis(axis).GetTitle() == hist.GetAxis(next_axis).GetTitle():
                continue
            h = hist.Projection(axis,next_axis)
            h.SetTitle(h.GetXaxis().GetTitle()+"vs"+h.GetYaxis().GetTitle())
            h.SetStats(0)
            if dirName:
                if dirName+" "+h.GetYaxis().GetTitle()+"vs"+h.GetXaxis().GetTitle() in canvas_list:
                    continue
                can = canvas(dirName+" "+h.GetTitle())
                can.SetLogz()
                h.SetTitle(" ")
                h.Draw("COLZ")
            #profX = h.ProfileX()
            #profX.SetTitle("Profile X "+h.GetXaxis().GetTitle()+" "+h.GetYaxis().GetTitle())
            #profY = h.ProfileY()
            #profY.SetTitle("Profile Y "+h.GetXaxis().GetTitle()+" "+h.GetYaxis().GetTitle())
            #hlist.append(profX)
            #hlist.append(profY)
    if dirName==None:
        #for h in hlist:
        #    print(h.GetXaxis().GetTitle())
        #    print(h.GetTitle())
            #print(h.GetName())
        return hlist


def drawPlots(InputDir="", Mode="", Save=""):
    f = TFile.Open(InputDir, "READ")
    if not f or not f.IsOpen():
        print("Did not get", f)
        return
    for dirName in  Directories:
        if (Mode=="Tree") and (dirName=="EventProp"):
            f.Close()
            # the AnalysisResults.root file, produced on hyperloop with tree creation->Contains eventProp's.
            f = TFile.Open(InputDir.strip("AnalysisResults_trees.root")+"AnalysisResults.root", "READ")
        elif dirName == "Centrality":#not calibrated
            return
        dir = f.Get(f"track-jet-qa/"+dirName).GetListOfKeys()
        for obj in dir:
            o = f.Get(f"track-jet-qa/"+dirName+"/"+obj.GetName())
            if not o:
                print("Did not get", o, " as object ", obj)
                continue
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
            elif "TH2" in o.ClassName():
                can = canvas(o.GetTitle())
                #sigma 1/pT labels are ugly.
                #if "#it{sigma1}{p}_{T}" in o.GetXaxis().GetTitle():
                #    o.GetXaxis().SetTitle("#it{p}_{T} * #sigma(1/#it{p}_{T})")
                #    input("wait")
                #if "p_{T} * sigma1{p}" == o.GetYaxis().GetTitle():
                #    o.GetYaxis().SetTitle("#it{p}_{T} * #sigma(1/#it{p}_{T})")
                #    input("wait")
                can.SetLogz()
                o.SetStats(0)
                o.Draw("COLZ")
                profileTH2X(o, dirName)
                if "etaVSphi" == o.GetName():
                    projectTH2(o, dirName)
            elif "TH3" in o.ClassName():
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
                    h.SetTitle("Projection range #it{p}_{T}: "+str(o.GetXaxis().GetBinCenter(i))+" - "+str(o.GetXaxis().GetBinCenter(j))+" GeV/#it{c}")
                    h.Draw("COLZ")
                    histos.append(h)
                    o.GetXaxis().SetRange(0, N)
            elif "THnSparse" in o.ClassName():
                ProjectTHnSparse(o,o.GetNdimensions(), dirName)
            else:
                print("we miss something..")
                print(o.ClassName())
        if Save=="True":
            dataSet = InputDir.strip("Results/"+"/AnalysisResults.root"+"/AnalysisResults_trees.root")
            if Mode=="Tree":
                save2 = f"Save_Tree/{dataSet}/"
                os.makedirs(os.path.dirname(save2), exist_ok=True)
                save_name = f"Save_Tree/{dataSet}/{dirName}.pdf"
            if Mode=="Full":
                save_name = f"Save/{dataSet}/{dirName}.pdf"
            saveCanvasList(canvas_list, save_name, dataSet)
            #input("wait")
        else:
            print("we don't save this ...")
            #input(dirName)
            clear_canvaslist()

def compareDataSets(DataSets={}, Save=""):
    files = {}
    histos = []
    for dataSet in DataSets:#make first one the base line for ratios and saving
        f = TFile.Open(f"Results/{dataSet}/AnalysisResults.root", "READ")
        if not f or not f.IsOpen():
            print("Did not get", f)
            return
        files[dataSet] = f
        for dirName in  Directories:
            if dirName == "Centrality":#not calibrated
                continue
            dir = f.Get(f"track-jet-qa/"+dirName).GetListOfKeys()
            for obj in dir:
                o = f.Get(f"track-jet-qa/"+dirName+"/"+obj.GetName())
                if not o:
                    print("Did not get", o, " as object ", obj)
                    continue
                if "TH1" in o.ClassName():
                    #print(o.GetName())
                    h = o.Clone()
                    h.SetName(dataSet+" "+dirName+" "+o.GetName())
                    histos.append(h)
                elif "TH2" in o.ClassName():#to be done as well
                    prof = o.ProfileX()
                    prof.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Profile "+o.GetXaxis().GetTitle())
                    prof.SetTitle(o.GetTitle()+" Profile "+o.GetXaxis().GetTitle())
                    histos.append(prof)
                    proj = o.ProjectionY()
                    proj.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Projection "+o.GetYaxis().GetTitle())
                    proj.SetTitle(o.GetTitle()+" Projection "+o.GetYaxis().GetTitle())
                    histos.append(proj)
                    if not "#it{p}_{T}" in o.GetXaxis().GetTitle():
                        proj = o.ProjectionX()
                        proj.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Projection "+o.GetXaxis().GetTitle())
                        proj.SetTitle(o.GetTitle()+" Projection "+o.GetXaxis().GetTitle())
                        histos.append(proj)
                elif "TH3":
                    continue
                elif "THnSparse" in o.ClassName():
                    continue
                else:
                    print("We miss some histotypes...")
    for dirName in Directories:
        for h in histos:
            if not dirName in h.GetName():
                continue
            if (f"Compare_{h.GetTitle()}") in canvas_list:
                continue
            else:
                can = canvas("Compare_"+h.GetTitle())
                name = h.GetTitle()
                histo = [h for h in histos if h.GetTitle() == name]
                col = 0
                can.cd()
                for h in histo:
                    col +=1
                    nEntries = h.GetEntries()
                    newName = h.GetName().strip(" "+dirName+" "+h.GetTitle())[:16]
                    h.SetName(newName)#+": "+f"{nEntries}")
                    h.SetLineColor(col)
                    h.SetMarkerColor(col)
                    h.SetMarkerStyle(22+col)
                    h.SetStats(0)
                    h.SetDirectory(0)
                    if col == 1:
                        h.Draw("E")
                    else:
                        h.Draw("SAME")
                    #input("Wait")
                legend = createLegend(objects=histo, x=[0.2,0.8], y=[0.86,0.97], columns=len(DataSets))
                legend.Draw("SAME")
                can.SetLogy()
                #input("wait..")
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/Compare{DataSets[0]}_to_{DataSets[1]}/{dirName}.pdf", f"Compare{DataSets[0]}_to_{DataSets[1]}")
        else:
            print("Wait, don't save this ... ")
            clear_canvaslist()

def ratioDataSets(DataSets={}, Save=""):#Legend + other histo types !
    files = {}
    histos = []
    for dataSet in DataSets:#make first one the base line for ratios and saving
        f = TFile.Open(f"Results/{dataSet}/AnalysisResults.root", "READ")
        if not f or not f.IsOpen():
            print("Did not get", f)
            return
        files[dataSet] = f
        for dirName in  Directories:
            if dirName == "Centrality":#not calibrated
                continue
            dir = f.Get(f"track-jet-qa/"+dirName).GetListOfKeys()
            for obj in dir:
                o = f.Get(f"track-jet-qa/"+dirName+"/"+obj.GetName())
                if not o:
                    print("Did not get", o, " as object ", obj)
                    continue
                if "TH1" in o.ClassName():
                    #print(o.GetName())
                    h = o.Clone()
                    h.SetName(dataSet+" "+dirName+" "+o.GetName())
                    histos.append(h)
                elif "TH2" in o.ClassName():#to be done as well
                    prof = o.ProfileX()
                    prof.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Profile "+o.GetXaxis().GetTitle())
                    prof.SetTitle(o.GetTitle()+" Profile "+o.GetXaxis().GetTitle())
                    histos.append(prof)
                    proj = o.ProjectionY()
                    proj.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Projection "+o.GetYaxis().GetTitle())
                    proj.SetTitle(o.GetTitle()+" Projection "+o.GetYaxis().GetTitle())
                    histos.append(proj)
                    if not "#it{p}_{T}" in o.GetXaxis().GetTitle():
                        proj = o.ProjectionX()
                        proj.SetName(" "+dataSet+" "+dirName+" "+o.GetName()+"Projection "+o.GetXaxis().GetTitle())
                        proj.SetTitle(o.GetTitle()+" Projection "+o.GetXaxis().GetTitle())
                        histos.append(proj)
                elif "TH3":
                    continue
                elif "THnSparse" in o.ClassName():
                    continue
                else:
                    print("We miss some histotypes...")
    for dirName in Directories:
        for h in histos:
            if not dirName in h.GetName():
                continue
            if (f"Compare_{h.GetTitle()}") in canvas_list:
                continue
            else:
                can = canvas("Ratio_"+h.GetTitle())
                name = h.GetTitle()
                histo = [h for h in histos if h.GetTitle() == name]
                col = 0
                can.cd()
                for h in histo:
                    col +=1
                    nEntries = h.GetEntries()
                    newName = h.GetName().strip(" "+dirName+" "+h.GetTitle())[:16]
                    h.SetName(newName)#+": "+f"{nEntries}")
                    h.SetLineColor(col)
                    h.SetMarkerColor(col)
                    h.SetMarkerStyle(22+col)
                    h.SetStats(0)
                    if col == 1:
                        continue
                    else:
                        h.Sumw2()
                        h.Divide(histo[0])
                        h.GetYaxis().SetTitle("(DataSet/"+histo[0].GetName()+")")
                        if col == 2:
                            h.Draw("E")
                        else:
                            h.Draw("SAME")
                    #input("Wait")
                legend = createLegend(objects=histo, x=[0.2,0.8], y=[0.86,0.97], columns=len(DataSets))
                legend.Draw("SAME")
                can.SetLogy()
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/Compare{DataSets[0]}_to_{DataSets[1]}/{dirName}Ratios.pdf", f"Compare{DataSets[0]}_to_{DataSets[1]}")
        else:
            print("Wait, we are at ")
            clear_canvaslist()
    print("Compared ratios of full dataset results")

def doRatio(pt,ptTRD, nSet, title="", makerStyle=0):
    r = pt.Clone()
    r.SetStats(0)
    r.Divide(ptTRD)
    r.SetLineColor(nSet+1)
    r.SetMarkerStyle(makerStyle)
    r.SetMarkerColor(nSet+1)
    r.GetYaxis().SetTitle(title)
    r.SetTitle(" ")
    return r

def draw2DSigmaPt(title=" ",sigma1Pt=None):
    sigma1Pt.SetStats(0)
    sigma1Pt.SetTitle(title)
    sigma1Pt.GetYaxis().SetTitle("#it{p}_{T} * #sigma(1/#it{p}_{T})")
    sigma1Pt.Draw("COLZ")
    return sigma1Pt

def draw2DSigmaPtOnCanvas(canS, sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, DataSets):
    if len(DataSets)==1:
        canS.Divide(1,3)
        canS.cd(1)
        sigma1Pt = draw2DSigmaPt("all tracks", sigma1Pt)
        canS.cd(1).SetLogz()
        canS.cd(2)
        sigma1Pt_TRD = draw2DSigmaPt("track.hasTRD()", sigma1Pt_TRD)
        canS.cd(2).SetLogz()
        canS.cd(3)
        sigma1Pt_noTRD = draw2DSigmaPt("!track.hasTRD()", sigma1Pt_noTRD)
        canS.cd(3).SetLogz()
    else:
        if dataSet == DataSets[0]:
            canS.cd(1)
            sigma1Pt = draw2DSigmaPt(f"{dataSet} all tracks",sigma1Pt)
            canS.cd(1).SetLogz()
            canS.cd(2)
            sigma1Pt_TRD = draw2DSigmaPt(f"{dataSet} track.hasTRD()",sigma1Pt_TRD)
            canS.cd(2).SetLogz()
            canS.cd(3)
            sigma1Pt_noTRD = draw2DSigmaPt(f"{dataSet} ! track.hasTRD()",sigma1Pt_noTRD)
            canS.cd(3).SetLogz()
        elif(len(DataSets)==2):
            canS.cd(4)
            sigma1Pt = draw2DSigmaPt(f"{dataSet} all tracks",sigma1Pt)
            canS.cd(4).SetLogz()
            canS.cd(5)
            sigma1Pt_TRD = draw2DSigmaPt(f"{dataSet} track.hasTRD()",sigma1Pt_TRD)
            canS.cd(5).SetLogz()
            canS.cd(6)
            sigma1Pt_noTRD = draw2DSigmaPt(f"{dataSet} ! track.hasTRD()",sigma1Pt_noTRD)
            canS.cd(6).SetLogz()
        else:
            print("Not enought canvas splits for sigma1Pt !!!")
    
def compareTRD(DataSets={}, Save=""):
    files = {}
    histos = []
    if len(DataSets) == 1:
        f = TFile.Open(f"{DataSets[0]}","READ")
        dataSet=DataSets[0].strip("Results/")[:15]#length of data set name
        sigma1Pt = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt")
        sigma1Pt_TRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasTRD")
        sigma1Pt_noTRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasNoTRD")

        canS = canvas("TH2 Sigma1Pt vs Pt", x=800, y=1200)
        draw2DSigmaPtOnCanvas(canS, sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, DataSets)
        #write a function that does this !
        canP = canvas("TH2 Sigma1Pt Profile over pT")
        prof = sigma1Pt.ProfileX()
        profTRD = sigma1Pt_TRD.ProfileX()
        profNoTRD = sigma1Pt_noTRD.ProfileX()
        prof.SetStats(0)
        prof.SetTitle(f"profiles of {dataSet}")
        prof.GetYaxis().SetTitle("mean of #it{p}_{T} * #sigma(1/#it{p}_{T})")
        prof.SetName("all tracks")
        prof.SetLineColor(2)
        profTRD.SetName("track.hasTRD()")
        profTRD.SetLineColor(4)
        profNoTRD.SetName("!track.hasTRD")
        profNoTRD.SetLineColor(1)
        prof.Draw("E")
        profTRD.Draw("ESAME")
        profNoTRD.Draw("ESAME")
        canP.SetLogz()
        canP.SetTopMargin(0.1)
        legP = createLegend(x=[0.2, 0.4], y=[0.6, 0.8], objects=[prof, profTRD, profNoTRD])
        legP.Draw()

        pt = f.Get(f"track-jet-qa/Kine/pt")
        ptTRD = f.Get(f"track-jet-qa/Kine/pt_TRD")

        Npt = pt.GetEntries()
        NptTRD = ptTRD.GetEntries()
        pt.SetTitle(" ")
        pt.SetName(f"{Npt}: tracks")
        ptTRD.SetName(f"{NptTRD}: withTRD")

        can = canvas("TH1F pT TRD ")
        pt.SetLineColor(2)
        pt.SetMarkerStyle(24)
        pt.SetMarkerColor(2)
        ptTRD.SetLineColor(4)
        ptTRD.SetMarkerStyle(25)
        ptTRD.SetMarkerColor(4)
        pt.SetStats(0)
        pt.SetTitle(f"{dataSet}")
        pt.Draw("E")
        ptTRD.Draw("ESAME")
        can.SetLogy()
        can.SetTopMargin(0.1)
        leg = createLegend(x=[0.5, 0.85], y=[0.6,0.85], objects=[pt,ptTRD])
        leg.Draw()

        canR = canvas("TH1F pT TRD ratio")
        r = doRatio(pt,ptTRD,1,"tracks/track.hasTRD()",24)
        r.SetName(dataSet)
        r.Draw("E")
        canR.SetLogy()
        legR = createLegend(x=[0.2, 0.8], y=[0.88,0.98], objects=[r])
        legR.Draw()
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/{dataSet}/TRD_checks.pdf", f"{dataSet}")
        else:
            clear_canvaslist()
        print(f"TRD checks for a {dataSet} are done")

    else:
        can = canvas("Compare TH1F's pT TRD ")
        leg = createLegend(x=[0.25, 0.8], y=[0.5,0.85], columns=1, objects=[])

        canR = canvas("Compare Ratios of TH1F's pT TRD ")#, x=700, y=900)
        canR.Divide(1,2)
        legR = createLegend(x=[0.2, 0.8], y=[0.45,0.5], columns=2, objects=[])

        canS = canvas("TH2 Sigma1Pt vs Pt", x=1000, y=1000)
        canS.Divide(3,len(DataSets))
        
        canP = canvas("Compare TH2 Sigma1Pt Profile over pT")
        legP = createLegend(x=[0.2, 0.8], y=[0.86,1], columns=3, objects=[])

        canPR = canvas("Compare Ratios TH2 Sigma1Pt Profile over pT")
        canPR.Divide(1,3)
        legP = createLegend(x=[0.2, 0.8], y=[0.86,1], columns=3, objects=[])


        nSet = 0
        for dataSet in DataSets:#make first one the base line for ratios and saving
            f = TFile.Open(f"Results/{dataSet}/AnalysisResults.root", "READ")
            if not f or not f.IsOpen():
                print("Did not get", f)
                return
            files[dataSet] = f
            #dir = f.Get(f"track-jet-qa/Kine").GetListOfKeys()
            pt = f.Get(f"track-jet-qa/Kine/pt")
            ptTRD = f.Get(f"track-jet-qa/Kine/pt_TRD")

            can.cd()
            Npt = pt.GetEntries()
            NptTRD = ptTRD.GetEntries()
            pt.SetTitle(" ")
            pt.SetName(f"{dataSet}: all tracks")
            ptTRD.SetName(f"{dataSet}: track.hasTRD()")
            if dataSet == DataSets[0]:
                pt.SetLineColor(2)
                pt.SetMarkerColor(2)
                pt.SetMarkerStyle(24)
                ptTRD.SetLineColor(4)
                ptTRD.SetMarkerStyle(24)
                ptTRD.SetMarkerColor(4)
                pt.SetStats(0)
                pt.SetTitle(" ")
                pt.Draw("E")
                ptTRD.Draw("ESAME")
                leg.AddEntry(pt, f"{pt.GetName()}", "lp")
                leg.AddEntry(ptTRD, f"{ptTRD.GetName()}", "lp")
            else:
                nSet += 1
                pt.SetMarkerStyle(24+nSet)
                pt.SetLineColor(2)
                pt.SetMarkerColor(2)
                ptTRD.SetLineColor(4)
                ptTRD.SetMarkerStyle(24+nSet)
                ptTRD.SetMarkerColor(4)
                pt.Draw("ESAME")
                ptTRD.Draw("ESAME")
                leg.AddEntry(pt, f"{pt.GetName()}", "lp")
                leg.AddEntry(ptTRD, f"{ptTRD.GetName()}", "lp")
            leg.Draw()
            can.SetTopMargin(0.1)
            can.SetLogy()
            r = doRatio(pt,ptTRD,nSet,"all tracks/track.hasTRD()")                                          #do ratio of ratios in split canvas !
            canR.cd(1)
            if dataSet == DataSets[0]:
                r.DrawCopy("E")
                r0 = r.Clone()
            else:
                dr = doRatio(r,r0,nSet, f"Ratio to {DataSets[0]}")
                r.Draw("ESAME")
                canR.cd()
                canR.cd(2)
                dr.Draw("ESAME")
            canR.cd()
            legR.AddEntry(r, f"{dataSet}", "le")
            legR.Draw("")
            canR.cd(1).SetLogy()
            canR.cd(2).SetLogy()

            sigma1Pt = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt")
            sigma1Pt_TRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasTRD")
            sigma1Pt_noTRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasNoTRD")

            canS.cd()
            draw2DSigmaPtOnCanvas(canS, sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, DataSets)
            # we need this per period and the ratios of periods
            canP.cd()
            prof = sigma1Pt.ProfileX()
            profTRD = sigma1Pt_TRD.ProfileX()
            profNoTRD = sigma1Pt_noTRD.ProfileX()
            prof.SetStats(0)
            #prof.SetTitle(f"profiles of ")
            prof.GetYaxis().SetTitle("mean of #it{p}_{T} * #sigma(1/#it{p}_{T})")
            prof.SetName(f"{dataSet} all tracks")
            prof.SetLineColor(1)
            prof.SetMarkerStyle(24+nSet)
            prof.SetMarkerColor(1)
            profTRD.SetName(f"track.hasTRD()")
            profTRD.SetMarkerColor(2)
            profTRD.SetLineColor(2)
            profTRD.SetMarkerStyle(24+nSet)
            profNoTRD.SetName(f"!track.hasTRD")
            profNoTRD.SetMarkerStyle(24+nSet)
            profNoTRD.SetMarkerColor(4)
            profNoTRD.SetLineColor(4)
            if dataSet==DataSets[0]:
                prof.SetTitle(" ")
                legP.AddEntry(prof, f"{prof.GetName()}", "lep")
                prof0 = prof.Clone()
                profTRD0 = profTRD.Clone()
                profNoTRD0 = profNoTRD.Clone()
                prof.Draw("E")
            else:
                legP.AddEntry(prof, f"{prof.GetName()}", "lep")
                rProf = doRatio(prof,prof0,0,f"Ratios to {DataSets[0]}",makerStyle=24+nSet)
                rProfTRD = doRatio(profTRD,profTRD0,1,f"Ratios to {DataSets[0]}",makerStyle=24+nSet)
                rProfNoTRD = doRatio(profNoTRD,profNoTRD0,3, f"Ratios to {DataSets[0]}", makerStyle=24+nSet)
                canPR.cd(1)
                rProf.Draw("h")
                canPR.cd(2)
                rProfTRD.Draw("hSAME")
                canPR.cd(3)
                rProfNoTRD.Draw("hSAME")
                #canPR.SetLogy()
                canP.cd()
                prof.Draw("ESAME")
            profTRD.Draw("ESAME")
            profNoTRD.Draw("ESAME")

            canP.SetLogy()
            canP.cd()
            legP.AddEntry(profTRD, f"{profTRD.GetName()}", "lep")
            legP.AddEntry(profNoTRD, f"{profNoTRD.GetName()}", "lep")
            legP.Draw("SAME")
                
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/Compare{DataSets[0]}_to_{DataSets[1]}/TRD_checks.pdf", f"Compare{DataSets[0]}_to_{DataSets[1]}")
        else:
            print("Wait, we are at ")
            clear_canvaslist()
    print("Compared ratios of full dataset results")


    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Mode", "-m", type=str,
                        default=["Full", "Tree", "CompareDataSets"], help="Activate 'CompareDataSets', or plots QA AnalysisResults from 'Full' , 'Tree'(derived) results")
    parser.add_argument("--Input", "-in", type=str,
                        default="Results/LHC22s_pass5/AnalysisResults.root", help="Path and File input")
    parser.add_argument("--DataSets","-d", type=str, nargs="+",
                        default="LHC23zzh_cpass1 LHC23zzh_cpass1", help="Specify the results from the periods you want to compare (without comma)")
    parser.add_argument("--Save", "-s", type=str,
                        default=["False", "True"], help="If you set this flag, it will save the documents")
    args = parser.parse_args()

    if args.Mode=="Tree" or args.Mode=="Full":
        #drawPlots(args.Input, args.Mode, args.Save)
        compareTRD([args.Input], args.Save)
        

    if args.Mode=="CompareDataSets":# to compare Full results
        #compareDataSets(args.DataSets, args.Save)
        #ratioDataSets(args.DataSets, args.Save)
        compareTRD(args.DataSets, args.Save)


    #compareCuts()
#./processResults.py --Mode CompareDataSets --DataSets LHC23zzh_cpass1 LHC23zzh_cpass2 --Save True
#./processResults.py --Mode Full --Input Results/LHC23zzh_cpass2/AnalysisResults.root --Save True

main()
    