import numpy as np

LOC_EXT_CONF_INT = 20


def find_lokal_extemes_indexes(trace):

    result = {"max": [], "min": []}
    current_begin_index = 0
    ring_buffer_back = [trace[i] for i in range(LOC_EXT_CONF_INT)]
    ring_buffer_front = [trace[i] for i in range(LOC_EXT_CONF_INT + 1, LOC_EXT_CONF_INT*2 + 1)]
    for i in range(LOC_EXT_CONF_INT, trace.size - LOC_EXT_CONF_INT - 1):
        sample = trace[i]
        if sample > max(ring_buffer_back) and sample > max(ring_buffer_front):
            result["max"].append(i)
        elif sample < min(ring_buffer_back) and sample < min(ring_buffer_front):
            result["min"].append(i)

        ring_buffer_front[current_begin_index] = trace[i + LOC_EXT_CONF_INT + 1]
        ring_buffer_back[current_begin_index] = trace[i]
        current_begin_index = (current_begin_index + 1) % LOC_EXT_CONF_INT
    return result


def test():
    trace = np.zeros(1000, dtype=np.int16)

    for index in range(trace.size):
        value = index % 40
        if (index // 40) % 2 == 0:
            trace[index] = value
        else:
            trace[index] = 40 - value

    print(trace)
    print(find_lokal_extemes_indexes(trace))


if __name__ == "__main__":
    test()