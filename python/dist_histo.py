def _get_histo_similarity(histo1, histo2):
    count = 0
    sum_diff = 0
    for i in range(len(histo1)):
        sum_diff += abs(histo1[i] - histo2[i])
        count += (histo1[i] + histo2[i])
    return 1 - float(sum_diff) / count

def get(histo1, histo2):
    return _get_histo_similarity(histo1, histo2)
