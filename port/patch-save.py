#!/usr/bin/env python3
"""Patch OpenRA yr snapshot saves: modify objectives state / player cash.

Usage:
  python3 patch-save.py <file.orasav> --set-objectives <player> <state>   # state: 0=incomplete 1=completed 2=failed
  python3 patch-save.py <file.orasav> --cash <player> <amount>
  python3 patch-save.py <file.orasav> --info

A .bak backup is written next to the file on first modification.
"""
import argparse
import os
import re
import struct
import sys

FOOTER = 16
EOF_MARKER = -2
SNAPSHOT_MARKER = -4


def parse(path):
    data = open(path, 'rb').read()
    if len(data) < FOOTER:
        raise SystemExit('file too small')
    meta, trait, snap, eof = struct.unpack('<4i', data[-FOOTER:])
    if eof != EOF_MARKER or snap <= 0:
        raise SystemExit('not a snapshot-format save (eof=%d snap=%d)' % (eof, snap))
    if struct.unpack('<i', data[snap:snap + 4])[0] != SNAPSHOT_MARKER:
        raise SystemExit('bad snapshot marker')
    ln = struct.unpack('<i', data[snap + 4:snap + 8])[0]
    text = data[snap + 8:snap + 8 + ln].decode('utf-8')
    trailing = data[snap + 8 + ln:-FOOTER]  # usually empty
    return data, meta, trait, snap, text, trailing


def write(path, data, meta, trait, snap, text, trailing):
    bak = path + '.bak'
    if not os.path.exists(bak):
        open(bak, 'wb').write(data)
    blob = text.encode('utf-8')
    out = data[:snap] + struct.pack('<ii', SNAPSHOT_MARKER, len(blob)) + blob + trailing \
        + struct.pack('<4i', meta, trait, snap, EOF_MARKER)
    open(path, 'wb').write(out)
    print('patched %s (backup at %s)' % (path, bak))


def get_objectives(text, player):
    m = re.search(r'^Objectives@%s: (.*)$' % re.escape(player), text, re.M)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--info', action='store_true')
    ap.add_argument('--set-objectives', nargs=2, metavar=('PLAYER', 'STATE'))
    ap.add_argument('--cash', nargs=2, metavar=('PLAYER', 'AMOUNT'))
    args = ap.parse_args()

    data, meta, trait, snap, text, trailing = parse(args.file)

    if args.info or not (args.set_objectives or args.cash):
        for m in re.finditer(r'^Objectives@(\w+): (.*)$', text, re.M):
            print('Objectives@%s:' % m.group(1))
            for i, ent in enumerate(m.group(2).split(';')):
                f = ent.split('|')
                print('  [%d] state=%s type=%s required=%s : %s' % (i, f[0], f[1], f[2], f[3]))
        for m in re.finditer(r'^PlayerResources@(\w+):\n\tCash: (-?\d+)\n\tResources: (-?\d+)', text, re.M):
            print('PlayerResources@%s: Cash=%s Resources=%s' % m.groups())
        return

    if args.set_objectives:
        player, state = args.set_objectives[0], args.set_objectives[1]
        int(state)  # validate
        m = get_objectives(text, player)
        if not m:
            raise SystemExit('no Objectives@%s node found' % player)
        ents = ['|'.join([state] + e.split('|')[1:]) for e in m.group(1).split(';')]
        text = text[:m.start(1)] + ';'.join(ents) + text[m.end(1):]
        print('set all objectives of %s to state %s' % (player, state))

    if args.cash:
        player, amount = args.cash[0], args.cash[1]
        int(amount)
        pat = r'(PlayerResources@%s:\n\tCash: )-?\d+' % re.escape(player)
        new, n = re.subn(pat, r'\g<1>' + amount, text)
        if n == 0:
            raise SystemExit('no PlayerResources@%s node found' % player)
        text = new
        print('set cash of %s to %s' % (player, amount))

    write(args.file, data, meta, trait, snap, text, trailing)


if __name__ == '__main__':
    main()