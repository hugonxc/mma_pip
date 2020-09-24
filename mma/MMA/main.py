# main.py

"""
The program "MMA - Musical Midi Accompaniment" and the associated
modules distributed with it are protected by copyright.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

Bob van der Poel <bob@mellowood.ca>

"""

import os

import mma.MMA.midi
import mma.MMA.midifuncs
import mma.MMA.parse
import mma.MMA.file
import mma.MMA.options
import mma.MMA.auto
import mma.MMA.docs
import mma.MMA.tempo
import mma.MMA.debug
from  mma.MMA.safe_eval import safeEnv

from mma.MMA import gbl
from mma.MMA.common import *
from mma.MMA.lyric import lyric

import mma.MMA.paths

cmdSMF = None

########################################
########################################

# This is the program mainline. It is called/executed
# exactly once from a call in the stub program mma.MMA.py.

# for some reason, someone might want a different encoding
# real easy to set it from env at startup
m = safeEnv( 'MMA_ENCODING' )
if m:    # don't set to empty ... will crash
    gbl.encoding = m

# MMA prints errors/warning/debug to stdout
# this will redirect to a file
gbl.logFile = safeEnv('MMA_LOGFILE')

mma.MMA.paths.init()   # initialize the lib/include paths


# Get our command line stuff

mma.MMA.options.opts()

#  LibPath and IncPath are set before option parsing, but
#  debug setting wasn't. So we need to do the debug for this now
if mma.MMA.debug.debug:
    dPrint("Initialization has set LibPath set to %s" % mma.MMA.paths.libPath)
    dPrint("Initialization has set IncPath set to %s" % mma.MMA.paths.incPath)

#######################################
# Set up initial meta track stuff. Track 0 == meta

m = gbl.mtrks[0] = mma.MMA.midi.Mtrk(0)

if gbl.infile:
    if gbl.infile != 1:
        fileName = mma.MMA.file.locFile(gbl.infile, None)
        if fileName and not gbl.noCredit:
            m.addTrkName(0, "%s" % fileName.rstrip(".mma"))
            m.addText(0, "Created by mma.MMA. Input filename: %s" % fileName)


m.addTempo(0, gbl.tempo)      # most user files will override this
mma.MMA.tempo.setTime(['4/4'])    # and this. IMPORTANT! Sets default chordTabs[]
   
# Read RC files
mma.MMA.paths.readRC()


################################################
# Update the library database file(s) (-g option)
# Note: This needs to be here, after reading of RC files

if gbl.makeGrvDefs:
    if gbl.infile:
        error("No filename is permitted with the -g option")
    mma.MMA.auto.libUpdate()                # update and EXIT


################################
# We need an input file for anything after this point.

if not gbl.infile:
    mma.MMA.options.usage("No input filename specified.")

################################
# Just extract docs (-Dxh, etc) to stdout.

if gbl.createDocs:
    if gbl.createDocs == 4:
        mma.MMA.docs.htmlGraph(gbl.infile)
    else:
        f = mma.MMA.file.locFile(gbl.infile, None)
        if not f:
            error("File '%s' not found" % gbl.infile)
        mma.MMA.parse.parseFile(f)
        mma.MMA.docs.docDump()
    sys.exit(0)


#########################################################
# This cmdline option overrides the setting in RC files

if mma.MMA.options.cmdSMF is not None:
    gbl.lineno = -1
    mma.MMA.midifuncs.setMidiFileType(['SMF=%s' % mma.MMA.options.cmdSMF])

######################################
# Create the output filename

if not mma.MMA.debug.noOutput:
    mma.MMA.paths.createOutfileName(".mid")


################################################
# Read/process files....

# First the mmastart files
mma.MMA.paths.dommaStart()

# The song file specified on the command line

if gbl.infile == 1:  # use stdin, set filename to 1
    f = 1
else:
    f = mma.MMA.file.locFile(gbl.infile, None)

    if not f:
        gbl.lineno = -1
        error("Input file '%s' not found" % gbl.infile)

mma.MMA.parse.parseFile(f)

# Finally, the mmaend files
mma.MMA.paths.dommaEnd() 

#################################################
# Just display the channel assignments (-c) and exit...

if mma.MMA.debug.chshow:
    msg = ["\nFile '%s' parsed, but no MIDI file produced!" % gbl.infile]
    msg.append("\nTracks allocated:\n")
    k = list(gbl.tnames.keys())
    k.sort()
    max = 0
    for a in k + gbl.deletedTracks:
        if len(a) > max:
            max = len(a)
    max += 1
    wrap = 0
    for a in k:
        wrap += max
        if wrap > 60:
            wrap = max
            msg.append('\n')
        msg.append(" %-*s" % (max, a))
    msg.append('\n')
    print(' '.join(msg))
    
    if gbl.deletedTracks:
        msg = ["Deleted Tracks:\n"]
        wrap = 0
        for a in gbl.deletedTracks:
            wrap += max
            if wrap > 60:
                wrap = max
                msg.append('\n')
            msg.append(" %-*s" % (max, a),)
        msg.append('\n')
        print(' '.join(msg))
        
    msg=["Channel assignments:\n"]
    for c, n in sorted(gbl.midiAssigns.items()):
        if n:
            wrap = 3
            msg.append(" %2s" % c)
            for nn in n:
                wrap += max
                if wrap > 63:
                    msg.append('\n    ')
                    wrap = max+3
                msg.append(" %-*s" % (max, nn))
            msg.append('\n')
    print(' '.join(msg))

    sys.exit(0)


####################################
# Dry run, no output

if mma.MMA.debug.noOutput:
    gbl.lineno = -1
    warning("Input file parsed successfully. No midi file generated")
    sys.exit(0)


##############################
# Create the output (MIDI) file

gbl.lineno = -1    # disable line nums for error/warning


""" We fix the outPath now. This lets you set outpath in the song file.

    The filename "outfile" was created in paths, get a copy.

    It is either the input filename with '.mma' changed to '.mid' (or kar)
    OR if -f<FILE> was used then it's just <FILE>.

    If any of the following is true we skip inserting the outputpath into the
    filename:

        - if outfile starts with a '/'
        - if outPath was not set
        - if -f was used

    Next, the outPath is inserted into the filename. If outPath starts with
    a ".", "/" or "\ " then it is inserted at the start of the path;
    otherwise it is inserted before the filename portion.
"""

outfile = mma.MMA.paths.outfile

if (not outfile.startswith('/')) and gbl.outPath \
        and not gbl.outfile and not gbl.playFile:
    if gbl.outPath[0] in '.\\/':
        outfile = "%s/%s" % (gbl.outPath, outfile)
    else:
        head, tail = os.path.split(outfile)
        outfile = "%s/%s/%s" % (head, gbl.outPath, tail)

fileExist = os.path.exists(outfile)

""" Check if any pending midi events are still around. Mostly
    this will be a DRUM event which was assigned to the 'DRUM'
    track, but no DRUM track was used, just DRUM-xx tracks used.
"""

for n in gbl.tnames.values():
    if n.channel:
        n.clearPending()
        n.doMidiClear()
        n.doChannelReset()
        if n.riff:
            warning("%s has pending Riff(s)" % n.name)

""" Check all the tracks and find total number used. When
    initializing each track (class) we made an initial entry
    in the track at offset 0 for the track name, etc. So, if the
    track only has one entry we can safely skip the entire track.
"""

trackCount = 1    # account for meta track

for n in sorted(gbl.mtrks.keys())[1:]:     # check all but 0 (meta)
    if len(gbl.mtrks[n].miditrk) > 1:
        trackCount += 1

if gbl.printProcessed:
    import mma.MMA.rangeify
    print ("Bars processed: %s" % mma.MMA.rangeify.rangeify(gbl.barLabels))

if trackCount == 1:  # only meta track
    if fileExist:
        print("\n")
    print("No data created. Did you remember to set a groove/sequence?")
    if fileExist:
        print("Existing file '%s' has not been modified." % outfile)
    sys.exit(1)

lyric.leftovers()

if fileExist:
    msg = "Overwriting existing"
else:
    msg = "Creating new"

print("%s midi file (%s bars, %.2f min / %d:%02d m:s): '%s'" %
    (msg, gbl.barNum, gbl.totTime, gbl.totTime, (gbl.totTime%1)*60, outfile))

# Insert the estimated play time in seconds into a comment line.
# A player program can search for this and display it. The value
# will be terminated by a null which should be easy enuf to search for.

gbl.mtrks[0].addText(0, "DURATION: %d" % (gbl.totTime*60) )

try:
    out = open(outfile, 'wb')
except IOError:
    error("Can't open file '%s' for writing" % outfile)

mma.MMA.midi.writeTracks(out)
out.close()

if gbl.playFile:
    import mma.MMA.player
    mma.MMA.player.playMidi(outfile)

if mma.MMA.debug.debug:
    dPrint("Completed processing file '%s'." % outfile)

