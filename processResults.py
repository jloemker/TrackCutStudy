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
#   - add multBinning for projections of ThNSparses uncertainty in ranges (needed once multiplicites are calibrated)
#   - add comparison step for different trackCuts and different data set + prepare standard legends and ratio plots based on what Alice did
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
    h_profileX.GetYaxis().SetTitle("Mean value")
    h_profileX.SetLineColor(kAzure+7)
    h_profileX.SetLineWidth(3)
    canX = canvas(dirName+" "+h_profileX.GetTitle())
    h_profileX.Draw("E")

def ProjectTHnSparse(hist, NumberOfAxis, dirName=None):
    hlist = []
    for axis in range(0,NumberOfAxis):
        histo = hist.Projection(axis)
        histo.SetTitle(hist.GetAxis(axis).GetTitle())
        hlist.append(histo)
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
                can.SetLogz()
                o.SetStats(0)
                o.Draw("COLZ")
                profileTH2X(o, dirName)
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
            input("wait")
        else:
            print("Wait, we are at ")
            input(dirName)
            clear_canvaslist()

def compareDataSets(DataSets={}, Save=""):#Legend + other histo types !
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
                canR = canvas("Ratio_"+h.GetTitle())
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
                    h.Draw("ESAME")
                legend = createLegend(objects=histo, x=[0.2,0.8], y=[0.86,0.97], columns=len(DataSets))
                legend.Draw()
                can.SetLogy()

                canR.cd()#put this into a second pad 
                for h in histo:
                    if h == histo[0]:
                        continue
                    h.Sumw2()
                    h.Divide(histo[0])#Replace contents of this histogram by the division of h1 by h2.)
                    h.SetTitle(h.GetTitle())
                    h.GetYaxis().SetTitle("(DataSet/"+histo[0].GetName()+")")
                    h.Draw("ESAME")
                legend = createLegend(objects=histo, x=[0.2,0.8], y=[0.86,0.97], columns=len(DataSets))
                legend.Draw()
                canR.SetLogy()

                #input("wait..")

    if Save=="True":
        saveCanvasList(canvas_list, f"Save/Compare/{DataSets[0]}_to_{DataSets[1]}.pdf", f"Compare")

    else:
        print("Wait, we are at ")
        clear_canvaslist()

    print("Compare full dataset results")
    input("Wait")



    
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
        drawPlots(args.Input, args.Mode, args.Save)

    if args.Mode=="CompareDataSets":# to compare Full results
        compareDataSets(args.DataSets, args.Save)


    #compareCuts()

main()
    