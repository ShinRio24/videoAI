from skimage.metrics import structural_similarity as ssim
import cv2
import time



st= time.time()

for x in range(15*15):
  # Load images in grayscale
  img1 = cv2.imread('media/refImgs/img0_7.jpg', cv2.IMREAD_GRAYSCALE)
  img2 = cv2.imread('media/refImgs/img0_7.jpg', cv2.IMREAD_GRAYSCALE)

  # Resize to the same size if needed
  img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

  # Compute SSIM
  score, diff = ssim(img1, img2, full=True)
 # print(f"SSIM: {score}")  # 1.0 = identical, closer to 0 = less similar

print("Time taken:", time.time() - st)