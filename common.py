import ROOT
from ROOT import TFile, TLegend, TCanvas, gStyle, TColor
from os import path
import os
import numpy as np

Directories = []
canvas_list = {}
legends = []

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
    #clear_canvaslist()

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

def make_color_range(ncolors, simple=False):
    if ncolors <= 0:
        input("ncolors")
    if ncolors == 1:
        simple = True
    if simple:
        if ncolors <= 3:
            colors = ['#e41a1c', '#377eb8', '#4daf4a']
        elif ncolors <= 4:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
        elif ncolors < 5:
            colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']
        else:
            colors = ['#00000', '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf']
        # print("Using colors", colors)
        if len(colors) < ncolors:
            return make_color_range(ncolors=ncolors, simple=False)
        return [TColor.GetColor(i) for i in colors]
    NRGBs = 5
    NCont = 256
    NCont = ncolors
    stops = np.array([0.00, 0.30, 0.61, 0.84, 1.00])
    red = np.array([0.00, 0.00, 0.57, 0.90, 0.51])
    green = np.array([0.00, 0.65, 0.95, 0.20, 0.00])
    blue = np.array([0.51, 0.55, 0.15, 0.00, 0.10])
    FI = TColor.CreateGradientColorTable(NRGBs,
                                         stops, red, green, blue, NCont)
    colors = []
    for i in range(NCont):
        colors.append(FI + i)
    colors = np.array(colors, dtype=np.int32)
    gStyle.SetPalette(NCont, colors)
    return [int(i) for i in colors]

def get_directories(file, keyDir):
    for key in file.Get(keyDir).GetListOfKeys():
        if key.GetTitle() != None:
            Directories.append(key.GetTitle())
