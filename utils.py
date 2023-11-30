import numpy as np

LOC_EXT_CONF_INT = 40

SIMILARITY_SEQUENCE_LEN = 100
VALUE_RANGE = 256
EXTREMES_MAX_JUMP = 50
VALUE_EQ_THRESHOLD = 0.1
DIST_EQ_THRESHOLD = 0.1

def find_lokal_extemes_indexes(trace):

    result = []
    current_begin_index = 0
    ring_buffer_back = [trace[i] for i in range(LOC_EXT_CONF_INT)]
    ring_buffer_front = [trace[i] for i in range(LOC_EXT_CONF_INT + 1, LOC_EXT_CONF_INT*2 + 1)]
    for i in range(LOC_EXT_CONF_INT, trace.size - LOC_EXT_CONF_INT - 1):
        sample = trace[i]
        if sample >= max(ring_buffer_back) and sample > max(ring_buffer_front) and (len(result) == 0 or i - result[-1] > LOC_EXT_CONF_INT):
            result.append(i)
        elif sample <= min(ring_buffer_back) and sample < min(ring_buffer_front) and (len(result) == 0 or i - result[-1] > LOC_EXT_CONF_INT):
            result.append(i)

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
    trace1 = trace1.astype(np.int16)
    trace2 = trace2.astype(np.int16)
    for offset1 in range(len(extremes1) - SIMILARITY_SEQUENCE_LEN):
        for offset2 in range(len(extremes2) - SIMILARITY_SEQUENCE_LEN):
            sum_similarity = 0
            count_similarity = 0
            jump = 0
            if (abs(trace1[extremes1[offset1]] - trace2[extremes2[offset2]])) / VALUE_RANGE < VALUE_EQ_THRESHOLD:
                for i in range(SIMILARITY_SEQUENCE_LEN - 1):
                    if offset2 + i + jump > len(extremes2) - 2:
                        return result
                    ext_index1 = extremes1[offset1 + i]
                    ext_index2 = extremes2[offset2 + i + jump]

                    distance = extremes1[offset1 + i + 1] - extremes1[offset1 + i]
                    lookup = extremes2[offset2+i+jump:min([offset2+i+jump+EXTREMES_MAX_JUMP, len(extremes2)])]
                    jump += [abs(j - ext_index2) for j in lookup].index(min([abs(j - ext_index2) for j in lookup]))
                    fe_dist_diff = abs(distance + ext_index2 - extremes2[offset2 + i + jump + 1])
                    fe_value1 = trace1[extremes1[offset1 + i + 1]]
                    fe_value2 = trace2[extremes2[offset2 + i + jump + 1]]
                    sum_similarity += (1 - abs(fe_dist_diff/distance)) * (1 - abs((fe_value1 - fe_value2) / VALUE_RANGE))
                    count_similarity += 1

            if count_similarity == 0:
                result.append((0, extremes1[offset1], extremes2[offset2]))
            elif sum_similarity == count_similarity:
                # early stop
                return result
            else:
                result.append((sum_similarity / count_similarity, extremes1[offset1], extremes2[offset2]))
    return result


def extremes_len_optimize(trace, lower_bound, upper_bound):
    global LOC_EXT_CONF_INT
    extremes = find_lokal_extemes_indexes(trace)
    while len(extremes) > upper_bound or len(extremes) < lower_bound:
        if len(extremes) > upper_bound:
            LOC_EXT_CONF_INT = LOC_EXT_CONF_INT * 2
        if len(extremes) < lower_bound:
            LOC_EXT_CONF_INT = LOC_EXT_CONF_INT * 0.75
        extremes = find_lokal_extemes_indexes(trace)


def extremes_calculate_shift(trace1, trace2, extremes1):
    extremes2 = find_lokal_extemes_indexes(trace2)
    print("extremes1 len: " + str(len(extremes1)))
    print("extremes2 len: " + str(len(extremes2)))
    evaluation = extremes_evaluation(trace1, trace2, extremes1, extremes2)
    evaluation.sort()
    if len(evaluation) == 0:
        print("NO SHIFT FOUND FOR THESE TRACES")
        return 0
    _, index1, index2 = evaluation[0]

    return index1 - index2


def test():
    trace = np.zeros(1000, dtype=np.int16)

    for index in range(trace.size):
        value = index % 40
        if (index // 40) % 2 == 0:
            trace[index] = value
        else:
            trace[index] = 40 - value

    print(trace)
    trace2 = np.zeros(1000, dtype=np.int16)
    for i in range(trace2.size):
        trace2[i] = trace[(i+10)%trace.size]

    print("extremes1: ", end='')
    print([trace[i] for i in find_lokal_extemes_indexes(trace)])
    print("extremes2: ", end='')
    print([trace2[i] for i in find_lokal_extemes_indexes(trace2)])
    print(extremes_evaluation(trace, trace2, find_lokal_extemes_indexes(trace), find_lokal_extemes_indexes(trace2)))


if __name__ == "__main__":
    print()
    #test()
