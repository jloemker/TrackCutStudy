#!/usr/bin/env python3

"""
Collection of functions -- i should really improve this; but for now it does the job.
"""

import ROOT
from common import canvas, canvas_list
ROOT.gROOT.SetBatch(True)

def projectCorrelationsTo1D(o,dim, dim_min=None, logy=False, scaled=False, output=None, dataSet=None):
    if (dim == 0) or (dim == dim_min):
        histo = o.Projection(dim)
        histo.GetYaxis().SetTitle("number of entries")
        if "#it{p}_{T}" in histo.GetXaxis().GetTitle():
            logy=True
        if scaled==True:
            histo.SetStats(0)
            histo.Scale(1/histo.Integral())
            histo.GetYaxis().SetTitle("scaled by 1/Integral")
        histo.SetName(histo.GetTitle())
        if output == None:
            can = canvas(histo.GetTitle())
            histo.Draw("E")
            if logy == True:
                can.SetLogy()
        else:
            output.append(histo)
    if dim_min != None:
        for axis in range(dim_min,dim):
            histo = o.Projection(axis)
            histo.GetYaxis().SetTitle("number of entries")
            if "#it{p}_{T}" in histo.GetXaxis().GetTitle():
                logy==True
            if scaled==True:
                histo.SetStats(0)
                histo.Scale(1/histo.Integral())
                histo.GetYaxis().SetTitle("scaled by 1/Integral")
            histo.SetName(histo.GetTitle())
            if output == None:
                can = canvas(histo.GetTitle())
                histo.Draw("E")
                if logy == True:
                    can.SetLogy()
            else:
                #histo.SetTitle(dataSet+" "+histo.GetTitle())
                #histo.SetName(dataSet+" "+histo.GetName())
                output.append(histo)
    else:
        for axis in range(0,dim):
            histo = o.Projection(axis)
            histo.GetYaxis().SetTitle("number of entries")
            if "#it{p}_{T}" in histo.GetXaxis().GetTitle():
                logy==True
            if scaled==True:
                histo.SetStats(0)
                histo.Scale(1/histo.Integral())
                histo.GetYaxis().SetTitle("scaled by 1/Integral")
            histo.SetName(histo.GetTitle())
            if output == None:
                can = canvas(histo.GetTitle())
                histo.Draw("E")
                if logy == True:
                    can.SetLogy()
            else:
                #histo.SetTitle(dataSet+" "+histo.GetTitle())
                histo.SetName(dataSet+" "+histo.GetName())
                output.append(histo)
    if output != None:
        return output

def projectCorrelationsTo2D(o, axis, output=None):
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
        #can.SetLogz()

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
        if output !=None:
            output.append(prof)
        else:
            canProf = canvas(prof.GetName())
            prof.Draw("E")
    if output !=None:
        return output

def projectEventProp(o, output=None, dataSet=None):
    tmp = []
    h = o.Projection(0)
    h.GetYaxis().SetTitle("number of entries")
    if output != None:
        tmp.append(h)
        return tmp
    else:
        h.SetName(o.GetName())
        can = canvas(o.GetName()+" "+o.GetAxis(0).GetTitle())
        h.Draw("E")
        h01 = o.Projection(0,1)
        h01.SetName(o.GetName()+" vs "+o.GetAxis(1).GetTitle())
        h01.SetStats(0)
        can2D = canvas(o.GetName()+" vs "+o.GetAxis(1).GetTitle())
        h01.Draw("COLZ")
        h02 = o.Projection(0,2)
        h02.SetName(o.GetName()+" vs "+o.GetAxis(2).GetTitle())
        h02.SetStats(0)
        can2D = canvas(o.GetName()+" vs "+o.GetAxis(2).GetTitle())
        h02.Draw("COLZ")
        h12 = o.Projection(1,2)
        h12.SetName(o.GetName()+": "+o.GetAxis(1).GetTitle()+" vs "+o.GetAxis(2).GetTitle())
        h12.SetStats(0)
        can2D = canvas(o.GetName()+": "+o.GetAxis(1).GetTitle()+" vs "+o.GetAxis(2).GetTitle())
        h12.Draw("COLZ")

def projectEtaPhiInPt(o, pt_ranges, logz=False, output=None, dataSet=None):
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
