import subprocess
import cv2
import numpy as np
import pickle

gphoto2 = subprocess.Popen(['gphoto2', '--capture-movie', '--stdout'], stdout=subprocess.PIPE)

buffer = b''

try:
    for i in range(3):
        buffer += gphoto2.stdout.read(2**18)

        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')

        if start != -1 and end != -1 and end > start:
            jpg = buffer[start:end+2]
            buffer = buffer[end+2:]  # Remove processed bytes

            np_img = np.frombuffer(jpg, dtype=np.uint8)
            print(np_img)
            print(np_img.shape)
            print(np_img.dtype)
            with open('my_array.pickle', 'wb') as f:
                # Pickle the array and write it to the file
                pickle.dump(np_img, f)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            if img is not None and img.shape == (640, 960, 3):
                cv2.imshow('Camera Demo', img)

        if cv2.waitKey(1) == 27:  # ESC to exit
            break
except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
gphoto2.terminate()