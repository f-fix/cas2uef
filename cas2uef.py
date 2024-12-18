#!/usr/bin/env python

import struct

def cas2uef(infn, outfn):
   '''cas2uef converts MSX CAS into BBC Model B UEF that appears to
   work in BeebEm. Give it an input filename infn and an output
   filename outfn, and it will read "compact" MSX-style CAS from infn
   and write UEF to outfn, clobbering any existing file with that
   name. It likely only works with well-behaved tapes that do not do
   anything strange in terms of encoding.

   UEF format specs:
   https://mdfs.net/Docs/Comp/BBC/FileFormat/UEFSpecs.htm

   CAS format specs: (ignore all the bits about file types and alignment)
   https://www.msx.org/forum/semi-msx-talk/emulation/how-do-exactly-works-cas-format

   It is intended specifically for use with CAS from DumpListEditor,
   which are "compact", i.e. they never insert padding NUL bytes
   between blocks and do not try to align blocks with 8-byte
   boundaries.

   Thanks to this conversion, you can use the much larger and more
   fault-tolerant library of MSX CAS conversion tools to convert your
   waveforms into CAS, and than use this tool to convert the CAS into
   UEF. Note that the CAS this handles is the kind with block headers
   (as used by openMSX and other modern MSX emulators) and without
   extra padding/alignment at the start of blocks (this is what the
   emulators support, but many CAS generation tools put extra padding
   NUL bytes before the second and subsequent blocks to align them to
   8-byte boundaries in the file)

   The resulting UEF is of course the opposite of audio-archival
   quality: all the timings are default ones, since the CAS does not
   record any timing information. The Python script looks for file
   header-looking bytes at the beginnings of blocks and inserts extra
   pauses when it sees a file header transition. This is a heuristic!

   It also inserts a dummy block at the beginning of the UEF to work
   around a bug in old BBC OS versions, as is standard practice. The
   resulting UEF is version 0.10

   This technique also allows you to hash the CAS file for software
   version identification purposes, which is not really possible with
   UEF in general.

   '''

   cas=open(infn,"rb").read()
   cashdr=b"\x1f\xa6\xde\xba\xcc\x13\x7d\x74"
   chunks=cas.split(cashdr)
   uef_major,uef_minor=0,10
   uef_hdr=b"UEF File!\0"+struct.pack("BB",uef_minor,uef_major)
   uef=(
       uef_hdr
       +
       struct.pack("<HLHH",0x0111,4,2400,9600)
       +
       b"".join([
           struct.pack("<HL",0x0100,len(chunks[i]))
           +
           chunks[i]
           +
           (
               struct.pack("<HLH",0x0110,2,2400)
           if chunks[i].split(b"\0")[0] == (chunks[i+1:]+[b""])[0].split(b"\0")[0]
           else
               struct.pack("<HLH",0x0110,2,12000)
               +
               struct.pack("<HLf",0x0116,4,10.0)
               +
               (
                   struct.pack("<HLH",0x0110,2,2400)
               if (i+1)<len(chunks)
               else
                   b""
               )
           )
       for i in range(len(chunks))
       if chunks[i]
       ])
   )
   open(outfn,"wb").write(uef)

if __name__ == "__main__":
   import sys
   _, _i, infn, _o, outfn = sys.argv; assert (_i == '-i') and (_o == '-o') # usage: cas2uef.py -i infile.cas -o outfile.uef
   cas2uef(infn, outfn)
