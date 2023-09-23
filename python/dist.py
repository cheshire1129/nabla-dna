import numpy as np
from numpy.linalg import norm
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
        iter = range(2, res, 2)
    else:
        iter = range(1, res, 2)
    for i in reversed(iter):
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


def get(type, dna1, dna2):
    dna1 = dna1.astype(np.float32)
    dna2 = dna2.astype(np.float32)
    dna1 = (dna1 - 127) / 128
    dna2 = (dna2 - 127) / 128
    if type == 'similarity':
        return _get_similarity(dna1, dna2)
    elif type == 'c-similarity':
        weights = _get_center_weights(_get_resolution(dna1))
        return _get_similarity(dna1, dna2, weights)
    elif type == "cosine":
        return _get_cosine(dna1, dna2)
    elif type == "euclidean":
        return _get_euclidean(dna1, dna2)
