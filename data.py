import datasets
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def preprocess(img):
  img = img.resize((img.size[0]//8, img.size[1]//8), Image.Resampling.NEAREST)
  img_array = np.asarray(img)/255.0
  img_array = img_array.astype('float32')
  max = np.max(img_array)
  min = np.min(img_array)
  img_array = (img_array - min)/(max-min)
  return img_array

def standardize(img):
  img['image'] = preprocess(img['image'])
  return img

# wte2_ds = datasets.load_dataset('../../../../Volumes/One_Touch/2D_World/WTe2_M100', streaming=True)
# wte2_ds = wte2_ds['train'].map(standardize)
# wte2_iter = iter(wte2_ds)

# graphene_ds = datasets.load_dataset('../../../../Volumes/One_Touch/2D_World/Graphene_M100', streaming=True)
# graphene_ds = graphene_ds['train'].map(standardize)
# graphene_iter = iter(graphene_ds)

mono_graphene_ds = datasets.load_dataset('../monolayerGraphene/monolayer_Graphene', streaming=True)
mono_graphene_ds = mono_graphene_ds['train'].map(standardize)
mono_graphene_iter = iter(mono_graphene_ds)

# hBN_ds = datasets.load_dataset('../../../../Volumes/One_Touch/2D_World/hBN_M100', streaming=True)
# hBN_ds = hBN_ds['train'].map(standardize)
# hBN_iter = iter(hBN_ds)