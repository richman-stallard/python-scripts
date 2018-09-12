import numpy as np
from scipy.ndimage import imread
from scipy.misc import imsave
import sys
from os.path import exists
from random import randint

def CheckImageListDimensions(aImages):
    vImage = aImages[0]
    Result = False
    
    Result = len(np.shape(aImages[0])) == 3 # dimensions
    Result = Result and np.shape(aImages[0])[2] == 3 # channels
    for vImage in aImages[1:]:
        Result = Result and np.shape(vImage) == np.shape(aImages[0]) # shape
    return Result

def glitchify(aImages):
    '''
    Combines the R channel of aImages[0], the G channel of aImages[1]
    and the B channel of aImages[2].
    '''
    assert len(aImages) == 3 # 3 images
    assert CheckImageListDimensions(aImages)
        
    chidx = 0
    Result = np.zeros(np.shape(aImages[0])) # default
    
    # glitchification
    for chidx in range(np.shape(Result)[2]):
        Result[:, :, chidx] = aImages[chidx][:, :, chidx]
        
    return Result

def glitchify_random(aImages, aBlocksize):
    '''
    Takes a series of images and combines them randomly, i.e. for each block
    takes a random channel at that pixel from a random image. Block size is
    determined by command line arg.
    '''
    assert len(aImages) > 1 # at least 2 images
    assert CheckImageListDimensions(aImages)
        
    chidx = 0
    vChannels = 0
    vImagesX = 0
    vImagesY = 0
    vNumBlocksY = 0
    vNumBlocksX = 0
    xidx = 0
    yidx = 0
    Result = np.zeros(np.shape(aImages[0])) # default
    
    # glitchification
    (vImagesY, vImagesX, vChannels) = np.shape(Result)
    vNumBlocksX = vImagesX/aBlocksize + (0 if vImagesX % aBlocksize == 0 else 1)
    vNumBlocksY = vImagesY/aBlocksize + (0 if vImagesY % aBlocksize == 0 else 1)
    for chidx in range(vChannels):
        for xidx in range(vNumBlocksX):
            for yidx in range(vNumBlocksY):
                Result[
                    yidx*aBlocksize:(yidx+1)*aBlocksize,
                    xidx*aBlocksize:(xidx+1)*aBlocksize,
                    chidx
                ] = aImages[randint(0, len(aImages)-1)][
                    yidx*aBlocksize:(yidx+1)*aBlocksize,
                    xidx*aBlocksize:(xidx+1)*aBlocksize,
                    randint(0, vChannels-1)
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
    if vQueryOverwriteExistingOutfile and exists(vOutFilePath):
        vLine = raw_input("Overwrite existing output File " + vOutFilePath \
            + "? [y|N] ")
        vOverwriteExistingOutfile = len(vLine) > 0 and vLine[0] == 'y'
    if exists(vOutFilePath) and not vOverwriteExistingOutfile:
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
