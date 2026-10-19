#!/usr/bin/env python3
"""Key generator — reverse-engineered from epc_kg22.exe (2002)."""

import argparse
from datetime import date

XOR_MASK = "10011100111000111011110101100110011110011110011110101010110011010110011001"
ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
DEFAULT_EPCKEY = "010111111100000000000000"

DISC_TYPES = {
    "6CD":       "0101110011000000",
    "8CD":       "0101111111000000",
    "10CD":      "0111111111110000",
    "Allmarket": "011111111111111111111111",
}


def int_to_bin_lsb(value, num_bits):
    """Convert integer to binary string, LSB first."""
    return ''.join('1' if (value >> i) & 1 else '0' for i in range(num_bits))


def generate_key(lan_id, epc_key, year, days):
    vin_hex = int(lan_id[4:], 16) & 0xFFFF
    year = max(year, 1) & 0xFFFF
    days = days & 0xFFFF

    # EPCKey buffer: 80 bytes of '0', then overlay the key
    buf = ['0'] * 80
    for i, c in enumerate(epc_key):
        buf[i] = c
    epc_buffer = ''.join(buf)

    num_ones = epc_buffer.count('1')

    # Structure fields
    b0, b1 = 2, 1
    w2 = year
    w4 = 0x65  # 101
    w6 = days
    w8 = vin_hex
    wa = 0
    dw_c = 80
    checksum = (b0 + b1 + w2 + w4 + w6 + w8 + wa + (dw_c & 0xFFFF) + num_ones) & 0xFFFF

    # Build binary string (all fields LSB-first)
    binary = (
        int_to_bin_lsb(b0, 8)
        + int_to_bin_lsb(b1, 8)
        + int_to_bin_lsb(w2, 16)
        + int_to_bin_lsb(w4, 16)
        + int_to_bin_lsb(w6, 16)
        + int_to_bin_lsb(w8, 16)
        + int_to_bin_lsb(wa, 16)
        + int_to_bin_lsb(dw_c, 32)
        + epc_buffer
        + int_to_bin_lsb(checksum, 16)
    )  # 224 chars

    # Pad with (len % 5) zeros
    binary += '0' * (len(binary) % 5)

    # XOR with repeating mask
    mask_len = len(XOR_MASK)
    binary = ''.join(
        '1' if (b == '1') != (XOR_MASK[i % mask_len] == '1') else '0'
        for i, b in enumerate(binary)
    )

    # Encode 5-bit groups (MSB-first) to alphabet
    num_groups = len(binary) // 5
    serial = "*"
    for g in range(num_groups):
        serial += ALPHABET[int(binary[g * 5 : g * 5 + 5], 2)]

    return serial[:46]


def date_to_days(d):
    """Convert a date to the day count used by the keygen (days since Dec 31, 1899)."""
    return (d - date(1899, 12, 31)).days


def wizard():
    print("=== epc_kg22 Key Generator ===\n")

    while True:
        lan_id = input("LanID (12 hex characters): ").strip().upper()
        if len(lan_id) == 12:
            try:
                int(lan_id, 16)
                break
            except ValueError:
                pass
        print("  Invalid — must be exactly 12 hex characters.\n")

    type_names = list(DISC_TYPES.keys())
    print("\nDisc type:")
    print("  0) Default (built-in key)")
    for i, name in enumerate(type_names, 1):
        print(f"  {i}) {name}")
    while True:
        choice = input(f"Choose [0-{len(type_names)}] (default 0): ").strip()
        if choice == "" or choice == "0":
            epc_key = DEFAULT_EPCKEY
            break
        if choice.isdigit() and 1 <= int(choice) <= len(type_names):
            epc_key = DISC_TYPES[type_names[int(choice) - 1]]
            break
        print("  Invalid choice.\n")

    while True:
        year_str = input("\nYear (default 2003): ").strip()
        if year_str == "":
            year = 2003
            break
        if year_str.isdigit():
            year = int(year_str)
            break
        print("  Invalid — enter a number.\n")

    while True:
        date_str = input("Date as YYYY-MM-DD (leave empty for none): ").strip()
        if date_str == "":
            days = 0
            break
        try:
            y, m, d = map(int, date_str.split("-"))
            days = date_to_days(date(y, m, d))
            break
        except (ValueError, TypeError):
            print("  Invalid — use YYYY-MM-DD format.\n")

    serial = generate_key(lan_id, epc_key, year, days)
    print(f"\nSerial: {serial}")


def main():
    parser = argparse.ArgumentParser(description="epc_kg22 key generator")
    parser.add_argument("lan_id", nargs="?", help="12-character LanID (hex)")
    parser.add_argument(
        "-t", "--type",
        choices=list(DISC_TYPES.keys()),
        default=None,
        help="Disc type (default: built-in key)",
    )
    parser.add_argument("-y", "--year", type=int, default=2003, help="Year (default: 2003)")
    parser.add_argument(
        "-d", "--date",
        default=None,
        help="Date as YYYY-MM-DD (default: no date, days=0)",
    )
    args = parser.parse_args()

    if args.lan_id is None:
        wizard()
        return

    lan_id = args.lan_id.upper()
    if len(lan_id) != 12:
        parser.error("LanID must have 12 characters")

    epc_key = DISC_TYPES.get(args.type, DEFAULT_EPCKEY) if args.type else DEFAULT_EPCKEY
    days = 0
    if args.date:
        y, m, d = map(int, args.date.split("-"))
        days = date_to_days(date(y, m, d))

    serial = generate_key(lan_id, epc_key, args.year, days)
    print(serial)


if __name__ == "__main__":
    main()
