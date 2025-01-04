# Nabla: Bitmap-based DNA Image

This project aims to develop an image DNA tool designed for use in filtering systems
to block the distribution of unauthorized/unlawful images.
Image DNA is a technology used for detecting image equivalence.
An equivalent image includes not only an identical replica of the original but
also derivative images created through various modifications from the original, such as
format conversion, caption addition, resizing, color adjustment, or applying facial mosaics.

Among various approaches to implementing image DNA,
this project focuses on a bitmap-based method called Nabla.
Additionally, the project partially supports other image DNA technologies,
including image processing-based methods and deep learning-based approaches.

Bitmap-based methods reduce an image’s two-dimensional representation into a
simplified bitmap to verify image equivalence. These methods employ straightforward
operations or preprocessing steps to compress bitmap information while maintaining image distinguishability.
Examples include histogram analysis and hash-based feature extraction,
such as average hash and difference hash. Bitmap-based methods operate on
low-level image data, resulting in low computational overhead for DNA generation.146
This study adopts a bitmap-based image DNA method termed Nabla DNA (∇-DNA),152
which converts image bitmaps into a reverse-pyramid structure. As illustrated in Figure
3, the method normalizes the brightness, color, and resolution of an image bitmap. It then
segments the bitmap into quadrants along the diagonal, averaging pixel intensities within
triangular regions to create a rotation-neutral vector representation.

## How to Build Nabla

The project uses cmake for its build system. Follow the steps below to build the Nabla tools:

1. Create a build directory and navigate into it:
   ```
   $ mkdir build
   $ cd build
   ```
2. Generate the Makefile using cmake:
   ```
   $ cmake ..
   ```

3. Build the project using make:
   ```
   make
   ```

4. After a successful build, the following binaries will be created:
   - mkdna: A tool for generating image DNA.
   - mkdb: A tool for extracting and searching image DNA databases.
   - getdist: A tool for measuring the similarity between image DNA.
    
   These binaries can be found in the build directory. Use them as per the project requirements.

## How to run Nabla

### mkdna
Make nabla DNA
```
Usage: mkdna [<options>] <image name/path/folder or list file>
   A list file must have a .txt extension
   <options>
   -h: help(this message)
   -x <resolution>: DNA resolution (default: 4)
   -d <depth>: DNA depth bit (default and max: 8)
   -I <image folder>: image folder(env var: IMAGE_FOLDER)
   -o <output>: save dna as text
```

### mkdb
Make image DNA database for managing many DNA's
```
Usage: mkdb [<options>] <image name/path/folder or list file>
   <options>
   -h: help(this message)
   -I <image folder>: image folder(env var: IMAGE_FOLDER)
   -A: DNA insert mode
   -x <dna resolution>: dna resolutions of an indexed dna and stored one
              default: 2(indexing) 4(stored). Must precede the -D option
              format: indexed:stored"
   -e <dna depth>: dna depth(default: 2:8)"
   -d <dna db>: existing dna db
   -D <dna db>: newly created dna db
   -t <threshold>: threshold for search DNA
```

## Python Version of Nabla
For the Python implementation of the Nabla tools,
please refer [python/README.md](python/README.md).
It contains detailed instructions and usage examples specific to the Python version.

## Deep Learning-based Image DNA
Deep learning-based Image DNA can be found in python/DL-DNA.
Please refer [python/DL-DNA/README.md](python/DL-DNA/README.md) for detailed information.

## Image Processing-based Image DNA
Image Processing-based Image DNA can be found in python/IMG-DNA.
Please refer [python/IMG-DNA/README.md](python/IMG-DNA/README.md) for detailed information.

## Dataset for Image DNA Experiments
To facilitate Image DNA experiments, we provide a dataset that can be accessed and used as follows:

- [Kaggle Dataset](https://drive.google.com/file/d/1rS8bLyyRt6u3wFj0tyg87p3XstRShRZh/view?usp=drive_link) : 
  non-duplicate 1,752 images from [a small-scale Kaggle Dataset](https://www.kaggle.com/datasets/pavansanagapati/images-dataset)
- [modified COCO Dataset](https://drive.google.com/file/d/1HXz7shc6VODwyh8KBG3ROvYTetAVy2PA/view?usp=drive_link) : 
  20 modified images from [COCO 2014](https://cocodataset.org/) 
