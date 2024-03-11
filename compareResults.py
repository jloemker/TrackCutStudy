#!/usr/bin/env python3

"""
Comparison script for ratios of QA processing - trackJetQa i.e. resolution at high pT.
"""
import ROOT
from ROOT import TFile, TMath
import numpy as np
import re
from common import Directories, get_directories, canvas, canvas_list, clear_canvaslist, saveCanvasList, createLegend, make_color_range
from projection import projectEventProp, projectCorrelationsTo1D, profile2DProjection

def propagateFullyCorrelatedError(hres, h0):
     res = hres.Clone()
     for i in range(0, res.GetNbinsX()):
         if ((abs(res.GetBinContent(i)) > 0) and (abs(h0.GetBinContent(i)) > 0)) :
             val = res.GetBinContent(i)/h0.GetBinContent(i)
             if (abs(res.GetBinError(i))>0 and abs(h0.GetBinError(i)) > 0):
                 term1 = pow(res.GetBinError(i) / res.GetBinContent(i), 2) 
                 term2 = pow(h0.GetBinError(i) / h0.GetBinContent(i), 2)
                 term3 = pow(res.GetBinError(i),2)/(res.GetBinContent(i)*h0.GetBinContent(i))
                 print("term1 ", term1, "term2 ", term2, "term3 ", term3)
                 err_avg = (res.GetBinContent(i)/h0.GetBinContent(i))*pow(abs(term1 + term2 - 2*term3), 0.5) 
             #err_low = (res.GetBinContent(i)/h0.GetBinContent(i))* ((res.GetBinContent(i) - res.GetBinError(i)) / (h0.GetBinContent(i) - h0.GetBinError(i))) 
             else:
                 err_avg = 0
             print("Bin Nr.: ", i, " bin value:", res.GetBinCenter(i), " ratio content: ", val, " err_avg:", err_avg)
         else:
             val = 0
             err_avg = 0
         res.SetBinContent(i,val)
         res.SetBinError(i, err_avg)
     return res

def ratioDataSets(histos=[]):
    if (f"Ratio_{histos[0].GetTitle()}") in canvas_list:
        return
    else:
        canR = canvas("Ratio_"+histos[0].GetTitle())  
        c = -1
        #col = [1,2,214,209,221]
        colors = make_color_range(len(histos))
    for o in histos:
        col = colors.pop(0)
        h = o.Clone()
        c +=1
        nEntries = h.Integral()
        newName = h.GetName().split(" ",1)
        h.SetTitle("Ratio "+h.GetTitle())
        h.SetName(newName[0])
        if abs(nEntries) > 0:
            h.Scale(1/nEntries)
            h.GetYaxis().SetTitle("scaled by (1/Integral)")
        h.SetLineColor(col)
        h.SetMarkerColor(col)
        h.SetMarkerStyle(23+c)
        h.SetStats(0)
        h.SetDirectory(0)
        canR.cd()
        if c == 0:
            #h.Sumw2()
            continue
        else:
            if histos[0] != 0:
                res = propagateFullyCorrelatedError(h, histos[0])
               # res.Divide(histos[0])
                res.GetYaxis().SetTitle("(DataSet/"+histos[0].GetName()+")")
            if c == 1:
                res.DrawCopy("E")
            else:
                res.DrawCopy("SAME")
    legR = createLegend(objects=histos, x=[0, 1], y=[0.87,0.93], columns=len(histos))
    canR.cd()
    legR.Draw("SAME")
    if histos[0].GetYaxis().GetBinCenter(0) > 0:
        canR.SetLogy()
    print("Compared ratios")

def compareDataSets(Path, DataSets={}, Save="", doRatios=None, CutVars=None, Grid=None):
    files = {}
    histos = []# try histos[DataSets] = [] ..or histos[dirName]
    #histos[DataSets][Directories] = []
    for dataSet in DataSets:#make first one the base line for ratios and saving
        if CutVars != None:
            for cutVar in CutVars:
               # if Grid != None:
                f = TFile.Open(f"{Path}/{dataSet}/CutVariations/AnalysisResults_{cutVar}.root", "READ")
                #f = TFile.Open(f"{Path}/CutVariations/{dataSet}/AnalysisResults_{cutVar}.root", "READ")
                #elif Grid==None:
                 #   f = TFile.Open(f"Results/{dataSet}/CutVariations/AnalysisResults_{cutVar}.root", "READ")
                if Directories == []:
                    get_directories(f, f"track-jet-qa{cutVar}")
                files[dataSet] = f
                for dirName in  Directories:
                    dir = f.Get(f"track-jet-qa{cutVar}/"+dirName).GetListOfKeys()
                    for obj in dir:
                        o = f.Get(f"track-jet-qa{cutVar}/"+dirName+"/"+obj.GetName())
                        if not o:
                            print("Did not get", o, " as object ", obj)
                            continue
                        elif "TH1" in o.ClassName():
                            h = o.Clone()
                            h.SetName(cutVar+" "+dirName+" "+o.GetName())
                            h.SetTitle(cutVar+" "+h.GetTitle())
                            h.SetDirectory(0)
                            histos.append(h)
                        elif "THnSparse" in o.ClassName():
                            tmp = []# to quick fix the existing functions with same renaming as before..
                            if "collisionVtxZ" in o.GetName():
                                tmp = projectEventProp(o, output=tmp, dataSet=dataSet)
                                for h in tmp:# seems to be redundant to do this loop for every case, but with only one else in the end I will get trouble for tgl..
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif "MultCorrelations" in o.GetName() and dirName=="EventProp":
                                tmp = projectCorrelationsTo1D(o,o.GetNdimensions(), output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                                tmp = projectCorrelationsTo1D(o,o.GetNdimensions(), output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif "EtaPhiPt" in o.GetName():#
                                tmp = profile2DProjection(o, [[0,1], [0,2], [0,3]], output=tmp, dataSet=dataSet)
                                projectCorrelationsTo1D(o, 4, scaled=False, output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif ("Sigma1Pt" in o.GetName()) or ("TRD" in o.GetName()):#included in eta phi pt case write/tune the extra function in additional script
                                    continue
                            elif "xyz" in o.GetName():
                                tmp = projectCorrelationsTo1D(o, 5, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                                profile2DProjection(o, [[0,2], [0,3], [0,4]], output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif "alpha" in o.GetName():
                                tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                                profile2DProjection(o, [[0,2]], output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            elif "signed1Pt" in o.GetName():#add ratio pos neg !
                                tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                                projectCorrelationsTo1D(o, 0, scaled=False, output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
                            else:
                                tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                                profile2DProjection(o, [[0,2]], output=tmp, dataSet=dataSet)
                                for h in tmp:
                                    h.SetName(cutVar+" "+dirName+" "+h.GetName())  
                                    h.SetTitle(cutVar+" "+h.GetTitle())
                                    h.SetDirectory(0)
                                    histos.append(h)
        if CutVars == None:
            f = TFile.Open(f"Results/{dataSet}/AnalysisResults.root", "READ")
            if not f or not f.IsOpen():
                print("Did not get", f)
                return
            if Directories == []:
                get_directories(f, f"track-jet-qa")
            files[dataSet] = f
            for dirName in  Directories:
                dir = f.Get(f"track-jet-qa/"+dirName).GetListOfKeys()
                for obj in dir:
                    o = f.Get(f"track-jet-qa/"+dirName+"/"+obj.GetName())
                    if not o:
                        print("Did not get", o, " as object ", obj)
                        continue
                    elif "TH1" in o.ClassName():
                        h = o.Clone()
                        h.SetName(dataSet+" "+dirName+" "+o.GetName())
                        h.SetTitle(dataSet+" "+h.GetTitle())
                        histos.append(h)
                    elif "THnSparse" in o.ClassName():
                        tmp = []# to quick fix the existing functions with same renaming as before..
                        if "collisionVtxZ" in o.GetName():
                            tmp = projectEventProp(o, output=tmp, dataSet=dataSet)
                            for h in tmp:# seems to be redundant to do this loop for every case, but with only one else in the end I will get trouble for tgl..
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(h.GetTitle())
                                histos.append(h)
                        elif "MultCorrelations" in o.GetName() and dirName=="EventProp":
                            tmp = projectCorrelationsTo1D(o,o.GetNdimensions(), output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        elif "MultCorrelations" in o.GetName() and dirName=="TrackEventPar":
                            tmp = projectCorrelationsTo1D(o,o.GetNdimensions(), output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        elif "EtaPhiPt" in o.GetName():#
                            tmp = profile2DProjection(o, [[0,1], [0,2], [0,3]], output=tmp, dataSet=dataSet)
                            projectCorrelationsTo1D(o, 4, scaled=False, output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        elif ("Sigma1Pt" in o.GetName()) or ("TRD" in o.GetName()):#included in eta phi pt case write/tune the extra function in additional script
                                continue
                        elif "xyz" in o.GetName():
                            tmp = projectCorrelationsTo1D(o, 5, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                            profile2DProjection(o, [[0,2], [0,3], [0,4]], output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        elif "alpha" in o.GetName():
                            tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                            profile2DProjection(o, [[0,2]], output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        elif "signed1Pt" in o.GetName():#add ratio pos neg !
                            tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                            projectCorrelationsTo1D(o, 0, scaled=False, output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
                        else:
                            print(o.GetTitle())
                            input("wait")
                            tmp = projectCorrelationsTo1D(o, 2, dim_min=2, scaled=False, output=tmp, dataSet=dataSet)
                            profile2DProjection(o, [[0,2]], output=tmp, dataSet=dataSet)
                            for h in tmp:
                                h.SetName(dataSet+" "+dirName+" "+h.GetName())  
                                h.SetTitle(dataSet+" "+h.GetTitle())
                                histos.append(h)
    for dirName in Directories:
        for h in histos:
            histo = []
            if not dirName in h.GetName():
                continue
            name = h.GetTitle().split(" ",1)
            if (f"Compare_{name[1]}") in canvas_list:
                continue
            else:
                can = canvas("Compare_"+name[1])
                if "tgl" in name[1]:
                    histo = [h for h in histos if (h.GetTitle().split(" ", 1)[1] == name[1])]
                else:
                    print(name[1], " name[1] ", name, " name ")
                    histo = [h for h in histos if (h.GetTitle().split(" ", 1)[1] == name[1])]
                if len(histo) < 2:
                    print("less than 2 histos to compare... ? You are comparing something to nothing...", name[1])
                    input("wait")
                colors = make_color_range(len(histo))
                #col = colors.pop(0)
                # col = [1,2,214,209,221]
                can.cd()
                c = -1
                for h in histo:
                    col = colors.pop(0)
                    c +=1
                    nEntries = h.Integral()
                    newName = h.GetName().split(" ",1)
                    newTitle = h.GetTitle().split(" ",1)
                    h.SetTitle(newTitle[1])
                    h.SetName(newName[0])#+": "+f"{nEntries}")
                    if abs(nEntries) > 0:
                        h.Scale(1/nEntries)
                        h.GetYaxis().SetTitle("scaled by (1/Intregral)")
                    h.SetLineColor(col)
                    h.SetMarkerColor(col)
                    h.SetMarkerStyle(23+c)
                    h.SetStats(0)
                    h.SetDirectory(0)
                    if c == 0:
                        h.Draw("E")
                    else:
                        h.Draw("SAME")
                legend = createLegend(objects=histo, x=[0, 1], y=[0.87,0.93], columns=len(DataSets))
                can.cd()
                legend.Draw("SAME")
                if h.GetYaxis().GetBinCenter(0) > 0:
                    can.SetLogy()
                if doRatios != None:
                    ratioDataSets(histos=histo)
    if (Save=="True"):
        if CutVars == None:
            saveCanvasList(canvas_list, f"Save/Compare_{DataSets[0]}_to_{DataSets[len(DataSets)-1]}/ProjectionsAndProfiles.pdf", f"Compare_{DataSets[0]}_to_{DataSets[len(DataSets)-1]}")  
            clear_canvaslist()
        elif CutVars != None:
            name = "Cuts"
            for cutVar in CutVars:
                name = name+f"_{cutVar}"
            saveCanvasList(canvas_list, f"Save/Compare_{DataSets[0]}_CutVariations/ProjectionsAndProfiles_{name}.pdf", f"Compare_{DataSets[0]}_CutVariations")  
            clear_canvaslist()
    else:
        print("Wait, don't save this ... ")
        input("Press enter to clear the canvas list")
        clear_canvaslist()
