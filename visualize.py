import trsfile
from trsfile.parametermap import TraceSetParameterMap
import trsfile.traceparameter as tp
import matplotlib.pyplot as plt
import sys

parameters = TraceSetParameterMap()
#print(parameters)

zoomS=0
zoomE=2200000
start = 0
number = 4
displayLabels = 4
displayData = True
dataStart=0
dataEnd=8
repeat = 1
together = False


with trsfile.open(sys.argv[1], 'r') as traces:
    print(traces.get_headers())
    # Show all headers
    for header, value in traces.get_headers().items():
        print(header, '=', value)
    print()

    if together:
        fig, ax = plt.subplots(repeat, sharex=True, sharey=True)
    else:
        fig = plt.figure()
    
    for r in range(repeat):
        #print(start+(r*number))
        #print(start+(r*number)+number-1)
        for i, trace in enumerate(traces[(start+(r*number)):(start+(r*number)+number)]):
            print ("aaaa ")
            print('Trace {0:d} contains {1:d} samples'.format((i+start), len(trace)))
            print(type(trace.samples[0]))
            print(trace.parameters['LEGACY_DATA'])
            if i<number:
                samples = trace.samples
                data = trace.parameters['LEGACY_DATA']
                if i < displayLabels: 
                    if displayData:
                        if not together: 
                            plt.plot(samples[zoomS:zoomE], label="Trace["+str(i+start+(r*number))+"]:"+str(data)[dataStart:dataEnd]+"...")
                        else:
                            #ax[i].set_title("Trace " + str(start+(r*number)+i))
                            ax[r].plot(samples[zoomS:zoomE], label="Trace["+str(i+start+(r*number))+"]:"+str(data)[dataStart:dataEnd]+"...")
                    else:
                        if not together: 
                            plt.plot(samples[zoomS:zoomE], label="Trace["+str(i+start+(r*number))+"]")
                        else:
                            #ax[i].set_title("Trace " + str(start+(r*number)+i))
                            ax[r].plot(samples[zoomS:zoomE], label="Trace["+str(i+start+(r*number))+"]")
                elif i == displayLabels:
                    if not together: 
                        plt.plot(samples[zoomS:zoomE], label="...")
                    else:
                        #ax[i].set_title("Trace" + str(start+(r*number)+i))
                        ax[r].plot(samples[zoomS:zoomE])
                else:
                    if not together: 
                        plt.plot(samples[zoomS:zoomE])
                    else:
                        #ax[i].set_title("Trace" + str(start+(r*number)+i))
                        ax[r].plot(samples[zoomS:zoomE])
            else: 
                break
        if not together:
            plt.xlabel("Time")
            plt.ylabel("Values")
            plt.title("Traces ("+str(start+(r*number))+"-"+str(number+(r*number))+")")
            plt.legend()
            plt.show()
        else: 
            if i > 1:
                ax[r].set_title("Traces ("+str(start+(r*number))+"-"+str(start+(r*number)+number-1)+")")
                ax[r].legend()
            else:
                ax[r].set_title("Trace "+str(start+(r*number)))
                if displayData:
                    ax[r].legend()
    if together:
        plt.xlabel("Time")
        #plt.ylabel("Values")
        fig.text(0.04, 0.5, "Values", va='center', rotation='vertical')
        fig.suptitle("Traces ("+str(start)+"-"+str(number+((r-1)*number))+")")
        #plt.title("Traces ("+str(start+(r*number))+"-"+str(number+(r*number))+")")
        #plt.legend()
        plt.show()

