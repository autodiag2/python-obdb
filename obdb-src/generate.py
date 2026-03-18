#!/usr/bin/env python3
import keyword
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REPO_NAMES_FILE = ROOT / "obdb-repositories.txt"
OUT_FILE = ROOT / "obdb" / "commands.py"


def py_ident(name):
    s = re.sub(r"[^0-9A-Za-z_]", "_", str(name))
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "unnamed"
    if s[0].isdigit():
        s = "_" + s
    if keyword.iskeyword(s):
        s = s + "_"
    return s


def load_source_names():
    if not REPO_NAMES_FILE.exists():
        raise FileNotFoundError(f"missing repository list: {REPO_NAMES_FILE}")

    items = []
    for line in REPO_NAMES_FILE.read_text(encoding="utf-8").splitlines():
        name = line.strip()
        if not name:
            continue
        items.append(name)
    return items


def emit_header(source_names):
    source_names_repr = repr(source_names)
    return f'''
import json
import keyword
import math
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from obd import OBDCommand, Unit


_SOURCE_NAMES = {source_names_repr}
_SOURCE_NAME_SET = set(_SOURCE_NAMES)


def _py_ident(name):
    s = re.sub(r"[^0-9A-Za-z_]", "_", str(name))
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        s = "unnamed"
    if s[0].isdigit():
        s = "_" + s
    if keyword.iskeyword(s):
        s = s + "_"
    return s


def _signal_py_name(signal, index):
    for key in ("id", "name", "path"):
        value = signal.get(key)
        if value:
            return _py_ident(value)
    return f"signal_{{index}}"


def _command_desc(signal, entry):
    parts = []
    for key in ("name", "id", "path"):
        value = signal.get(key)
        if value:
            parts.append(str(value))
            break
    hdr = entry.get("hdr")
    if hdr:
        parts.append(f"hdr={{hdr}}")
    return " | ".join(parts) if parts else "OBDb signal"


def _clean_hex(value):
    return "".join(ch for ch in str(value) if ch in "0123456789abcdefABCDEF").upper()


def _parse_cmd(cmd_map):
    if not isinstance(cmd_map, dict) or len(cmd_map) != 1:
        return None
    service_hex, pid_hex = next(iter(cmd_map.items()))
    service_hex = _clean_hex(service_hex)
    pid_hex = _clean_hex(pid_hex)
    if not service_hex or not pid_hex:
        return None
    return {{
        "service_hex": service_hex,
        "pid_hex": pid_hex,
        "command_hex": service_hex + pid_hex,
        "response_prefix_hex": f"{{int(service_hex, 16) + 0x40:02X}}{{pid_hex}}",
    }}


def _expected_bytes(signals):
    bit_end = 0
    for signal in signals:
        fmt = signal.get("fmt", {{}})
        bix = int(fmt.get("bix", 0))
        bitlen = int(fmt.get("len", 0))
        if bit_end < bix + bitlen:
            bit_end = bix + bitlen
    return math.ceil(bit_end / 8)


def _bytes_to_int(data):
    value = 0
    for b in data:
        value = (value << 8) | int(b)
    return value


def _twos_complement(value, bits):
    if bits <= 0:
        return value
    sign_bit = 1 << (bits - 1)
    if value & sign_bit:
        return value - (1 << bits)
    return value


def _extract_bits_be(payload, bix, bitlen, signed=False):
    if bitlen <= 0:
        return 0
    total_bits = len(payload) * 8
    if bix < 0 or total_bits < bix + bitlen:
        raise ValueError(f"bit range out of payload: bix={{bix}} len={{bitlen}} total={{total_bits}}")
    raw = _bytes_to_int(payload)
    shift = total_bits - (bix + bitlen)
    mask = (1 << bitlen) - 1
    value = (raw >> shift) & mask
    if signed:
        value = _twos_complement(value, bitlen)
    return value


def _strip_response_prefix(data, response_prefix):
    if len(data) >= len(response_prefix) and bytes(data[:len(response_prefix)]) == response_prefix:
        return bytes(data[len(response_prefix):])
    if len(data) >= 1 and response_prefix and data[0] == response_prefix[0]:
        return bytes(data[1:])
    return bytes(data)


def _unit_from_name(unit_name):
    if unit_name is None:
        return None

    text = str(unit_name).strip()
    if not text:
        return None

    aliases = {{
        "percent": "%",
        "percentage": "%",
        "scalar": "count",
        "count": "count",
        "counts": "count",
        "kilometer": "kilometer",
        "kilometers": "kilometer",
        "kilometersperhour": "kilometer_per_hour",
        "km": "kilometer",
        "second": "second",
        "seconds": "second",
        "sec": "second",
        "s": "second",
        "minute": "minute",
        "minutes": "minute",
        "hour": "hour",
        "hours": "hour",
        "celsius": "degC",
        "degc": "degC",
        "rpm": "revolutions_per_minute",
        "kpa": "kilopascal",
        "pa": "pascal",
        "bar": "bar",
        "volt": "volt",
        "volts": "volt",
        "v": "volt",
        "amp": "ampere",
        "amps": "ampere",
        "ampere": "ampere",
        "a": "ampere",
        "gram/second": "gram / second",
        "grams/second": "gram / second",
        "g/s": "gram / second",
        "ratio": "dimensionless",
    }}

    parsed = aliases.get(text.lower(), text)

    try:
        return Unit(parsed)
    except Exception:
        return None


def _quantity_from_value_unit(value, unit):
    if unit is None:
        return value
    try:
        return Unit.Quantity(value, unit)
    except Exception:
        return value * unit


def _make_decoder(response_prefix, bix, bitlen, mul, add, div, signed, unit_name, value_min, value_max):
    unit = _unit_from_name(unit_name)

    def decoder(messages):
        if not messages:
            return None
        data = bytes(messages[0].data)
        payload = _strip_response_prefix(data, response_prefix)
        value = _extract_bits_be(payload, bix, bitlen, signed=signed)
        value = (value * mul) / div + add

        if value_min is not None and value < value_min:
            value = value_min
        if value_max is not None and value > value_max:
            value = value_max

        return _quantity_from_value_unit(value, unit)

    return decoder


def _source_url(source_name):
    return f"https://raw.githubusercontent.com/OBDb/{{source_name}}/master/signalsets/v3/default.json"


def _load_source_data(source_name):
    if source_name not in _SOURCE_NAME_SET:
        raise KeyError(f"unknown OBDb source: {{source_name}}")

    url = _source_url(source_name)

    try:
        with urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(f"cannot fetch {{source_name}} signalset from {{url}}: HTTP {{e.code}}") from e
    except URLError as e:
        raise RuntimeError(f"cannot fetch {{source_name}} signalset from {{url}}: {{e.reason}}") from e


_ORIGINAL_SOURCE_NAMES = {{}}
_ORIGINAL_COMMAND_NAMES = {{}}
_LOADED_SOURCE_COMMANDS = {{}}


def _build_source_commands(source_name, source_ident):
    cached = _LOADED_SOURCE_COMMANDS.get(source_ident)
    if cached is not None:
        return cached

    data = _load_source_data(source_name)
    commands = {{}}
    original_names = {{}}
    used_names = set()

    for entry in data.get("commands", []):
        cmd_info = _parse_cmd(entry.get("cmd"))
        signals = entry.get("signals", [])
        if not cmd_info or not signals:
            continue

        hdr = entry.get("hdr")
        hdr = _clean_hex(hdr) if hdr else None
        bytes_expected = _expected_bytes(signals)

        for index, signal in enumerate(signals):
            fmt = signal.get("fmt", {{}})
            bitlen = int(fmt.get("len", 0))
            if bitlen <= 0:
                continue

            name_original = signal.get("id") or signal.get("name") or signal.get("path") or f"signal_{{index}}"
            name_ident = _signal_py_name(signal, index)

            if name_ident in used_names:
                suffix = 2
                while f"{{name_ident}}_{{suffix}}" in used_names:
                    suffix += 1
                name_ident = f"{{name_ident}}_{{suffix}}"
            used_names.add(name_ident)

            bix = int(fmt.get("bix", 0))
            mul = fmt.get("mul", 1)
            add = fmt.get("add", 0)
            div = fmt.get("div", 1)
            unit = fmt.get("unit")
            value_min = fmt.get("min")
            value_max = fmt.get("max")
            signed = bool(fmt.get("signed", False))
            desc = _command_desc(signal, entry)

            kwargs = {{}}
            if hdr:
                kwargs["header"] = hdr.encode("ascii")

            commands[name_ident] = OBDCommand(
                name_ident,
                desc,
                cmd_info["command_hex"].encode("ascii"),
                bytes_expected + len(bytes.fromhex(cmd_info["command_hex"])),
                _make_decoder(
                    bytes.fromhex(cmd_info["response_prefix_hex"]),
                    bix,
                    bitlen,
                    mul,
                    add,
                    div,
                    signed,
                    unit,
                    value_min,
                    value_max,
                ),
                **kwargs,
            )
            original_names[name_ident] = name_original

    _ORIGINAL_SOURCE_NAMES[source_ident] = source_name
    _ORIGINAL_COMMAND_NAMES[source_ident] = original_names
    _LOADED_SOURCE_COMMANDS[source_ident] = commands
    return commands


class _LazyNamespace:
    def __init__(self, source_name, source_ident):
        self._source_name = source_name
        self._source_ident = source_ident
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        commands = _build_source_commands(self._source_name, self._source_ident)
        for name, command in commands.items():
            setattr(self, name, command)
        self._loaded = True

    def __getattr__(self, name):
        self._load()
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"{{self._source_ident}}.{{name}}")

    def __dir__(self):
        self._load()
        return sorted(set(super().__dir__()) | set(self.__dict__.keys()))

    def __repr__(self):
        state = "loaded" if self._loaded else "lazy"
        return f"<_LazyNamespace {{self._source_ident}} ({{state}})>"
'''


def emit_source_block(source_name):
    source_ident = py_ident(source_name)
    return (
        f'{source_ident} = _LazyNamespace("{source_name}", "{source_ident}")\n'
        f'_ORIGINAL_SOURCE_NAMES["{source_ident}"] = "{source_name}"\n'
        f'_ORIGINAL_COMMAND_NAMES["{source_ident}"] = {{}}\n'
    )


def emit_footer(source_names):
    exported = [py_ident(name) for name in source_names]
    exported.append("_ORIGINAL_SOURCE_NAMES")
    exported.append("_ORIGINAL_COMMAND_NAMES")
    return "__all__ = [\n    " + ",\n    ".join(repr(x) for x in exported) + "\n]\n"


def main():
    source_names = load_source_names()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    parts = [emit_header(source_names)]
    for source_name in source_names:
        parts.append(emit_source_block(source_name))
    parts.append(emit_footer(source_names))

    OUT_FILE.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()