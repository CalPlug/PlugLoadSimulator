import numpy as np
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
import os

import datetime

num_graphs = 1

def make_integral_array(power_array: list, integration_period: int):
    to_return = [0] #initialize the array with a 0
    for i in range(len(power_array)): #previously, len(power_array)-1, this would never evaluate length 1 arrays
        to_return.append(energy_used(power_array[i:i+2], integration_period) + to_return[-1]) #after first array entry, add new value to appended value
    return to_return

def energy_used(power_array, int_period: int):
    ''' Integrate the array given period length per hour'''
    #return (sum(power_array[1:])/3600*int_period + sum(power_array[:len(power_array)-1])/3600*int_period)/2 # or     #return ((sum(power_array[1:]))/(int_period * len(power_array))) #previously, len(power_array)-1, this would never evaluate length 1 arrays, prior '''trapezoidal riemman sum estimate of the amount of power used'''
    #return(np.trapz(power_array,dx=(int_period/3600)))#print (np.trapz(power_array,dx=(int_period/3600))) #debug print out of step integration value, the problem here is this needs a range, but we are using unitary periods
    return(sum(power_array)/len(power_array)*(int_period/3600)) #calculate with unitary period addition versus integration

    

    

def make_graph(data: list, int_period, x_label, y_label, title, fig, sub)-> None:
    ''' graphs the data from the list using each point as a y coordinate in the line graph
    x is a range from 0 to len(list) with the integration period int_period
    '''

    if y_label == 'power':
        y_label = 'Power (W)'
    elif y_label == 'thdI':
        y_label = 'THDi(%)'
    elif y_label == 'power_factor':
        y_label = 'Power Factor(PF)'
    elif y_label.__contains__('_'):
        y_label = ' '.join([i.capitalize() for i in y_label.split('_')])

    step = int_period/3600
    data = np.array(data)

    time = np.arange(0.0, step*len(data), step)

    if(len(data) != len(time)):
        # takes care of floating point division error incurred in line 11
        # print(len(data), len(time))
        data = data[:min(len(time), len(data))]
        time = time[:min(len(time), len(data))]

    plt.figure(fig,figsize=(15,15))

    plt.subplot(sub[0], sub[1], sub[2])
    plt.plot(time, data, 'k',label=y_label)
    plt.legend(loc = 'upper right',prop={'size': 6})

    plt.ylim(bottom=(min(data) - abs(min(data))))
    plt.ylim(top=(max(data) + abs(max(data))))

    plt.title(title, fontsize=7)
    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)
    plt.xlabel(x_label, fontsize=6)
    plt.ylabel(y_label, fontsize=6)
    plt.gca().yaxis.grid(True,linestyle=':',linewidth=0.2,color='k')

def make_power_graph(input_data: list, int_period, x_label, y_label, title, legend_label, fig, sub) -> None:
    global num_graphs
    ''' graphs the data from the list using each point as a y coordinate in the line graph
    x is a range from 0 to len(list) with the integration period int_period
    '''

    if y_label == 'power':
        y_label = 'Power (W)'
    elif y_label == 'thdI':
        y_label = 'THDi(%)'
    elif y_label == 'power_factor':
        y_label = 'Power Factor(PF)'
    elif y_label.__contains__('_'):
        y_label = ' '.join([i.capitalize() for i in y_label.split('_')])

    step = int_period / 3600
    data = np.array(input_data)

    time = np.arange(0.0, step * len(data), step)


    if (len(data) != len(time)):
        # takes care of floating point division error incurred in line 11
        # print(len(data), len(time))
        data = data[:min(len(time), len(data))]
        time = time[:min(len(time), len(data))]

    plt.figure(fig, figsize=(15, 15))
    # plt.ylim([0, max(data)+30])
    plt.subplot(sub[0],sub[1],sub[2])

    # plot data
    # mean
    if legend_label == 'Energy':
        plt.plot(time, data, 'k', label='Period Energy Use (WHr)')
    else:
        plt.plot(time, data,'k',label='Average Power (W)')
        # power spread
        mean_array = data
        median = data
        median_array = np.zeros_like(data) + median
        # median
        plt.plot(time, median_array,'--',label='Median Power Usage (W)',linewidth=1)
        # +1 std
        plt.plot(time, mean_array + np.std(data),'--',label='Average Power (W) + 1Std.Dev.',linewidth=1)
        # -1 std
        plt.plot(time, mean_array - np.std(data),'--',label='Average Power (W)  -  1Std.Dev.',linewidth=1)

        plt.ylim(bottom=(min(mean_array - np.std(data))-abs(min(mean_array - np.std(data)))))
        plt.ylim(top=(max(mean_array + np.std(data)) + abs(max(mean_array + np.std(data)))))

    #plot formatting
    plt.legend(loc = 'upper right',prop={'size': 6})
    plt.title(title, fontsize=7)
    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)
    plt.xlabel(x_label, fontsize=6)
    plt.ylabel(y_label, fontsize=6)
    plt.gca().yaxis.grid(True,linestyle=':',linewidth=0.2,color='k')

    #Save graph function below
    #Tested formats: eps, pdf, pgf, png, ps, raw, rgba, svg, svgz
    #Easiest formats are pdf and png, svg and eps saves lossless quality but need to convert
    #IF WE HAVE THE COMPUTING POWER, SET DPI TO 1000/1200 for highest quality: WARNING, takes multiple minutes to run
    # plt.savefig("./graphs/graph" + str(num_graphs) + ".png", dpi = 300)
    
    num_graphs += 1

def show_graph():
    plt.show()

def save_graph(output_folder, profile_id, file_name, isbatch):
    num = 1
    figs = [plt.figure(n) for n in plt.get_fignums()]

    if isbatch:
        file_path = output_folder + '/' + profile_id + "graph" + str(num) + ".png"
    else:
        file_path = output_folder + "/graph" + str(num) + ".png"
    
    for fig in figs:
        fig.savefig(file_path, dpi=300)
        num += 1
    
    # print("**************************", output_folder,"**************************")

def reset():
    plt.clf()
