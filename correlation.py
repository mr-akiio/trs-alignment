import trsfile
from trsfile.parametermap import TraceSetParameterMap
import trsfile.traceparameter as tp
from trsfile.parametermap import TraceParameterMap, TraceParameterDefinitionMap
from trsfile.traceparameter import ByteArrayParameter, ParameterType, TraceParameterDefinition
import matplotlib.pyplot as plt
import sys
import numpy as np
#import random, os

def mean(X):
    return np.sum(X, axis=0)/len(X)

def std_dev(X, X_bar):
    return np.sqrt(np.sum((X-X_bar)**2, axis=0))

def cov(X, X_bar, Y, Y_bar):
    return np.sum((X-X_bar)*(Y-Y_bar), axis=0)

parameters = TraceSetParameterMap()
print(parameters)

zoomS=0
zoomE=220000
#zoomE=22000

fig = plt.figure()
start = 0
number = 1000
displayLabels = 4

dataS=0
dataN=1

data = np.zeros((dataN-dataS,number),np.int)

trace_array = np.zeros((number,zoomE-zoomS),np.float)

#print(trace_array) 

scale_X = None
with trsfile.open(sys.argv[1], 'r') as traces:
    print(traces.get_headers())
    # Show all headers
    for header, value in traces.get_headers().items():
        print(header, '=', value)
    scale_X = traces.get_headers().get(trsfile.Header.SCALE_X)

#    print(dir(traces))

    for i, trace in enumerate(traces[start:start+number]):
        #print(trace.parameters['LEGACY_DATA'])
        trace_array[i] = trace.samples[zoomS:zoomE]
        #print(trace.samples)
        #print(type(trace_array[i]))
        for j in range(dataS,dataN):
            data[j][i] = trace.parameters['LEGACY_DATA'].value[j]


print("trace_array")
print(trace_array)
print(trace_array.shape)
print("data")
print(data)
print(data.shape)

with trsfile.trs_open(
        sys.argv[1][0:-4]+'+CORR.trs',                 # File name of the trace set
        'w',                             # Mode: r, w, x, a (default to x)
        # Zero or more options can be passed (supported options depend on the storage engine)
        engine = 'TrsEngine',            # Optional: how the trace set is stored (defaults to TrsEngine)
        headers = {                      # Optional: headers (see Header class)
            trsfile.Header.TRS_VERSION: 1,
            trsfile.Header.SCALE_X: scale_X,
            trsfile.Header.SCALE_Y: 1,
            trsfile.Header.DESCRIPTION: 'Correlation Traces',
            trsfile.Header.TRACE_PARAMETER_DEFINITIONS: TraceParameterDefinitionMap(
                {'LEGACY_DATA': TraceParameterDefinition(ParameterType.BYTE, 1, 0)})
        },
        padding_mode = trsfile.TracePadding.AUTO,# Optional: padding mode (defaults to TracePadding.AUTO)
        live_update = True               # Optional: updates the TRS file for live preview (small performance hit)
                                         #   0 (False): Disabled (default)
                                         #   1 (True) : TRS file updated after every trace
                                         #   N        : TRS file is updated after N traces
    ) as ctraces:

    t_bar = mean(trace_array)
    #print("t_bar")
    #print(t_bar)
    o_t = std_dev(trace_array, t_bar)
    #print("o_t")
    #print(o_t)

    for j in range(dataS,dataN):
        intermediate = np.array([data[j]]).transpose()
        #print("intermediate")
        #print(intermediate)

        d_bar = mean(intermediate)
        o_d = std_dev(intermediate, d_bar)
        covariance = cov(trace_array, t_bar, intermediate, d_bar)
        correlation = covariance/(o_t*o_d)

        #plt.plot(correlation, label="Inp["+str(j)+"]")
        if j < displayLabels: 
            plt.plot(correlation, label="Inp["+str(j)+"]")
        elif j == displayLabels:
            plt.plot(correlation, label="...")
        else:
            plt.plot(correlation)

        # Adding one Trace
        ctraces.append(
            trsfile.Trace(
                trsfile.SampleCoding.FLOAT,
                correlation,
                TraceParameterMap({'LEGACY_DATA': ByteArrayParameter([j])})
            )
        )

plt.xlabel("Time")
plt.ylabel("Correlation")
plt.title("Correlation of bytes: ["+str(dataS)+"-"+str(dataS+dataN-1)+"]")
plt.legend()
plt.show()
