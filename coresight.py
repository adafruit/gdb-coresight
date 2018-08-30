# The MIT License (MIT)
#
# Copyright (c) 2018 Scott Shawcroft
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`coresight`
====================================================

Source into GDB to be able to interact with debug registers

* Author(s): Scott Shawcroft
"""

#from __future__ import print_statement

import gdb
import struct

inferior = gdb.selected_inferior()

ROM_TABLE_COMPONENT = 0x1

COMPONENT_CLASSES = {
    0x0: "Generic Verification",
    ROM_TABLE_COMPONENT: "ROM Table",
    0x9: "CoreSight Component",
    0xB: "Peripheral Test Block",
    0xE: "Generic IP",
    0xF: "CoreLink, PrimeCell or non standard"
}

DESIGNER = {
    (4, 0x3b): "ARM"
}

print("coresight")

def dump_rom_table(address, depth=0):
    try:
        mem = inferior.read_memory(address + 0xfd0, 4*12)
    except gdb.MemoryError:
        print("Unable to read 0x{:08x}".format(address))
        return
    ids = struct.unpack("<IIIIIIIIIIII", mem)
    if ids[1] != 0 or ids[2] != 0 or ids[3] != 0 or ids[8] != 0xd or ids[10] != 0x5 or ids[11] != 0xb1:
        print("invalid rom table")
    pidr4 = ids[0]
    pidr0, pidr1, pidr2, pidr3 = ids[4:8]
    cidr1 = ids[9]
    component_class = cidr1 >> 4 & 0xf
    revand = pidr3 >> 4 & 0xf
    cmod = pidr3 & 0xf
    revision = pidr2 >> 4 & 0xf
    jedec = pidr2 >> 3 & 0x1
    jep106_id = (pidr2 & 0x7) << 4 | pidr1 >> 4 & 0xf
    jep106_continuation_code = pidr4 & 0xf
    print("  " * depth + "{:08x}".format(address))
    print("  " * depth + COMPONENT_CLASSES[component_class])
    print("  " * depth + "JEDEC ID: " + "0x7f " * jep106_continuation_code + "0x{:02x}".format(jep106_id))
    print("  " * depth + "Designer: " + DESIGNER.get((jep106_continuation_code, jep106_id), "Unknown"))
    print("  " * depth + " ".join(["{:08x}".format(x) for x in ids]))

    if component_class == ROM_TABLE_COMPONENT:
        mem = inferior.read_memory(address, 4)
        entry = struct.unpack("<I", mem)[0]

        i = 0
        while entry != 0:
            dump_rom_table((address + ((entry >> 12) << 12)) & 0xffffffff, depth+1)


            i += 1
            mem = inferior.read_memory(address + i * 4, 4)
            entry = struct.unpack("<I", mem)[0]

#dump_rom_table(0xe00ff000)
dump_rom_table(0x41003000)
#dump_rom_table(0x23000000)
