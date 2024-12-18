#!/usr/bin/env python3

"""
Collection of functions -- i should really improve this; but for now it does the job.
"""

import ROOT
from common import canvas, canvas_list
ROOT.gROOT.SetBatch(True)

def projectCorrelationsTo1D(o,dim, dim_min=None, logy=False, scaled=False, output=None, dataSet=None, scaleFactor=100):
    if (dim == 0) or (dim == dim_min):
        histo = o.Projection(dim)
        histo.GetYaxis().SetTitle("number of entries")
        if scaled==True:
            histo.SetStats(0)
            histo.Scale(1/scaleFactor)
            histo.GetYaxis().SetTitle("scaled by 1/N_{Events}")
        histo.SetName(histo.GetTitle())
        if output == None:
            can = canvas(histo.GetTitle())
            histo.SetMarkerStyle(34)
            histo.SetLineColor(1)
            histo.Draw("E")
            if logy == True:
                can.SetLogy()
        else:
            output.append(histo)
    if dim_min != None:
        for axis in range(dim_min,dim):
            histo = o.Projection(axis)
            histo.GetYaxis().SetTitle("number of entries")
            if scaled==True:
                histo.SetStats(0)
                histo.Scale(1/scaleFactor)
                histo.GetYaxis().SetTitle("scaled by 1/N_{Events}")
            histo.SetName(histo.GetTitle())
            if output == None:
                can = canvas(histo.GetTitle())
                histo.SetMarkerStyle(34)
                histo.SetLineColor(1)
                histo.Draw("E")
                if logy == True:
                    can.SetLogy()
            else:
                output.append(histo)
    else:
        for axis in range(0,dim):
            histo = o.Projection(axis)
            histo.GetYaxis().SetTitle("number of entries")
            if scaled==True:
                print("scaling histos")
                histo.SetStats(0)
                histo.Scale(1/scaleFactor)
                histo.GetYaxis().SetTitle("Counts/N_{Event}")
            histo.SetName(histo.GetTitle())
            if output == None:
                can = canvas(histo.GetTitle())
                histo.SetStats(0)
                histo.SetMarkerStyle(34)
                histo.SetLineColor(1)
                histo.Draw("E")
                if logy==True:
                    can.SetLogy()
                if ("#phi" in histo.GetXaxis().GetTitle()):
                    min_y = histo.GetBinContent(histo.GetMinimumBin())-histo.GetBinContent(histo.GetMinimumBin())/3
                    max_y = histo.GetBinContent(histo.GetMaximumBin())+histo.GetBinContent(histo.GetMaximumBin())/3
                    histo.GetYaxis().SetRangeUser(min_y, max_y)
                    histo.GetYaxis().SetMoreLogLabels()
            else:
                histo.SetName(dataSet+" "+histo.GetName())
                output.append(histo)
    if output != None:
        return output

def projectCorrelationsTo2D(o, axis, logz=False, output=None):
    for a in axis:
        h = o.Projection(a[0],a[1])
        if output != None:
            output.append(h)
        elif h.GetTitle() in canvas_list:
            print(h.GetTitle(), " is already in canvas list")
            continue
        else:
            h.SetName(h.GetTitle())
            can = canvas(h.GetTitle())
            h.SetStats(0)
            print("Drawing 2D")
            h.Draw("COLZ")
        if logz==True:
            can.SetLogz()

def profile2DProjection(o, axis, output=None, dataSet=None):
    for a in axis:
        proj = o.Projection(a[1],a[0])
        if dataSet != None:
            proj.SetTitle(dataSet+" "+proj.GetTitle())
            proj.SetName(dataSet+" "+proj.GetName())
        prof = proj.ProfileX()
        prof.GetYaxis().SetTitle(f"mean {o.GetAxis(a[1]).GetTitle()}")
        prof.SetTitle(o.GetTitle()+": - profile "+o.GetAxis(a[1]).GetTitle())
        prof.SetDirectory(0)
        if ("#eta" in o.GetAxis(a[1]).GetTitle()) or ("cm" in o.GetAxis(a[1]).GetTitle()) or ("#alpha" in o.GetAxis(a[1]).GetTitle()) or ("q" in o.GetAxis(a[1]).GetTitle()):
            prof.GetYaxis().SetRangeUser(-1,1)
        if ("#it{Length} [cm]" in o.GetAxis(a[1]).GetTitle()):
            prof.GetYaxis().SetRangeUser(300,600)
        if output !=None:
            output.append(prof)
        else:
            canProf = canvas(prof.GetName())
            prof.SetMarkerStyle(34)
            prof.SetLineColor(1)
            prof.Draw("E")
    if output !=None:
        return output

def projectEventProp(o, output=None, dataSet=None, extractScale=None, Centrality=False, logz=False):
    tmp = []
    h = o.Projection(0)
    h.GetYaxis().SetTitle("number of entries")
    if (output != None) and (extractScale==None) :
        tmp.append(h)
        return tmp
    else:
        h.SetName(o.GetName())
        can = canvas(o.GetName()+" "+o.GetAxis(0).GetTitle())
        h.Draw("E")
        if Centrality == True:
          h01 = o.Projection(0,1)
          h01.SetName(o.GetName()+" vs "+o.GetAxis(1).GetTitle())
          h01.SetStats(0)
          can2D = canvas(o.GetName()+" vs "+o.GetAxis(1).GetTitle())
          h01.Draw("COLZ")
          if logz==True:
            can2D.SetLogz() 
          h02 = o.Projection(0,2)
          h02.SetName(o.GetName()+" vs "+o.GetAxis(2).GetTitle())
          h02.SetStats(0)
          can2D = canvas(o.GetName()+" vs "+o.GetAxis(2).GetTitle())
          h02.Draw("COLZ")
          if logz==True:
            can2D.SetLogz() 
          h12 = o.Projection(1,2)
          h12.SetName(o.GetName()+": "+o.GetAxis(1).GetTitle()+" vs "+o.GetAxis(2).GetTitle())
          h12.SetStats(0)
          can2D = canvas(o.GetName()+": "+o.GetAxis(1).GetTitle()+" vs "+o.GetAxis(2).GetTitle())
          h12.Draw("COLZ")
          if logz==True:
            can2D.SetLogz() 
    if (extractScale == True) and (output == None):
        print("extracting scale..", h.GetName())
        if h.GetName() == "collisionVtxZ":
            print("h.GetName() ", h.GetName(), " h.Integral() ", h.Integral())
            return h.Integral()
    if (extractScale == True) and (output != None):
        print("extracting scale..", h.GetName())
        if h.GetName() == "collisionVtxZ":
            print("h.GetName() ", h.GetName(), " h.Integral() ", h.Integral())
            tmp.append(h)
            return h.Integral(), tmp


def projectEtaPhiInPt(o, pt_ranges, logz=False, output=None, dataSet=None):
    proj = o.Projection(2,3)
    proj.SetStats(0)
    proj.SetName("FUll projection")
    proj.SetTitle("Projection for full p_{T} range")
    if output != None:
        output.append(proj)
    else:
        can = canvas("full p_{T} projection")
        proj.Draw("COLZ") 
        if logz==True:
            can.SetLogz()   
    for pT in pt_ranges: 
        tmp = o
        tmp.GetAxis(0).SetRange(pT[0], pT[1])#Range in terms of bins - need to convert into pT value for label !
        proj = tmp.Projection(2,3)
        proj.SetStats(0)
        proj.SetName(proj.GetTitle()+f"{pT[0]}_{pT[1]}")
        proj.SetTitle("Projection for p_{T}"+ f" in range {o.GetAxis(0).GetBinCenter(pT[0])} - {o.GetAxis(0).GetBinCenter(pT[1])}"+" GeV/#it{c}")
        if output != None:
            output.append(proj)
        else:
            can = canvas(proj.GetTitle()+f"{pT[0]}_{pT[1]}")
            proj.Draw("COLZ") 
            if logz==True:
                can.SetLogz()       
        tmp.GetAxis(0).SetRange(0, 0)
