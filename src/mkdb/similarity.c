#include "config.h"

#include <math.h>

static double
dot_product(unsigned char *dna, unsigned char *dna2, int size)
{
	double	prod = 0.0;

	for (int i = 0; i < size; i++) {
		prod += (double)dna[i] * (double)dna2[i];
	}
	return prod;
}

static double
magnitude(unsigned char *dna, int size)
{
	double sum = 0.0;

	for (int i = 0; i < size; i++) {
		sum += (double)dna[i] * (double)dna[i];
	}
	return sqrt(sum);
}

double
cosine_similarity(unsigned char *dna1, unsigned char *dna2, int size)
{
	double	numerator = dot_product(dna1, dna2, size);
	double	denominator = magnitude(dna1, size) * magnitude(dna2, size);

	if (denominator == 0.0) {
		return 0.0;
	} else {
		return numerator / denominator;
	}
}
