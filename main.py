"""CLI для лабораторної роботи 4: hex <-> ціле беззнакове число (little/big-endian).

Приклади:
    python main.py hex2int le ff00000000000000000000000000000000000000000000000000000000000000
    python main.py hex2int be 01234567
    python main.py int2hex le 255 --bytes 32
    python main.py int2hex be 4294967295
    python main.py vectors          # тестові вектори з методички
"""

import argparse
import sys

import hexint

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VECTORS = [
    ("Vector 1", "ff" + "00" * 31),
    ("Vector 2", "aaaa" + "00" * 30),
    ("Vector 3", "FFFFFFFF"),
    ("Vector 4", "F0" + "00" * 511),
]


def _short(n: int, width: int = 60) -> str:
    s = str(n)
    return s if len(s) <= width else f"{s[:28]}...{s[-28:]} ({len(s)} цифр)"


def show_vectors() -> None:
    for name, value in VECTORS:
        shown = value if len(value) <= 70 else f"{value[:12]}...{value[-6:]} ({len(value)} hex-символів)"
        print(name)
        print(f"  Value:         {shown}")
        print(f"  Number of bytes: {hexint.byte_count(value)}")
        print(f"  Little-endian: {_short(hexint.hex_to_little_endian(value))}")
        print(f"  Big-endian:    {_short(hexint.hex_to_big_endian(value))}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("hex2int", help="HEX -> ціле число")
    a.add_argument("order", choices=["le", "be"])
    a.add_argument("hex")

    b = sub.add_parser("int2hex", help="ціле число -> HEX")
    b.add_argument("order", choices=["le", "be"])
    b.add_argument("number", type=int)
    b.add_argument("--bytes", type=int, default=None, dest="num_bytes",
                   help="довжина результату в байтах")

    sub.add_parser("vectors", help="показати тестові вектори")
    args = p.parse_args(argv)

    try:
        if args.cmd == "vectors":
            show_vectors()
        elif args.cmd == "hex2int":
            fn = hexint.hex_to_little_endian if args.order == "le" else hexint.hex_to_big_endian
            print(fn(args.hex))
        else:
            fn = hexint.little_endian_to_hex if args.order == "le" else hexint.big_endian_to_hex
            print(fn(args.number, args.num_bytes))
    except (ValueError, OverflowError, TypeError) as e:
        print(f"Помилка: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
