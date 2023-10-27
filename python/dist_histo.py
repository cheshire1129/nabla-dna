def _get_histo_similarity(dna1, dna2):
    count = 0
    sum_diff = 0
    for i in range(len(dna1)):
        sum_diff += abs(dna1[i] - dna2[i])
        count += (dna1[i] + dna2[i])
    return 1 - float(sum_diff) / count

def get(histo1, histo2):
    return _get_histo_similarity(histo1, histo2)
