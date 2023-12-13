import trsfile
from trsfile.parametermap import TraceSetParameterMap
import trsfile.traceparameter as tp
from trsfile.parametermap import TraceParameterMap, TraceParameterDefinitionMap
from trsfile.traceparameter import StringParameter, ByteArrayParameter, ParameterType, TraceParameterDefinition
import matplotlib.pyplot as plt
import sys
import numpy as np
# import random, os
import math
import sys
from numpy.random import randn
from numpy.random import seed
from scipy.stats import pearsonr

# choose specific section what to compare with correlation
corrS = 15000
corrE = 17000
# how many sampes look to left and right
interval = 500

def calculate_shift(master, trace2):
    shift = -interval
    best = -1

    for i in range(-interval, interval):
        llist = trace2[(corrS + i):(corrE + i)]
        corr, _ = pearsonr(master, llist)
        if corr > best:
            best = corr
            shift = i

    return -shift


parameters = TraceSetParameterMap()
print(parameters)

zoomS = 0
zoomE = 22000

start = 0
number = 5
displayLabels = 1

with trsfile.open(sys.argv[1], 'r') as traces:
    print(traces.get_headers())
    # Show all headers
    for header, value in traces.get_headers().items():
        print(header, '=', value)
    
    scale_X = traces.get_headers().get(trsfile.Header.SCALE_X)
    scale_Y = traces.get_headers().get(trsfile.Header.SCALE_Y)
    lengthData = traces.get_headers().get(trsfile.Header.LENGTH_DATA)
    coding = traces.get_headers().get(trsfile.Header.SAMPLE_CODING)
    nameTrace = sys.argv[1][0:-4]+'+CORR('+str(start)+','+str(number)+').trs'
    
    with trsfile.trs_open(
        nameTrace,                 # File name of the trace set
        'w',                             # Mode: r, w, x, a (default to x)
        # Zero or more options can be passed (supported options depend on the storage engine)
        # Optional: how the trace set is stored (defaults to TrsEngine)
        engine='TrsEngine',
        headers={                      # Optional: headers (see Header class)
            trsfile.Header.TRS_VERSION: 2,
            trsfile.Header.SCALE_X: scale_X,
            trsfile.Header.SCALE_Y: scale_Y,
            trsfile.Header.DESCRIPTION: 'Copied',
        },
        # Optional: padding mode (defaults to TracePadding.AUTO)
        padding_mode=trsfile.TracePadding.AUTO,
        # Optional: updates the TRS file for live preview (small performance hit)
        live_update=False
        #   0 (False): Disabled (default)
        #   1 (True) : TRS file updated after every trace
        #   N        : TRS file is updated after N traces

    ) as wrtraces:
        master_trace = traces[0].samples[corrS:corrE]
        
        for i in range(number):
            print(f"Calculating trace {i}")
            trace = traces[i]
            data = trace.parameters['LEGACY_DATA'].value

            trace_array = trace.samples[zoomS:zoomE]
            rand_trace_array = np.zeros(trace_array.size, dtype=np.int8)

            if i == 0:
                for i in range(trace_array.size):
                    rand_trace_array[i] = trace_array[i]
            else:
                shift = calculate_shift(master_trace, trace_array)
                print(shift)

                if shift > 0:
                    for i in range(trace_array.size-shift):
                        rand_trace_array[i+shift] = trace_array[i]
                else:
                    for i in range(trace_array.size+shift):
                        rand_trace_array[i] = trace_array[i-shift]

            # Adding one Trace
            wrtraces.append(
                trsfile.Trace(
                    coding,
                    rand_trace_array,
                    TraceParameterMap({'LEGACY_DATA': ByteArrayParameter(data)  # ,
                                       # 'COEFFICIENTS': StringParameter(coeffs)
                                       })
                )
            )

        print("done")
