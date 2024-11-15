import sift
import orb

def get_img_dna_model(model_type):
    if model_type == 'sift':
        return sift.SIFT()
    elif model_type == 'orb':
        return orb.ORB()
    print(f"invalid model type: {model_type}")
    exit(1)