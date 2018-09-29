#!/usr/bin/python2
#
# This program splits a sound file according to information contained in a track
# file.
#
# Syntax: split.py SOUNDFILE TRACKFILE
#
# Dependencies: Python 2, ffmpeg plus the necessary codecs.
#
# The track file should contain the timecode of the start of each track followed
# by a space, and then the title of the track. It is assumed that tracks follow
# each other, that the last track goes to the end of the sound file and that the
# track titles do not contain newline characters -- those are the seperators for
# tracks. All time codes must have the same format (either MM:SS or HH:MM:SS).
# Time code elements are seperated by columns. Furthermore, it is assumed that
# the sound file is to be split into fewer than 100 tracks.
# An example track file can be found at the end of this script.
#
# The new files are stored in the current working directory.

import subprocess
import sys
import os

def main(argv):
    AUDIOCODEC = "libmp3lame" # default = libmp3lame
    AUDIOBITRATE = "320k" # default = 320k

    if "-h" in argv or "-?" in argv:
        print "split.py SOUNDFILE TRACKFILE"
        return

    soundfile = argv[1]
    trackfile = argv[2]

    # Create track list from track file contents.
    fp = open(trackfile, 'r')
    filecontents = fp.readlines()
    fp.close()
    tracklist = []
    for track in filecontents:
        track = track.replace('\n', '')
        tracklist.append(track.split(' ', 1))
        tracklist[-1][0] = tracklist[-1][0].split(':')

    # Create conversion commands.
    cmds = []
    for idx in range(len(tracklist) - 1):
        tracklength = 0
        timecode = "0"
        if len(tracklist[idx][0]) == 3:
            # Time code format is assumed to be HH:MM:SS.
            tracklength = (
                60 * 60 * ( # hours
                    int(tracklist[idx+1][0][0])
                    - int(tracklist[idx][0][0])
                )
                + 60 * ( # minutes
                    int(tracklist[idx+1][0][1])
                    - int(tracklist[idx][0][1])
                )
                + ( # seconds
                    int(tracklist[idx+1][0][2])
                    - int(tracklist[idx][0][2])
                )
            )
            timecode = "%s:%s:%s" % (
                tracklist[idx][0][0],
                tracklist[idx][0][1],
                tracklist[idx][0][2]
            )
        elif len(tracklist[idx][0]) == 2:
            # Time code format is assumed to be MM:SS.
            tracklength = (
                + 60 * ( # minutes
                    int(tracklist[idx+1][0][0])
                    - int(tracklist[idx][0][0])
                )
                + ( # seconds
                    int(tracklist[idx+1][0][1])
                    - int(tracklist[idx][0][1])
                )
            )
            timecode = "%s:%s" % (
                tracklist[idx][0][0],
                tracklist[idx][0][1]
            )
        else:
            raise Exception("Invalid timecode!")
        outfilename = "%02d - %s.mp3" % (
            idx + 1,
            tracklist[idx][1]
        )
        cmd = "ffmpeg -ss %s -i \"%s\" -t %d -vn -sn -c:a %s -b:a %s \"%s\"" % (
            timecode,
            soundfile,
            tracklength,
            AUDIOCODEC,
            AUDIOBITRATE,
            outfilename
        )
        cmds.append(cmd)

    # ... and the last track.
    if len(tracklist[-1][0]) == 3:
        timecode = "%s:%s:%s" % (
            tracklist[-1][0][0],
            tracklist[-1][0][1],
            tracklist[-1][0][2]
        )
    elif len(tracklist[-1][0]) == 2:
        timecode = "%s:%s" % (
            tracklist[-1][0][0],
            tracklist[-1][0][1]
        )
    else:
        raise Exception("Invalid timecode!")
    outfilename = "%02d - %s.mp3" % (
        len(tracklist),
        tracklist[-1][1]
    )
    cmd = "ffmpeg -ss %s -i \"%s\" -vn -sn -c:a %s -b:a %s \"%s\"" % (
        timecode,
        soundfile,
        AUDIOCODEC,
        AUDIOBITRATE,
        outfilename
    )
    cmds.append(cmd)

    # Start converting.
    for cmd in cmds:
        cmd = "cd \"%s\" && %s" % (
            os.getcwd(),
            cmd
        )
        try:
            subprocess.call(cmd, shell=True)
        except OSError as E:
            print E
            print "Failed command:"
            print cmd

if __name__ == "__main__":
    main(sys.argv)

# Example track file:
#
# 00:00 Mister Sandman
# 02:18 Jerry's Breakdown
# 04:29 Canned Heat
# 07:05 The Nashville Jump
# 09:36 Big Foot
# 11:20 Freight Train
# 13:23 Ay Ay Ay
# 15:50 Waiting For Susie B.
# 19:06 A Little Mark Musik
# 22:16 Jam Man
# 25:36 I Still Write Your Name In The Snow
# 28:40 Pu Uana Hulu
# 32:41 Happy Again
# 35:33 Sweet Alla Lee
# 38:27 Maybelle
# 41:38 Mr. Bo Jangles
# 44:45 cheek To Cheek
# 48:01 You Do Something To Me
# 50:57 Ave Maria
# 54:21 Mystery Train
