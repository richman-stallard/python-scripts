import numpy as np
from scipy.ndimage import imread
from scipy.misc import imsave
import sys
import os
import random

def check_img_list_dimensions(imgs):
    Result = len(np.shape(imgs[0])) == 3 # dimensions
    Result = Result and np.shape(imgs[0][2]) == 3 # channels
    for img in imgs[1:]:
        Result = Result and np.shape(img) == np.shape(imgs[0]) # shape
    return Result

def glitchify(imgs):
    '''
    Combines the R channel of imgs[0], the G channel of imgs[1]
    and the B channel of imgs[2].
    '''
    assert len(imgs) == 3 # 3 images
    assert check_img_list_dimensions
        
    Result = np.zeros(np.shape(imgs[0])) # default
    
    # glitchification
    for ch in range(3):
        Result[:, :, ch] = imgs[ch][:, :, ch]
        
    return Result

def glitchify_random(imgs, blocksize):
    '''
    Takes a series of images and combines them randomly, i.e. for each block
    takes a random channel at that pixel from a random image. Block size is
    determined by command line arg.
    '''
    assert len(imgs) > 1 # at least 2 images
    assert check_img_list_dimensions
        
    Result = np.zeros(np.shape(imgs[0])) # default
    
    # glitchification
    (Y, X, Channels) = np.shape(Result)
    numblocksx = X/blocksize + (0 if X % blocksize == 0 else 1)
    numblocksy = Y/blocksize + (0 if Y % blocksize == 0 else 1)
    for ch in range(Channels):
        for blockx in range(numblocksx):
            for blocky in range(numblocksy):
                Result[
                    blocky*blocksize:(blocky+1)*blocksize,
                    blockx*blocksize:(blockx+1)*blocksize,
                    ch
                ] = imgs[random.randint(0, len(imgs)-1)][
                    blocky*blocksize:(blocky+1)*blocksize,
                    blockx*blocksize:(blockx+1)*blocksize,
                    random.randint(0, Channels-1)
                ]
    
    return Result

C_HELPTEXT = [
    "glitchify.py -h",
    "glitchify.py [-r BLOCKSIZE] [-(y|n)] OUTFILE {INFILES}",
    "",
    "ARGS:",
    "  -h  Print this help and exit.",
    "",
    "  -r  Use randomized combination of N images. Block edge length is",
    "      determined by BLOCKSIZE.",
    "",
    "  -y  Overwrite existing OUTFILE without querying.",
    "  -n  Do not overwrite existing OUTFILE, do not query. Overrides -y.",
    "",
    "BLOCKSIZE:",
    "  Must be an integer greater than or equal to 1 and must immediately",
    "    follow the -r option. The randomized algorithm takes a random",
    "    channel from a random image in INFILES for each block. Blocks are",
    "    BLOCKSIZE pixels wide and high.",
    "    A BLOCKSIZE of 1 will lead to pixel-wise randomization.",
    "    Small values increase calculation time dramatically!",
    "",
    "OUTFILE:",
    "  Path to file that will contain the result. Will be created if it",
    "    does not exist. If the file exists, use of -y or -n dictates whether",
    "    it will be overwritten. Otherwise, user is queried.",
    "",
    "INFILES:",
    "  All images must have the same dimensions.",
    "  The default algorithm only uses the first three images. It combines the",
    "    R channel of img1, the G channel of img2 and the B channel of img3.",
    "  The randomized algorithm uses a random channel from a random image for",
    "    each block."
]

def main(argv):
    # Variables
    idx = 0
    vBlockSize = 1
    vFile = None
    vFileList = []
    vGlitchified = np.zeros((20, 20, 3))
    vImgList = []
    vImgDimensions = []
    vImg = np.zeros((20, 20, 3))
    vLine = ""
    vOverwriteExistingOutfile = False
    vOutFilePath = ""
    vQueryOverwriteExistingOutfile = True
    vUseRandomAlgorithm = False
    
    # Arg handling
    if "-h" in argv:
        for vLine in C_HELPTEXT:
            print vLine
        return 0
    if "-r" in argv:
        vUseRandomAlgorithm = True
        idx = 0
        while not argv[idx] == "-r":
            idx = idx + 1
        vBlockSize = int(argv[idx + 1])
        argv = argv[:idx+1] + argv[idx+2:] # remove BLOCKSIZE
        while "-r" in argv:
            argv.remove("-r")
    if "-y" in argv:
        vOverwriteExistingOutfile = True
        vQueryOverwriteExistingOutfile = False
        while "-y" in argv:
            argv.remove("-y")
    if "-n" in argv:
        vOverwriteExistingOutfile = False
        vQueryOverwriteExistingOutfile = False
        while "-n" in argv:
            argv.remove("-n")
    assert (len(argv) > (3 if vUseRandomAlgorithm else 4)), \
        "Too few arguments!"
    vOutFilePath = argv[1]
    vFileList = argv[2:] if vUseRandomAlgorithm else argv[2:5]
    
    # Overwrite?
    if vQueryOverwriteExistingOutfile and os.path.exists(vOutFilePath):
        vLine = raw_input("Overwrite existing output File " + vOutFilePath \
            + "? [y|N] ")
        vOverwriteExistingOutfile = len(vLine) > 0 and vLine[0] == 'y'
    if os.path.exists(vOutFilePath) and not vOverwriteExistingOutfile:
        print vOutFilePath, "exists and will not be overwritten. Exiting..."
        return 0
        
    # Loading images
    for vLine in vFileList:
        try:
            vFile = open(vLine, 'r')
            vImgList.append(imread(vFile, mode="RGB"))
        except IOError as e:
            raise IOError("Could not access file", vLine)
        finally:
            vFile.close()
            
    # Checking image dimensions
    vImgDimensions = np.size(vImgList[0])
    for vImg in vImgList[1:]:
        assert np.size(vImg) == vImgDimensions, \
            "All images must have the same dimensions!"
    
    # Glitchification, storing result
    vGlitchified = \
        glitchify_random(vImgList, vBlockSize) if vUseRandomAlgorithm \
        else glitchify(vImgList)
    print "Glitchification success! Storing in", vOutFilePath
    try:
        vFile = open(vOutFilePath, 'w')
        imsave(vFile, vGlitchified)
    except IOError as e:
        raise IOError("Could not access file", vOutFilePath)
    finally:
        vFile.close()
        
    return 0

if __name__ == "__main__":
    main(sys.argv)
