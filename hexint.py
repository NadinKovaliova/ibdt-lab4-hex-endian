"""Перетворення шістнадцяткових (hex) значень у цілі беззнакові числа і назад
з урахуванням порядку байтів (endianness).

Hex-рядок розглядається як послідовність байтів, записаних зліва направо
(по два hex-символи на байт), наприклад "01234567" -> 01 23 45 67.

 - Big-endian:    перший байт - старший (так число записують люди).
                  "01234567" -> 0x01234567
 - Little-endian: перший байт - молодший (так число зберігає x86/ARM у пам'яті).
                  "01234567" -> 0x67452301

Перетворення виконано вручну (без int.from_bytes / int.to_bytes), щоб було видно
сам механізм: число = число * 256 + наступний байт.
"""

_HEX_DIGITS = "0123456789abcdef"


def _parse_hex(hex_str: str) -> list[int]:
    """Розбирає hex-рядок на список байтів (за порядком запису)."""
    if not isinstance(hex_str, str):
        raise TypeError("hex-значення має бути рядком")
    s = "".join(hex_str.split())  # пробіли/переноси дозволені як роздільники
    if s[:2].lower() == "0x":
        s = s[2:]
    if not s:
        raise ValueError("порожнє hex-значення")
    if len(s) % 2:
        raise ValueError("непарна кількість hex-символів: байт має складатися з двох")
    s = s.lower()
    bad = next((c for c in s if c not in _HEX_DIGITS), None)
    if bad is not None:
        raise ValueError(f"недопустимий hex-символ: {bad!r}")
    return [_HEX_DIGITS.index(s[i]) * 16 + _HEX_DIGITS.index(s[i + 1])
            for i in range(0, len(s), 2)]


def _bytes_to_hex(data: list[int]) -> str:
    return "".join(_HEX_DIGITS[b >> 4] + _HEX_DIGITS[b & 0x0F] for b in data)


def _to_bytes_big(value: int, num_bytes: int | None) -> list[int]:
    """Байти числа від старшого до молодшого."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("значення має бути цілим числом")
    if value < 0:
        raise ValueError("число має бути беззнаковим (>= 0)")
    out = []
    v = value
    while v:
        out.append(v & 0xFF)
        v >>= 8
    out.reverse()
    if num_bytes is None:
        return out or [0]
    if num_bytes < 1:
        raise ValueError("кількість байтів має бути додатною")
    if len(out) > num_bytes:
        raise OverflowError(f"число не вміщується в {num_bytes} байт(и)")
    return [0] * (num_bytes - len(out)) + out


def byte_count(hex_str: str) -> int:
    """Кількість байтів у hex-значенні."""
    return len(_parse_hex(hex_str))


def hex_to_big_endian(hex_str: str) -> int:
    """HEX -> ціле число, перший байт старший."""
    value = 0
    for b in _parse_hex(hex_str):
        value = value * 256 + b
    return value


def hex_to_little_endian(hex_str: str) -> int:
    """HEX -> ціле число, перший байт молодший."""
    value = 0
    for b in reversed(_parse_hex(hex_str)):
        value = value * 256 + b
    return value


def big_endian_to_hex(value: int, num_bytes: int | None = None) -> str:
    """Ціле число -> HEX, старший байт першим.

    num_bytes - довжина результату в байтах (доповнюється нулями); без нього -
    мінімально можлива довжина.
    """
    return _bytes_to_hex(_to_bytes_big(value, num_bytes))


def little_endian_to_hex(value: int, num_bytes: int | None = None) -> str:
    """Ціле число -> HEX, молодший байт першим."""
    return _bytes_to_hex(list(reversed(_to_bytes_big(value, num_bytes))))
