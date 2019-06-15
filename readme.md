# PLUG LOAD SIMULATOR FOR LINKED DEVICES (PLSim) ![build passing](https://img.shields.io/circleci/project/github/badges/shields/master.svg)

## California Plug Load Research Center (CalPlug)

##### Code development by Klint Segarra, Jerry Lee, Siddhant Kasat, Liangze Yu, Carol Varkey, Madhumitha Govindaraju, Sean Kerr,Elvin Kang, Haosong Liu, Bonnie Tang, Huanjia Liang, Jerry Xu, Pooja Senthil Kumar
##### University of California, Irvine (UC Irvine) 
##### Project Leaders: Dr. Michael J. Klopfer & Prof. G.P. Li 
Copyright The Regents of the University of California, 2016 (v.1)  
Developed with support from Southern California Edison / Edison International  
Built with open source software and released into the public domain under GNU License for permissive use.  
	
# ***NOTICE:: Run through project "PLSim 1.2" as the set relative location within the entire project, accordingly if this is run in a new project each input and output file may need to have a modified file path corresponding to this new file structure ***

# Input Files
INPUT_XML = "xmls/PLSim2Format.xml"  #This is the input power usage "database" format

# Output Files
OUTPUT_PICKLE = 'run_params' #this is the pickled object file passed with the selected device list onto the calculation engine  
OUTPUT_CONFIG = 'csvs/run_perams.cfg' #This is the list of parameters for the scheduler run, similar in content to the PICKLE file.  
OUTPUT_CSV = 'csvs/test_group.csv'  #This is the generated schedule for device operation  
  
### Version 1.3 (6/14/19) Current Release
Changes in this version:  
	1) Reconfiguration of structure of codebase  
	2) New features in Calculation Engine  
	3) Easier usability for general users  
	4) Easier way to develop for developers 
	5) Graph output files from CalculationEngine saved into the graphs subdirectory, as .png 
	6) In addition to all the output being printed on console is now logged into the file called logfile.log in the same directory, 	after the termination of the CalculationEngine
	7)Improved resolution of CalculationEgine saved .jpg file
	
### Version 1.2 (11/27/18) Current Release  
This version of the program can be found in folder PLSim_1.1. This version is built using plugloadsimDefault from Version 1.1 and is developed in the same Eclipse IDE setup.
This version is compliant with the PLSim 2 XML format (future version relative to this version), allowing it to use the same XML files without having issues being an older version.
This version introduces object pickling, allowing for seperation of the simulator into two programs:  
	1) **Scheduler.py**  
		 - a) Run this program first   
		 - b) Takes information from database in xml and allows for user to configure devices to be simulated  
	2) **CalculationEngine.py**  
		 - a) After Scheduler.py has completed, run this program   
		 - b) Calculates and displays the simulation information  

### Version 1.1 (2/28/2018)  
This is a program that simulates how different sets of devices operating in different states consume energy.  It can be used to quickly tabulate energy use for multiple schedules of operation.  Additionally linked devices can be simulated.

In the current functional level, this program is run from Eclipse IDE.  One must install all dependancies to make it function as described below.

Application for residential entertainment centers and Advanced Power Strip (APS) control:
For example, in a living room, there may be a TV, but a TV can be in an off, on, or standby state. Each state
consumes different amounts of energy. With multiple devices, each of which have four to five states at any given
time, the energy usage can be hard to analyse and calculate. This command-line program helps solve this problem.


  
## INSTALLATION DETAILS
### Option 0 (For general users / non-developers)  
Double click on Installer.sh to run installation.  
### Option 1

### Option 2
1) Download the package manager/installer Conda from http://conda.pydata.org/miniconda.html   
	a) Choose the Python 3.5 installer  
    b) Download and run the installer, follow all the instructions in the installer  

2) In the command line, issue the following command  
		a) conda install matplotlib (it will automatically install all the dependencies)- for reference: http://conda.pydata.org/docs/using/pkgs.html  
		note: In Windows the "Anaconda Prompt" is available from the start menu, this points to the proper Python installation for Anaconda if multiple are present on your system and   environmental variables for other installs are in place))  RIN PIP and other package installers from this prompt to update components.  

3) Download Java and then download Eclipse (if this is not on your computer already)  
	@ - https://eclipse.org/downloads/  [Tested in Photon Eclipse Java version] (Use the default install option of Java developers if prompted)  
	  - https://java.com/en/download/  
	  
4) Download PyDev for Eclipse --http://www.pydev.org/manual_101_install.html for reference  (Please files into the 	  "eclipse/dropins" folder, per instructions)  

5) Open Eclipse with your desired workspace directory  

6) Click Window->Preferences->Pydev->Interpreters->Python Interpreters  
  	a) Click New...  
  	b) In the "Interpreter Executable" field copy paste the directory of the Python Interpreter in MiniConda3
        ie: C:\Users\[user_name]\Miniconda3\python.exe 
	    or C:\ProgramData\Miniconda3\python.exe  
  	c) A new screen will pop up check mark all the radio boxes and click OK, make sure to add requested environmental variables.  
  	
7) Open or Create a new Project (the PLSIMPROG directory is an eclipse workspace with three projects inside) and put in all the files assuming you have them all in a zip  
8) Alternatively fork on Github @ https://github.com/ksegarra/CalPlug-Power-Usage-Sim (original launch version) or https://github.com/CalPlug/PlugLoadSimulator-PLSim (current maintained version)

9) On Luanch verify that the workspace and run configurations are in place.  This can be a common point of concern in developing with Eclipse.  The workspace, start point and interpreter should be in place in the run configurations.  

  	
## INSTRUCTIONS FOR USE  
1) 	Run the program  
2) 	The menu contains commands for us to manipulate the simulation environment  
	a: adds a device, first it selects the  
                                           a) kind of class of device to add,  
										   b) then the type of device,   
										   c) then the brand,  
										   d) then finally the model  
	d: deletes a device  
	p: prints the current set of devices  

3) 	To run a simulation use the r command  
4)	In the simulation it will prompt for a integration period in seconds, this is a sample rate which the program  
  	uses in its calculations in general. For the most accurate results minimize the integration time and make it a  
  	multiple of 60 (minimizes float arithmetic errors). Smaller integration factors slow down the program.  
5)	The program will then prompt for a time interval. This is the length of time in minutes that a with certain   
	configuration of states in our simulation environment. Then, for each device, whether it is in use. If yes,  
	it will ask which state is the device in. If no it will assume the device is off and consuming no energy.  
6)	To end the simulation enter 0.  
  
## OUTPUTS:  
1)	First output is the energy used in W*hrs (may be changeable to kWhrs)  
2)	The second output is two graphs:  
		(a) the first one is the graph of Power vs. Time   
		(b) the second graph is Energy Used vs. Time  
3) 	Also in the outputs folder is the a csv that contains all the information from the graph  

## NOTES ON IMPLEMENTATION:  
1)	Data about documented devices is stored in an xml file, which is organized hierarchically like so:  
							(a)	device-class  
							   (b) device-type   
								  (c) device-brand  
								   	(d) device-model  
								   	
2)	Simulations are saved onto csv files, in which the on/off value of a state is represented by 1 and 0  
	respectively.   
