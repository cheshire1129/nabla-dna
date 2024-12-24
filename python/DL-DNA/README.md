# DL-DNA: DNA tools via Deep Learning

DL-DNA can extract feature vector(DNA) for a 2D image and calculate image similarities between two images using Deep-Learning models.

## Features

- Extract image feature vector (DNA)
- Calculate similarity between two images
- Perform similarity calculations with an image pair file
- Train and save custom models
- Load pre-trained models
## Tools Usage

### dl\_dna
Here are help messages for dl\_dna.
```
Usage: dl-dna.py [<options>] <image name> : show DNA
                             <image name> <image name>: get similarity
                             <image pair file>: get similarities
   <options>
   -h: help(this message)
   -m <model>: triplet_loss(default), mobilenet, vgg, autoencoder
   -t <training file>: training mode with file path
       triplet_loss: image list with triple fields
       autoencoder: image list
       mobilenet, vgg: not supported
   -T <threshold>: threshold for model
      mobilenet: minimum value of vector elements to be included in vector distance calculation
   -s <path for save>: path for saving model
   -l <path for load>: path for loading model
   -u <units>: unit count for embedding vector (N_UNITS: env variable)
   -f <image folder> (IMAGE_FOLDER)
   -o <output image>: decoded image path(autoencoder only)
   -e <epochs> (EPOCHS)
   -S <seed> (SEED): random seed for deterministic run
   -b <batch_size>: 0 means full batch
   -v <options>: enable verbose output
      k: keras output
      t: triple loss output
      T: simple triple loss output
```


Here are some examples.  

1. Extracting DNA from a single image  
 ```
 python dl_dna.py -m mobilenet -f /path/to/images -u 4 horse-142
 ```

2. Calculating similarity between two images 
```
python dl_dna.py -m mobilenet -f /path/to/images -u 8 rider-1 rider-2
```
You can also calculate similarity for pairs of images listed in a file.
```
python dl_dna.py -m mobilenet -f /path/to/images -u 8 /path/to/pairs/test_pairs.txt
```

3. Train and Save a model
```
python dl-dna.py -m autoencoder -t train_list.txt -s /path/to/save/model -u 4 -f /path/to/images
```

4. Load & Use a model
```
python dl-dna.py -m mobilenet -l /path/to/load/model -u 4 -f /path/to/images horse-142
```