import trsfile
from trsfile.parametermap import TraceSetParameterMap
import trsfile.traceparameter as tp
from trsfile.parametermap import TraceParameterMap, TraceParameterDefinitionMap
from trsfile.traceparameter import StringParameter, ByteArrayParameter, ParameterType, TraceParameterDefinition
import matplotlib.pyplot as plt
import sys
import numpy as np
#import random, os
import math 
import statistics

import sys

def find_max(trace):
    max_val = trace[0]
    max_index = 0
    count = 0
    
    for i in range(2, trace.size, 5):
        if trace[i] > max_val:
            max_val = trace[i]
            max_index = i
            count = 0
        else:
            count += 1
            if count == 20:
                break
    return max_index


parameters = TraceSetParameterMap()
print(parameters)

zoomS=0
zoomE=220000

start = 0
number = 20
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

    #header = traces.get_headers()
    #header[trsfile.Header.NUMBER_SAMPLES] = 1
    nameTrace = sys.argv[1][0:-4]+'+SAVE('+str(start)+','+str(number)+')+repaired.trs'
    with trsfile.trs_open(
        nameTrace,                 # File name of the trace set
        'w',                             # Mode: r, w, x, a (default to x)
        # Zero or more options can be passed (supported options depend on the storage engine)
        engine = 'TrsEngine',            # Optional: how the trace set is stored (defaults to TrsEngine)
        headers = {                      # Optional: headers (see Header class)
            trsfile.Header.TRS_VERSION: 2,
            trsfile.Header.SCALE_X: scale_X,
            trsfile.Header.SCALE_Y: scale_Y,
            trsfile.Header.DESCRIPTION: 'Copied',
            #Header.TITLE_SPACE = 255
            #Header.LENGTH_DATA = 63
            #trsfile.Header.TRACE_PARAMETER_DEFINITIONS: TraceParameterDefinitionMap(
            #    {'LEGACY_DATA': TraceParameterDefinition(ParameterType.BYTE, 16, 0)})
        },
        padding_mode = trsfile.TracePadding.AUTO,# Optional: padding mode (defaults to TracePadding.AUTO)
        live_update = False              # Optional: updates the TRS file for live preview (small performance hit)
                                         #   0 (False): Disabled (default)
                                         #   1 (True) : TRS file updated after every trace
                                         #   N        : TRS file is updated after N traces

    ) as wrtraces:
        master_trace = traces[0]
        for i in range(number):
            print(f"Trace {i}")
            if ((i) % 100000)==0:
                print("here:",i)
            trace = traces[i]
            #print(trace)
            trace_array = trace.samples[zoomS:zoomE]
            data = trace.parameters['LEGACY_DATA'].value
            #coeffs = trace.parameters['COEFFICIENTS'].value
            #print(coeffs)
            #print("here",trace_array,data)
            trace_array = trace.samples[zoomS:zoomE]
            # generate some integers
            rand_trace_array = np.zeros(trace_array.size,dtype=np.int8)
            for j in range(2, trace_array.size, 5):
                a = int(statistics.mean(trace_array[j-2:j+3]))

                rand_trace_array[j] = a
                rand_trace_array[j+1] = a
                rand_trace_array[j-1] = a
                rand_trace_array[j-2] = a
                rand_trace_array[j+2] = a
                
            if i == 0:
                max_master = find_max(rand_trace_array)
            else:
                shift = max_master - find_max(rand_trace_array)
                rand_trace_array = np.zeros(trace_array.size,dtype=np.int8)
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
                    TraceParameterMap({'LEGACY_DATA': ByteArrayParameter(data)#,
                                    #'COEFFICIENTS': StringParameter(coeffs)
                                    })
                )
            )

        print("done")