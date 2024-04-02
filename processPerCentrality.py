#!/usr/bin/env python3

"""
Post processing script to handle the QA output from trackJetQa per centrality bin i.e. resolution at high pT.
"""

import ROOT
from ROOT import TFile, kRainbow
import re
import argparse
import numpy as np
import warnings
from common import Directories, get_directories, canvas, canvas_list, clear_canvaslist, saveCanvasList, createLegend, make_color_range

ROOT.gStyle.SetPalette(kRainbow)

def projectCorrelationsPerCentralityTo2D(o, CentralityBins, cent_axis, axis):
    hc = []
    for a in axis:
        t = o
        for c in CentralityBins:#FT0C   
            can = canvas(o.GetName()+f" Centrality [{c[0],c[1]}]% "+o.GetAxis(a[0]).GetTitle()+" vs "+o.GetAxis(a[0]).GetTitle())
            if c[0] == 0:
                t.GetAxis(cent_axis).SetRange(1,c[1])
            else:
                t.GetAxis(cent_axis).SetRange(c[0],c[1])
            p = t.Projection(a[0],a[1])
            p.SetStats(0)
            p.SetName(f"[{c[0]},{c[1]}]%")
            p.Draw("COLZ")
            p.SetDirectory(0)
            hc.append(p)
            t.GetAxis(cent_axis).SetRange(0,0)
            leg = createLegend( x=[0.55, 0.85], y=[0.5,0.8], title=f"Centralitie FT0C: [{c[0],c[1]}]%")
            leg.Draw("")
        
def projectCorrelationsPerCentralityTo1D(o, CentralityBins, cent_axis, axis, yrange=[0,1000], xrange=[None,None], Scale=False, logy=False):
    for a in axis:
        can = canvas(o.GetName()+" Centrality "+o.GetAxis(a).GetTitle())
        tmp = o
        tmp.GetAxis(cent_axis).SetRange(1,100)#FT0C
        proj = tmp.Projection(a)
        proj.SetName("MB")
        proj.SetStats(0)
        proj.GetYaxis().SetTitle("number of entries")
        nCol = len(CentralityBins)
        colors = make_color_range(nCol)
        t = o
        hc = []
        max_y = 0
        for c in CentralityBins:#FT0C            
            col = colors.pop(0)
            if c[0] == 0:
                t.GetAxis(cent_axis).SetRange(1,c[1])
            else:
                t.GetAxis(cent_axis).SetRange(c[0],c[1])
            p = t.Projection(a)
            p.SetStats(0)
            p.SetName(f"[{c[0]},{c[1]}]%")
            p.SetLineColor(col)
            p.GetYaxis().SetTitle("number of entries")
            p.GetYaxis().SetRangeUser(yrange[0],yrange[1])
            if Scale == True:
                p.SetStats(0)
                if abs(p.Integral()) > 0:
                    p.Scale(1/abs(p.Integral()))
                p.GetYaxis().SetTitle("scaled by 1/Integral")
                if xrange[0] != None:
                    p.GetXaxis().SetRangeUser(xrange[0],xrange[1])
            p.Draw("same")
            hc.append(p)
            t.GetAxis(cent_axis).SetRange(0,0)
        if logy==True:
            can.SetLogy()
        if "#phi" in o.GetAxis(a).GetTitle():
            legP = createLegend( x=[0.15, 0.9], y=[0.85,0.93], title="Centralities FT0C", columns=5, objects=hc)
            can.cd()
            legP.Draw("")
            continue
        if "tgl" in o.GetAxis(a).GetTitle():
            legP = createLegend( x=[0.25, 0.85], y=[0.22,0.38], title="Centralities FT0C", columns=3, objects=hc)
            can.cd()
            legP.Draw("")
            continue
        if "#eta" in o.GetAxis(a).GetTitle():
            legE = createLegend( x=[0.25, 0.85], y=[0.22,0.38], title="Centralities FT0C", columns=3, objects=hc)
            can.cd()
            legE.Draw("")
            continue
        if "z" in o.GetAxis(a).GetTitle():
            if "tracks.size()" in o.GetAxis(a).GetTitle():
                legZ = createLegend( x=[0.65, 0.83], y=[0.6,0.83], title="Centralities FT0C", columns=2, objects=hc)
            else:
                legZ = createLegend( x=[0.4, 0.6], y=[0.3,0.6], title="Centralities FT0C", columns=2, objects=hc)
            can.cd()
            legZ.Draw("")
            continue
        if "#alpha" in o.GetAxis(a).GetTitle():
            legA = createLegend( x=[0.2, 0.85], y=[0.85,0.95], title="Centralities FT0C", columns=4, objects=hc)
            can.cd()
            legA.Draw("")
            continue
        if (" shared " in o.GetAxis(a).GetTitle()) or ("crossed"  in o.GetAxis(a).GetTitle()) :
            legS = createLegend( x=[0.6, 0.83], y=[0.6,0.83], title="Centralities FT0C", columns=2, objects=hc)
            can.cd()
            legS.Draw("")
            continue
        if " clusters " in o.GetAxis(a).GetTitle():
            legI = createLegend( x=[0.2, 0.43], y=[0.6,0.83], title="Centralities FT0C", columns=2, objects=hc)
            can.cd()
            legI.Draw("")
            continue
        else:
            leg = createLegend( x=[0.6, 0.83], y=[0.6,0.83], title="Centralities FT0C", columns=2, objects=hc)
            can.cd()
            leg.Draw("")
            continue
    
def projectEventPropPerCentrality(o, CentralityBins):
    can = canvas(o.GetName()+" Centrality "+o.GetAxis(0).GetTitle())
    tmp = o
    tmp.GetAxis(2).SetRange(1,100)#FT0C
    proj = tmp.Projection(0)
    proj.SetName("MB")
    proj.SetStats(0)
    proj.GetYaxis().SetTitle("number of entries")
    nCol = len(CentralityBins)
    colors = make_color_range(nCol)
    t = o
    hc = []
    for c in CentralityBins:#FT0C            
        col = colors.pop(0)
        if c[0] == 0:
            t.GetAxis(2).SetRange(1,c[1])
        else:
            t.GetAxis(2).SetRange(c[0],c[1])
        p = t.Projection(0)
        p.SetStats(0)
        p.SetName(f"[{c[0]},{c[1]}]%")
        p.SetLineColor(col)
        p.GetYaxis().SetRangeUser(0, proj.Integral()/300)
        p.GetXaxis().SetRangeUser(-15, 15)
        p.GetYaxis().SetTitle("number of entries")
        p.Draw("same")
        hc.append(p)
        t.GetAxis(2).SetRange(0,0)
    leg = createLegend( x=[0.65, 0.83], y=[0.6,0.83], title="Centralities FT0C", columns=2, objects=hc)
    leg.Draw("")

def profile2DProjectionPerCentrality(o, CentralityBins, cent_axis, axis):
    for a in axis:
        hc = []
        canProf = canvas(o.GetName()+" Profile Ratios Centralities "+f"{a[1]}")
        tmp = o
        tmp.GetAxis(cent_axis).SetRange(1,100)#FT0C
        proj0 = tmp.Projection(a[1],a[0])
        proj0.SetName("MB projection "+o.GetAxis(a[1]).GetTitle())
        prof0 = proj0.ProfileX()
        prof0.SetName("MB profile "+o.GetAxis(a[1]).GetTitle())
        nCol = len(CentralityBins)
        colors = make_color_range(nCol)
        if [0,100] in CentralityBins:
            MBreducedCentralityBins = CentralityBins.copy()
            MBreducedCentralityBins.pop()
        else:
            MBreducedCentralityBins = CentralityBins
        for c in MBreducedCentralityBins:#FT0C            
            col = colors.pop(0)
            if c[0] == 0:
                tmp.GetAxis(cent_axis).SetRange(1,c[1])
            else:
                tmp.GetAxis(cent_axis).SetRange(c[0],c[1])
            pj = tmp.Projection(a[1],a[0])
            pj.SetName("projectio "+o.GetAxis(a[1]).GetTitle())
            pj.SetTitle("projection "+o.GetAxis(a[1]).GetTitle())
            pf = pj.ProfileX()
            pf.SetName(f" [{c[0],c[1]}]% ")
            #prof.SetTitle(f" Centrality [{c[0],c[1]}]% profile "+o.GetAxis(a[1]).GetTitle())
            pf.SetTitle(" profile "+o.GetAxis(a[1]).GetTitle())
            pf.GetYaxis().SetTitle(f"ratio [Percentile]% / MB of mean {o.GetAxis(a[1]).GetTitle()} ")
            pf.SetStats(0)
            pf.Divide(prof0)
            pf.GetYaxis().SetRangeUser(0,4)
            if ("#eta" in pf.GetYaxis().GetTitle()) or ("cm" in pf.GetTitle()) or ("#alpha" in pf.GetTitle()) or ("q" in pf.GetTitle()):
                pf.GetYaxis().SetRangeUser(-2,2)
            pf.SetLineColor(col)
            tmp.GetAxis(cent_axis).SetRange(0,0)
            hc.append(pf)
            pf.Draw("lsame")
        if ("#eta" in pf.GetYaxis().GetTitle()) or ("cm" in pf.GetTitle()) or ("#alpha" in pf.GetTitle() or ("q" in pf.GetTitle())):
            leg = createLegend([0.52,0.82], [0.25,0.50], "Centralities FT0C",objects=hc, columns=2)
        else:
            leg = createLegend([0.52,0.82], [0.55,0.8], "Centralities FT0C",objects=hc, columns=2)
        canProf.cd()
        leg.Draw("")


def drawNPlots(InputDir="", Save="", CentralityBins=list[list]):
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
                o.GetYaxis().SetTitle("number of entries")#maybe overwrite the axis
                o.Draw("E")
                print(o.GetName())
            elif "TH2" in o.ClassName():#Flag bits i dont carer rn...
                continue
            elif "THnSparse" in o.ClassName():
                if "collisionVtxZ" in o.GetName():
                    projectEventPropPerCentrality(o, CentralityBins)
                if "MultCorrelations" in o.GetName() and dirName=="EventProp":
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,1, [6,7], [0,2000], False)
                if "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,3, [0], yrange=[0,1.2], xrange=[0,10], Scale=True)
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,3, [1], yrange=[0,1], xrange=[0,0.1], Scale=True) 
                    projectCorrelationsPerCentralityTo2D(o, CentralityBins,3, [[1,0]])
                    projectCorrelationsPerCentralityTo2D(o, CentralityBins,8, [[1,0]])
                if "EtaPhiPt" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,5, [0],xrange=[0,100], yrange=[0,0.5] , Scale=True, logy=True)
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,5, [1],xrange=[0,0.5], yrange=[0,0.5] , Scale=True, logy=True)
                    projectCorrelationsPerCentralityTo1D(o,CentralityBins, 5, [2,3],yrange=[0,0.5] , Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,5, [[0,1], [0,2], [0,3]])
                if "xyz" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,6, [2,3,4], Scale=True, logy=True)
                    profile2DProjectionPerCentrality(o, CentralityBins,6, [[0,1], [0,2], [0,3]])
                if "alpha" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "signed1Pt" in o.GetName():#add ratio pos neg !
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "snp" in o.GetName():#improve binning !
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tgl" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "dcaXY" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], xrange=[-0.15,0.15], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "dcaZ" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2],xrange=[-0.15,0.15], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "length" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "itsNCls" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "itsChi2NCl" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=True)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "itsHits" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [1], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,1]])
                if "tpcNClsFindable" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tpcNClsFound" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tpcNClsShared" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=True)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tpcNClsCrossedRows" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tpcFractionSharedCls" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=True)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "tpcCrossedRowsOverFindableCls" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [1], Scale=True, logy=False)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,1]])
                if "tpcChi2NCl" in o.GetName():
                    projectCorrelationsPerCentralityTo1D(o, CentralityBins,4, [2], Scale=True, logy=True)
                    profile2DProjectionPerCentrality(o, CentralityBins,4, [[0,2]])
                if "Sigma1Pt" in o.GetName():
                    if "TRD" in o.GetName():
                        continue
                    else:
                        projectCorrelationsPerCentralityTo1D(o, CentralityBins,3, [1], Scale=True, logy=True)
                        profile2DProjectionPerCentrality(o, CentralityBins,3, [[0,1]])
                else:
                    print(o.GetName())

            else: 
                print(o.GetName())
                input("we miss something..")
                print(o.ClassName())
            if Save ==False:
                input("Wait a second and check the histograms !")
    if Save=="True":
        dataSetArr = re.findall(r'\/.*?\/', InputDir)
        dataSet=dataSetArr[0].strip("/")
        print(f"Save/{dataSet}/CentralityTrackQA_{dataSet}.pdf")
        saveCanvasList(canvas_list, f"Save/{dataSet}/CentralityTrackQA_{dataSet}.pdf", dataSet)
    else:
        input("Wait a second")
        print("we don't save this ...")
        clear_canvaslist()
    
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Cent", "-c", type=str, 
                        default=None, help="Put this flag only if you want check specific centrality ranges: 0_1, ..., 0_100 (MB last!)", nargs="+")
    parser.add_argument("--Input", "-in", type=str,
                        default="Results/LHC22s_pass5/AnalysisResults.root", help="Path and File input")
    parser.add_argument("--Save", "-s", type=str,
                        default=["False", "True"], help="If you set this flag, it will save the documents")
    args = parser.parse_args()

    CentralityBins = [[0,1], [1,5], [5,10], [10,15], [15,20], [20,30], [30,40], [40,50], [50,60], [60,70], [70,80], [80,90], [90,100], [0,100]]
    if args.Cent !=None:
            CentralityBins = []
            for i in args.Cent:
                if i == None or i == "None" or i == "":
                    i = None
                else:
                    i = i.split("_")
                    i = [int(i[0]), int(i[1])]
                    CentralityBins.append(i)
    drawNPlots(args.Input, args.Save, CentralityBins=CentralityBins)
#./processPerCentrality.py --Input Results/LHC_Test/AnalysisResults.root 
    #o.GetAxis(0).GetBinCenter(pT[0]) --- add the exact bin center on legends to see if over/underflow
main()
    
