# Python-based nabla-DNA tool

These Python-based tools are developed as a POC for nabla DNA tools: mkdna.py, mkhisto.py, getdist.py and showbmp.py.

## Tools Usage

### mkdna.py
Make nabla DNA
```
mkdna.py [<options>] <image path or folder>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -N: skip normalization
   -S: skip nabla sum
   -o <output>: save dna as an image or text
   -c <threshold>: apply sobel filter(contour) with threshold(drop ratio)
                   if threshold > 1, pixels over threshold - 1 will be 255 gray depth.
   -C <threshold>: crop area outside contour
   -P <pairs file>: only make DNA's for matched pairs
```

### getdist.py
Get similarity distance between two images
```
getdist.py [<options>] <image path> <pis path or dir> or
                       <image path>: get similarity of all pis pairs
   <options>
   -h: help(this message)
   -s <minimum similarity value>: only shows pairs with larger value
   -d <DNA depth>: DNA depth. If not given and not guessed, depth 8 will be assumed
   -t <type>: distance type
      similarity(default): cosine similarity
      c-similarity(default): center weighted cosine similarity
      cosine: cosine distance
      euclidean: euclidean distance
      histogram: histogram similarity
      similarity_histo: similarity with histogram check
   -P <pairs file>: only show matched pairs
```

### showbmp.py
Show an image bitmap with 
```
showbmp.py [<options>] <image path>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -m <mode>: bitmap, averaged, rotated, nabla
   -r: show as raw texts
   -s <scale factor>: image scaling if it is too small
   -c <threshold>: apply sobel filter(contour) with threshold(drop ratio)
                   if threshold > 1, pixels over threshold - 1 will be 255 gray depth.
   -C <threshold>: crop area outside contour
   -k <kernel size>: kernel size for sobel filter
```

### mkhisto.py
Make histogram for an image
```
Usage: mkhisto.py [<options>] <image or PIS path/folder>
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit(default and max: 8)
   -N: skip normalization
   -s: do nabla sum
   -o <output>: save histogram as text
```