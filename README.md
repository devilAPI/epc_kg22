# epc_kg22 keygen

Reverse-engineered reimplementation of the `epc_kg22.exe` key generator (2002) in Python.

The original is a 32-bit Windows MFC application, UPX-packed (v1.90, NRV method 9).
This project reconstructs the key generation algorithm from disassembly of the unpacked binary.

## Usage

### Interactive wizard

```
python3 epc_keygen.py
```

Prompts for all inputs step by step.

### Command line

```
python3 epc_keygen.py <LanID> [-t TYPE] [-y YEAR] [-d DATE]
```

| Argument | Description |
|---|---|
| `LanID` | 12 hex characters |
| `-t`, `--type` | Disc type: `6CD`, `8CD`, `10CD`, or `Allmarket` |
| `-y`, `--year` | Year (default: 2003) |
| `-d`, `--date` | Date as `YYYY-MM-DD` (optional) |

### Examples

```
python3 epc_keygen.py ABCDEF123456
python3 epc_keygen.py ABCDEF123456 -t 8CD -y 2003 -d 2003-06-15
```

## Algorithm

The key generation pipeline:

1. Parse the LanID — extract hex characters from position 4 onward, convert to a 16-bit value
2. Prepare an 80-byte EPCKey buffer from the selected disc type
3. Pack a fixed structure: version, type, year, day count, LanID value, EPCKey length, and a checksum
4. Encode all fields as LSB-first binary strings (224 bits total)
5. XOR with a repeating 74-character mask baked into the original binary
6. Group into 5-bit chunks, read MSB-first, and index into a 36-character alphabet (`a-z0-9`)
7. Prefix with `*` — final serial is 46 characters

## Requirements

Python 3.6+ (standard library only).

## License

MIT
