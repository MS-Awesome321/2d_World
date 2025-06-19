import cv2

img = cv2.imread('test.jpeg', cv2.IMREAD_COLOR)
encoded = cv2.imencode('.jpg', img)[1]
print(encoded, type(encoded))
decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
print(decoded.shape, decoded.dtype)

with open("my_array.pickle", "rb") as f:
    import pickle
    arr = pickle.load(f)
    print(arr, type(arr))
    print(cv2.imdecode(arr, cv2.IMREAD_COLOR))