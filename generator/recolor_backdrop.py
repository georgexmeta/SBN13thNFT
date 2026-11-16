import cv2, numpy as np, sys
def recolor(src, dst, hexcol):
    img = cv2.imread(src); h, w = img.shape[:2]
    small = cv2.resize(img, (512, 512)); mask = np.zeros((512, 512), np.uint8)
    rect = (40, 25, 432, 487)   # figure sits centred; edges are backdrop
    bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
    cv2.grabCut(small, mask, rect, bg, fg, 6, cv2.GC_INIT_WITH_RECT)
    m = np.where((mask == 1) | (mask == 3), 1.0, 0.0).astype(np.float32)
    m = cv2.resize(m, (w, h)); m = cv2.GaussianBlur(m, (0, 0), 2.5)[..., None]
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0]; bgL = L[m[..., 0] < 0.5]; meanL = bgL.mean()
    t = np.uint8([[[int(hexcol[4:6], 16), int(hexcol[2:4], 16), int(hexcol[0:2], 16)]]])
    tl = cv2.cvtColor(t, cv2.COLOR_BGR2LAB).astype(np.float32)[0, 0]
    new = np.empty_like(lab)
    new[..., 0] = np.clip(tl[0] + (L - meanL) * 0.9, 0, 255); new[..., 1] = tl[1]; new[..., 2] = tl[2]
    newbgr = cv2.cvtColor(new.astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    out = img.astype(np.float32) * m + newbgr * (1 - m)
    cv2.imwrite(dst, out.astype(np.uint8))
if __name__ == "__main__":
    recolor(sys.argv[1], sys.argv[2], sys.argv[3])
