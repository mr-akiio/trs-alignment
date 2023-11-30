import sys
from time import time
import statistics
import trsfile
from trsfile.parametermap import TraceSetParameterMap
from trsfile.parametermap import TraceParameterMap
from trsfile.traceparameter import ByteArrayParameter
import numpy as np

by_group = 5


def find_max(trace_array_input):
    max_val = trace_array_input[0]
    max_index = 0

    for i in range(by_group // 2, trace_array_input.size // 2, by_group):
        if trace_array_input[i] > max_val:
            max_val = trace_array_input[i]
            max_index = i
    return max_index

parameters = TraceSetParameterMap()
print(parameters)

zoomS = 0
zoomE = 220000

start = 0
number = 10
displayLabels = 1

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

    nameTrace = sys.argv[1][0:-4] + \
        '+peak_repaired.trs'
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
        master_trace = traces[0]
        for i in range(number):
            print(f"Processing trace N° {i}")

            trace = traces[i]
            data = trace.parameters['LEGACY_DATA'].value

            trace_array = trace.samples[zoomS:zoomE]
            rand_trace_array = np.zeros((trace_array.size), dtype=np.int8)

            for j in range(by_group // 2, trace_array.size, by_group):

                low = by_group // 2
                high = by_group // 2 + 1 if by_group % 2 == 1 else by_group // 2
                a = int(statistics.mean(trace_array[j-low:j+high]))

                for u in range(j - low, j + high):
                    rand_trace_array[u] = a
                # rand_trace_array[j+1] = a
                # rand_trace_array[j-1] = a
                # rand_trace_array[j-2] = a
                # rand_trace_array[j+2] = a

            if i == 0:
                max_master = find_max(rand_trace_array)
                rand_trace_array = np.zeros(trace_array.size, dtype=np.int8)

                for i in range(trace_array.size):
                    rand_trace_array[i] = trace_array[i]
            else:
                shift = max_master - find_max(rand_trace_array)
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
                    TraceParameterMap({'LEGACY_DATA': ByteArrayParameter(data)})
                )
            )
        end_time = time()
        print(f"done in {(end_time - start_time) // 60}m {((end_time - start_time) / 60) - ((end_time - start_time) // 60) }s")
