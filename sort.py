import os
import shutil
from tqdm import tqdm


src_folder = "../../../../Volumes/One_Touch/2D_World/hBN-new/"
dst_folder = "../../../../Volumes/One_Touch/2D_World/hBN_M100/"
for filename in tqdm(os.listdir(src_folder)):
    if "M100" in filename:
        shutil.move(src_folder+filename, dst_folder+filename)