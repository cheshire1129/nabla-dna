import numpy as np
from scipy import spatial


def _get_similarity(dna1, dna2, weights=None):
    return 1 - _get_cosine(dna1, dna2, weights)


def _get_cosine(dna1, dna2, weights=None):
    return spatial.distance.cosine(dna1, dna2, weights)


def _get_euclidean(dna1, dna2):
    return np.linalg.norm(dna1 - dna2)


def _get_center_weights(res):
    weights = []
    if res % 2:
        iteration = range(2, res, 2)
    else:
        iteration = range(1, res, 2)
    for i in reversed(iteration):
        w = 1 / i
        for j in range(i):
            weights.append(w)
    if res % 2:
        weights.append(1.0)
    return weights


def _get_resolution(dna):
    nrfpixel = len(dna)
    if nrfpixel == 1:
        return 1

    reshalf = 1
    while True:
        if reshalf * (reshalf - 1) + 1 == nrfpixel:
            return reshalf * 2 - 1
        elif reshalf * reshalf == nrfpixel:
            return reshalf * 2
        reshalf += 1


def get(dist_type, dna1, dna2, depth: int):
    dna1 = dna1.astype(np.float32)
    dna2 = dna2.astype(np.float32)
    dna1 = dna1 - (2 ** depth - 1) / 2
    dna2 = dna2 - (2 ** depth - 1) / 2
    if dist_type == 'similarity':
        return _get_similarity(dna1, dna2)
    elif dist_type == 'c-similarity':
        weights = _get_center_weights(_get_resolution(dna1))
        return _get_similarity(dna1, dna2, weights)
    elif dist_type == "cosine":
        return _get_cosine(dna1, dna2)
    elif dist_type == "euclidean":
        return _get_euclidean(dna1, dna2)
