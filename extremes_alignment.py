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
import utils
import sys

parameters = TraceSetParameterMap()
print(parameters)

zoomS = 0
zoomE = 220000

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

    # header = traces.get_headers()
    # header[trsfile.Header.NUMBER_SAMPLES] = 1
    nameTrace = sys.argv[1][0:-4] + '+SAVE(' + str(start) + ',' + str(number) + '_).trs'
    with trsfile.trs_open(
            nameTrace,  # File name of the trace set
            'w',  # Mode: r, w, x, a (default to x)
            # Zero or more options can be passed (supported options depend on the storage engine)
            engine='TrsEngine',  # Optional: how the trace set is stored (defaults to TrsEngine)
            headers={  # Optional: headers (see Header class)
                trsfile.Header.TRS_VERSION: 2,
                trsfile.Header.SCALE_X: scale_X,
                trsfile.Header.SCALE_Y: scale_Y,
                trsfile.Header.DESCRIPTION: 'Copied',
                # Header.TITLE_SPACE = 255
                # Header.LENGTH_DATA = 63
                # trsfile.Header.TRACE_PARAMETER_DEFINITIONS: TraceParameterDefinitionMap(
                #    {'LEGACY_DATA': TraceParameterDefinition(ParameterType.BYTE, 16, 0)})
            },
            padding_mode=trsfile.TracePadding.AUTO,  # Optional: padding mode (defaults to TracePadding.AUTO)
            live_update=False  # Optional: updates the TRS file for live preview (small performance hit)
            #   0 (False): Disabled (default)
            #   1 (True) : TRS file updated after every trace
            #   N        : TRS file is updated after N traces

    ) as wrtraces:
        master_trace_array = traces[0].samples[zoomS:zoomE]
        master_trace = np.zeros(master_trace_array.size, dtype=np.int8)
        for i in range(master_trace.size):
            master_trace[i] = master_trace_array[i]

        print("Calculating master trace and optimizing extremes length")
        utils.extremes_len_optimize(master_trace, 100, 200)
        master_extremes = utils.find_lokal_extemes_indexes(master_trace)
        print(f"master trace extremes length: {len(master_extremes)}\n")
        print(f"master extremes: {master_extremes}")
        for i in range(number):
            print(f"Calculating trace {i}")
            data = traces[i].parameters['LEGACY_DATA'].value

            trace_array = traces[i].samples[zoomS:zoomE]
            trace = np.zeros(trace_array.size, dtype=np.int8)
            for j in range(trace.size):
                trace[j] = trace_array[j]
            print(f"second extremes: {utils.find_lokal_extemes_indexes(trace)}")
            rand_trace_array = np.zeros(trace_array.size, dtype=np.int8)

            if i != 0:
                shift = utils.extremes_calculate_shift(master_trace, trace, master_extremes)
                print(shift)
            else:
                shift = 0

            if shift > 0:
                for j in range(trace.size - shift):
                    rand_trace_array[j + shift] = trace[j]
            else:
                for j in range(trace.size + shift):
                    rand_trace_array[j] = trace[j - shift]

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