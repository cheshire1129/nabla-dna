import triplet_model
import autoencoder_model
import mobilenet
import vgg

def get_dl_dna_model(model_type):
    if model_type == 'triplet_loss':
        return triplet_model.ModelTriplet()
    elif model_type == 'autoencoder':
        return autoencoder_model.AutoEncoder()
    elif model_type == 'mobilenet':
        return mobilenet.ModelMobileNet()
    elif model_type == 'vgg':
        return vgg.VGG()
    print(f"invalid model type: {model_type}")
    exit(1)