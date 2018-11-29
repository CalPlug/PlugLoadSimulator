PLUG LOAD SIMULATOR for SIM HOME

This is a program that simulates how different sets of devices operating in different states consume energy.
For example, in a living room, there may be a TV, but a TV can be in an off, on, or standby state. Each state
consumes different amounts of energy. With multiple devices, each of which have four to five states at any given
time, the energy usage can be hard to analyze and calculate. This command-line program helps solve this problem.
  
INSTALLATION DETAILS
(1) Download the package manager/installer Conda from http://conda.pydata.org/miniconda.html 
		(a) Choose the Python 3.5 installer
		(b) Download and run the installer, follow all the instructions in the installer

(2) In the command line, issue the following command
		(a) conda install matplotlib (it will automatically install all the dependencies)- for reference: http://conda.pydata.org/docs/using/pkgs.html

(2) Download Java and then download Eclipse (if this is not on your computer already)
	@ - https://eclipse.org/downloads/
	  - https://java.com/en/download/
	  
(3) Download PyDev for Eclipse --http://www.pydev.org/manual_101_install.html for reference

(4) Open Eclipse with your desired workspace directory

(5) Click Window->Preferences->Pydev->Interpreters->Python Interpreters
  	(a) Click New...
  	(b) In the "Interpreter Executable" field copy paste the directory of the Python Interpreter in MiniConda3
  		ie: C:\Users\[user_name]\Miniconda3\python.exe
  	(c) A new screen will pop up check mark all the radio boxes and click OK
  	
(6) Create a new Project and put in all the files assuming you have them all in a zip
(7) Alternatively fork on Github @ https://github.com/ksegarra/CalPlug-Power-Usage-Sim


  	
INSTRUCTIONS FOR USE
1) 	Run the program
2) 	The menu contains commands for us to manipulate the simulation environment
	a: adds a device, first it selects the (a) kind of class of device to add,
										   (b) then the type of device, 
										   (c) then the brand,
										   (d) then finally the model
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

OUTPUTS:
1)	First output is the energy used in W*hrs (may be changeable to kWhrs)
2)	The second output is two graphs:
		(a) the first one is the graph of Power vs. Time 
		(b) the second graph is Energy Used vs. Time
3) 	Also in the outputs folder is the a csv that contains all the information from the graph

NOTES ON IMPLEMENTATION:
1)	Data about documented devices is stored in an xml file, which is organized hierarchically like so:
							(a)	device-class
							   (b) device-type 
								  (c) device-brand
								   	(d) device-model
								   	
2)	Simulations are saved onto csv files, in which the on/off value of a state is represented by 1 and 0
	respectively. 
	
  
  