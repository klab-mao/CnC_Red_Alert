#!/usr/bin/env python3
"""
Edit money (Cash/Resources) in a Yuri's Revenge OpenRA save file (.orasav).

Usage:
  python3 edit_yr_money.py <savefile>                    # show current money
  python3 edit_yr_money.py <savefile> --cash 50000       # set cash for all players
  python3 edit_yr_money.py <savefile> --cash 50000 --player Multi0
  python3 edit_yr_money.py <savefile> --resources 1000   # set stored resources

The save file format (16-byte footer):
  [orders] [metadata] [traitdata] [snapshot] [footer]
  footer = metadataOffset(i32) traitDataOffset(i32) snapshotOffset(i32) EOFMarker(i32)
  snapshot = SnapshotMarker(i32=-4) length(i32) utf8_yaml_bytes

# python3 port/edit_yr_money.py "port/openra-yr/engine/Support/Saves/yr/release-20200503/<new-save>.orasav"
"""

import sys
import struct
import argparse

EOF_MARKER = -2 & 0xFFFFFFFF
SNAPSHOT_MARKER = -4 & 0xFFFFFFFF
METADATA_MARKER = -1 & 0xFFFFFFFF
TRAIT_DATA_MARKER = -3 & 0xFFFFFFFF


def read_u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def read_i32(data, offset):
    return struct.unpack_from('<i', data, offset)[0]


def parse_snapshot_yaml(yaml_str):
    """Parse the simple flat YAML used by OpenRA snapshots into a list of (key, dict) entries."""
    entries = []
    current_key = None
    current_dict = None

    for line in yaml_str.split('\n'):
        if not line.strip():
            continue

        if not line.startswith(' ') and not line.startswith('\t'):
            # Top-level key: Type@ID:
            if current_key is not None:
                entries.append((current_key, current_dict))
            current_key = line.rstrip().rstrip(':')
            current_dict = {}
        else:
            # Sub-property: Key: Value
            stripped = line.strip()
            if ':' in stripped:
                k, v = stripped.split(':', 1)
                current_dict[k.strip()] = v.strip()

    if current_key is not None:
        entries.append((current_key, current_dict))

    return entries


def build_snapshot_yaml(entries):
    """Rebuild YAML from parsed entries."""
    lines = []
    for key, props in entries:
        lines.append('{}:'.format(key))
        for k, v in props.items():
            lines.append('\t{}: {}'.format(k, v))
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Edit money in YR save file')
    parser.add_argument('savefile', help='Path to .orasav save file')
    parser.add_argument('--cash', type=int, help='Set cash amount')
    parser.add_argument('--resources', type=int, help='Set stored resources amount')
    parser.add_argument('--player', help='Player internal name (e.g. Multi0). Default: all players')
    args = parser.parse_args()

    with open(args.savefile, 'rb') as f:
        data = bytearray(f.read())

    file_len = len(data)

    # Read 16-byte footer
    footer_off = file_len - 16
    metadata_offset = read_u32(data, footer_off)
    trait_data_offset = read_u32(data, footer_off + 4)
    snapshot_offset = read_u32(data, footer_off + 8)
    eof_marker = read_i32(data, footer_off + 12)

    if eof_marker != -2:
        # Try 12-byte footer (old format, no snapshot)
        footer_off = file_len - 12
        metadata_offset = read_u32(data, footer_off)
        trait_data_offset = read_u32(data, footer_off + 4)
        eof_marker = read_i32(data, footer_off + 8)
        snapshot_offset = 0
        if eof_marker != -2:
            print('Error: Invalid save file (bad footer marker: {})'.format(eof_marker))
            sys.exit(1)

    if snapshot_offset == 0:
        print('Error: No snapshot in this save file. Save with the latest engine version.')
        sys.exit(1)

    # Read snapshot
    marker = read_i32(data, snapshot_offset)
    if marker != -4:
        print('Error: Invalid snapshot marker: {}'.format(marker))
        sys.exit(1)

    str_len = read_u32(data, snapshot_offset + 4)
    snapshot_yaml = data[snapshot_offset + 8 : snapshot_offset + 8 + str_len].decode('utf-8')

    # Parse and find PlayerResources entries
    entries = parse_snapshot_yaml(snapshot_yaml)

    money_entries = [(k, v) for k, v in entries if k.startswith('PlayerResources@')]

    if not money_entries:
        print('No PlayerResources entries found in snapshot.')
        print('Save the game with the latest engine build first (money was recently added).')
        sys.exit(1)

    print('Found {} player(s) with money data:'.format(len(money_entries)))
    for key, props in money_entries:
        player_name = key.split('@')[1] if '@' in key else key
        cash = props.get('Cash', '0')
        resources = props.get('Resources', '0')
        print('  {}: Cash={}, Resources={}'.format(player_name, cash, resources))

    if args.cash is None and args.resources is None:
        print('\nNo --cash or --resources specified. Showing current values only.')
        return

    # Modify entries
    modified = False
    for i, (key, props) in enumerate(entries):
        if not key.startswith('PlayerResources@'):
            continue

        player_name = key.split('@')[1] if '@' in key else key
        if args.player and args.player != player_name:
            continue

        if args.cash is not None:
            props['Cash'] = str(args.cash)
            print('Set {} Cash = {}'.format(player_name, args.cash))
            modified = True
        if args.resources is not None:
            props['Resources'] = str(args.resources)
            print('Set {} Resources = {}'.format(player_name, args.resources))
            modified = True

    if not modified:
        print('No matching players modified.')
        return

    # Rebuild snapshot YAML
    new_yaml = build_snapshot_yaml(entries)
    new_yaml_bytes = new_yaml.encode('utf-8')
    new_str_len = len(new_yaml_bytes)

    old_snapshot_data_start = snapshot_offset + 8
    old_snapshot_data_end = snapshot_offset + 8 + str_len
    new_snapshot_data = struct.pack('<I', new_str_len) + new_yaml_bytes

    # Replace snapshot data in file
    new_data = (
        data[:snapshot_offset]
        + struct.pack('<I', SNAPSHOT_MARKER)
        + new_snapshot_data
        + data[old_snapshot_data_end:]
    )

    # Footer offsets don't change because snapshot is the last section before footer
    # and we only changed the string content (offsets before snapshot are unaffected).
    # The footer itself is at the end and its offsets (metadata, traitdata) are before snapshot.
    # snapshot_offset also doesn't change. Only the total file length may change.

    with open(args.savefile, 'wb') as f:
        f.write(new_data)

    print('Save file updated successfully.')


if __name__ == '__main__':
    main()