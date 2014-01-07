# -*- coding: utf8 -*-
#!/usr/bin/env python


'''
Script for a go/nogo task to be used with hypnotically induced hand analgesia in or out of fMRI scanner

'''

import time
import sys
from psychopy import visual,event,core, data, logging, gui
import csv
import random
import os
from psychopy.hardware.emulator import launchScan
from psychopy import parallel

core.wait(0.5)


def getResponse(validResponses,duration=0):
	"""Returns keypress and RT. Specify a duration (in secs) if you want response collection to last 
        that long. Unlike event.waitkeys(maxWait=..), this function will not exit until duration. 
        Use waitKeys with a maxWait parameter if you want to have a response deadline, but exit as soon 
        as a response is received."""
	event.clearEvents() #important - prevents buffer overruns
	responded = False
	timeElapsed = False
	rt = '*'
	responseTimer = core.Clock()
 
	if duration==0:
		responded = event.waitKeys(keyList=validResponses)
		rt = responseTimer.getTime()
		return [responded[0],rt] #only get the first response. no timer for waitKeys, so do it manually w/ a clock
	else:
		while responseTimer.getTime() < duration:
			if not responded:
				responded = event.getKeys(keyList=validResponses,timeStamped=responseTimer)
		if not responded:
			return ['*','*']
		else:
			return responded[0]  #only get the first resp


def empathyp(expe):
	#---------------------------------------
	# Set Variables
	#---------------------------------------

	TRIALS_FILE = 'trialList_short.csv'
	PAUSE = 10 # Time to pause for hypnosis reinforcement
	STIM_SIZE = 0.1,0.15 
	BACKGROUND_COLOR = [-0.5, -0.5, -0.5]
	
	start_expe = 0
	#---------------------------------------
	# Set Keys for responses and expe flow
	#---------------------------------------

	if expe == 'behav':
		is_fmri = 0
	
		keyInd = ['space'] # for induction picture
		keyGo = ['up', 'none'] # response to go stimuli
		keyPass = ['space'] # for passing screens
	
	elif expe == 'fmri':
		is_fmri = 1

		keyInd = ['space'] # for induction picture
		keyGo = ['3', 'none'] # response to go stimuli
		keyPass = ['space'] # for passing screens
	else:
		print('Experience type can be behav or fmri only ')

	
		
	#---------------------------------------
	# Create timers
	#---------------------------------------
	globalClock = core.Clock()  # to track the time since experiment started
	respTime = core.Clock()
	trialClock = core.Clock()
	#countDown= core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

	#---------------------------------------
	# Store info about the experiment session
	#---------------------------------------

	expName = 'Empathyp'  
	expInfo = {'participant':'', 'session':}
	dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
	if dlg.OK == False: core.quit()  # user pressed cancel  
	expInfo['date'] = data.getDateStr()  # add a simple timestamp  
	expInfo['expName'] = expName

	# Experiment handler
	thisExp = data.ExperimentHandler(name=expName, version='',
	    extraInfo=expInfo, runtimeInfo=None,
	    originPath=None,
	    savePickle=False, saveWideText=False) #prevent the experiment handler to write expe data upon termination (and overwriting our files)
	
	#---------------------------------------
	# Load trial files 
	#---------------------------------------

	# read from csv file
	trialList = data.importConditions(TRIALS_FILE, returnFieldNames=False)
	trials = data.TrialHandler(trialList, nReps=1, method='sequential', extraInfo=expInfo)
	trials.data.addDataType('respKey')
	trials.data.addDataType('respTime')
	trials.data.addDataType('stimOnset')

	#---------------------------------------
	# Setup files for logfile  saving
	#---------------------------------------

	if not os.path.isdir('Logdata'):
	    os.makedirs('Logdata')  # if this fails (e.g. permissions) we will get error
	filename = 'Logdata' + os.path.sep + '%s_%s' %(expInfo['participant'], expInfo['date'])
	logging.setDefaultClock(globalClock)
	logFileExp = logging.LogFile(filename +'.log', level=logging.EXP)
	logging.console.setLevel(logging.INFO)  # this outputs to the screen, not a file


	#---------------------------------------
	# Setup the Window
	#---------------------------------------
	win = visual.Window([1280,1024],color = BACKGROUND_COLOR,monitor ='testMonitor',  units='height',
	fullscr = False, colorSpace = 'rgb')

	#---------------------------------------
	# Setup Paths to read files
	#---------------------------------------

	im_dir = 'Stim'

	#---------------------------------------
	# Hypnosis  Induction Routine
	#---------------------------------------
	def induction():
		fixation.draw()
		fixation_cross.draw()
		win.flip()
	
	#---------------------------------------
	# Setup instructions
	#--------------------------------------- 
	#instrPracticeClock = core.Clock()
	instruct1 = visual.TextStim(win=win, ori=0, name='instruct1',
	    text="Consignes : \n\n Pressez le bouton uniquement lorsque l'image est celle d'une main droite. \n\n Ne pressez pas le bouton lorsque l'image est une image de main gauche. \n\n\n Appuyer sur espace pour continuer.", font='Arial',
	    pos=[0, 0], height=0.04, wrapWidth=None,
	    color='white', colorSpace='rgb', opacity=1.0,
	    depth=0.0)

	#---------------------------------------
	# Setup end message
	#--------------------------------------- 
	#instrPracticeClock = core.Clock()
	theEnd = visual.TextStim(win=win, ori=0, name='theEnd',
	    text="Fin", font='Arial',
	    pos=[0, 0], height=0.04, wrapWidth=None,
	    color='black', colorSpace='rgb', opacity=1,
	    depth=0.0)



	#---------------------------------------
	# Setup Fixation cross and circle
	#---------------------------------------

	
	fixation_cross=visual.TextStim(win=win, ori=0, name='fixation_cross',
		   text='+',
		   font='Arial',
		   pos=[0, 0], height=0.06,		
		   color='black')
	fixation_cross.setLineWidth = 0.4

	StimDuration =.5



	if is_fmri == 1 :
		#---------------------------------------
		# Set up parallel port for eye tracker
		#---------------------------------------

		#parallel.PParallelInpOut32(address = 0x0378) #may need to be changed
		#parallel.setData(0)


		#---------------------------------------
		# Settings for launch scan 
		#---------------------------------------

		MR_settings={
			'TR': 2.000, # duration (sec) per volume
			'volumes':5, # number of whole-brain 3D volumes/frames
			'sync': '5', # character used as sync timing event; assumed to come at start of a volume
			'skip': 5, # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
			'sound': False # True: in test mode only
			}

		#infoDlg = gui.DlgFromDict(MR_settings, title='FMRI parameters', order=['TR', 'volumes'])
		#if not infoDlg.OK: core.quit() 

		globalClock = core.Clock()

		#summary of run timing for each key press:
		output = 'vol onset key\n'

		for i in range (-1*MR_settings['skip'], 0):
			output += '%d prescan skip (no sync)\n' % i


		key_code = MR_settings['sync']
		counter = visual.TextStim(win, height=.05, pos=(0,0), color=win.rgb+0.5)
		output += "0	0.000 %s start of scanning run, vol 0\n" % key_code 
		pause_during_delay = (MR_settings['TR']>.4)
		sync_now = False


		# can simulate user responses, here 3 key presses in order 'a', 'b', 'c' (they get sorted by time):
		simResponses = [(0.123, 'a'), (4.789, 'c'), (2.456, 'b')]


		#---------------------------------------
		# launch scanner
		# operator selects Scan or Test 
		#---------------------------------------
		vol = launchScan(win, MR_settings, globalClock=globalClock, simResponses=simResponses)

		infer_missed_sync = False # best no to use it but might be useful
		max_slippage = 0.02 # how long to afford before treating a slow sync as missed

		duration = MR_settings['volumes']*MR_settings['TR']
		# globalClock has been reset to 0 by launchScan()

		while globalClock.getTime() < duration:
			allKeys = event.getKeys()
			for key in allKeys:
				if key != MR_settings['sync']:
					output += "%3d %7.3f %s\n" % (vol-1, globalClock.getTime(), str(key))
			if 'escape' in allKeys:
				output += 'user cancel,'
				break
			#detect sync or infer it shoul have happened:
			if MR_settings['sync'] in allKeys:
				sync_now = key_code #flag
				onset = globalClock.getTime()
			if infer_missed_sync:
				expected_onset = vol*MR_setting['TR']
				now = globalClock.getTime()
				if now > expected_onset + max_slippage:
					 sync_now = '(inferred onset)' # flag
					 onset = expected_onset
			if sync_now:
				start_expe = 1
	else:	
		start_expe = 1
		
	if start_expe == 1:
	 
		#--------------------------------------
		# Show Instructions
		#--------------------------------------
		instruct1.draw(win)
		win.flip()
		event.waitKeys(keyList= keyPass)
		
	
		trialStart = 0
		#--------------------------------------
		# Do Hypnosis Induction	
		#--------------------------------------
		induction()
		event.waitKeys(keyList = keyInd)
		
		#--------------------------------------
		# START EXPERIMENT
		#--------------------------------------
		fixation_cross.draw()
		win.flip()
	
		win.setRecordFrameIntervals(True) # frame time tracking
		globalClock.reset()		

		trialStart = 1
		if trialStart == 1:
	
			t = 0
			frameN=-1
			nDone=0
			
		#--------------------------------------
		# Show Instruction		
		#--------------------------------------
		
			fixation_cross.setAutoDraw(True)
			win.flip()
			core.wait(2)

			
		#--------------------------------------
		# Run Trials
		#--------------------------------------
			for thisTrial in trials:

			# save data for the trial loop using psychopy function
				trials.saveAsWideText(filename + '.csv', delim=';', appendFile = False)
	
	
				thisRespKeys = []

		
				#--------------------------------------
				# Load stimuli image and set trials
				# variables
				#--------------------------------------
				if thisTrial['Stim'] != 'pause':	
					stim = visual.ImageStim(win, image = os.path.join(im_dir, thisTrial['Stim']), size=(STIM_SIZE ), opacity = 1.0)
					stim.setPos(thisTrial['Position'])
				thisITI = thisTrial['ITI']
				stimOnset = trialClock.getTime()
				
				if thisTrial['Position'] == [0, 0]: # remove fixation cross if stim is centered
					fixation_cross.setAutoDraw(False)
				
				#--------------------------------------
				# Display trials		
				#--------------------------------------
				if thisTrial['Stim'] != 'probe.png' and thisTrial['Stim'] != 'pause': # case trial is stimuli 
					#fade(stim)
					while trialClock.getTime() < stimOnset + StimDuration :
						fixation_cross.draw()
						fixation.draw()
						stim.draw()
						win.flip()
						
					theseKeys= getResponse(keyList= keyGo, duration = stimDuration ) # evaluate response
					if len(theseKeys)>0: # at least one key was pressed
						thisRespKeys = theseKeys[-1] # get just the last key pressed
						thisResponseTime = trialClock.getTime() 
				
				elif thisTrial['Stim'] == 'probe.png': # case trial is thought probe
					stim.setSize([0.1,0.1])
					fixation.draw()
					stim.draw()
					win.flip()	
				#	core.wait(1,hogCPUperiod=1)
					theseKeys = event.waitKeys(keyList= keyProbe)
					if len(theseKeys)>0: # at least one key was pressed
						thisRespKeys = theseKeys[-1] # get just the last key pressed
						thisResponseTime = trialClock.getTime() 

				elif thisTrial['Stim'] == 'pause':	# case pause for hypnosis reinforcement
					fixation.draw()
					win.flip()
					core.wait(PAUSE)
					theseKeys= []
		
				fixation.draw()
				fixation_cross.setAutoDraw(True)
				win.flip()
				core.wait(thisITI) 
				nDone +=1
					
									
		#		if(thisRespKeys == thisTrial['corrAns']) or (thisRespKeys == [] and thisTrial['corrAns'] =='n') :
		#			respCorr = 1 # lookup response for go and no go trials
		#		else: respCorr = 0
				
					
				#--------------------------------------
				# store trial data
				#--------------------------------------
				trials.addData('respKey',thisRespKeys)
	#			trials.addData('respCorr', respCorr)
				trials.addData('stimOnset', stimOnset)
				if theseKeys != []:
					trials.addData('respTime', thisResponseTime)
				thisExp.nextEntry() 
		# get names of stimulus parameters
				if trials.trialList in ([], [None], None): params = []
				else: params = trials.trialList[0].keys()
		
				if event.getKeys(['q',' escape']):			
					win.close()
					core.quit()
	
		#--------------------------------------
		# End Experiment	
		#--------------------------------------
			core.wait(1)
			fixation_cross.setAutoDraw(False)
			win.flip()
			
			fixation.draw()	
			theEnd.draw(win)
			win.flip()
			core.wait(3)
	
		#--------------------------------------
		# Revert Hypnosis Induction	
		#--------------------------------------
			induction()
			event.waitKeys(keyList = keyInd)	


	
			if is_fmri == 1:
				sync_now = False
				
				output+= "end of scan (vol 0..%d= %d of %s). duration = %7.3f" %(vol-1, vol, MR_settings['volumes'], globalClock.getTime())
				logging.info(output)




		
	core.wait(1)
	win.close()
	core.quit()

tubex('behav')				