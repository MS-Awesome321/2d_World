import subprocess
import cv2
import numpy as np

# ImageFile.LOAD_TRUNCATED_IMAGES = True

gphoto2 = subprocess.Popen(['gphoto2', '--capture-movie', '--stdout'], stdout=subprocess.PIPE)

buffer = b''

try:
    while True:
        buffer += gphoto2.stdout.read(2**16)

        start = buffer.find(b'\xff\xd8')
        end = buffer.find(b'\xff\xd9')

        if start != -1 and end != -1 and end > start:
            jpg = buffer[start:end+2]
            print(len(jpg), start, end)
            buffer = buffer[end+2:]

            img = np.frombuffer(jpg, dtype=np.uint8)
            print(img)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            print(img)

            # cv2.imshow('Camera Feed', img)

        if cv2.waitKey(1) == 27:
            break
except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
gphoto2.terminate()