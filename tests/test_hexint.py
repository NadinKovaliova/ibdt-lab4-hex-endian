import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hexint  # noqa: E402

V1 = "ff" + "00" * 31
V2 = "aaaa" + "00" * 30
V3 = "FFFFFFFF"
V4 = "F0" + "00" * 511

# Значення Big-endian для векторів 1 і 2 - дослівно з методички
V1_BIG = 115339776388732929035197660848497720713218148788040405586178452820382218977280
V2_BIG = 77193548260167611359494267807458109956502771454495792280332974934474558013440


class VectorsFromMethodical(unittest.TestCase):
    def test_vector_1(self):
        self.assertEqual(hexint.byte_count(V1), 32)
        self.assertEqual(hexint.hex_to_little_endian(V1), 255)
        self.assertEqual(hexint.hex_to_big_endian(V1), V1_BIG)

    def test_vector_2(self):
        self.assertEqual(hexint.byte_count(V2), 32)
        self.assertEqual(hexint.hex_to_little_endian(V2), 43690)
        self.assertEqual(hexint.hex_to_big_endian(V2), V2_BIG)

    def test_vector_3(self):
        self.assertEqual(hexint.byte_count(V3), 4)
        self.assertEqual(hexint.hex_to_little_endian(V3), 4294967295)
        self.assertEqual(hexint.hex_to_big_endian(V3), 4294967295)

    def test_vector_4(self):
        self.assertEqual(len(V4), 1024)
        self.assertEqual(hexint.byte_count(V4), 512)
        self.assertEqual(hexint.hex_to_little_endian(V4), 240)
        big = hexint.hex_to_big_endian(V4)
        self.assertEqual(big, 0xF0 * 256 ** 511)
        s = str(big)
        self.assertEqual(len(s), 1233)
        self.assertTrue(s.startswith("97911457632483047502351816629683535866871648348192229411021889057870678"))
        self.assertTrue(s.endswith("0791685877738232879406346334603566914069127957053440"))


class Conversions(unittest.TestCase):
    def test_endianness_example(self):
        self.assertEqual(hexint.hex_to_big_endian("01234567"), 0x01234567)
        self.assertEqual(hexint.hex_to_little_endian("01234567"), 0x67452301)

    def test_int_to_hex_pads_to_length(self):
        self.assertEqual(hexint.little_endian_to_hex(255, 32), V1)
        self.assertEqual(hexint.little_endian_to_hex(43690, 32), V2)
        self.assertEqual(hexint.big_endian_to_hex(0x01234567), "01234567")
        self.assertEqual(hexint.little_endian_to_hex(0x01234567), "67452301")
        self.assertEqual(hexint.big_endian_to_hex(255, 4), "000000ff")

    def test_zero(self):
        self.assertEqual(hexint.hex_to_big_endian("00"), 0)
        self.assertEqual(hexint.big_endian_to_hex(0), "00")
        self.assertEqual(hexint.little_endian_to_hex(0, 3), "000000")

    def test_vector_roundtrips(self):
        for v in (V1, V2, V3, V4):
            n = hexint.byte_count(v)
            self.assertEqual(hexint.little_endian_to_hex(hexint.hex_to_little_endian(v), n), v.lower())
            self.assertEqual(hexint.big_endian_to_hex(hexint.hex_to_big_endian(v), n), v.lower())

    def test_against_int_from_bytes(self):
        rng = random.Random(1)
        for _ in range(200):
            data = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 70)))
            h = data.hex()
            self.assertEqual(hexint.hex_to_big_endian(h), int.from_bytes(data, "big"))
            self.assertEqual(hexint.hex_to_little_endian(h), int.from_bytes(data, "little"))
            n = len(data)
            self.assertEqual(hexint.big_endian_to_hex(int.from_bytes(data, "big"), n), h)
            self.assertEqual(hexint.little_endian_to_hex(int.from_bytes(data, "little"), n), h)

    def test_input_formats(self):
        self.assertEqual(hexint.hex_to_big_endian("0xAbCd"), 0xABCD)
        self.assertEqual(hexint.hex_to_big_endian("ab cd\n"), 0xABCD)


class Errors(unittest.TestCase):
    def test_invalid_hex(self):
        for bad in ("", "0x", "abc", "zz", "12 3"):
            with self.assertRaises(ValueError):
                hexint.hex_to_big_endian(bad)
            with self.assertRaises(ValueError):
                hexint.hex_to_little_endian(bad)

    def test_invalid_numbers(self):
        with self.assertRaises(ValueError):
            hexint.big_endian_to_hex(-1)
        with self.assertRaises(OverflowError):
            hexint.little_endian_to_hex(256, 1)
        with self.assertRaises(TypeError):
            hexint.big_endian_to_hex("5")
        with self.assertRaises(TypeError):
            hexint.hex_to_big_endian(255)


if __name__ == "__main__":
    unittest.main()
