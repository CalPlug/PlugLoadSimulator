import numpy as np
import matplotlib.pyplot as plt

def make_graph(data: list, int_period, x_label, y_label, title, fig = 1, sub=111)-> None:
    ''' graphs the data from the list using each point as a y coordinate in the line graph
    x is a range from 0 to len(list) with the integration period int_period
    '''
    step = int_period/3600
    data = np.array(data)

    time = np.arange(0.0, step*len(data), step)

    if(len(data) != len(time)):
        # takes care of floating point division error incurred in line 11
        # print(len(data), len(time))
        data = data[:min(len(time), len(data))]
        time = time[:min(len(time), len(data))]

    plt.figure(fig,figsize=(15,15))
    #plt.ylim([0, max(data)+30])
    plt.subplot(sub)
    plt.plot(time, data, 'k')

    if fig == 1:
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
    else:
        plt.title(title, fontsize=7)
        plt.rc('xtick', labelsize=6)
        plt.rc('ytick', labelsize=6)
        plt.xlabel(x_label,fontsize=6)
        plt.ylabel(y_label,fontsize=6)


def make_power_graph(input_data: list, int_period, x_label, y_label, title, fig=1, sub=111) -> None:
    ''' graphs the data from the list using each point as a y coordinate in the line graph
    x is a range from 0 to len(list) with the integration period int_period
    '''
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
    plt.subplot(sub)

    # plot data
    plt.plot(time, data,'k',label='power')

    # power spread
    mean = np.mean(data)
    mean_array = np.zeros_like(data)+mean
    median = np.median(data)
    median_array = np.zeros_like(data) + median
    # mean
    plt.plot(time,mean_array,'--',label='mean')
    # median
    plt.plot(time, median_array,'--',label='median')
    # +2 std
    plt.plot(time, mean_array + 2*np.std(data),'--',label='+2std')
    # -2 std
    plt.plot(time, mean_array - 2*np.std(data),'--',label='-2std')
    plt.legend()

    if fig == 1:
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
    else:
        plt.title(title, fontsize=7)
        plt.rc('xtick', labelsize=6)
        plt.rc('ytick', labelsize=6)
        plt.xlabel(x_label, fontsize=6)
        plt.ylabel(y_label, fontsize=6)
    
def show_graph():
    plt.show()