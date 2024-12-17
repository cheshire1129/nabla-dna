#include "config.h"

#include <math.h>

static double
dot_product(char *dna1, char *dna2, int size)
{
	double	prod = 0.0;

	for (int i = 0; i < size; i++) {
		prod += (double)dna1[i] * (double)dna2[i];
	}
	return prod;
}

static double
magnitude(char *dna, int size)
{
	double sum = 0.0;

	for (int i = 0; i < size; i++) {
		sum += (double)dna[i] * (double)dna[i];
	}
	return sqrt(sum);
}

static double
cosine_similarity(char *dna1, char *dna2, int size)
{
	double	numerator = dot_product(dna1, dna2, size);
	double	denominator = magnitude(dna1, size) * magnitude(dna2, size);

	if (denominator == 0.0) {
		return 0.0;
	} else {
		return numerator / denominator;
	}
}

double
get_similarity(unsigned char *dna1, unsigned char *dna2, int size)
{
	return cosine_similarity((char *)dna1, (char *)dna2, size);
}
