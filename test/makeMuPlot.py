#!/usr/bin/env python
import os, subprocess, sys
from array import array
import CombineHarvester.CombineTools.ch as ch
from ROOT import *
from math import sqrt, sin, cos, tan, exp
import numpy as np
import glob
workingDir = os.getcwd()
execfile("python/data_manager_makePostFitPlots.py")
from collections import OrderedDict

## type 1

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--input_folder", type="string",
    dest="input_folder", help="Where the cards with result by category will be (it will guess where the ones with the full combo are based on that, assuming you used the script run_limits... for running everything)"
    )
parser.add_option(
    "--is_tH",
    action="store_true",
    dest="is_tH",
    help="self-explaining",
    default=False
    )
parser.add_option(
    "--is_decay",
    action="store_true",
    dest="is_decay",
    help="self-explaining",
    default=False
    )
parser.add_option(
    "--era", type="int",
    dest="era",
    help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.",
    default=2017
    )
parser.add_option(
    "--draw_stats_only",
    action="store_true",
    dest="draw_stats_only",
    help="self-explaining",
    default=False
    )
# combined
# combined stats only
# era
(options, args) = parser.parse_args()

input_folder = options.input_folder

era = options.era
is_tH = options.is_tH
is_decay = options.is_decay
draw_stats_only = options.draw_stats_only

process = "ttH"
if options.is_tH :
    process = "tH"
if options.is_decay :
    process = "ttH"

dprocs = OrderedDict()
#dprocs["ttW"]           = [[], 12.25, "ttW"]
#dprocs["ttZ"]           = [[], 10.25, "ttZ"]
if options.is_decay :
    dprocs["ttH_hww"]         = [[], 14.25, "t#bar{t}H #to WW" ]
    dprocs["ttH_htt"]         = [[], 13.75, "t#bar{t}H #to #tau#tau"]
    dprocs["ttH_hzz"]         = [[], 13.25, "t#bar{t}H #to ZZ"]
    dprocs["tH_full"]         = [[], 12.75, "tHq + tHW" ]
else :
    dprocs["%s_2lss_0tau" % process]    = [[], 14.25, "2lss + 0#tau_{h}" ]
    dprocs["%s_3l_0tau" % process]    = [[], 12.75, "3l + 0#tau_{h}"]
    dprocs["%s_2lss_1tau" % process]  = [[], 11.25, "2lss + 1#tau_{h}"]
    if not options.is_tH :
        dprocs["%s_1l_2tau" % process]    = [[], 9.75, "1l + 2#tau_{h}"]
        dprocs["%s_2los_1tau" % process]    = [[], 8.25, "2los + 1#tau_{h}"]
        dprocs["%s_3l_1tau" % process]  = [[], 6.75, "3l + 1#tau_{h}"]
        dprocs["%s_2l_2tau" % process]    = [[], 5.25, "2l + 2#tau_{h}"]
        dprocs["%s_4l" % process]    = [[], 3.75, "4l + 0#tau_{h}"]
        dprocs["%s_0l_2tau" % process]    = [[], 2.25,  "0l + 2#tau_{h}"]
        dprocs["%s_1l_1tau" % process]         = [[], 0.75, "1l + 1#tau_{h}"]

ymax = 18.0 # 12.
ymin = 0.
ylinemax = 14. # 10.0
if options.is_tH :
    ymin = 10.25
    ymax = 16. # 12.
    ylinemax = 15. # 10.0
elif is_decay :
    ymin     = 11.25
    ymax     = 16.25
    ylinemax = 15.5


for key in dprocs.keys() :
    my_file_pattern =  os.path.join(input_folder, "*rate_%s*test.log" % (key)) #"%s/ttH_%s_rate.txt" % (input_folder, key)
    #my_file = os.path.join(input_folder, "ttH_%s*.out" % (key))
    my_files = glob.glob(my_file_pattern)
    if not len(my_files) > 0 :
        dprocs[key][0] = [1, 1, 1]
        print ("did not found pattern:", my_file_pattern)
        continue
    my_file = my_files[len(my_files) - 1]
    print ("reading:", my_file)
    try: open(my_file, 'r')
    except :
        dprocs[key][0] = [1, 1, 1]
        print ("Could not open the file:", my_file)
        continue
    with open(my_file, 'r') as in_file :
      for line in in_file :
        if "r_%s :" % (key) in line :
            for li in line.split() :
                try: float(li)
                except ValueError:
                    for li2 in li.split("/") :
                        try: float(li2)
                        except ValueError: continue
                        print float(li2)
                        dprocs[key][0].append(float(li2))
                    continue
                print li
                dprocs[key][0].append(float(li))
    if not len(dprocs[key][0]) > 0 :
        print ("file did not had rate written ", my_file)
        dprocs[key][0] = [1, 1, 1]
print " "
### read combined
erastring = "dumbCombo"
if options.era > 0 : erastring = str(options.era)
if options.era == 0 : erastring = "all"
if options.era > 0 :
    my_file = "%s/../combo_ttHmultilep_%s_rate_data_%s.log" % (input_folder, str(era), process)
else :
    my_file = "%s/../combo_ttHmultilep_rate_data_%s.log" % (input_folder, process)

print ("reading:", my_file)
combined = []
print "Combined: "
with open(my_file, 'r') as in_file :
  for line in in_file :
    if "r_ttH :" in line or "r_tH :" in line :
        for li in line.split() :
            try: float(li)
            except ValueError:
                for li2 in li.split("/") :
                    try: float(li2)
                    except ValueError: continue
                    #print float(li2)
                    combined = combined + [float(li2)]
                continue
            print li
            combined = combined + [float(li)]
print combined
### read combined
if draw_stats_only :
    #my_file = "%s/../combo_ttHmultilep_%s_rate_asimov_%s.log" % (input_folder, erastring, process)
    my_file = "%s/../combo_ttHmultilep_rate_%s_stats_only.log" % (input_folder, process )
    combined_stas_only = []
    print "Combined stat only: "
    count = 0
    with open(my_file, 'r') as in_file :
      for line in in_file :
        if "r_ttH :" in line or "r_tH :" in line:
            for li in line.split() :
                try: float(li)
                except ValueError:
                    for li2 in li.split("/") :
                        try: float(li2)
                        except ValueError: continue
                        #print float(li2)
                        count += 1
                        add = 0
                        #if count == 1 : add = 0.01
                        #if count == 2 : add = -0.01
                        combined_stas_only = combined_stas_only + [float(li2) + add]
                    continue
                print li
                combined_stas_only = combined_stas_only + [float(li)]
    print ("combined_stas_only", combined_stas_only)

########################
y_comb = 7.5
y_header = 1.5
if is_tH :
    y_header = 1
    y_comb = (ymax - ymin)/2
elif is_decay :
    y_header = 7.
    y_comb = 3.

mu_comb_m1s = abs(combined[1])
mu_comb_p1s = combined[2]

if draw_stats_only :
    mu_comb_p1s_stat = combined_stas_only[2]
    mu_comb_m1s_stat = abs(combined_stas_only[1])
    gr_mu_comb_stat = TGraphAsymmErrors()
    gr_mu_comb_stat.SetPoint(0, combined_stas_only[0], ymin + (ymax - ymin)/2 - y_header)
    gr_mu_comb_stat.SetPointError(0, abs(combined_stas_only[1]), combined_stas_only[2], y_comb, y_comb)
    gr_mu_comb_stat.SetLineWidth(2)
    gr_mu_comb_stat.SetMarkerSize(0)
    gr_mu_comb_stat.SetFillColor(8) #ROOT.kGreen+2)

gr_mu_comb_syst = TGraphAsymmErrors()
gr_mu_comb_syst.SetPoint(0, combined[0], ymin + (ymax - ymin)/2 - y_header)
gr_mu_comb_syst.SetPointError(0, abs(combined[1]), combined[2], y_comb, y_comb)
gr_mu_comb_syst.SetLineWidth(2)
gr_mu_comb_syst.SetMarkerSize(0)
if not draw_stats_only :
    gr_mu_comb_syst.SetFillColor(8) #ROOT.kGreen)
else :
    gr_mu_comb_syst.SetFillColor(5) #ROOT.kYellow)

gr_mu_comb = TGraphAsymmErrors()
gr_mu_comb.SetPoint(0,combined[0],y_comb)
gr_mu_comb.SetPointError(0,ymin,ymin,y_comb,y_comb)
gr_mu_comb.SetLineWidth(3)
gr_mu_comb.SetLineColor(1)
gr_mu_comb.SetMarkerSize(1)
gr_mu_comb.SetMarkerColor(1)

mg = TMultiGraph()
mg.Add(gr_mu_comb, "PL")
mg.Add(gr_mu_comb_syst, "E2")
if draw_stats_only :
    mg.Add(gr_mu_comb_stat, "E2")

for kk, key in enumerate(dprocs.keys()) :
    print (key, abs(dprocs[key][0][2]), dprocs[key][0][1])
    gr_mu = TGraphAsymmErrors()
    gr_mu.SetPoint(0,dprocs[key][0][0], dprocs[key][1])
    gr_mu.SetPointError(0, abs(dprocs[key][0][1]), dprocs[key][0][2], 0, 0)
    gr_mu.SetLineWidth(3)
    gr_mu.SetLineColor(2) #ROOT.kRed)
    gr_mu.SetMarkerStyle(21)
    gr_mu.SetMarkerSize(1.5)
    mg.Add(gr_mu, "P")
#################################

c = TCanvas("c","c",750,700)
#c = TCanvas("c","c",800,750)
c.SetLeftMargin(0.25)
c.SetBottomMargin(0.15)

gStyle.SetEndErrorSize(0)
mg.Draw("A")
gPad.RedrawAxis()

xmin = -6.0 #-3.0 #-2.8
xmax = 10.0 #5.0
xsumComb = -5.0 #-2.0
xcomb = 0.5
if is_tH :
    xmin = -28.
    xmax = 36.
    xcomb = 1
    xsumComb = -18.5
elif is_decay :
    xmin = -1.
    xmax = 36.
    xcomb = 1
    xsumComb = -16.5


mg.GetXaxis().SetLimits(xmin, xmax)
mg.GetYaxis().SetRangeUser(ymin, ymax)
mg.GetYaxis().SetLabelSize(0)
mg.GetYaxis().SetTickSize(0)
if is_tH :
    mg.GetXaxis().SetTitle("Best fit #mu(tH)")
else :
    mg.GetXaxis().SetTitle("Best fit #mu(t#bar{t}H)")
mg.GetXaxis().SetTitleOffset(1.5)
mg.GetYaxis().SetTitle("")
mg.GetYaxis().SetTitleSize(0.)
mg.GetYaxis().SetLabelSize(0.)
mg.GetYaxis().SetTickLength(0.)
mg.GetYaxis().SetTickSize(0.)
mg.Draw("A")

link = TLine(combined[0], ymin, combined[0], ylinemax)
link.SetLineWidth(2)
link.SetLineColor(1)
link.Draw()

luminosity=137
print ("era", era)
if era == 2016 : luminosity = 35.92
if era == 2017 : luminosity = 41.53
if era == 2018 : luminosity = 59.74
if era == 0    : luminosity = 137
tex = TLatex()
tex.SetTextSize(0.045)
tex.SetTextFont(61)
tex.DrawLatexNDC(0.26, 0.91, "CMS")
tex.SetTextSize(0.035)
tex.SetTextFont(42)
if era == 0    :
    tex.DrawLatexNDC(0.66, 0.91, "%.0f fb^{-1} (13 TeV)" % (luminosity))
else :
    tex.DrawLatexNDC(0.66, 0.91, "%.1f fb^{-1} (13 TeV)" % (luminosity))
tex.SetTextSize(0.042)
tex.SetTextFont(52)
tex.DrawLatexNDC(0.36,0.91,"Preliminary")

tex2 = TLatex()
tex2.SetTextSize(0.035)
tex3 = TLatex()
tex3.SetTextSize(0.018)
xtext = 4.75 #1.75
ysumtext = + 0.3
ycomb = 16.5 # 11.
if is_tH :
    xtext = 18
    ysumtext = -0.01
    ycomb = 15.5 # 11.
if is_decay :
    xtext = 15
    ysumtext = -0.01
    ycomb = 15.75 # 11.

for kk, key in enumerate(dprocs.keys()) :
    tex2.DrawLatex(-xtext+xmin, dprocs[key][1] + ysumtext, dprocs[key][2])
    #tex3.DrawLatex(-xtext+xmin-0.4, dprocs[key][1]-0.35, "#bf{#mu_{%s} = %.2f ^{+%.2f}_{%.2f}}" % (process, dprocs[key][0][0], abs(dprocs[key][0][2]), dprocs[key][0][1]))
    if is_decay :
        tex3.DrawLatex(-xtext+xmin-0.50, dprocs[key][1]-0.18, "#bf{#mu_{%s} = %.2f +%.2f %.2f}" % (process, dprocs[key][0][0], abs(dprocs[key][0][2]), dprocs[key][0][1]))
    else :
        tex3.DrawLatex(-xtext+xmin-0.50, dprocs[key][1]-0.38, "#bf{#mu_{%s} = %.2f +%.2f %.2f}" % (process, dprocs[key][0][0], abs(dprocs[key][0][2]), dprocs[key][0][1]))

if draw_stats_only :
    mu_comb_m1s_syst = sqrt(mu_comb_m1s*mu_comb_m1s-mu_comb_m1s_stat*mu_comb_m1s_stat)
    mu_comb_p1s_syst = sqrt(mu_comb_p1s*mu_comb_p1s-mu_comb_p1s_stat*mu_comb_p1s_stat)


tex2.DrawLatex(xsumComb+xmin, ycomb, "Combined")
tex2.SetTextSize(0.04)
if draw_stats_only :
    tex2.DrawLatex(xcomb+xmin, ycomb, "#mu = %.2f ^{+%.2f}_{-%.2f}  #bf{#left[ {}^{+%.2f}_{-%.2f}(stat.) {}^{+%.2f}_{-%.2f}(syst.)#right]}" % (combined[0], mu_comb_p1s, mu_comb_m1s, mu_comb_p1s_stat, mu_comb_m1s_stat, mu_comb_p1s_syst, mu_comb_m1s_syst))
else :
    tex2.DrawLatex(xcomb+xmin, ycomb, "#mu_{%s} = %.2f ^{+%.2f}_{-%.2f}" % (process, combined[0], mu_comb_p1s, mu_comb_m1s))


"""labels = addLabel_CMS_preliminary()
for ll in labels :
    ll.Draw()"""

if options.is_decay :
    process = process + "_decay"

savefile = os.path.join(input_folder, "test_mu_%s_%s.pdf" % (process, erastring))
c.SaveAs(savefile)
savefile = os.path.join(input_folder, "test_mu_%s_%s.root" % (process, erastring))
c.SaveAs(savefile)
