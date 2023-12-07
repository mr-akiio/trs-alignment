import numpy as np
import math

# this one is global variable changed by extremes_len_optimize
LOC_EXT_CONF_INT = 40
# how much extremes are searched to evaluate the sequence. Must be less than number of extremes
SIMILARITY_SEQUENCE_LEN = 10
# how much most misaligned extremes are not taken in count in order to count similarity
EXTREMES_MAX_JUMP = 2

VALUE_RANGE = 256
# difference of values in the first couple of extremes in similarity sequence divided by VALUE_RANGE
# must be less than threshold
VALUE_EQ_THRESHOLD = 0.1


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


def norm_euk_dist(x1, x2, y1, y2, x_transformation):
    return math.sqrt(math.pow(y1 - y2, 2) + math.pow((x1 - x2) * x_transformation, 2))


""""
this function is searching for the most similar sequence between extremes1 and extremes2.
comparison between sequences works in this fashion:
It projects extremes with its values as points in 2d space
The x axis is stretched, to make x and y nearly the same weight in euklidian distance
each point from extremes1 finds closest point from extremes2 and the same for the other way.
score is calculated based on sum of these distances and divided by the sample count in similarity interval.
So lower score are better.
"""
def extremes_evaluation(trace1, trace2, extremes1, extremes2):
    result = []
    trace1 = trace1.astype(np.int16)
    trace2 = trace2.astype(np.int16)
    for offset1 in range(len(extremes1) - SIMILARITY_SEQUENCE_LEN):
        for offset2 in range(len(extremes2) - SIMILARITY_SEQUENCE_LEN):
            if (abs(trace1[extremes1[offset1]] - trace2[extremes2[offset2]])) / VALUE_RANGE < VALUE_EQ_THRESHOLD:
                # candidate_shift = extremes1[offset1] - extremes2[offset2]
                ext_array1 = extremes1[offset1:offset1+SIMILARITY_SEQUENCE_LEN]
                ext_x_array1 = [i - ext_array1[0] for i in ext_array1]
                ext_y_array1 = [trace1[i] for i in ext_array1]
                ext_array2 = extremes2[offset2:offset2 + SIMILARITY_SEQUENCE_LEN]
                ext_x_array2 = [i - ext_array2[0] for i in ext_array2]
                ext_y_array2 = [trace2[i] for i in ext_array2]
                sum_distances = 0
                list_distances = []
                # attempt to normalize x magnitude of euklidian distance, so both x and y
                # have similar weights in euklidian distance
                x_transformation = VALUE_RANGE / (ext_x_array1[-1] / SIMILARITY_SEQUENCE_LEN)
                for i in range(SIMILARITY_SEQUENCE_LEN):
                    dist1 = norm_euk_dist(ext_x_array1[i], ext_x_array2[i], ext_y_array1[i],
                                        ext_y_array2[i], x_transformation)
                    dist2 = dist1
                    j = 1
                    # searching for closest points

                    # search min distance for point extremes2[i]
                    # search left in extremes2
                    while i - j > 0 and norm_euk_dist(ext_x_array1[i], ext_x_array2[i-j],
                                                    ext_y_array1[i], ext_y_array2[i-j], x_transformation) < dist1:
                        dist1 = norm_euk_dist(ext_x_array1[i], ext_x_array2[i-j],
                                            ext_y_array1[i], ext_y_array2[i-j], x_transformation)
                        j += 1

                    # search right in extremes2
                    j = 1
                    while i + j < SIMILARITY_SEQUENCE_LEN and norm_euk_dist(ext_x_array1[i], ext_x_array2[i+j],
                                                                          ext_y_array1[i], ext_y_array2[i+j],
                                                                          x_transformation) < dist1:
                        dist1 = norm_euk_dist(ext_x_array1[i], ext_x_array2[i+j],
                                            ext_y_array1[i], ext_y_array2[i+j], x_transformation)
                        j += 1

                    # search min distance for point extremes1[i]
                    # search left in extremes2
                    j = 1
                    while i - j > 0 and norm_euk_dist(ext_x_array1[i-j], ext_x_array2[i],
                                                    ext_y_array1[i-j], ext_y_array2[i], x_transformation) < dist2:
                        dist2 = norm_euk_dist(ext_x_array1[i-j], ext_x_array2[i],
                                            ext_y_array1[i-j], ext_y_array2[i], x_transformation)
                        j += 1

                    # search right in extremes2
                    j = 1
                    while i + j < SIMILARITY_SEQUENCE_LEN and norm_euk_dist(ext_x_array1[i+j], ext_x_array2[i],
                                                                          ext_y_array1[i+j], ext_y_array2[i],
                                                                          x_transformation) < dist2:
                        dist2 = norm_euk_dist(ext_x_array1[i+j], ext_x_array2[i],
                                            ext_y_array1[i+j], ext_y_array2[i], x_transformation)
                        j += 1

                    sum_distances += dist1 + dist2
                    list_distances.append(dist1)
                    list_distances.append(dist2)

                list_distances.sort()
                for i in range(EXTREMES_MAX_JUMP):
                    list_distances.pop()

                result.append((sum(list_distances) / ext_x_array1[-1], extremes1[offset1], extremes2[offset2]))

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
    score, index1, index2 = evaluation[0]
    print(f"master trace index: {index1}\n trace index: {index2}")
    return index1 - index2


def moving_average(a, n=4):
    ret = np.cumsum(a)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] // n


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
