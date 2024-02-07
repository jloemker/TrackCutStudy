#!/usr/bin/env python3

"""
Post processing script to handle the QA output from trackJetQa i.e. resolution at high pT.
"""

import ROOT
from ROOT import TFile
from os import path
import re

from common import canvas_list, canvas, clear_canvaslist, saveCanvasList, createLegend

def doRatio(pt,ptTRD, nSet, title="", makerStyle=0):
    r = pt.Clone()
    r.Sumw2()
    r.SetStats(0)
    if ptTRD != 0:
        r.Divide(ptTRD)
    r.SetLineColor(nSet+1)
    r.SetMarkerStyle(makerStyle)
    r.SetMarkerColor(nSet+1)
    r.GetYaxis().SetTitle(title)
    r.SetDirectory(0)
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
        elif(dataSet == DataSets[1]):
            canS.cd(4)
            sigma1Pt = draw2DSigmaPt(f"{dataSet} all tracks",sigma1Pt)
            canS.cd(4).SetLogz()
            canS.cd(5)
            sigma1Pt_TRD = draw2DSigmaPt(f"{dataSet} track.hasTRD()",sigma1Pt_TRD)
            canS.cd(5).SetLogz()
            canS.cd(6)
            sigma1Pt_noTRD = draw2DSigmaPt(f"{dataSet} ! track.hasTRD()",sigma1Pt_noTRD)
            canS.cd(6).SetLogz()
        elif(dataSet == DataSets[2]):
            canS.cd(7)
            sigma1Pt = draw2DSigmaPt(f"{dataSet} all tracks",sigma1Pt)
            canS.cd(7).SetLogz()
            canS.cd(8)
            sigma1Pt_TRD = draw2DSigmaPt(f"{dataSet} track.hasTRD()",sigma1Pt_TRD)
            canS.cd(8).SetLogz()
            canS.cd(9)
            sigma1Pt_noTRD = draw2DSigmaPt(f"{dataSet} ! track.hasTRD()",sigma1Pt_noTRD)
            canS.cd(9).SetLogz()
        else:
            print("Not enought canvas splits for sigma1Pt !!!")

def profilesTRD(sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, nSet=None):
    prof = sigma1Pt.ProfileX()
    profTRD = sigma1Pt_TRD.ProfileX()
    profNoTRD = sigma1Pt_noTRD.ProfileX()
    prof.SetStats(0)
    prof.GetYaxis().SetTitle("mean of #it{p}_{T} * #sigma(1/#it{p}_{T})")
    prof.SetName(f"{dataSet} all tracks")
    prof.SetTitle(f"profiles of {dataSet}")
    prof.SetLineColor(1)
    profTRD.SetName("track.hasTRD()")
    profTRD.SetLineColor(2)
    profNoTRD.SetName("!track.hasTRD")
    profNoTRD.SetLineColor(4)
    if nSet is not None:
        prof.SetTitle(" ")
        prof.SetMarkerStyle(24+nSet)
        prof.SetMarkerColor(1)
        profTRD.SetMarkerColor(2)
        profTRD.SetName(f"{dataSet} track.hasTRD()")
        profTRD.SetMarkerStyle(24+nSet)
        profNoTRD.SetName(f"{dataSet} !track.hasTRD")
        profNoTRD.SetMarkerStyle(24+nSet)
        profNoTRD.SetMarkerColor(4)
    return prof, profTRD, profNoTRD

def histosTRD(pt, ptTRD, dataSet, nSet=None):
    Npt = pt.GetEntries()
    NptTRD = ptTRD.GetEntries()
    pt.SetTitle(" ")
    pt.GetYaxis().SetTitle("number of entries")
    pt.GetXaxis().SetRangeUser(0,100)
    pt.SetLineColor(2)
    pt.SetMarkerColor(2)
    ptTRD.SetLineColor(4)
    ptTRD.SetMarkerColor(4)
    pt.SetName(f"{dataSet}: all tracks")
    ptTRD.SetName(f"{dataSet}: track.hasTRD()")
    if nSet==None:
        pt.SetMarkerStyle(24)
        pt.SetMarkerColor(2)
        ptTRD.SetMarkerStyle(25)
        ptTRD.SetMarkerColor(4)
        pt.SetStats(0)
        pt.SetTitle(f"{dataSet}")
        pt.SetName(f"{Npt}: tracks")
        ptTRD.SetName(f"{NptTRD}: withTRD")
    elif nSet==0:
        pt.SetMarkerStyle(24)
        ptTRD.SetMarkerStyle(24)
        pt.SetStats(0)
        pt.SetTitle(" ")
    elif nSet>0:
        pt.SetMarkerStyle(24+nSet)
        ptTRD.SetMarkerStyle(24+nSet)

def compareTRD(DataSets={}, Save=""):
    files = {}
    histos = []
    if len(DataSets) == 1:
        f = TFile.Open(f"{DataSets[0]}","READ")
        dataSetArr = re.findall(r'\/.*?\/', DataSets[0])
        dataSet=dataSetArr[0].strip("/")
        sigma1Pt = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt").Projection(1,0)
        sigma1Pt_TRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasTRD").Projection(1,0)
        sigma1Pt_noTRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasNoTRD").Projection(1,0)

        canS = canvas("TH2 Sigma1Pt vs Pt", x=320, y=900)
        draw2DSigmaPtOnCanvas(canS, sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, DataSets)
        canP = canvas("TH2 Sigma1Pt Profile over pT")
        prof, profTRD, profNoTRD = profilesTRD(sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, None)
        prof.GetXaxis().SetRangeUser(0,100)
        prof.Draw("E")
        profTRD.Draw("ESAME")
        profNoTRD.Draw("ESAME")
        canP.SetLogz()
        canP.SetTopMargin(0.1)
        legP = createLegend(x=[0.6, 0.8], y=[0.25, 0.45], objects=[prof, profTRD, profNoTRD])
        legP.Draw()

        pt = f.Get(f"track-jet-qa/Kine/pt").Projection(0)
        ptTRD = f.Get(f"track-jet-qa/Kine/pt_TRD").Projection(0)
        can = canvas("TH1F pT TRD ")
        histosTRD(pt, ptTRD, dataSet, None)
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
            clear_canvaslist() 
        else:
            input("wait before closing - this will not be saved !")
            clear_canvaslist()
        print(f"TRD checks for a {dataSet} are done")

    else:
        can = canvas("Compare TH1F's pT TRD ")
        leg = createLegend(x=[0.25, 0.8], y=[0.5,0.85], columns=1, objects=[])

        canR = canvas("Compare Ratios of TH1F's pT TRD ")
        canR.Divide(1,2)

        canS = canvas("TH2 Sigma1Pt vs Pt", x=1000, y=1000)
        canS.Divide(3,len(DataSets))
        
        canP = canvas("Compare TH2 Sigma1Pt Profile over pT")
        legP = createLegend(x=[0.2, 0.8], y=[0.86,1], columns=3, objects=[])

        canPR = canvas("Compare Ratios TH2 Sigma1Pt Profile over pT")
        canPR.Divide(len(DataSets)-1,3)
        legP = createLegend(x=[0.2, 0.8], y=[0.86,1], columns=3, objects=[])

        nSet = 0
        rArr = []
        for dataSet in DataSets:#
            f = TFile.Open(f"Results/{dataSet}/AnalysisResults.root", "READ")
            if not f or not f.IsOpen():
                print("Did not get", f)
                return
            files[dataSet] = f
            #dir = f.Get(f"track-jet-qa/Kine").GetListOfKeys()
            pt = f.Get(f"track-jet-qa/Kine/pt").Projection(0)
            ptTRD = f.Get(f"track-jet-qa/Kine/pt_TRD").Projection(0)

            can.cd()
            if dataSet == DataSets[0]:
                histosTRD(pt, ptTRD, dataSet, nSet)
                pt.Draw("E")
                ptTRD.Draw("ESAME")
                leg.AddEntry(pt, f"{pt.GetName()}", "lp")
                leg.AddEntry(ptTRD, f"{ptTRD.GetName()}", "lp")
            else:
                nSet += 1
                histosTRD(pt, ptTRD, dataSet, nSet)
                pt.Draw("ESAME")
                ptTRD.Draw("ESAME")
                leg.AddEntry(pt, f"{pt.GetName()}", "lp")
                leg.AddEntry(ptTRD, f"{ptTRD.GetName()}", "lp")
            leg.Draw()
            can.SetTopMargin(0.1)
            can.SetLogy()
            r = doRatio(pt,ptTRD,nSet,"all tracks/track.hasTRD()")
            r.SetDirectory(0)
            r.SetName(f"{dataSet}")
            rArr.append(r)
            #print(r)

            canR.cd(1)
            if dataSet == DataSets[0]:
                r.DrawCopy("E")
                r0 = r.Clone()
                r0.SetDirectory(0)
            else:
                dr = doRatio(r,r0,nSet, f"Ratio to {DataSets[0]}")
                r.DrawCopy("ESAME")
                canR.cd(2)
                if dataSet ==DataSets[1]:
                    dr.DrawCopy("E")
                else:
                    dr.DrawCopy("ESAME")
            canR.cd()
            if dataSet == DataSets[len(DataSets)-1]:
                legR = createLegend(x=[0.2, 0.8], y=[0.45,0.5], columns=2, objects=rArr)
                legR.Draw()
                canR.cd(1).SetLogy()
                canR.cd(2).SetLogy()

            sigma1Pt = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt").Projection(1,0)
            sigma1Pt_TRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasTRD").Projection(1,0)
            sigma1Pt_noTRD = f.Get(f"track-jet-qa/TrackPar/Sigma1Pt_hasNoTRD").Projection(1,0)

            canS.cd()
            draw2DSigmaPtOnCanvas(canS, sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, DataSets)
            canP.cd()
            prof, profTRD, profNoTRD = profilesTRD(sigma1Pt, sigma1Pt_TRD, sigma1Pt_noTRD, dataSet, nSet)
            if dataSet==DataSets[0]:
                legP.AddEntry(prof, f"{prof.GetName()}", "lep")
                prof0 = prof.Clone()
                profTRD0 = profTRD.Clone()
                profNoTRD0 = profNoTRD.Clone()
                prof.Draw("E")
            else:
                legP.AddEntry(prof, f"{prof.GetName()}", "lep")
                rProf = doRatio(prof,prof0,0,f"{dataSet} / {DataSets[0]}",makerStyle=24+nSet)
                rProfTRD = doRatio(profTRD,profTRD0,1,f"{dataSet} / {DataSets[0]}",makerStyle=24+nSet)
                rProfNoTRD = doRatio(profNoTRD,profNoTRD0,3, f"{dataSet} / {DataSets[0]}", makerStyle=24+nSet)
                if len(DataSets) == 2:
                    canPR.cd(1)
                    rProf.DrawCopy("E")
                    canPR.cd(2)
                    rProfTRD.DrawCopy("E")
                    canPR.cd(3)
                    rProfNoTRD.DrawCopy("E")
                elif len(DataSets) == 3:
                    if dataSet == DataSets[1]:
                        canPR.cd(1)
                        rProf.DrawCopy("E")
                        canPR.cd(3)
                        rProfTRD.DrawCopy("E")
                        canPR.cd(5)
                        rProfNoTRD.DrawCopy("E")
                    elif dataSet == DataSets[2]:
                        canPR.cd(2)
                        rProf.DrawCopy("E")
                        canPR.cd(4)
                        rProfTRD.DrawCopy("E")
                        canPR.cd(6)
                        rProfNoTRD.DrawCopy("E")
                canP.cd()
                prof.Draw("ESAME")
            profTRD.Draw("ESAME")
            profNoTRD.Draw("ESAME")
            #canP.SetLogy()
            canP.cd()
            legP.AddEntry(profTRD, f"{profTRD.GetName()}", "lep")
            legP.AddEntry(profNoTRD, f"{profNoTRD.GetName()}", "lep")
            legP.Draw("SAME")
        if Save=="True":
            saveCanvasList(canvas_list, f"Save/Compare_{DataSets[0]}_to_{DataSets[len(DataSets)-1]}/TRD_checks.pdf", f"Compare_{DataSets[0]}_to_{DataSets[len(DataSets)-1]}")         
            clear_canvaslist()
        else:
            print("Wait, we are at ")
            clear_canvaslist()
    print("Compared ratios of full dataset results")



