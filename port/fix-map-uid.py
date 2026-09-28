#!/usr/bin/env python3
"""Recompute soviet-06 map UID and patch saves' Map: field to match.

Usage: python3 fix-map-uid.py [--dry]
"""
import hashlib
import os
import re
import shutil
import struct
import sys

ROOT = '/Volumes/mao-data/prg/klab/github/CnC_Red_Alert/port'
MAP = os.path.join(ROOT, 'openra-yr/mods/yr/maps/soviet-06')
SAVES = os.path.join(ROOT, 'openra-yr/engine/Support/Saves/yr/release-20200503')
SAVE_FILES = ['Flying to Moon.orasav', 'Flying to Moon (1).orasav', 'Flying to Moon (2).orasav']

dry = '--dry' in sys.argv

# Engine Folder package enumerates files via Directory.GetFiles (native order)
order = [n for n in os.listdir(MAP) if n.endswith(('.yaml', '.bin', '.lua'))]
print('dir order:', order)
h = hashlib.sha1()
for n in order:
    h.update(open(os.path.join(MAP, n), 'rb').read())
uid = h.hexdigest()
print('current map UID:', uid)

for f in SAVE_FILES:
    p = os.path.join(SAVES, f)
    d = open(p, 'rb').read()
    meta, trait, snap, eof = struct.unpack('<4i', d[-16:])
    m = re.search(rb'\tMap: ([0-9a-f]+)', d[meta:meta + 400])
    if not m:
        print(f, ': no Map field found, skip')
        continue
    old = m.group(1).decode()
    if old == uid:
        print(f, ': already current, skip')
        continue
    if dry:
        print(f, ': would patch', old, '->', uid)
        continue
    bkp = p + '.mapbak'
    if not os.path.exists(bkp):
        shutil.copy2(p, bkp)
    off = meta + m.start(1)
    assert len(uid) == len(old) == 40
    open(p, 'wb').write(d[:off] + uid.encode() + d[off + 40:])
    print(f, ': Map:', old, '->', uid, '(backup .mapbak)')