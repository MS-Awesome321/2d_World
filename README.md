# Using Segmenter

``` python
from segmenter import Segmenter
from material import wte2, graphene
import tensorflow as tf
import numpy as np
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt
```

``` python
# Dictionaries telling the Segmenter how to color image after labelling

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    'trilayer': np.array([198,22,22])/255.0, # Red
    'fewlayer': np.array([255,165,0])/255.0, # Orange
    'manylayer': np.array([255,165,0])/255.0, # Orange
    'bluish_layers': np.array([255,165,0])/255.0, # Orange
    'bulk': np.array([152,7,235])/255.0, # Purple
    'dirt': np.array([255, 255, 0])/255.0, # Yellow
    'more_bluish_layers': np.array([255, 255, 0])/255.0, # Yellow
    'bg': np.array([0, 0, 0])/255.0, # Uncolored
}


# Inputs to future AI model (Currently focusing on Monolayer, Bilayer, and >Bilayer for Segmentation)
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
```

## WTe2

``` python
test_wte2_PIL = Image.open('test_images/wte2_28.jpg')
test_wte2 = np.array(test_wte2_PIL)
test_wte2_PIL
```

![](vertopal_8221410835314baa8dd3b841091fa638/6da5e599123665034eeeff5464a4aeb43da9b106.jpg)


``` python
segmenter = Segmenter(test_wte2,
                        material=wte2,
                        size = test_wte2.shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )

segmenter.go()
```

``` python
segmenter.prettify()
plt.imshow(segmenter.colored_masks)
```

![](vertopal_8221410835314baa8dd3b841091fa638/6f5a27e9ab444341efa4fa34174e2eb2678d87e5.png)

## Graphene

``` python
test_graphene_PIL = Image.open('test_images/graphene.jpg')
test_graphene = np.array(test_graphene_PIL)
test_graphene_PIL
```

![](vertopal_8221410835314baa8dd3b841091fa638/a185e9ce37515872897251d1d9b9016cd623b97b.jpg)

``` python
segmenter = Segmenter(test_graphene,
                        material=graphene,
                        size = test_graphene.shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )

segmenter.shift_multiplier = 0
segmenter.max_area = 100000
segmenter.go()
```

``` python
segmenter.prettify()
plt.imshow(segmenter.colored_masks)
```

![](vertopal_8221410835314baa8dd3b841091fa638/76a447a30b4b4b0b17d28b17a37768300d1f63d8.png)

### Convert to Training Data for a Neural Network

```python
segmenter.number()
plt.imshow(segmenter.numbered_masks)
plt.colorbar()
plt.show()
```

![](vertopal_8221410835314baa8dd3b841091fa638/ai_input.png)