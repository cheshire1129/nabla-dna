# DL-DNA: DNA tools via Deep Learning

DL-DNA can extract feature vector(DNA) for a 2D image.

## Tools Usage

### dl\_dna
Here are help messages for dl\_dna.
```
Usage: dl_dna.py [<options>]
   <options>
   -h: help(this message)
   -m <model>: triplet_loss(default), mobilenet, autoencoder
   -t <training file>: training mode with file path
       triplet_loss: image list with triple fields
       mobilenet: not supported
   -s <path for save>: path for saving model
   -l <path for load>: path for loading model
   -u <units>: unit count for embedding vector (N_UNITS: env variable)
   -f <image folder> (IMAGE_FOLDER)
   -e <epochs> (EPOCHS)
   -S <seed> (SEED): random seed for deterministic run
   -b <batch_size>: 0 means full batch
   -v <options>: enable verbose output
      k: keras output
      t: triple loss output
      T: simple triple loss output
```

dl\_dna supports 3 DL models: triplet loss, mobilenet., autoencoder

Here is a training example for triplet loss model.

```
$ python dl_dna.py -t trining_data.txt -s triploss.keras -u 32 -f /data/images
```
