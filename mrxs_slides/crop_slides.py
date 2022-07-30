#!/usr/bin/env python

from ctypes import *
# path to your openslide bin folder
import os
os.environ['PATH'] = "openslide\\bin\\" + ";" + os.environ['PATH']
cdll.LoadLibrary('openslide\\bin\\libopenslide-0.dll')

from multiprocessing import Pool
import multiprocessing as mp
from PIL import Image
import traceback
import argparse
import os
from datetime import datetime
from openslide import OpenSlide
import cv2
import numpy as np
import sys

BG_PERCENT_TH = 95 # won't filter
H_EXTREME_PERCENT_TH = 85 # won't filter
BW_H_TH = 0.8
BW_L_TH = 0.1
H_H_TH = 330
H_L_TH = 250
    
def convert(data, size, row):
    UNIT_X, UNIT_Y = int(size), int(size)
    try:
        fname, input_dir, output_dir = data
        save_name = fname.split(".")[0]
        print("Processing : %s"%fname)
        os_obj = OpenSlide(input_dir+"/"+fname)
        w, h = os_obj.dimensions      
        
        w_rep, h_rep = int(w/UNIT_X)+1, int(h/UNIT_Y)+1
        w_end, h_end = w%UNIT_X, h%UNIT_Y
        w_size, h_size = UNIT_X, UNIT_Y
        w_start, h_start = 0, row * UNIT_Y
        for i in range(row, h_rep):
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

                    # filter or activate mask
                    numPixels = imMask.shape[0] * imMask.shape[1]

                    numWhitePixels = sum(sum(imMask.astype(int)))
                    numBlackPixels = sum(sum(imBlackMask.astype(int)))

                    bgPercent =  ((float(numWhitePixels) + float(numBlackPixels))/ float(numPixels)) * 100.0   

                    filename_good = os.path.join(output_dir, "good", save_name + "_" + str(i) + "_" + str(j) + ".png")
                    filename_bad = os.path.join(output_dir, "bad", save_name + "_" + str(i) + "_" + str(j) + "_bg:" +str(format(bgPercent, '.2f')) + ".png")
                    if ( bgPercent < float(BG_PERCENT_TH)):
                        img.save(filename_good)
                    else:
                        img.save(filename_bad)

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
    parser.add_argument("--size", "-s", default=1024,
                        help="Size of each patch. default=1024")
    parser.add_argument("--row", "-r", default=0,
                        help="First row to start croping from. default=0")

    args = parser.parse_args()
    print("------- Program Started -------")
    try:
        os.mkdir(os.path.join(args.output, "good"))
        os.mkdir(os.path.join(args.output, "bad"))
    except:
        pass

    try:
        f_lst = sorted([f for f in os.listdir(args.input) if ".mrxs" in f])
        f_lst = [[f, args.input, args.output] for f in f_lst]
        
        print("------- Convert Started -------", datetime.now())
        for slide_file in f_lst:
            convert(slide_file, args.size, int(args.row))
        print("------- Convert Ended -------", datetime.now())

    except:
        traceback.print_exc()
    
    print("------- Program Ended -------")
    return


if __name__ == "__main__":
    main()

