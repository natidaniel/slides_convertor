from multiprocessing import Pool
import multiprocessing as multi
from PIL import Image
import traceback
import argparse
import os
from datetime import datetime
from openslide import OpenSlide
import cv2
import numpy as np
import matplotlib

BG_PERCENT_TH = 80
H_EXTREME_PERCENT_TH = 65
BW_H_TH = 0.8
BW_L_TH = 0.05
H_H_TH = 330
H_L_TH = 250

def convert(data):
    UNIT_X, UNIT_Y = 1200, 1200
    try:
        fname, input_dir, output_dir = data
        save_name = fname.split(".")[0]
        print("Processing : %s"%fname)
        os_obj = OpenSlide(input_dir+"/"+fname)
        w, h = os_obj.dimensions
        w_rep, h_rep = int(w/UNIT_X)+1, int(h/UNIT_Y)+1
        w_end, h_end = w%UNIT_X, h%UNIT_Y
        w_size, h_size = UNIT_X, UNIT_Y
        w_start, h_start = 0, 0
        for i in range(h_rep):
            if i == h_rep-1:
                break
            for j in range(w_rep):
                print(i, " / ", h_rep, "  :  ", j, " / ", w_rep)
                if j != w_rep-1:
                  img = os_obj.read_region((w_start,h_start), 0, (w_size,h_size))
                  img = img.convert("RGB")
                                  
                  # load and create masks
                  imBW = cv2.cvtColor(np.float32(img), cv2.COLOR_BGR2GRAY)
                  imBW = imBW / 255
                  imBlackMask = ((imBW < BW_L_TH).astype(int)) > 0
                  imMask = ((imBW > BW_H_TH).astype(int)) > 0
                  kernel = np.ones((2, 2), np.uint8)
                  imMask = cv2.morphologyEx(np.float32(imMask), cv2.MORPH_OPEN, kernel)
                  
                  #rgb masks
                  npimage = np.asarray(img, dtype=np.float32) / 255
                  #hsvimage = matplotlib.colors.rgb_to_hsv(npimage)
                  hsvimage = cv2.cvtColor(npimage, cv2.COLOR_BGR2HSV)
                  h = hsvimage[:,:,0]
                  HMask = ( ( ( (h > H_H_TH).astype(int) + (h < H_L_TH).astype(int) ) > 0 ).astype(int) * (imBW < BW_H_TH).astype(int) ) > 0
                  # filter or activate mask
                  numPixels = imMask.shape[0] * imMask.shape[1]
                  
                  numWhitePixels = sum(sum(imMask.astype(int)))
                  numBlackPixels = sum(sum(imBlackMask.astype(int)))
                  numHExtPixels = sum(sum(HMask.astype(int)))
                            
                  bgPercent =  ((float(numWhitePixels) + float(numBlackPixels))/ float(numPixels)) * 100.0 
                  hExtPercent = bgPercent
                  if numWhitePixels != numPixels:
                    hExtPercent = (float(numHExtPixels) / float(numPixels - numWhitePixels)) * 100.0    
                  
                  filename_good = output_dir + "/good/" + save_name + "_" + str(i) + "_" + str(j) + ".jpg"
                  #filename_good = output_dir + "/good/" + save_name + "_" + str(i) + "_" + str(j) + "_bg:" +str(format(bgPercent, '.2f')) + "_H:" +str(format(hExtPercent, '.2f')) + ".jpg"
                  filename_bad = output_dir + "/bad/" + save_name + "_" + str(i) + "_" + str(j) + "_bg:" +str(format(bgPercent, '.2f')) + "_H:" +str(format(hExtPercent, '.2f')) + ".jpg"
                  if ( bgPercent < float(BG_PERCENT_TH)) and (hExtPercent < float(H_EXTREME_PERCENT_TH)):
                      img.save(filename_good)
                      print(filename_good, "was saved. ##################R:", hExtPercent, " W:", bgPercent )
                  else:
                      img.save(filename_bad)
                      print(filename_bad, "was filtered. R:", hExtPercent, " W:", bgPercent  )
  
                  w_start += UNIT_X

            w_size = UNIT_X
            h_start += UNIT_Y
            w_start = 0

    except:
        print("Can't open image file : %s"%fname)
        traceback.print_exc()
    return    


def main():
    parser = argparse.ArgumentParser(description='This script is ...'
                                    , formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--input", "-i", default="./input",
                        help="Directory name where the input image is saved. default='./input'")
    parser.add_argument("--output", "-o", default="./output",
                        help="Directory name where the converted image is saved. default='./output'")
    parser.add_argument("--multi", "-m", type=int, default=2,
                        help="Number of CPU cores to use for conversion. default=2")

    args = parser.parse_args()
    print("------- Program Started -------")

    try:
        f_lst = sorted([f for f in os.listdir(args.input) if ".bif" in f])
        f_lst = [[f, args.input, args.output] for f in f_lst]
        p = Pool(args.multi)
        print("------- Convert Started -------", datetime.now())
        p.map(convert, f_lst)
        print("------- Convert Ended -------", datetime.now())
        p.close()
    except:
        traceback.print_exc()
    
    print("------- Program Ended -------")
    return


if __name__ == "__main__":
    main()
