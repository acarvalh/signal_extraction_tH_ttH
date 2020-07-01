
#!/usr/bin/env python
import sys, os, re, shlex
import multiprocessing
from subprocess import Popen, PIPE
import ROOT
#from pathlib2 import Path
execfile("cards/options.dat")
import CombineHarvester.CombineTools.ch as ch
# ulimit -s unlimited

from optparse import OptionParser
parser = OptionParser()
parser.add_option(
    "--cardToRead", type="string",
    dest="cardToRead",
    help="add it without its .txt extension"
    )
parser.add_option(
    "--namePlot", type="string",
    dest="namePlot",
    help="  Set ",
    default="test"
    )
parser.add_option(
    "--cardFolder", type="string",
    dest="cardFolder",
    help="  Set ",
    default="multilep_3l_withTH_withMET_only_CRs_2017"
    )
parser.add_option("--ttW", action="store_true", dest="ttW", help="add as POI", default=False)
parser.add_option("--ttZ", action="store_true", dest="ttZ", help="add as POI", default=False)
parser.add_option("--tH", action="store_true", dest="tH", help="do results also with tH floating", default=False)
parser.add_option(
    "--ttH_tH",
    action="store_true", dest="ttH_tH",
    help="do results also with ttH and tH floating as SM",
    default=False
    )
parser.add_option(
    "--HH",
    action="store_true", dest="HH",
    help="do results also with ttH and tH floating as SM",
    default=False
    )
parser.add_option(
    "--float_all_sig",
    action="store_true", dest="float_all_sig",
    help="do results also with ttH and tH floating separated",
    default=False
    )
parser.add_option(
    "--plainBins",
    type="string",
    dest="plainBins",
    help="Overwrite the option on the cards/options.dat\n Chose between True / False / No\n -- 'No' does not overwrite ",
    default="No"
    )
parser.add_option(
    "--unblinded",
    type="string",
    dest="unblinded",
    help="Overwrite the option on the cards/options.dat\n Chose between True / False / No\n -- 'No' does not overwrite the cards/options.dat",
    default="No"
    )
parser.add_option(
    "--era", type="int",
    dest="era",
    help="To appear on the name of the file with the final plot. If era == 0 it assumes you gave the path for the 2018 era and it will use the same naming convention to look for the 2017/2016.",
    default=2017
    )
parser.add_option(
    "--channel", type="string", dest="channel",
    help="Name of the category as it is appear on the input file",
    default="1l_2tau"
    )
parser.add_option(
    "--savePlotsOn",
    type="string",
    dest="savePlotsOn",
    help="If a full path is given, it will save plots there (you need to create it first) ",
    default="none"
    )
parser.add_option("--CR", action="store_true", dest="CR", help="add as POI", default=False)

(options, args) = parser.parse_args()
CR = options.CR
HH = options.HH
## type-3

ToSubmit = " "
if sendToCondor :
    ToSubmit = " --job-mode condor --sub-opt '+MaxRuntime = 18000' --task-name"

if sendToLXBatch :
    ToSubmit = "  --job-mode lxbatch --sub-opts=\"-q 1nh\" --task-name " ## you need to add a task name using it

def runCombineCmd(combinecmd, outfolder=".", saveout=None):
    print ("Command: ", combinecmd)
    try:
        p = Popen(shlex.split(combinecmd) , stdout=PIPE, stderr=PIPE, cwd=outfolder)
        comboutput = p.communicate()[0]
    except OSError:
        print ("command not known\n", combinecmd)
        comboutput = None
    if not saveout == None :
        saveTo = outfolder + "/" + saveout
        with open(saveTo, "w") as text_file:
            text_file.write(comboutput)
        print ("Saved result to: " + saveTo)
    print ("\n")
    return comboutput

def run_cmd(command):
  print ("executing command = '%s'" % command)
  p = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
  stdout, stderr = p.communicate()
  return stdout

category      = options.channel
cardToRead    = options.cardToRead
namePlot      = options.namePlot
cardFolder    = options.cardFolder
era           = options.era
channel       = options.channel

#runCombineCmd("mkdir %s"  % (cardFolder))
FolderOut = cardFolder + "/results/"
runCombineCmd("mkdir %s"  % (FolderOut))

plainBinsLocal = options.plainBins
savePlotsOn    = options.savePlotsOn

unblinded       = options.unblinded
if unblinded == "True" : # True / False / No
    blinded = False
if unblinded == "False" : # True / False / No
    blinded = True

setpar = "--setParameters r_ttH=1,r_tH=1"
if options.ttW : setpar += ",r_ttW=1"
if options.ttZ : setpar += ",r_ttZ=1"


floating_ttV = " "
if not HH :
    if options.ttW : floating_ttV += " --PO 'map=.*/TTW.*:r_ttW[1,0,6]' --PO 'map=.*/TTWW.*:r_ttW[1,0,6]'"
    if options.ttZ : floating_ttV += " --PO 'map=.*/TTZ.*:r_ttZ[1,0,6]' "

float_sig_rates = ""
if not HH :
    if doCategoriesWS_decay :
        float_sig_rates = " --PO 'map=.*/ttH_hww.*:r_ttH_hww[1,-1,3]' --PO 'map=.*/ttH_hzz.*:r_ttH_hzz[1,-40,40]' --PO 'map=.*/ttH_htt.*:r_ttH_htt[1,-1,3]'  --PO 'map=.*/tHW.*:r_tH[1,-40,40]' --PO 'map=.*/tHq.*:r_tH[1,-40,40]'"
    elif options.ttH_tH and not doCategoriesWS:
        float_sig_rates = " --PO 'map=.*/ttH.*:r_SM[1,-1,3]' --PO 'map=.*/tHW.*:r_SM[1,-40,40]' --PO 'map=.*/tHq.*:r_SM[1,-40,40]'"
    else :
        if not CR and not doCategoriesWS:
            float_sig_rates = " --PO 'map=.*/ttH.*:r_ttH[1,-1,3]'"
        if options.tH and not doCategoriesWS_tH :
            float_sig_rates += " --PO 'map=.*/tHW.*:r_tH[1,-40,40]' --PO 'map=.*/tHq.*:r_tH[1,-40,40]'"
else :
    float_sig_rates += " --PO 'map=.*/signal_ggf_nonresonant_hh.*:r_HH[1,-20,100]' "

print("Floating signal:", float_sig_rates)

if options.ttH_tH :
    cardToRead = cardToRead + "_SMrate"
if options.float_all_sig :
    cardToRead = cardToRead + "_ttH_tH_float"

WS_output = cardToRead + "_WS"
blindStatement = " "
if blinded :
    blindStatement = " -t -1 "
if do_kt_scan_no_kin :
    ## add break if not options.tH
    cmd = "text2workspace.py"
    cmd += " %s.txt" % cardToRead.replace("_SMrate", "")
    cmd += " %s" % floating_ttV
    cmd += "  -P HiggsAnalysis.CombinedLimit.LHCHCGModels:K5 --PO verbose  --PO BRU=0"
    cmd += " -o %s/%s_kappas.root" % (FolderOut, cardToRead)
    #cmd += " ulimit -s unlimited"
    runCombineCmd(cmd, cardFolder)
    print ("done %s/%s_kappas.root" % (FolderOut, cardToRead))

    cmd = "combine -M MultiDimFit"
    cmd += " %s_kappas.root" % cardToRead
    if blinded :
        cmd += blindStatement
    cmd += " --algo grid --points 100"
    cmd += " --redefineSignalPOIs kappa_t --setParameterRanges kappa_t=-3,3 --setParameters kappa_t=1.0,kappa_V=1.0,r_ttH=1,r_tH=1"
    cmd += " --freezeParameters kappa_V,kappa_tau,kappa_mu,kappa_b,kappa_c,kappa_g,kappa_gam -m 125 --fastScan"
    cmd += " -n kt_scan_%s" % namePlot
    runCombineCmd(cmd, FolderOut)

    print ("done:  " + FolderOut + "/" + "higgsCombinekt_scan_" +namePlot + ".MultiDimFit.mH125.root")
    runCombineCmd("python test/plot_1D_kappa_scan.py --input higgsCombinekt_scan_" +namePlot + ".MultiDimFit.mH125.root --label "+ options.namePlot + " --outputFolder " + FolderOut)
    # do 1D kt scan
    # python test/plot_1D_kappa_scan.py --input2 higgsCombinekt_scan_test.MultiDimFit.mH125.root --label2 "NN_v5" --outputFolder /afs/cern.ch/work/a/acarvalh/CMSSW_10_2_10/src/tth-bdt-training/treatDatacards/2lss_1tau_NN_tHcat_2019Jun17/

if doWS :
    if not era == 0 :
        cmd = "text2workspace.py"
        cmd += " %s.txt  " % cardToRead
        cmd += " -o %s/%s_WS.root" % (FolderOut, cardToRead)
        cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
        cmd += " %s" % floating_ttV
        cmd += " %s" % float_sig_rates
        #cmd += " ulimit -s unlimited"
        runCombineCmd(cmd, cardFolder)
        print ("done %s/%s_WS.root" % (FolderOut, cardToRead))

doFor = [blindStatement]
if not blinded : doFor += [" "]

if not options.ttH_tH :
    signals = ["ttH"]
    if options.tH :
        signals += ["tH"]
else :
    signals = ["SM"]

if doRateAndSignificance :
    for signal in signals :
      #if signal == "tH" : continue
      for ss, statements in enumerate(doFor) :
        #if ss == 1 :
        label = "data"
        #if ss == 0 : label = "asimov"
        if signal == "SM"  :
            redefine = " --redefineSignalPOI r_SM  "
        else :
            if signal == "ttH" :
                redefine = " --redefineSignalPOI r_ttH  "
                if options.tH and not options.float_all_sig  :
                    redefine += " --freezeParameters r_tH  "
            if signal == "tH"  :
                redefine = " --redefineSignalPOI r_tH "
                if options.tH  :
                    if not options.float_all_sig :
                        redefine = " --freezeParameters r_ttH "

        cmd = "combineTool.py -M Significance --signif"
        cmd += " %s_WS.root" % cardToRead
        #cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
        cmd += " %s" % blindStatement
        cmd += " %s" % redefine
        cmd += " %s " % setpar
        cmd += " --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic "
        runCombineCmd(cmd, FolderOut, saveout="%s_significance_%s_%s.log" % (cardToRead, label, signal))

        cmd = "combineTool.py  -M MultiDimFit"
        cmd += " %s_WS.root" % cardToRead
        cmd += " --algo singles --cl=0.68"
        cmd += " %s" % blindStatement
        cmd += " %s" % redefine
        cmd += " -P r_%s" % signal
        cmd += " %s " % setpar
        cmd += " --floatOtherPOI=1 --saveFitResult -n step1%s  --saveWorkspace" % cardToRead
        cmd += " --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic "
        runCombineCmd(cmd, FolderOut, saveout="%s_rate_%s_%s.log" % (cardToRead, label, signal))
        ## --saveWorkspace to extract the stats only part of the errors and the limit woth mu=1 injected
        ### Some example of this concept here: https://cms-hcomb.gitbooks.io/combine/content/part3/commonstatsmethods.html#useful-options-for-likelihood-scans
        # --freezeParameters (instead of -S 0) also work on the above

        if 1 < 0 : # ss == 1 :
            cmd = "combineTool.py  -M MultiDimFit"
            cmd += " %s_WS.root" % cardToRead
            cmd += " --algo singles --cl=0.68"
            cmd += " %s" % blindStatement
            cmd += " %s" % redefine
            cmd += " -P r_%s" % signal
            cmd += " %s -S 0" % setpar
            cmd += " --floatOtherPOI=1 --saveFitResult -n step1statsonly  --saveWorkspace"
            runCombineCmd(cmd, FolderOut, saveout="%s_rate_%s_%s_stats_only_scratch.log" % (cardToRead, label, signal))

            ## Rate: stats only
            cmd = "combine -M MultiDimFit "
            cmd += " -d  higgsCombinestep1%s.MultiDimFit.mH120.root" % cardToRead
            cmd += " -w w --snapshotName \"MultiDimFit\" "
            cmd += " -n teststep2_%s" % cardToRead
            cmd += " -P r_%s" % signal
            cmd += " %s" % blindStatement
            cmd += " -S 0 --algo singles "
            runCombineCmd(cmd, FolderOut, saveout="%s_rate_%s_stats_only.log" % (cardToRead, signal))


if doRateAndSignificance_ttV :
  for signal in ["ttW", "ttZ"] :
    for ss, statements in enumerate(doFor) :
      #if ss == 1 :
      label = "data"
      #continue
      #if ss == 0 :
      #label = "asimov"
      redefine = " --redefineSignalPOI r_%s  " % signal

      cmd = "combineTool.py -M Significance --signif"
      cmd += " %s_WS.root" % cardToRead
      #cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
      cmd += " %s" % statements
      cmd += " %s" % redefine
      cmd += " %s --X-rtd MINIMIZER_analytic " % setpar
      runCombineCmd(cmd, FolderOut, saveout="%s_significance_%s_%s.log" % (cardToRead, label, signal))

      cmd = "combineTool.py  -M MultiDimFit"
      cmd += " %s_WS.root" % cardToRead
      cmd += " --algo singles --cl=0.68"
      cmd += " %s" % statements
      cmd += " %s" % redefine
      cmd += " -P r_%s" % signal
      cmd += " %s " % setpar
      cmd += " --floatOtherPOI=1 --saveFitResult -n step1%s  --saveWorkspace" % cardToRead
      cmd += " --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic "
      runCombineCmd(cmd, FolderOut, saveout="%s_rate_%s_%s.log" % (cardToRead, label, signal))


if doLimits :
    ## do in two steps: fit to data + limits mu=1 injected
    for signal in signals :
        cmd = "combine -M AsymptoticLimits "
        cmd += " %s_WS.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " %s" % setpar
        cmd += " --redefineSignalPOI r_%s -n from0_r_%s " % (signal, signal)
        runCombineCmd(cmd, FolderOut, saveout="%s_limit_%s_from0.log" % (cardToRead, signal))

        if not blinded :
            # calculate limits mu=1 injected only for final runs
            cmd = "combine -M AsymptoticLimits "
            cmd += " -t -1 higgsCombinestep1.MultiDimFit.mH120.root"
            cmd += " %s" % setpar
            cmd += " --redefineSignalPOI r_%s  -n from1_r_%s" % (signal, signal)
            cmd += " --snapshotName \"MultiDimFit\"  --toysFrequentist --bypassFrequentistFit"
            runCombineCmd(cmd, FolderOut, saveout="%s_limit_%s_from1.log" % (cardToRead, signal))

bkgs = []
if options.ttW : bkgs += ["ttW"]
if options.ttZ : bkgs += ["ttZ"]
print(bkgs)





if do2Dlikelihoods_ttH_ttZ or do2Dlikelihoods_ttH_ttW or do2Dlikelihoods_ttH_tH  :
  for ss, statements in enumerate(doFor) :
    if ss == 1 : label = "data"
    if ss == 0 :
        continue
        label = "asimov"
    if do2Dlikelihoods_with_tH :
        bkgs += ["tH"]
    ## ttH x (ttZ , ttW)
    for bkg in bkgs :
      if not bkg == "ttZ" and do2Dlikelihoods_ttH_ttZ : continue
      if not bkg == "ttW" and do2Dlikelihoods_ttH_ttW : continue
      if not bkg == "tH"  and do2Dlikelihoods_ttH_tH  : continue
      ranges = "-8,15" if bkg == "tH" else "0,3"
      for typeFit in ["central", "68", "95"] :
        cmd = "combine -M MultiDimFit "
        cmd += " %s_WS.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --cminDefaultMinimizerStrategy 0 "
        cmd += " -n For2D_ttH_%s_%s" % (bkg, typeFit)
        #cmd += " --fastScan"
        if not typeFit == "central":
            cmd += " --cl=0.%s" % typeFit
            cmd += " --algo contour2d --points=35 "
        else :
            cmd += " --algo grid --points 10000 "
        cmd += " --redefineSignalPOIs r_ttH,r_%s" % bkg
        cmd += " --setParameterRanges r_ttH=0,2:r_%s=%s" % (bkg,ranges)
        cmd += " --setParameters"
        ##TODO: set the other parameter to one
        countcoma = 0
        for rest in list(set(list(bkgs)) - set([bkg])) :
            if countcoma == 0 : cmd += " r_%s=1.0" % rest
            else : cmd += ",r_%s=1.0" % rest
            countcoma += 1
            #--setParameters kappa_t=1.0,kappa_V=1.0,r_ttH=1,r_tH=1
        runCombineCmd(cmd, FolderOut, saveout="%s_2Dlik_ttH_%s.log" % (cardToRead, bkg))
        print(cmd)
        runCombineCmd("mv higgsCombineFor2D_ttH_%s_%s.MultiDimFit.mH120.root %s_2Dlik_ttH_%s_%s_%s.root"  % (bkg, typeFit, cardToRead, bkg, typeFit, label), FolderOut)
        print ("mv higgsCombineFor2D_ttH_%s_%s.MultiDimFit.mH120.root %s_2Dlik_ttH_%s_%s_%s.root"  % (bkg, typeFit, cardToRead, bkg, typeFit, label))
      cmd = "python test/plot2DLLScan.py "
      cmd += " --input %s/%s_2Dlik_ttH_%s_%s_%s.root" % (FolderOut, cardToRead, bkg, "central", label)
      cmd += " --input68 %s/%s_2Dlik_ttH_%s_%s_%s.root" % (FolderOut, cardToRead, bkg, "68", label)
      cmd += " --input95 %s/%s_2Dlik_ttH_%s_%s_%s.root" % (FolderOut, cardToRead, bkg, "95", label)
      cmd += " --second %s" % bkg
      cmd += " --plotName  %s" % namePlot
      cmd += " --label  %s" % namePlot
      cmd += " --outputFolder  %s" % FolderOut
      runCombineCmd(cmd, saveout="%s/nllscan_%s-vs_ttH_%s.log" % (FolderOut, bkg, namePlot))
      print ("saved " +  "%s/nllscan_%s-vs_ttH_%s.pdf" % (FolderOut, bkg, namePlot))
      # plot2DLLScan.py --input /home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/legacy_27Jan_lepOv_tauTLL/results/combo_ttHmultilep_all_2Dlik_ttH_tH_central_asimov.root --input68 /home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/legacy_27Jan_lepOv_tauTLL/results/combo_ttHmultilep_all_2Dlik_ttH_tH_68_asimov.root --input95 /home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/legacy_27Jan_lepOv_tauTLL/results/combo_ttHmultilep_all_2Dlik_ttH_tH_95_asimov.root --second tH  --plotName 68only  --label " " --outputFolder /home/acaan/VHbbNtuples_8_0_x/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/deeptauWPS/legacy_27Jan_lepOv_tauTLL/results/

if do2DlikelihoodsttV :
    for ss, statements in enumerate(doFor) :
      if ss == 1 : label = "data"
      if ss == 0 :
          continue
          label = "asimov"
      ## (ttZ X ttW)
      for typeFit in ["central", "68", "95"] :
        cmd = "combine -M MultiDimFit "
        cmd += " %s_WS.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --cminDefaultMinimizerStrategy 0 "
        cmd += " -n For2D_ttZ_ttW_%s" % ( typeFit)
        cmd += " --fastScan"
        if not typeFit == "central":
            cmd += " --cl=0.%s" % typeFit
            cmd += " --algo contour2d --points=25 "
        else :
            cmd += " --algo grid --points 1800 "
        cmd += " --redefineSignalPOIs r_ttZ,r_ttW"
        cmd += " --setParameterRanges r_ttZ=-1,3:r_ttW=-1,3"
        cmd += " --setParameters"
        ##TODO: set the other parameter to one
        countcoma = 0
        cmd += " r_ttH=1.0,r_tH=1.0"
        #for rest in list(set(list(bkgs))) :
        #    if countcoma == 0 : cmd += " r_%s=1.0" % rest
        #    else : cmd += ",r_%s=1.0" % rest
        #    countcoma += 1
        #    #--setParameters kappa_t=1.0,kappa_V=1.0,r_ttH=1,r_tH=1
        runCombineCmd(cmd, FolderOut, saveout="%s_2Dlik_ttZ_ttW.log" % (cardToRead))
        runCombineCmd("mv higgsCombineFor2D_ttZ_ttW_%s.MultiDimFit.mH120.root %s_2Dlik_ttZ_ttW_%s_%s.root"  % (typeFit, cardToRead, typeFit, label), FolderOut)
      cmd = "python test/plot2DLLScan.py "
      cmd += " --input %s/%s_2Dlik_ttZ_ttW_%s_%s.root" % (FolderOut, cardToRead, "central", label)
      cmd += " --input68 %s/%s_2Dlik_ttZ_ttW_%s_%s.root" % (FolderOut, cardToRead,  "68", label)
      cmd += " --input95 %s/%s_2Dlik_ttZ_ttW_%s_%s.root" % (FolderOut, cardToRead, "95", label)
      cmd += " --second ttW"
      cmd += " --first ttZ"
      cmd += " --plotName  %s" % namePlot
      cmd += " --label  %s" % namePlot
      cmd += " --outputFolder  %s" % FolderOut
      runCombineCmd(cmd, saveout="%s/nllscan_%s-vs_ttZ_ttW.log" % (FolderOut,  namePlot))
      print ("saved " +  "%s/nllscan_%s-vs_ttZ_ttW.pdf" % (FolderOut,  namePlot))


if doHessImpacts :
    for signal in signals :
        if signal == "SM"  :
            redefine = " --redefineSignalPOI r_SM  "
        else :
            if signal == "ttH" :
                redefine = " --redefineSignalPOI r_ttH  "
                #if options.tH  : redefine += " --freezeParameters r_tH  "
            if signal == "tH"  :
                redefine = " --redefineSignalPOI r_tH " # --freezeParameters r_ttH
        # hessian impacts
        folderHessian = "%s/HesseImpacts_%s_%s"  % (FolderOut, cardToRead, signal)
        runCombineCmd("mkdir %s"  % (folderHessian))
        cmd = "combineTool.py -M Impacts"
        cmd += " -d ../%s_WS.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --rMin -2 --rMax 5"
        cmd += " -m 125 --doFits --approx hesse"
        cmd += redefine
        cmd += " --setParameters r_ttH=1" #",r_ttW=1,r_ttZ=1,r_tH=1"
        cmd += " --maxFailedSteps 20 --X-rtd MINIMIZER_analytic"
        runCombineCmd(cmd, folderHessian)
        cmd = "combineTool.py -M Impacts"
        cmd += " -d ../%s_WS.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += redefine
        cmd += " --setParameters r_ttH=1,r_ttW=1,r_ttZ=1,r_tH=1"
        cmd += " --rexclude _bin"
        cmd += "  -m 125 -o impacts.json --approx hesse --rMin -2 --rMax 5"
        cmd += " --maxFailedSteps 20 --X-rtd MINIMIZER_analytic"
        runCombineCmd(cmd, folderHessian)
        blindedOutputOpt = ' '
        runCombineCmd("plotImpacts.py -i impacts.json -o  impacts_%s_%s  --cms-label %s %s" % (cardToRead, signal, cardToRead, blindedOutputOpt), folderHessian)

if doImpactsNoSubmit :
    #run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root %s --redefineSignalPOI r_ttH  --parallel 8 %s --doInitialFit  --keepFailures ; cd - "  % (WS_output, setpar,blindStatement))
    #run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root %s --redefineSignalPOI r_ttH  --parallel 8 %s --robustFit 1 --doFits  ; cd - "  % (WS_output, setpar, blindStatement))
    #if blindedOutput : blindedOutputOpt =  ' --blind'
    #run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root  -o impacts.json    %s ; plotImpacts.py -i impacts.json %s -o impacts_btagCorr%s_blinded%s  ; cd -" % (WS_output, redefineToTTH, str(blindedOutputOpt), str(btag_correlated), str(blinded)))
    folderImpacts = "%s/Impacts_%s"  % (FolderOut, cardToRead)
    runCombineCmd("mkdir %s"  % (folderImpacts))
    cmd = "combineTool.py -M Impacts"
    cmd += " -d ../%s_WS.root" % cardToRead
    cmd += " %s" % blindStatement
    cmd += " --rMin -2 --rMax 5"
    #cmd += " -n _%s" % (namePlot)
    cmd += " -m 125  --parallel 8 --doInitialFit  --keepFailures"
    cmd += "  --redefineSignalPOI r_ttH "
    cmd += setpar
    runCombineCmd(cmd, folderImpacts)
    cmd = "combineTool.py -M Impacts"
    cmd += " -d ../%s_WS.root" % cardToRead
    cmd += " %s" % blindStatement
    cmd += " --rMin -2 --rMax 5"
    #cmd += " -n _%s" % (namePlot)
    cmd += " -m 125  --parallel 8 --robustFit 1 --doFits"
    cmd += "  --redefineSignalPOI r_ttH "
    cmd += setpar
    runCombineCmd(cmd, folderImpacts)
    cmd = "combineTool.py -M Impacts"
    cmd += " -d ../%s_WS.root" % cardToRead
    cmd += " %s" % blindStatement
    #cmd += " -n _%s" % (namePlot)
    cmd += "  -m 125 -o impacts.json  --rMin -2 --rMax 5"
    cmd += "  --redefineSignalPOI r_ttH"
    cmd += setpar
    cmd += " --rexclude _bin" # to remove stats from impact
    runCombineCmd(cmd, folderImpacts)
    blindedOutputOpt = ' '
    if blindedOutput : blindedOutputOpt =  ' --blind'
    runCombineCmd("plotImpacts.py -i impacts.json -o  impacts_%s %s  --cms-label %s" % (namePlot, blindedOutputOpt, cardToRead), folderImpacts)

##############################################################################
## to make separate mu / limits
## this needs to be adapted to the naming convention of the bins on the input card, and to how we want to do fit for legacy
sigRates = [
    "ttH_2lss_0tau",
    "ttH_3l_0tau",
    "ttH_4l",
    "ttH_2lss_1tau",
    "ttH_3l_1tau",
    "ttH_2l_2tau",
    "ttH_1l_2tau",
    "ttH_0l_2tau",
    "ttH_1l_1tau",
    "ttH_2los_1tau"
    ]
folderCat = "%s/categories_%s"  % (FolderOut, cardToRead)

if doCategoriesWS :
    runCombineCmd("mkdir %s"  % (folderCat))
    floating_by_cat = ""
    for sigRate in sigRates :
        if "2l_2tau" in sigRate :
            floating_by_cat += " --PO 'map=.*%s.*/ttH.*:r_%s[1,0,10]'" % (sigRate, sigRate)
        else :
            floating_by_cat += " --PO 'map=.*%s.*/ttH.*:r_%s[1,-5,10]'" % (sigRate, sigRate)
    cmd = "text2workspace.py "
    cmd += " %s/../%s.txt" % (FolderOut, cardToRead)
    cmd += " -o %s_Catpoi_final.root" % cardToRead
    cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
    cmd += " %s" % floating_ttV
    cmd += " %s" % float_sig_rates
    cmd += " %s" % floating_by_cat
    #cmd += " ulimit -s unlimited"
    print (cmd)
    runCombineCmd(cmd, folderCat)

if doCategoriesMu :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1"
    if options.tH :
        if options.ttW or options.ttZ : parameters += ","
        parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates + bkgs :
        #if rate in [
        #"ttH_2lss_0tau",
        #"ttH_3l_0tau",
        #"ttH_4l",
        #"ttH_2lss_1tau",
        #"ttH_3l_1tau",
        #"ttH_2l_2tau",
        #] : continue #
        #if rate not in ["ttZ", "ttW"] : continue
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo singles --cl=0.68"
        cmd += " -P r_%s" % rate
        cmd += " -n rate_%s_%s" % (rate, namePlot)
        cmd += " --cminDefaultMinimizerStrategy 0  --keepFailures " # --X-rtd MINIMIZER_analytic
        cmd += " --floatOtherPOI=1 "
        cmd += " --robustFit 1"
        if sendToCondor :
            cmd += " %s ttH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_rate_%s_%s.log" % (cardToRead, rate, namePlot))
        print (cmd)
    ####
    cmd = "python test/makeMuPlot.py "
    cmd += " --input_folder  %s" % folderCat
    cmd += " --era  %s" % str(era)
    output = run_cmd(cmd)
    fileInfo = "%s/makeMuPlot_ttH_%s.log" % (folderCat, str(era))
    ff = open(fileInfo ,"w+")
    ff.write(output)
    ff.close()
    didPlot = False
    for line in open(fileInfo):
        if '.pdf' in line and "saved" in line :
            print(line)
            didPlot = True
            break
    if didPlot == False :
        print ("!!!!!!!!!!!!!!!!!!!!!!!! The makeMuPlots did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % fileInfo)
        print(cmd)
        print ("")
        print ("First suspect: ")
        print ("   --> It does assume that you had already run with 'doRateAndSignificance = True' above")
        print ("   --> It will take the log files of those to add the combo result on the plot of mu/categories")
        print ("-----> Did you ran it?")
        sys.exit()
    ## python test/makeMuPlot.py --input_folder /home/acaan/CMSSW_10_2_13/src/cards_set/legacy_11April20_unblinded/results//categories_combo_ttHmultilep_2018 --era 2018 --is_tH


if doCategoriesMu_likScan :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1"
    if options.tH :
        if options.ttW or options.ttZ : parameters += ","
        parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates + bkgs :
        #if rate in [
        #"ttH_2lss_0tau",
        #"ttH_3l_0tau",
        #"ttH_4l",
        #"ttH_2lss_1tau",
        #"ttH_3l_1tau",
        #"ttH_2l_2tau",
        #] : continue
        if rate in ["ttZ", "ttW"] : continue
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo=grid --points 70 " # --rMin -6 --rMax 11
        cmd += " -P r_%s" % rate
        cmd += " -n rate_%s_%s_grid" % (rate, namePlot)
        cmd += " --cminDefaultMinimizerStrategy 0   " # --X-rtd MINIMIZER_analytic
        cmd += " --floatOtherPOI=1 " #  --keepFailures -S 0 --cminDefaultMinimizerType Minuit
        #cmd += " --robustFit 1"
        if sendToCondor :
            cmd += " %s ttH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_rate_%s_%s_grid.log" % (cardToRead, rate, namePlot))
        print (cmd)


if doCategoriesSig :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1"
    if options.tH :
        if options.ttW or options.ttZ : parameters += ","
        parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates + bkgs :
        #if rate in [
        #"ttH_2lss_0tau",
        #"ttH_3l_0tau",
        #"ttH_4l",
        #"ttH_2lss_1tau",
        #"ttH_3l_1tau",
        #"ttH_2l_2tau",
        #] : continue
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " -M Significance --signif " # remember why it was --algo none
        cmd += " --redefineSignalPOI r_%s" % rate
        cmd += " -n rate_%s_%s" % (rate, namePlot)
        cmd += " --floatOtherPOI=1 --cminDefaultMinimizerType Minuit --keepFailures" #  -S 0
        if sendToCondor :
            cmd += " %s ttH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_sig_%s_%s.log" % (cardToRead, rate, namePlot))
        #print (cmd)

#cmd = "combineTool.py -M Significance --signif"
#cmd += " %s_WS.root" % cardToRead
#cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
#cmd += " %s" % blindStatement
#cmd += " %s" % redefine
#cmd += " %s " % setpar

if doCategoriesWS_tH :
    runCombineCmd("mkdir %s"  % (folderCat))
    floating_by_cat = ""
    for sigRate in sigRates :
        floating_by_cat += " --PO 'map=.*%s.*/tH.*:r_%s[1,-30,30]'" % (sigRate.replace("ttH", "tH"), sigRate.replace("ttH", "tH"))
    cmd = "text2workspace.py "
    cmd += " %s/../%s.txt" % (FolderOut, cardToRead)
    cmd += " -o %s_Catpoi_final_tH.root" % cardToRead
    cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
    cmd += " %s" % floating_ttV
    cmd += " %s" % float_sig_rates
    cmd += " %s" % floating_by_cat
    runCombineCmd(cmd, folderCat)

if doCategoriesMu_tH :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1,"
    parameters += "r_ttH=1"
    #if options.tH :
    #    if options.ttW or options.ttZ : parameters += ","
    #    parameters += "r_tH=1"
    for rate in sigRates :
        parameters = parameters + ",r_"+rate.replace("ttH", "tH")+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates :
        print (rate)
        if rate not in [
        "ttH_2lss_0tau",
        "ttH_3l_0tau",
        #"ttH_4l",
        "ttH_2lss_1tau",
        #"ttH_3l_1tau",
        #"ttH_2l_2tau",
        ] : continue
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final_tH.root" % cardToRead
        #cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo singles --cl=0.68" # remember why it was --algo none
        cmd += " -P r_%s" % rate.replace("ttH", "tH")
        cmd += " -n rate_%s_%s" % (rate.replace("ttH", "tH"), namePlot)
        cmd += " --floatOtherPOI=1 --keepFailures " #  -S 0
        #cmd += " --freezeParameters r_ttH "
        cmd += " --robustFit 1"
        cmd += "  --cminDefaultMinimizerStrategy 0 " # --robustFit  --X-rtd MINIMIZER_analytic
        if sendToCondor :
            cmd += " %s tH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_rate_%s_%s.log" % (cardToRead, rate.replace("ttH", "tH"), namePlot))
    ####
    cmd = "python test/makeMuPlot.py "
    cmd += " --input_folder  %s" % folderCat
    cmd += " --era  %s" % str(era)
    cmd += " --is_tH"
    output = run_cmd(cmd)
    fileInfo = "%s/MuPlot_tH_%s.log" % (folderCat, str(era))
    ff = open(fileInfo ,"w+")
    ff.write(output)
    ff.close()
    didPlot = False
    for line in open(fileInfo):
        if '.pdf' in line and "saved" in line :
            print(line)
            didPlot = True
            break
    if didPlot == False and 0 > 1:
        print ("!!!!!!!!!!!!!!!!!!!!!!!! The makeMuPlot did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % fileInfo)
        print(cmd)
        print ("")
        print ("First suspect: ")
        print ("   --> It does assume that you had already run with 'doRateAndSignificance = True' above")
        print ("   --> It will take the log files of those to add the combo result on the plot of mu/categories")
        print ("-----> Did you ran it?")
        sys.exit()

if doCategoriesMu_tH_likScan :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1,"
    parameters += "r_ttH=1"
    #if options.tH :
    #    if options.ttW or options.ttZ : parameters += ","
    #    parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_"+rate.replace("ttH", "tH")+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates :
        if rate not in [
        "ttH_2lss_0tau",
        "ttH_3l_0tau",
        #"ttH_4l",
        "ttH_2lss_1tau",
        #"ttH_3l_1tau",
        #"ttH_2l_2tau",
        ] : continue
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final_tH.root" % cardToRead
        #cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo=grid --points 100 " # --rMin -6 --rMax 11
        #cmd += " --algo singles --cl=0.68" # remember why it was --algo none
        cmd += " -P r_%s" % rate.replace("ttH", "tH")
        cmd += " -n rate_%s_%s_grid" % (rate.replace("ttH", "tH"), namePlot)
        cmd += " --floatOtherPOI=1 --keepFailures " #  -S 0
        cmd += " --freezeParameters r_ttH "
        #cmd += " --robustFit 1"
        cmd += " --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic " # --robustFit
        if sendToCondor :
            cmd += " %s tH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_rate_%s_%s_grid.log" % (cardToRead, rate.replace("ttH", "tH"), namePlot))

if doCategoriesWS_decay :
    runCombineCmd("mkdir %s"  % (folderCat))
    #floating_by_decay =  = ""
    #for sigRate in sigRates :
    #    floating_by_cat += " --PO 'map=.*%s.*/tH.*:r_%s[1,-30,30]'" % (sigRate.replace("ttH", "tH"), sigRate.replace("ttH", "tH"))
    cmd = "text2workspace.py "
    cmd += " %s/../%s.txt" % (FolderOut, cardToRead)
    cmd += " -o %s_Catpoi_final_decay.root" % cardToRead
    cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
    cmd += " %s" % floating_ttV
    cmd += " %s" % float_sig_rates
    #cmd += " %s" % floating_by_cat
    runCombineCmd(cmd, folderCat)

if doCategoriesMu_decay :
    runCombineCmd("mkdir %s"  % (folderCat))
    ## test foldercat cmd += " -o %s_Catpoi_final_decay.root" % cardToRead
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1,"
    #parameters += "r_ttH=1"
    #if options.tH :
    #    if options.ttW or options.ttZ : parameters += ","
    #    parameters += "r_tH=1"
    sigRates = [ "ttH_hzz", "ttH_htt", "ttH_hww", "tH"]
    for rate in sigRates :
        parameters = parameters + ",r_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates :
        print (rate)
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " %s_Catpoi_final_decay.root" % cardToRead
        #cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo singles --cl=0.68" # remember why it was --algo none
        cmd += " -P r_%s" % rate
        cmd += " -n rate_%s_%s" % (rate, namePlot)
        cmd += " --floatOtherPOI=1 --keepFailures " #  -S 0
        #cmd += " --freezeParameters r_ttH "
        cmd += " --robustFit 1"
        cmd += "  --cminDefaultMinimizerStrategy 0 " # --robustFit  --X-rtd MINIMIZER_analytic
        if sendToCondor :
            cmd += " %s ttH_%s_%s" % (ToSubmit.replace("+MaxRuntime = 1800", "+MaxRuntime = 900"), rate,  namePlot) # .replace("+MaxRuntime = 1800", "+MaxRuntime = 60")
            runCombineCmd(cmd, folderCat)
        else :
            runCombineCmd(cmd, folderCat, saveout="%s_rate_%s_%s.log" % (cardToRead, rate.replace("ttH", "tH"), namePlot))


if doCategoriesLimits :
    runCombineCmd("mkdir %s"  % (folderCat))
    parameters = ""
    if options.ttW : parameters += "r_ttW=1"
    if options.ttZ :
        if options.ttW : parameters += ","
        parameters += "r_ttZ=1"
    if options.tH :
        if options.ttW or options.ttZ : parameters += ","
        parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates + bkgs :
        cmd = "combineTool.py -M AsymptoticLimits"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " -P r_%s" % rate
        cmd += " --floatOtherPOI=1 -S 0 --cminDefaultMinimizerType Minuit --keepFailures"
        runCombineCmd(cmd, folderCat, saveout="%s/%s_limit_%s.log" % (folderCat, cardToRead, rate))

# calculate limits mu=1 injected only for final runs
## This does not seem correct -- check before using it again
if doCategoriesLimitsFromMu1 :
        cmd = "combineTool.py -M AsymptoticLimits"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --redefineSignalPOI r_%s" % rate
        cmd += " -n from0_%s " % (rate)
        if sendToCondor : cmd += " %s from0_%s" % (ToCondor, rate)
        runCombineCmd(cmd, folderCat, saveout="%s/%s_limit_from0_%s.log" % (folderCat, WS_output_byCat, rate))

if preparePlotHavester or preparePlotCombine :
    if str(plainBinsLocal) == "True" : # True / False / No
        plainBins = True
    if str(plainBinsLocal) == "False" : # True / False / No
        plainBins = False

    eraDraw = era
    if era == 0 :
        eraDraw = 0
        era = 2018
        print ("=====> Mind that 'era 0 ' will only work if the other eras are already done")

    if preparePlotCombine and not eraDraw == 0 and not drawPlotOnly:
        cmd = "combineTool.py -M FitDiagnostics "
        cmd += " %s_WS.root" % cardToRead
        if blinded :
            cmd += " -t -1 "
        cmd += " --saveShapes --saveWithUncertainties "
        #cmd += " --freezeParameters CMS_ttHl_ZZ_lnU,CMS_ttHl_WZ_lnU"
        # redefineToTTH
        if doPostFit         :
            cmd += " --saveNormalization "
        else :
            cmd += " --skipBOnlyFit "
        cmd += " -n _shapes_combine_%s" % cardToRead
        #cmd += " --forceRecreateNLL"
        #if not plainBins : cmd += " -d %s.txt"        % cardToRead
        if sendToLXBatch or sendToCondor : cmd += " %s %s" % (ToSubmit, cardToRead)
        runCombineCmd(cmd, FolderOut)
        print ("created " + FolderOut + "/fitDiagnostics_shapes_combine_%s.root" % cardToRead)

    if preparePlotHavester and not eraDraw == 0 and not drawPlotOnly:
        print ("[WARNING:] combineHavester does not deal well with autoMCstats option for bin by bin stat uncertainty -- it does some approximations on errors -- this is good option to run fast prefit plots on diagnosis stage")
        # to have Totalprocs computed
        cmd = "combineTool.py -M FitDiagnostics %s_WS.root" % cardToRead
        if blinded :
            cmd += " -t -1 "
        if sendToLXBatch :
            cmd += " %s %s" % (ToSubmit, cardToRead)
        cmd += " -n _%s" % cardToRead
        #cmd += " --freezeParameters CMS_ttHl_ZZ_lnU,CMS_ttHl_WZ_lnU"
        runCombineCmd(cmd, FolderOut)
        print ("the diagnosis that input Havester is going to be on fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine -- check if that was the case you have a crash!")

        shapeDatacard    = "%s_shapes.root" % cardToRead
        if doPostFit :
            shapeDatacard = shapeDatacard.replace(".root", "_postfit.root")
        else  :
            shapeDatacard = shapeDatacard.replace(".root", "_prefit.root")
        if plainBins :
            shapeDatacard = shapeDatacard.replace(".root", "_plainBins.root")

        cmd = "PostFitShapesFromWorkspace "
        cmd += " --workspace %s_WS.root" % cardToRead
        cmd += " --o %s" % shapeDatacard
        cmd += " --sampling --print "
        if doPostFit         :
            cmd += " --postfit "
        cmd += "-f fitDiagnostics_%s.root:fit_s " % cardToRead
        if not plainBins :
            cmd += " -d ../%s.txt"     % cardToRead
        runCombineCmd(cmd, FolderOut)
        print ("created " + FolderOut + "/" + shapeDatacard )

    if savePlotsOn == "none" :
        savePlotsOn = FolderOut
    cmd = "python test/makePlots.py "
    if preparePlotHavester  :
        cmd += " --input  %s" % FolderOut + "/" + shapeDatacard
        cmd += " --fromHavester"
    if preparePlotCombine :
        cmd += " --input  %s" % FolderOut + "/fitDiagnostics_shapes_combine_" + cardToRead + ".root"
    cmd += " --odir %s" % savePlotsOn
    #if doPostFit         :
    #    cmd += " --postfit "
    if not plainBins :
        cmd += " --original %s/../%s.root"        % (FolderOut, cardToRead)
    cmd += " --era %s" % str(eraDraw)
    cmd += " --nameOut %s" % cardToRead.replace(str(era), str(eraDraw))
    #cmd += " --do_bottom "
    cmd += " --channel %s" % channel
    if HH :
        cmd += " --HH --binToRead HH_1l_0tau --binToReadOriginal  HH_1l_0tau "
        cmd += "--nameLabel %s_%s_%s --labelX %s" % (cardToRead.split("_")[2], cardToRead.split("_")[3], cardToRead.split("_")[6], namePlot)
    if not blinded         :
        cmd += " --unblind  "
    if drawPlot and not doPostFit :
        output = run_cmd(cmd)
        fileInfo = "%s/%s.log" % (savePlotsOn, cardToRead)
        ff = open(fileInfo ,"w+")
        ff.write(output)
        ff.close()
        didPlot = False
        for line in open(fileInfo):
            if '.pdf' in line and "saved" in line :
                print(line)
                didPlot = True
                break
        if didPlot == False :
            print ("!!!!!!!!!!!!!!!!!!!!!!!! The makePlots did not worked, to debug please check %s to see up to when the script worked AND run again for chasing the error:" % fileInfo)
            print(cmd)
            sys.exit()
    else :
        print ("suggestion of command to run to have the plot: ")
        print (cmd)

    if doTableYields :
        execfile("python/data_manager_makePostFitPlots.py")
        ROOT.gSystem.Load('libHiggsAnalysisCombinedLimit')
        print ("Retrieving yields from workspace: %s_WS.root" % cardToRead)
        fin = ROOT.TFile("%s/%s_WS.root" % (FolderOut, cardToRead))
        wsp = fin.Get('w')
        cmb = ch.CombineHarvester()
        cmb.SetFlag("workspaces-use-clone", True)
        ch.ParseCombineWorkspace(cmb, wsp, 'ModelConfig', 'data_obs', False)
        print "datacardToRead parsed"
        import os
        print ("taking uncertainties from: fitDiagnostics_%s.root " % cardToRead)
        mlf = ROOT.TFile("%s/fitDiagnostics_%s.root " % (FolderOut, cardToRead))
        rfr = mlf.Get('fit_s')
        fit = "prefit"
        if doPostFit :
            fit = "postfit"
        if fit == "postfit" :
            cmb.UpdateParameters(rfr)
            print ' Parameters updated '
        colapseCat = False
        filey = open(FolderOut + "/" + cardToRead + "_prefit_yields_" + str(era) + ".log","w")
        labels = ["ttH_%s" % channel]
        if fit == "prefit" :
            PrintTable(cmb, tuple(), filey, blindedOutput, labels, type)
        if fit == "postfit" :
            PrintTable(cmb, (rfr, 500), filey, blindedOutput, labels, type)





###############################################
#### ---- stoped the update here: to be continued
if 0 > 1 :
    if doLimitsByCat :
        parameters0 = "r_ttW=1"
        for rate in sigRates :
            parameters0 = parameters0+","+rate+"=0"

        for rate in sigRates + [ "r_ttW" ]:

            if sendToCondor : run_cmd("cd "+enterHere+" ; combineTool.py -M AsymptoticLimits %s.root %s --setParameters %s --redefineSignalPOI %s  -n from0_%s %s from0_%s > %s_limit_from0_%s.log  ; cd -"  % (WS_output_byCat, blindStatement, parameters0, rate, rate , ToCondor, rate , WS_output_byCat, rate)) #  --floatOtherPOI=1
            else :
                run_cmd("cd "+enterHere+" ; combineTool.py -M AsymptoticLimits %s.root %s --setParameters %s --redefineSignalPOI %s  -n from0_%s  > %s_limit_from0_%s.log  ; cd -"  % (WS_output_byCat, blindStatement, parameters0, rate, rate ,  WS_output_byCat, rate)) #  --floatOtherPOI=1
                run_cmd("cd "+enterHere+" ; combineTool.py -M AsymptoticLimits %s.root %s --setParameters %s --redefineSignalPOI %s -t -1 -n from0_%s  > %s_limit_from1_%s.log  ; cd -"  % (WS_output_byCat, blindStatement, parameters0, rate, rate ,  WS_output_byCat, rate))

            #run_cmd("cd "+enterHere+" ; combineTool.py -M MultiDimFit %s.root %s --setParameters %s --algo singles --cl=0.68 -P %s --floatOtherPOI=1 --saveFitResult -n step1_%s --saveWorkspace ; cd -"  % (WS_output_byCat, blindStatement, parameters, rate, rate))
            ### I do not try to submit as this is not so slow, and the output of this is needed for the next step

            #run_cmd("cd "+enterHere+" ; combineTool.py -M AsymptoticLimits -t -1   higgsCombinestep1_%s.MultiDimFit.mH120.root   --setParameters %s --redefineSignalPOI %s  -n from1_%s --snapshotName \"MultiDimFit\"  --toysFrequentist --bypassFrequentistFit %s from1_%s -n from1_%s  > %s_limit_from1_%s.log ; cd -"  % (rate, parameters, rate, rate, ToCondor, rate, rate, WS_output_byCat, rate)) #  --floatOtherPOI=1
            #    --redefineSignalPOI r_ttH_thiscategory --floatOtherPOI 1 is:
            # - consider only r_ttH_thiscategory as parameter of interest
            # - the other POIs are left freely floating

            #run_cmd("cd "+enterHere+" ; combineTool.py -M AsymptoticLimits   higgsCombinestep1_%s.MultiDimFit.mH120.root   --setParameters %s --redefineSignalPOI %s  -n from1_%s --snapshotName \"MultiDimFit\"  --toysFrequentist --bypassFrequentistFit %s from1_%s -n from1_%s_notAsimov  > %s_limit_from1_%s.log ; cd -"  % (rate, parameters, rate, rate, ToCondor, rate, rate, WS_output_byCat, rate))

    if doRatesByLikScan :
        typeFitRates      = [ " ", " -t -1 "]
        typeFitRatesLabel = [ "Obs", "Exp"]
        run_cmd("mkdir "+os.getcwd()+"/"+mom_result+"/categories_"+card+"_folder")
        #enterHere = os.getcwd()+"/"+mom_result+"/categories_"+card+"_folder"
        print enterHere
        WS_output_byCat = card+"_Catpoi_final"

        parameters = "r_ttW=1,r_ttZ=1"
        for rate in ["r_ttH_2lss_0tau", "r_ttH_3l_0tau", "r_ttH_4l", "r_ttH_2lss_1tau", "r_ttH_3l_1tau", "r_ttH_2l_2tau", "r_ttH_1l_2tau"] :
            parameters = parameters+","+rate+"=1"
        print "Will fit the parameters "+parameters

        for rate in ["r_ttH_2l_2tau"] : # sigRates + [ "r_ttW" , "r_ttZ" ] :
            for ll, label in enumerate(typeFitRatesLabel) :
                if not "2l_2tau" in rate : continue
                doPlotsByLikScan = False
                if not doPlotsByLikScan :
                    submit = " "
                    ToCondor1 = ToCondor+" "+label+rate+" --split-points 40"
                    run_cmd("cd "+enterHere+" ; combineTool.py -M MultiDimFit %s.root --setParameters %s -P %s --floatOtherPOI=1 -m 125 --algo=grid --points 200 --rMin 0 --rMax 10  -n %s %s %s  ; cd -"  % (WS_output_byCat,  parameters, rate, label+"_"+rate, typeFitRates[ll],  ToCondor1 )) #
                    ### hadd the result files

                if doPlotsByLikScan :
                    ## hadd the results, the plotter bellow will also create a file with the crossings
                    ## hadd higgsCombineObs_r_ttH_2l_2tau.POINTS.MultiDimFit.mH125.root higgsCombineObs_r_ttH_2l_2tau.POINTS.*.MultiDimFit.mH125.root
                    run_cmd("cd "+enterHere+" ; $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plot1DScan.py higgsCombine%s_%s.MultiDimFit.mH125.root --others higgsCombine%s_%s.MultiDimFit.mH125.root:Expected:2 --POI %s -o ML_%s"  % ( label, rate, label, rate, rate, rate ))

if (cardToRead == cardToRead and doImpactCombo) or ( doImpact2017) :
    ### For impacts 2017 + 2016 only
    ## there is a funcionality for ignoring the bin stats errors in this fork https://github.com/gpetruc/CombineHarvester/commit/28c66f57649a7f9b279cd3298fe905b2073e095a
    ## it creates many files !!!!
    if not sendToCondor or impactsSubmit :
        run_cmd("mkdir "+os.getcwd()+"/"+mom_result+"/impacts_"+card)
        enterHere = os.getcwd()+"/"+mom_result+"/impacts_"+card
        run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root %s --redefineSignalPOI r_ttH  --parallel 8 %s --doInitialFit  --keepFailures ; cd - "  % (WS_output, setpar,blindStatement))
        run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root %s --redefineSignalPOI r_ttH  --parallel 8 %s --robustFit 1 --doFits  ; cd - "  % (WS_output, setpar, blindStatement))
    if not sendToCondor or not impactsSubmit :
        blindedOutputOpt = ' '
        if blindedOutput : blindedOutputOpt =  ' --blind'
        run_cmd("cd "+enterHere+" ; combineTool.py -M Impacts -m 125 -d ../%s.root  -o impacts.json    %s ; plotImpacts.py -i impacts.json %s -o impacts_btagCorr%s_blinded%s  ; cd -" % (WS_output, redefineToTTH, str(blindedOutputOpt), str(btag_correlated), str(blinded)))

if (cardToRead == cardToRead and doGOFCombo) or (doGOF2017) :
    ## it creates many files !!!!
    run_cmd("mkdir "+os.getcwd()+"/"+mom_result+"/gof_"+card)
    enterHere = os.getcwd()+"/"+mom_result+"/gof_"+card
    if sendToCondor :
        ### if you are submitting to condor you need to do in 2 steps, the second step collect the toys
        if GOF_submit :
            run_cmd("cd "+enterHere+' ;  combineTool.py -M GoodnessOfFit --algo=saturated  %s %s.root ; cd -' % (redefineToTTH, WS_output))
            filesh = open(enterHere+"/submit_gof.sh","w")
            filesh.write(
                "#!/bin/bash\n"+\
                "for ii in {1..500}\n" # this makes 1000 toys
                "do\n"
                "  r=$(( $RANDOM % 10000 ))\n"
                "  #echo $r \n"
                "  combineTool.py -M GoodnessOfFit --algo=saturated  "+redefineToTTH+"  -t 2 -s $r -n .toys$ii "+enterHere+"/"+WS_output+".root  --saveToys --toysFreq "+sendToCondor+" \n"
                "done\n"
                )
            run_cmd(os.getcwd()+"/"+mom_result+"/GOF"+' ; bash submit_gof.sh ; cd -' )
        else : # CollectGoodnessOfFit
            run_cmd("combineTool.py -M CollectGoodnessOfFit --input higgsCombine.Test.GoodnessOfFit.mH120.root higgsCombine*.GoodnessOfFit.mH120.*.root -o gof.json")
            run_cmd("cd "+os.getcwd()+"/"+mom_result+" ;  $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotGof.py --statistic saturated --mass 120.0 gof.json -o GoF_saturated_"+WS_output+'_btagCorr'+str(btag_correlated)+'_blinded'+str(blinded)+" ; cd -")
    else : # do all toys in series
        run_cmd("cd "+enterHere+' ;  combineTool.py -M GoodnessOfFit --algo=saturated  %s  %s.root ; cd -' % (redefineToTTH, WS_output))
        run_cmd("cd "+enterHere+' ; combineTool.py -M GoodnessOfFit --algo=saturated  -t 1000 -s 12345  --saveToys --toysFreq %s   %s.root ; cd -' % (redefineToTTH, WS_output)) -- here
        run_cmd("cd "+enterHere+' ; combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH120.root higgsCombineTest.GoodnessOfFit.mH120.12345.root -o gof.json ; cd -')
        run_cmd("cd "+enterHere+" ;  $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotGof.py --statistic saturated --mass 120.0 gof.json -o GoF_saturated_"+WS_output+'_btagCorr'+str(btag_correlated)+'_blinded'+str(blinded)+" ; cd -")


if doYieldsAndPlots :

    #takeYields = cardToRead + "_3poi_ttVFromZero"
    takeYields = WS_output
    doPostfit = "none"
    if blinded : blindStatementPlot = '  '
    else : blindStatementPlot = ' --unblind '

    enterHere = os.getcwd()+"/"+mom_result
    doPostFitCombine = True
    if 0>1 :
        doPostfit = savePostfitCombine
        fileShapes = "fitDiagnostics.root"
        appendHavester = " "
        fileoriginal = "--original %s/../%s.root" % (enterHere,card)
    if 1 > 0 : # doPostfitHavester
        doPostfit = savePostfitHavester
        fileShapes = WS_output+"_shapes.root"
        appendHavester = " --fromHavester "
        fileoriginal = " "
    if doPostfit == "none" :
        run_cmd("cd "+enterHere+' ; combineTool.py -M FitDiagnostics %s/../%s.root %s ; cd -' % (enterHere, WS_output, redefineToTTH))
    else : enterHere = enterHere+"/"+doPostfit

    run_cmd("cd "+enterHere+' ; python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a fitDiagnostics.root -g plots.root  -p r_ttH  ; cd -')
    gSystem.Load('libHiggsAnalysisCombinedLimit')
    print ("Retrieving yields from workspace: ", os.getcwd()+"/"+takeYields)
    fin = TFile(os.getcwd()+"/"+mom_result+takeYields+".root")
    wsp = fin.Get('w')
    cmb = ch.CombineHarvester()
    cmb.SetFlag("workspaces-use-clone", True)
    ch.ParseCombineWorkspace(cmb, wsp, 'ModelConfig', 'data_obs', False)
    print "datacardToRead parsed"
    import os
    print ("taking uncertainties from: "+enterHere+'/fitDiagnostics.root')
    print ("the diagnosis that input Havester is going to be on fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine -- check if you have a crash!")
    mlf = TFile(enterHere+'/fitDiagnostics.root')
    rfr = mlf.Get('fit_s')
    typeFit = " "
    for fit in ["prefit"] : # , "postfit"
        print fit+' tables:'
        if fit == "postfit" :
            cmb.UpdateParameters(rfr)
            print ' Parameters updated '
            typeFit = " --doPostFit "
        if not takeCombo :
            labels = [
            "1l_2tau_OS_mvaOutput_final_x_2017",
            "2l_2tau_sumOS_mvaOutput_final_x_2017",
            "3l_1tau_OS_mvaOutput_final_x_2017",
            "2lss_1tau_sumOS_mvaOutput_final_x_2017"
            ]
        else :
            labels=[
            "1l_2tau_OS",
            "2l_2tau_sumOS",
            "3l_1tau_OS",
            "2lss_1tau_sumOS"
            ]
        type = 'tau'
        colapseCat = False
        filey = open(os.getcwd()+"/"+mom_result+"yields_"+type+"_from_combo_"+fit+".tex","w")
        if fit == "prefit" : PrintTables(cmb, tuple(), filey, blindedOutput, labels, type)
        if fit == "postfit" : PrintTables(cmb, (rfr, 500), filey, blindedOutput, labels, type)
        print ("the yields are on this file: ", os.getcwd()+"/"+mom_result+"yields_"+type+"_from_combo_"+fit+".tex")
        if not doPostfit == "none" :
            optionsToPlot = [
                ' --minY 0.07 --maxY 5000. --useLogPlot --notFlips --unblind ',
                ' --minY -0.35 --maxY 14 --notFlips --notConversions --unblind ',
                ' --minY -0.2 --maxY 6.9 --MC_IsSplit --notFlips --unblind ',
                ' --minY -0.9 --maxY 24 --MC_IsSplit --unblind '
            ]
            for ll, label in enumerate(labels) :
                run_cmd('python makePostFitPlots_FromCombine.py --channel  ttH_%s  --input %s %s %s %s %s --original %s/../%s.root > %s' % (label, enterHere+"/"+fileShapes, appendHavester, typeFit, blindStatementPlot, optionsToPlot[ll], enterHere, card, enterHere+"/"+fileShapes+"_"+label+".log"))
