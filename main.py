from data import mono_graphene_iter
from segmenter import Segmenter
from material import Material, wte2, graphene
import tensorflow as tf
import numpy as np
from tqdm import tqdm
import warnings
import matplotlib.pyplot as plt

warnings.simplefilter("ignore", UserWarning)

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    # 'trilayer': np.array([198,22,22])/255.0, # Red
    'trilayer': np.array([255,165,0])/255.0, # Orange
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}

number_by_layer = {
    'bg': 0,
    'monolayer': 1,
    'bilayer': 2,
    'trilayer': 3,
    'fewlayer': 3,
    'manylayer': 3,
    'bluish_layers':3,
    'more_bluish_layers':3,
    'bulk': 3,
    'dirt': 3,
}

hBN_colors = {
    'bg': np.array([0,0,0])/255.0, #Uncolored
    '0-10': np.array([0,163,255])/255.0, # Blue
    '10-20': np.array([29,255,0])/255.0, # Green
    '20-30': np.array([198,22,22])/255.0, # Red
    '30+': np.array([255,165,0])/255.0, # Orange
    '35+': np.array([255,165,0])/255.0, # Orange
    # 'bluish_layers': np.array([53, -8, -12]),
    # 'more_bluish_layers': np.array([50, 1, -10]),
    'dirt': np.array([255, 255, 0])/255.0, # Yellow
}

hBN_numbers = { # cielab colorspace
                  'bg':0,
                  '0-10': 1,
                  '10-20': 2,
                  '20-30': 3,
                  '30+': 4,
                  '35+': 4,
                  # 'bulk': 4,
                  # 'bluish_layers': 4,
                  # 'more_bluish_layers': 4,
                  'dirt': 4,
              }


# The LOOP
i = 0
for image in tqdm(mono_graphene_iter):
    i+=1
    if i > 400:
        break

    try:
        segmenter = Segmenter(image['image'],
                        material=graphene,
                        size = image['image'].shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )

        segmenter.shift_multiplier = 0
        segmenter.max_area = 100000
        segmenter.go()
        pretty = segmenter.prettify()
        numbered = segmenter.number()
        # tf.keras.utils.save_img('../../../../Volumes/One_Touch/2D_World/monolayer_Graphene_Labeled/Inputs/'+str(i)+'.jpg', image['image'])
        # tf.keras.utils.save_img('../../../../Volumes/One_Touch/2D_World/monolayer_Graphene_Labeled/Colored_Masks/'+str(i)+'.jpg', pretty)
        # tf.keras.utils.save_img('../../../../Volumes/One_Touch/2D_World/monolayer_Graphene_Labeled/AI_Inputs/'+str(i)+'.jpg', tf.expand_dims(numbered, axis=-1))

        tf.keras.utils.save_img('../monolayerGraphene/monolayer_Graphene_Labeled/Inputs/'+str(i)+'.jpg', image['image'])
        tf.keras.utils.save_img('../monolayerGraphene/monolayer_Graphene_Labeled/Colored_Masks/'+str(i)+'.jpg', pretty)
        tf.keras.utils.save_img('../monolayerGraphene/monolayer_Graphene_Labeled/AI_Inputs/'+str(i)+'.jpg', tf.expand_dims(numbered, axis=-1))
    except:
        pass