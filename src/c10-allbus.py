#!/usr/bin/env python

"""usage: c10-allbus <src> <dst> [-b <bus>] [options]

Switch 1553 format 1 messages to indicate the same bus (A or B).

Options:
    -b <bus>, --bus <bus>  Select which bus to indicate [default: a].
    -f, --force            Overwrite existing dst file if present.
"""

from docopt import docopt
from chapter10 import C10

from common import FileProgress


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<dst>'], 'wb') as out, \
            FileProgress(args['<src>']) as progress:
        for packet in C10(args['<src>']):

            raw = bytes(packet)
            progress.update(len(raw))

            # Write non-1553 out as-is.
            if packet.data_type != 0x19:
                out.write(raw)

            else:
                # Write out packet header secondary if applicable) and CSDW.
                offset = 28
                if packet.secondary_header:
                    offset += 12
                out.write(raw[:offset])

                # Walk through messages and update bus ID as needed.
                for msg in packet.body:
                    if args['--bus'].lower() == 'a':
                        msg.bus_id = 0
                    else:
                        msg.bus_id = 1
                    packed = msg.pack(packet.body.iph_format)
                    out.write(packed)
                    offset += len(packed)

                # Write filler.
                for i in range(packet.packet_length - offset):
                    out.write('0')
