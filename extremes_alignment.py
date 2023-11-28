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
    nameTrace = sys.argv[1][0:-4] + '+SAVE(' + str(start) + ',' + str(number) + ').trs'
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
        master_trace = traces[0]
        for i in range(1, number + 1):
            print(f"Calculating trace {i}")
            trace = traces[i]
            data = trace.parameters['LEGACY_DATA'].value

            rand_trace_array = np.zeros(trace.size, dtype=np.int8)


            shift = utils.extremes_calculate_shift(master_trace, trace)
            print(shift)

            if shift > 0:
                for i in range(trace.size - shift):
                    rand_trace_array[i + shift] = trace[i]
            else:
                for i in range(trace.size + shift):
                    rand_trace_array[i] = trace[i - shift]

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