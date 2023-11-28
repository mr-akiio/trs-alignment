import numpy as np

LOC_EXT_CONF_INT = 20

SIMILARITY_SEQUENCE_LEN = 50
VALUE_RANGE = 256
EXTREMES_MAX_JUMP = 5
VALUE_EQ_THRESHOLD = 0.1
DIST_EQ_THRESHOLD = 0.1

def find_lokal_extemes_indexes(trace):

    result = {"max": [], "min": [], "extremes": []}
    current_begin_index = 0
    ring_buffer_back = [trace[i] for i in range(LOC_EXT_CONF_INT)]
    ring_buffer_front = [trace[i] for i in range(LOC_EXT_CONF_INT + 1, LOC_EXT_CONF_INT*2 + 1)]
    for i in range(LOC_EXT_CONF_INT, trace.size - LOC_EXT_CONF_INT - 1):
        sample = trace[i]
        result["extremes"].append(i)
        if sample > max(ring_buffer_back) and sample > max(ring_buffer_front):
            result["max"].append(i)
        elif sample < min(ring_buffer_back) and sample < min(ring_buffer_front):
            result["min"].append(i)

        ring_buffer_front[current_begin_index] = trace[i + LOC_EXT_CONF_INT + 1]
        ring_buffer_back[current_begin_index] = trace[i]
        current_begin_index = (current_begin_index + 1) % LOC_EXT_CONF_INT
    return result

""""
 start and end of computing with extremes1 of length 16 and extremes2 of length 9 with SIMILIARITY_SEQUENCE_LEN = 5
        [][][][][][][][][][][][][][][][]   --\   [][][][][][][][][][][][][][][][] (16)
[][][][][][][][][]                         --/                         [][][][][][][][][] (9)  => [][][][][][][][][][][][][][][] (15)

"""
def extremes_evaluation(trace1, trace2, extremes1, extremes2):
    result = []
    offset1 = 0
    offset2 = len(extremes2["extremes"]) - 1 - SIMILARITY_SEQUENCE_LEN
    for index in range(len(extremes2["extremes"]) + len(extremes1["extremes"]) - 2 * SIMILARITY_SEQUENCE_LEN):
        sum_similarity = 0
        count_similarity = 0
        jump = 0
        cnt = False
        for i in range(SIMILARITY_SEQUENCE_LEN):
            ext_index1 = extremes1["extremes"][offset1 + i]
            ext_index2 = extremes2["extremes"][offset2 + i + jump]
            if ((trace1[ext_index1] - trace2[ext_index2]) / VALUE_RANGE >= VALUE_EQ_THRESHOLD):
                cnt
                continue

            distance = extremes1["extremes"][offset1 + i + 1] - extremes1["extremes"][offset1 + i]
            shift = ext_index2 - ext_index1
            lookup = extremes2["extremes"][offset2+i+jump:offset2+i+jump+EXTREMES_MAX_JUMP]
            nearest_ext_dist = lookup.index(min([j - ext_index2 for j in lookup]))
            jump += nearest_ext_dist
            found_extreme = extremes2["extremes"][ext_index2 + nearest_ext_dist]
            fe_dist_diff = abs(distance - nearest_ext_dist) # TO BE EVALUATED
            fe_value1 = trace1[extremes1["extremes"][offset1 + i + 1]]
            fe_value2 = trace2[extremes2["extremes"][offset2 + i + jump]]
            sum_similarity += (1 - abs(fe_dist_diff/distance)) * (1 - abs((fe_value1 - fe_value2) / VALUE_RANGE))
            count_similarity += 1

        result.append(sum_similarity / count_similarity)


        if index >= len(extremes2["extremes"]) - SIMILARITY_SEQUENCE_LEN:
            offset1 += 1
        if offset2 > 0:
            offset2 -= 1

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