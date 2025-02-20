---
jupyter:
  kernelspec:
    display_name: 2d_World
    language: python
    name: python3
  language_info:
    codemirror_mode:
      name: ipython
      version: 3
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython3
    version: 3.12.8
  nbformat: 4
  nbformat_minor: 2
---

::: {.cell .code execution_count="8"}
``` python
from segmenter import Segmenter
from material import wte2, graphene
import tensorflow as tf
import numpy as np
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt
```
:::

::: {.cell .code execution_count="23"}
``` python
test_wte2_PIL = Image.open('test_images/wte2_28.jpg')
test_wte2 = np.array(test_wte2_PIL)
test_wte2_PIL
```

::: {.output .execute_result execution_count="23"}
![](vertopal_57756a3b6d594cd5ae404025e2b3c632/6da5e599123665034eeeff5464a4aeb43da9b106.jpg)
:::
:::

::: {.cell .code}
``` python
# Dictionaries telling the Segmenter how to color image after labelling

colors_by_layer = {
    'monolayer': np.array([0,163,255])/255.0, # Blue
    'bilayer': np.array([29,255,0])/255.0, # Green
    # 'trilayer': np.array([198,22,22])/255.0, # Red
    'trilayer': np.array([255,165,0])/255.0, # Orange
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
:::

::: {.cell .code execution_count="32"}
``` python
segmenter = Segmenter(test_wte2,
                        material=wte2,
                        size = test_wte2.shape[:2],
                        mask_colors=colors_by_layer,
                        magnification=100,
                        mask_numbers=number_by_layer
                    )
segmenter.shift_multiplier = 96
segmenter.go()
```
:::

::: {.cell .code execution_count="33"}
``` python
segmenter.prettify()
plt.imshow(segmenter.colored_masks)
```

::: {.output .execute_result execution_count="33"}
    <matplotlib.image.AxesImage at 0x177ef7a70>
:::

::: {.output .display_data}
![](vertopal_57756a3b6d594cd5ae404025e2b3c632/4cff6bdd9789f7b10ed2bcf51af89874c8f0311a.png)
:::
:::
