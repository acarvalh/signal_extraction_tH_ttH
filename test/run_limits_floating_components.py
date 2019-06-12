
#!/usr/bin/env python
import sys, os, re, shlex
import multiprocessing
from subprocess import Popen, PIPE
#from pathlib2 import Path
execfile("cards/options.dat")
import CombineHarvester.CombineTools.ch as ch

from optparse import OptionParser
parser = OptionParser()
parser.add_option("--cardToRead", type="string", dest="cardToRead", help="add it without its .txt extension")
parser.add_option("--namePlot", type="string", dest="namePlot", help="  Set ", default="test")
parser.add_option("--cardFolder", type="string", dest="cardFolder", help="  Set ", default="multilep_3l_withTH_withMET_only_CRs_2017")
parser.add_option("--ttW", action="store_true", dest="ttW", help="add as POI", default=False)
parser.add_option("--ttZ", action="store_true", dest="ttZ", help="add as POI", default=False)
parser.add_option("--tH", action="store_true", dest="tH", help="do results also with tH floating", default=False)
(options, args) = parser.parse_args()

## type-3

ToSubmit = " "
if sendToCondor :
    ToSubmit = " --job-mode condor --sub-opt '+MaxRuntime = 18000'"

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
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

cardToRead = options.cardToRead     
namePlot = options.namePlot 
cardFolder = options.cardFolder
blinded = True

setpar = "--setParameters r_ttH=1,r_tH=1"
if options.ttW : setpar += ",r_ttW=1"
if options.ttZ : setpar += ",r_ttZ=1"


floating_ttV = " "
if options.ttW : floating_ttV += " --PO 'map=.*/TTW.*:r_ttW[1,0,6]' --PO 'map=.*/TTWW.*:r_ttW[1,0,6]'"
if options.ttZ : floating_ttV += " --PO 'map=.*/TTZ.*:r_ttZ[1,0,6]' "

float_sig_rates = " --PO 'map=.*/ttH.*:r_ttH[1,-1,3]'"
if options.tH : float_sig_rates += "--PO 'map=.*/tHW.*:r_tH[1,-40,40]' --PO 'map=.*/tHq.*:r_tH[1,-40,40]'"

WS_output = cardToRead + "_3poi"
blindStatement = " -t -1 "
if do_kt_scan_no_kin :
    ## add break if not options.tH
    cmd = "text2workspace.py"
    cmd += " %s.txt" % cardToRead
    cmd += " %s" % floating_ttV
    cmd += "  -P HiggsAnalysis.CombinedLimit.LHCHCGModels:K5 --PO verbose  --PO BRU=0"
    cmd += " -o %s_kappas.root" % cardToRead
    runCombineCmd(cmd, cardFolder)

    cmd = "combine -M MultiDimFit"
    cmd += " %s_kappas.root" % cardToRead
    if blinded : cmd += blindStatement
    cmd += " --algo grid --points 1500" 
    cmd += " --redefineSignalPOIs kappa_t --setParameterRanges kappa_t=-3,3 --setParameters kappa_t=1.0,kappa_V=1.0,r_ttH=1,r_tH=1"
    cmd += " --freezeParameters kappa_V,kappa_tau,kappa_mu,kappa_b,kappa_c,kappa_g,kappa_gam -m 125 --fastScan" 
    cmd += " -n kt_scan_%s" % namePlot
    runCombineCmd(cmd, cardFolder)

    print ("done:  " + cardFolder + "/" + "higgsCombinekt_scan_" +namePlot + ".MultiDimFit.mH125.root")

if doWS :
    cmd = "text2workspace.py"
    cmd += " %s.txt" % cardToRead
    cmd += " -o %s_3poi.root" % cardToRead
    cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
    cmd += " %s" % floating_ttV
    cmd += " %s" % float_sig_rates
    runCombineCmd(cmd, cardFolder)

doFor = [blindStatement]
if not blinded : doFor += [" "]

signals = ["ttH"]
if options.tH : signals == ["tH"]

if doRateAndSignificance :
    for signal in signals :
      for ss, statements in enumerate(doFor) :
        if ss == 1 : label = "data"
        if ss == 0 : label = "asimov"
        if signal == "ttH" : redefine = " --freezeParameters r_tH --redefineSignalPOI r_ttH "
        if signal == "tH"  : redefine = " --freezeParameters r_ttH --redefineSignalPOI r_tH " 

        cmd = "combine -M Significance --signif"
        cmd += " %s_3poi.root" % cardToRead
        #cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
        cmd += " %s" % blindStatement
        cmd += " %s" % redefine
        runCombineCmd(cmd, cardFolder, saveout="%s_significance_%s_%s.log" % (cardToRead, label, signal))

        cmd = "combine -M MultiDimFit"
        cmd += " %s_3poi.root" % cardToRead
        cmd += " --algo singles --cl=0.68"
        cmd += " %s" % blindStatement
        cmd += " %s" % redefine
        cmd += " -P r_%s" % signal
        cmd += " --floatOtherPOI=1 --saveFitResult -n step1  --saveWorkspace"
        runCombineCmd(cmd, cardFolder, saveout="%s_rate_%s_%s.log" % (cardToRead, label, signal))
        ## --saveWorkspace to extract the stats only part of the errors and the limit woth mu=1 injected
        ### Some example of this concept here: https://cms-hcomb.gitbooks.io/combine/content/part3/commonstatsmethods.html#useful-options-for-likelihood-scans
        # --freezeParameters (instead of -S 0) also work on the above

        if ss == 1 :
            ## Rate: stats only
            cmd = "combine -M MultiDimFit "
            cmd += " -d  higgsCombinestep1.MultiDimFit.mH120.root" 
            cmd += " -w w --snapshotName \"MultiDimFit\" "
            cmd += " -n teststep2 %s_3poi" % cardToRead
            cmd += " -P r_%s" % signal
            cmd += " -S 0 --algo singles" 
            runCombineCmd(cmd, cardFolder, saveout="%s_rate_%s_stats_only.log" % (cardToRead, signal))

if doLimits :
    ## do in two steps: fit to data + limits mu=1 injected
    for signal in signals :
        cmd = "combine -M AsymptoticLimits "
        cmd += " %s_3poi.root" % cardToRead 
        cmd += " %s" % blindStatement
        cmd += " %s" % setpar
        cmd += " --redefineSignalPOI r_%s -n from0_r_%s " % (signal, signal)
        runCombineCmd(cmd, cardFolder, saveout="%s_limit_%s_from0.log" % (cardToRead, signal))

        if not blinded :
            # calculate limits mu=1 injected only for final runs
            cmd = "combine -M AsymptoticLimits "
            cmd += " -t -1 higgsCombinestep1.MultiDimFit.mH120.root"  
            cmd += " %s" % setpar
            cmd += " --redefineSignalPOI r_%s  -n from1_r_%s" % (signal, signal)
            cmd += " --snapshotName \"MultiDimFit\"  --toysFrequentist --bypassFrequentistFit"  
            runCombineCmd(cmd, cardFolder, saveout="%s_limit_%s_from1.log" % (cardToRead, signal))

bkgs = []
if options.ttW : bkgs += ["ttW"]
if options.ttZ : bkgs += ["ttZ"]

if do2Dlikelihoods :
  for ss, statements in enumerate(doFor) :
    if ss == 1 : label = "data"
    if ss == 0 : label = "asimov"
    ## ttH x (ttZ , ttW)
    for bkg in bkgs :
        cmd = "combine -M MultiDimFit "
        cmd += " %s_3poi.root" % cardToRead 
        cmd += " %s" % blindStatement
        cmd += " -n For2D_ttH_%s" % bkg
        cmd += " --algo grid --points 80000 --fastScan"
        cmd += " --redefineSignalPOIs r_ttH,r_%s" % bkg
        cmd += " --setParameterRanges r_ttH=-1,3:r_%s=-1,3" % bkg
        runCombineCmd(cmd, cardFolder)
        runCombineCmd("mv %s/higgsCombineFor2D_ttH_%s.MultiDimFit.mH120.root %s/%s_2Dlik_ttH_%s_%s.root"  % (cardFolder, bkg, cardFolder, cardToRead, bkg, label))
        runCombineCmd("python test/plot2DLLScan.py %s/%s_2Dlik_ttH_%s_%s.root  \"r_%s\" \"%s\" \"%s\" 0 0 "  % (cardFolder, cardToRead, bkg, label, bkg, cardToRead, cardFolder), '.')

if do2Dlikelihoods_with_tH :
  ## add break if not options.tH
  for ss, statements in enumerate(doFor) :
    if ss == 1 : label = "data"
    if ss == 0 : label = "asimov"
    ## tH x ttH
    cmd = "combine -M MultiDimFit "
    cmd += " %s_3poi.root" % cardToRead 
    cmd += " %s" % blindStatement
    cmd += " -n For2D_ttH_tH" 
    cmd += " --algo grid --points 150000 --fastScan"
    cmd += " --redefineSignalPOIs r_ttH,r_tH"
    cmd += " --setParameterRanges r_tH=-1,3:r_tH=-40,40" 
    runCombineCmd(cmd, cardFolder)
    runCombineCmd("mv %s/higgsCombineFor2D_ttH_tH.MultiDimFit.mH120.root %s/%s_2Dlik_ttH_tH_%s.root"  % (cardFolder, cardFolder, cardToRead, label))
    runCombineCmd("python test/plot2DLLScan.py %s/%s_2Dlik_ttH_tH_%s.root  \"r_tH\" \"%s\" \"%s\" 0 0 "  % (cardFolder, cardToRead, label, cardToRead, cardFolder), '.')

    # To make contours -- it does not work yet
    #    #run_cmd("cd "+os.getcwd()+"/"+mom_result+" ; combine -M MultiDimFit -t -1 --algo contour2d --points=20 --cl=0.95  --X-rtd ADDNLL_RECURSIVE=0 -m 125 --verbose 0 -n contour_95_ttZ_%s %s.root --redefineSignalPOIs r_ttH,r_ttZ --freezeParameters r_tH -m 125 --setParameters r_ttH=1:r_ttZ=1 --cminDefaultMinimizerTolerance 0.01  --cminDefaultMinimizerStrategy 0 --cminPreScan --X-rtd MINIMIZER_analytic --setParameterRanges r_ttZ=-1.0,3.0:r_ttH=-1.0,3.0 ; cd -"  % (namePlot, WS_output))
    #    #run_cmd("cd "+os.getcwd()+"/"+mom_result+" ; combine -M MultiDimFit -t -1 --algo contour2d --points=20 --cl=0.68  --X-rtd ADDNLL_RECURSIVE=0 -m 125 --verbose 0 -n contour_68_ttZ_%s %s.root --redefineSignalPOIs r_ttH,r_ttZ  --cminDefaultMinimizerTolerance 0.01  --cminDefaultMinimizerStrategy 0 --cminPreScan --X-rtd MINIMIZER_analytic --setParameterRanges r_ttZ=-1.0,3.0:r_ttH=-1.0,3.0 --freezeParameters r_tH -m 125 --setParameters r_ttH=1:r_ttZ=1; cd -"  % (namePlot, WS_output))
    #    #run_cmd("cd "+os.getcwd()+"/"+mom_result+" ; python %s/plot_rate_2D.py --input %s_2Dlik_asimov.root --output %s/%s_asimov.pdf --second 'r_ttZ'; cd -"  % (os.getcwd(), WS_output ,os.getcwd()+"/"+mom_result, WS_output))

if doHessImpacts :
    # hessian impacts
    folderHessian = "%s/HesseImpacts_%s"  % (cardFolder, cardToRead)
    runCombineCmd("mkdir %s"  % (folderHessian))
    cmd = "combineTool.py -M Impacts"
    cmd += " -d %s_3poi.root" % cardToRead 
    cmd += " %s" % blindStatement
    cmd += " --rMin -2 --rMax 5"
    cmd += " -m 125 --doFits --approx hesse"
    runCombineCmd(cmd, folderHessian)
    cmd = "combineTool.py -M Impacts"
    cmd += " -d %s_3poi.root" % cardToRead 
    cmd += " %s" % blindStatement
    cmd += "  -m 125 -o impacts.json --approx hesse --rMin -2 --rMax 5"
    runCombineCmd(cmd, folderHessian)
    runCombineCmd("plotImpacts.py -i impacts.json -o  impacts", folderHessian)

if doCategoriesWS :
    folderCat = "%s/categories_%s"  % (cardFolder, cardToRead)
    runCombineCmd("mkdir %s"  % (folderCat))
    ## to make separate mu / limits
    ## this needs to be adapted to the naming convention of the bins on the input card, and to how we want to do fit for legacy 
    sigRates = ["ttH_2lss_0tau", "ttH_3l_0tau", "ttH_4l", "ttH_2lss_1tau", "ttH_3l_1tau", "ttH_2l_2tau", "ttH_1l_2tau" ]
    floating_by_cat = ""
    for sigRate in sigRates :
        floating_by_cat += " --PO 'map=.*%s*/ttH.*:r_%s[1,-5,10]" (sigRate, sigRate)
    cmd = "text2workspace.py "
    cmd += " ../%s.txt" % cardToRead 
    cmd += " -o %s_Catpoi_final.root" % cardToRead
    cmd += " -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose"
    cmd += " %s" % floating_ttV
    cmd += " %s" % float_sig_rates
    cmd += " %s" % floating_by_cat
    runCombineCmd(cmd, folderCat)

if doCategoriesMuAndLimits :
    parameters = ""
    if options.ttW : parameters += "r_ttW=1,"
    if options.ttZ : parameters += "r_tH=1"
    for rate in sigRates : parameters = parameters + ",r_ttH_"+rate+"=1"
    print ("Will fit the parameters "+parameters)
    for rate in sigRates + bkg : 
        cmd = "combineTool.py -M MultiDimFit"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --algo none --cl=0.68" 
        cmd += " -P r_%s" % rate
        cmd += " --floatOtherPOI=1 -S 0 --cminDefaultMinimizerType Minuit --keepFailures" 
        runCombineCmd(cmd, folderCat, saveout="%s/%s_rate_%s.log" % (folderCat, cardToRead, rate))
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
    if sendToCondor :
        cmd = "combineTool.py -M AsymptoticLimits"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --redefineSignalPOI r_%s" % rate
        cmd += " -n from0_%s %s from0_%s" % (rate , ToCondor, rate) 
        runCombineCmd(cmd, folderCat, saveout="%s/%s_limit_from0_%s.log" % (folderCat, WS_output_byCat, rate))
    else :
        cmd = "combineTool.py -M AsymptoticLimits"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --redefineSignalPOI r_%s" % rate
        cmd += " -n from0_%s " % (rate) 
        runCombineCmd(cmd, folderCat, saveout="%s/%s_limit_from0_%s.log" % (folderCat, WS_output_byCat, rate))
        cmd = "combineTool.py -M AsymptoticLimits"
        cmd += " -o %s_Catpoi_final.root" % cardToRead
        cmd += " %s" % blindStatement
        cmd += " --setParameters %s" % parameters
        cmd += " --redefineSignalPOI r_%s" % rate
        cmd += " -n from0_%s " % (rate) 
        runCombineCmd(cmd, folderCat, saveout="%s/%s_limit_from0_%s.log" % (folderCat, WS_output_byCat, rate))

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
        run_cmd("cd "+enterHere+' ; combineTool.py -M GoodnessOfFit --algo=saturated  %s  -t 1000 -s 12345  %s.root --saveToys --toysFreq ; cd -' % (redefineToTTH, WS_output))
        run_cmd("cd "+enterHere+' ; combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH120.root higgsCombineTest.GoodnessOfFit.mH120.12345.root -o gof.json ; cd -')
        run_cmd("cd "+enterHere+" ;  $CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotGof.py --statistic saturated --mass 120.0 gof.json -o GoF_saturated_"+WS_output+'_btagCorr'+str(btag_correlated)+'_blinded'+str(blinded)+" ; cd -")

savePostfitCombine  = "PostFitCombine_"+cardToRead 
savePostfitHavester = "PostFitHavester_"+cardToRead 
if preparePostFitCombine :
    ### for category by category - 2017 only
    run_cmd("mkdir "+savePostfitCombine)
    enterHere = os.getcwd()+"/"+mom_result+"/"+savePostfitCombine
    run_cmd("cd "+enterHere+' ; combineTool.py -M FitDiagnostics %s/../%s.root %s --saveNormalization --saveShapes --saveWIthUncertainties %s ; cd -' % (enterHere, WS_output, redefineToTTH, sendToCondor))
    print ("the output with the shapes is going to be fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine")
    ##### PostFitShapesFromWorkspace_mergeMultilep --workspace /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/../comb_2017v2_withCR_sanity_3poi.root -o /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/comb_2017v2_withCR_sanity_3poi_shapes_combo.root --sampling --print
    ## -f fitDiagnostics.Test.root:fit_s --postfit
    ## -d /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/^CostFitHavester_comb_2017v2_withCR_sanity/../comb_2017v2_withCR_sanity.txt -o comb_2017v2_withCR_sanity_3poi_shapes.root

    # PostFitShapesFromWorkspace_mergeMultilep --workspace /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/../comb_2017v2_withCR_sanity_3poi.root -o /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/comb_2017v2_withCR_sanity_3poi_shapes_combo.root --sampling --print -d  /afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/../comb_2017v2_withCR_sanity.txt -f f/afs/cern.ch/work/a/acarvalh/CMSSW_8_1_0/src/CombineHarvester/ttH_htt/test/gpetrucc_2017/PostFitHavester_comb_2017v2_withCR_sanity/fitDiagnostics.Test.root:fit_s --postfit

if preparePostFitHavester  :
    print ("[WARNING:] combine does not deal well with autoMCstats option for bin by bin stat uncertainty")
    run_cmd("mkdir "+os.getcwd()+"/"+mom_result+"/"+savePostfitHavester)
    enterHere = os.getcwd()+"/"+mom_result+"/"+savePostfitHavester
    run_cmd("cd "+enterHere+' ; combineTool.py -M FitDiagnostics %s/../%s.root %s ; cd -' % (enterHere, WS_output, redefineToTTH))
    print ("the diagnosis that input Havester is going to be on fitDiagnostics.Test.root or fitDiagnostics.root depending on your version of combine -- check if you have a crash!")
    doPostfit = " -f fitDiagnostics.root:fit_s --postfit "
    run_cmd("cd "+enterHere+' ; PostFitShapesFromWorkspace --workspace %s/../%s.root -d %s/../%s.txt -o %s_shapes.root -m 125 --sampling --print %s ; cd -' % (enterHere, WS_output, enterHere, card, WS_output, doPostfit)) # --skip-prefit
    print ("the output with the shapes is "+enterHere+WS_output+"_shapes.root")

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