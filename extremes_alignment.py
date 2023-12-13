import trsfile
from trsfile.parametermap import TraceSetParameterMap
from trsfile.parametermap import TraceParameterMap
from trsfile.traceparameter import ByteArrayParameter
import numpy as np
import utils
import sys
from time import time


parameters = TraceSetParameterMap()
print(parameters)

outputZoomS = 0
outputZoomE = 220000

# interval where is search for similar sequences
alignZoomS = 0
alignZoomE = 22000

# numbers of extremes chosen from align zoom above will be within this interval
EXTREMES_L_BOUND = 15
EXTREMES_UP_BOUND = 30

start = 0
number = 30
displayLabels = 1
AVG_BY = 100

start_time = time()


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
    nameTrace = sys.argv[1][0:-4] + '+EXTREMES(' + str(start) + ',' + str(number) + ').trs'
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
        master_trace_array = traces[0].samples[alignZoomS:alignZoomE]
        master_trace = np.zeros(master_trace_array.size, dtype=np.int8)
        for i in range(master_trace.size):
            master_trace[i] = master_trace_array[i]

        master_trace = utils.moving_average(master_trace, n=AVG_BY)

        print("Calculating master trace and optimizing extremes length")
        utils.extremes_len_optimize(master_trace, EXTREMES_L_BOUND, EXTREMES_UP_BOUND)
        master_extremes = utils.find_lokal_extemes_indexes(master_trace)
        print(f"master trace extremes length: {len(master_extremes)}\n")
        print(f"master extremes: {master_extremes}")
        for i in range(number):
            print(f"\nCalculating trace {i}")
            data = traces[i].parameters['LEGACY_DATA'].value

            trace_array = traces[i].samples[alignZoomS:alignZoomE]
            trace = np.zeros(trace_array.size, dtype=np.int8)
            for j in range(trace.size):
                trace[j] = trace_array[j]
            rand_trace_array = np.zeros(outputZoomE - outputZoomS, dtype=np.int8)

            if i != 0:
                shift = utils.extremes_calculate_shift(master_trace, utils.moving_average(trace, n=AVG_BY), master_extremes)
                print(f"shift: {shift}")
            else:
                shift = 0

            if shift > 0:
                for j in range(outputZoomE - outputZoomS - shift):
                    rand_trace_array[j + shift] = traces[i][j + outputZoomS]
            else:
                for j in range(outputZoomE - outputZoomS + shift):
                    rand_trace_array[j] = traces[i][j - shift + outputZoomS]

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
        end_time = time()
        print(f"done in {(end_time - start_time) // 60}m {((end_time - start_time)) - (((end_time - start_time) // 60) * 60)}s")
        