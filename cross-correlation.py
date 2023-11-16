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

import sys

def find_max(trace_array_input):
    max_val = trace_array_input[0]
    max_index = 0

    for i in range(len(trace_array_input)):
        if trace_array_input[i] > max_val:
            max_val = trace_array_input[i]
            max_index = i
    return max_index


def calculate_shift(trace1, trace2):
    correlation = np.correlate(np.array(trace1), np.array(trace2), mode='full')
    
    max_index = find_max(correlation)
    
    result = max_index + 1 - trace2.size
    
    return result

parameters = TraceSetParameterMap()
print(parameters)

zoomS=0
zoomE=22000

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
    nameTrace = sys.argv[1][0:-4]+'+SAVE('+str(start)+','+str(number)+').trs'
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

        for i in range(number):
            print(f"Calculating trace {i}")
            trace = traces[i]
            #print(trace)
            trace_array = trace.samples[zoomS:zoomE]
            data = trace.parameters['LEGACY_DATA'].value
            
            if i == 0:
                rand_trace_array = np.zeros(trace_array.size, dtype=np.int8)
                for i in range(trace_array.size):
                    rand_trace_array[i] = trace_array[i]
            else:
                shift = calculate_shift(traces[0], trace)
                rand_trace_array = np.zeros(trace_array.size, dtype=np.int8)

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