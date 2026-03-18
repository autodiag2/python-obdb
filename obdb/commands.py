
import json
import keyword
import math
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from obd import OBDCommand, Unit


_SOURCE_NAMES = ['Abarth', 'Abarth-500', 'Abarth-595', 'Acura', 'Acura-CL', 'Acura-ILX', 'Acura-Integra', 'Acura-MDX', 'Acura-RDX', 'Acura-TL', 'Acura-TLX', 'Acura-TSX', 'Acura-ZDX', 'Aiways', 'Aiways-U5', 'Alfa-Romeo', 'Alfa-Romeo-Giulia', 'Alfa-Romeo-Giulietta', 'Alfa-Romeo-MiTo', 'Alfa-Romeo-Tonale', 'Alpine', 'Aston-Martin-Vantage', 'Audi', 'Audi-A1', 'Audi-A3', 'Audi-A3-e-tron', 'Audi-A4', 'Audi-A5', 'Audi-A6', 'Audi-A7', 'Audi-e-tron', 'Audi-Q2', 'Audi-Q3', 'Audi-Q4-e-tron', 'Audi-Q5', 'Audi-Q7', 'Audi-Q8', 'Audi-Q8-e-tron', 'Audi-RS-3', 'Audi-RS-5', 'Audi-RS-e-tron', 'Audi-S3', 'Audi-S4', 'Audi-S5', 'Audi-S6', 'Audi-SQ2', 'Audi-SQ5', 'Audi-SQ7', 'Audi-TT', 'Bentley', 'Bentley-Bentayga', 'BMW', 'BMW-1-Series', 'BMW-116i', 'BMW-2-Grand-Coupe', 'BMW-2-Series', 'BMW-230e', 'BMW-3-Series', 'BMW-3-Series-eDrive', 'BMW-330e', 'BMW-4-Series', 'BMW-5-Series', 'BMW-5-Series-xDrive', 'BMW-640i-f13', 'BMW-7-Series', 'BMW-840i', 'BMW-E91', 'BMW-E92', 'BMW-F34', 'BMW-i3', 'BMW-i3s', 'BMW-i4', 'BMW-i5', 'BMW-i8', 'BMW-iX', 'BMW-iX3', 'BMW-M2', 'BMW-M3', 'BMW-M4', 'BMW-M440i', 'BMW-M5', 'BMW-X1', 'BMW-X2', 'BMW-X3', 'BMW-X4', 'BMW-X5', 'BMW-X7', 'BMW-Z3', 'BMW-Z4', 'Buick', 'Buick-Encore', 'Buick-Encore-GX', 'Buick-Envision', 'Buick-LaCrosse', 'BYD', 'BYD-Atto-3', 'BYD-Dolphin-Mini', 'BYD-Sealion-6', 'Cadillac', 'Cadillac-CT4', 'Cadillac-CT5', 'Cadillac-CTS', 'Cadillac-ELR', 'Cadillac-Escalade', 'Cadillac-LYRIQ', 'Cadillac-XT5', 'Changan', 'Chery', 'Chery-Tiggo-7-Pro', 'Chery-Tiggo-8', 'Chevrolet', 'Chevrolet-Aveo', 'Chevrolet-Blazer-EV', 'Chevrolet-Bolt-EUV', 'Chevrolet-Bolt-EV', 'Chevrolet-Camaro', 'Chevrolet-Celta', 'Chevrolet-Cobalt', 'Chevrolet-Colorado', 'Chevrolet-Corvette', 'Chevrolet-Cruze', 'Chevrolet-D-Max', 'Chevrolet-Equinox', 'Chevrolet-Equinox-EV', 'Chevrolet-Express-Cargo', 'Chevrolet-Impala', 'Chevrolet-Malibu', 'Chevrolet-Montana', 'Chevrolet-Prizm', 'Chevrolet-S-10', 'Chevrolet-Silverado', 'Chevrolet-Silverado-1500', 'Chevrolet-Silverado-2500', 'Chevrolet-Silverado-3500', 'Chevrolet-Silverado-EV', 'Chevrolet-Sonic', 'Chevrolet-Spark', 'Chevrolet-Tahoe', 'Chevrolet-Trailblazer', 'Chevrolet-Traverse', 'Chevrolet-Trax', 'Chevrolet-Volt', 'Chrysler', 'Chrysler-200', 'Chrysler-300', 'Chrysler-Pacifica', 'Chrysler-Pacifica-Hybrid', 'Chrysler-Sebring', 'Citroen', 'Citroen-Basalt', 'Citroen-Berlingo', 'Citroen-C3', 'Citroen-C4', 'Citroen-CZero', 'Citroen-E-C4', 'Citroen-eC4-X', 'Cupra', 'Cupra-Born', 'Cupra-Formentor', 'Cupra-Leon', 'Cupra-Leon-Sportstourer', 'Dacia', 'Dacia-Duster', 'Dacia-Lodgy', 'Dacia-Sandero', 'Dacia-Spring', 'Daihatsu', 'Datsun', 'Dodge', 'Dodge-Challenger', 'Dodge-Charger', 'Dodge-Dakota', 'Dodge-Durango', 'Dodge-Grand-Caravan', 'Dodge-Hornet', 'Dodge-Journey', 'Dongfeng', 'DongFeng-Seres-3', 'DS', 'DS-7', 'Ferrari-458-Italia', 'Fiat', 'FIAT-500', 'FIAT-500e', 'FIAT-500X', 'FIAT-Fastback', 'Fiat-Grande-Punto', 'FIAT-Panda', 'Fiat-Punto', 'Fisker', 'Fisker-Ocean', 'Ford', 'Ford-Bronco', 'Ford-Bronco-Sport', 'Ford-E-Series', 'Ford-EcoSport', 'Ford-Edge', 'Ford-Escape', 'Ford-Everest', 'Ford-Expedition', 'Ford-Explorer', 'Ford-F-150', 'Ford-F-150-Lightning', 'Ford-F-250', 'Ford-F-350', 'Ford-Fiesta', 'Ford-Five-Hundred', 'Ford-Flex', 'Ford-Focus', 'Ford-Focus-RS', 'Ford-Focus-ST', 'Ford-Fusion', 'Ford-Fusion-Energi', 'Ford-Fusion-Hybrid', 'Ford-Ka', 'Ford-Kuga', 'Ford-Maverick', 'Ford-Mondeo', 'Ford-Mustang', 'Ford-Mustang-Mach-E', 'Ford-Puma', 'Ford-Ranger', 'Ford-Sierra', 'Ford-Taurus', 'Ford-Territory', 'Ford-Transit', 'Ford-Transit-Connect', 'FSO-Polonez', 'Genesis', 'Genesis-G70', 'Genesis-G80', 'GMC', 'GMC-Acadia', 'GMC-Canyon', 'GMC-Safari', 'GMC-Sierra-1500', 'GMC-Terrain', 'GMC-Yukon', 'GMC-Yukon-XL', 'Haval', 'Haval-H6-HEV', 'Haval-Jolion', 'Haval-Jolion-HEV', 'Holden', 'Holden-Commodore', 'Holden-Cruze', 'Honda', 'Honda-Accord', 'Honda-Accord-Hybrid', 'Honda-Brio', 'Honda-City', 'Honda-Civic', 'Honda-Clarity', 'Honda-CR-V', 'Honda-CR-V-Hybrid', 'Honda-CR-Z', 'Honda-e', 'Honda-Element', 'Honda-Fit', 'Honda-HR-V', 'Honda-Insight', 'Honda-Jazz', 'Honda-M-NV', 'Honda-Odyssey', 'Honda-Pilot', 'Honda-Prologue', 'Honda-Ridgeline', 'Honda-WRV', 'Honda-ZR-V', 'Hyundai', 'Hyundai-Accent', 'Hyundai-Avante', 'Hyundai-Elantra', 'Hyundai-Genesis-Coupe', 'Hyundai-i10', 'Hyundai-i20', 'Hyundai-i30', 'Hyundai-IONIQ-5', 'Hyundai-IONIQ-6', 'Hyundai-IONIQ-Electric', 'Hyundai-IONIQ-PlugIn-Hybrid', 'Hyundai-Kona', 'Hyundai-Kona-Electric', 'Hyundai-Palisade', 'Hyundai-Santa-Cruz', 'Hyundai-Santa-Fe', 'Hyundai-Santa-Fe-Hybrid', 'Hyundai-Sonata', 'Hyundai-Tucson', 'Hyundai-Tucson-Hybrid', 'Hyundai-Veloster', 'Hyundai-Venue', 'Hyundai-Verna', 'INFINITI', 'INFINITI-G-Sedan', 'INFINITI-G35', 'INFINITI-G37', 'INFINITI-Q45', 'INFINITI-Q50', 'INFINITI-Q70', 'INFINITI-QX55', 'INFINITI-QX70', 'JAC-EJ7', 'Jaecoo-J7', 'Jaguar', 'Jaguar-F-PACE', 'Jaguar-F-TYPE', 'Jaguar-I-PACE', 'Jeep', 'Jeep-Avenger', 'Jeep-Cherokee', 'Jeep-Commander', 'Jeep-Compass', 'Jeep-Gladiator', 'Jeep-Grand-Cherokee', 'Jeep-Liberty', 'Jeep-Patriot', 'Jeep-Renegade', 'Jeep-Wagoneer', 'Jeep-Wrangler', 'Jeep-Wrangler-4xe', 'Jeep-Wrangler-JK', 'Kawasaki-W800', 'Kia', 'Kia-Cadenza', 'Kia-Carens', 'Kia-Carnival', 'Kia-Ceed', 'Kia-Cerato', 'Kia-EV3', 'Kia-EV6', 'Kia-EV9', 'Kia-Forte', 'Kia-K4', 'Kia-K5', 'Kia-Niro', 'Kia-Niro-EV', 'Kia-Optima', 'Kia-Picanto', 'Kia-Rio', 'Kia-Rondo', 'Kia-Seltos', 'Kia-Sonet', 'Kia-Sorento', 'Kia-Soul', 'Kia-Sportage', 'Kia-Sportage-HEV', 'Kia-Stinger', 'Kia-Stonic', 'Kia-Telluride', 'KTM', 'KTM-RC', 'KTM-RC-390', 'Lamborghini', 'Lamborghini-Huracan-evo', 'Land-Rover', 'Land-Rover-Defender', 'Land-Rover-LR4', 'Land-Rover-Range-Rover', 'Land-Rover-Range-Rover-Velar', 'Landrover', 'Lexus', 'Lexus-CT-200h', 'Lexus-ES', 'Lexus-ES-300h', 'Lexus-GX', 'Lexus-GX-460', 'Lexus-GX-470', 'Lexus-IS', 'Lexus-LC-500', 'Lexus-LS', 'Lexus-NX-350h', 'Lexus-RX', 'Lexus-RX-350', 'Lexus-RX-450h', 'Lexus-UX', 'Lincoln', 'Lincoln-Aviator', 'Lincoln-Corsair', 'Lincoln-MKX', 'Lincoln-MKZ', 'Lincoln-Nautilus', 'Lincoln-Navigator', 'Lincoln-Town-Car', 'Lotus', 'Lucid-Air', 'Maruti', 'Maruti-Celerio', 'Maruti-Suzuki-Fronx-Delta', 'Maserati', 'Maserati-Levante', 'Maxus', 'Maxus-eDeliver-3', 'Mazda', 'Mazda-2', 'Mazda-3', 'Mazda-5', 'Mazda-6', 'Mazda-BT50', 'Mazda-CX-3', 'Mazda-CX-30', 'Mazda-CX-5', 'Mazda-CX-50', 'Mazda-CX-60', 'Mazda-CX-7', 'Mazda-CX-70', 'Mazda-CX-9', 'Mazda-CX-90', 'Mazda-MX-30', 'Mazda-MX-5', 'Mazda-RX-7', 'Mazda-Tribute', 'McLaren-Artura', 'Mercedes-Benz', 'Mercedes-Benz-A-180', 'Mercedes-Benz-A-200', 'Mercedes-Benz-A-220', 'Mercedes-Benz-AMG-A-45', 'Mercedes-Benz-AMG-GT', 'Mercedes-Benz-C-180', 'Mercedes-Benz-C-Class', 'Mercedes-Benz-C200d', 'Mercedes-Benz-CLA-200', 'Mercedes-Benz-CLA-Class', 'Mercedes-Benz-CLS', 'Mercedes-Benz-E-Class', 'Mercedes-Benz-E180', 'Mercedes-Benz-EQA', 'Mercedes-Benz-EQB', 'Mercedes-Benz-EQE', 'Mercedes-Benz-EQS', 'Mercedes-Benz-EQS-Class-Sedan', 'Mercedes-Benz-G-Class', 'Mercedes-Benz-GLA250', 'Mercedes-Benz-GLB-250', 'Mercedes-Benz-GLC-Class', 'Mercedes-Benz-Ml63', 'Mercedes-Benz-S-Class', 'MG', 'MG-Comet', 'MG-Hector', 'MG-HS', 'MG-MG4', 'MG-One', 'MG-ZS', 'MG-ZS-EV', 'MINI', 'MINI-Clubman', 'MINI-Cooper', 'MINI-Cooper-S', 'MINI-Cooper-SE', 'MINI-Countryman', 'MINI-Hardtop', 'MINI-JCW', 'Mitsubishi', 'Mitsubishi-ASX', 'Mitsubishi-Challenger', 'Mitsubishi-Eclipse-Cross', 'Mitsubishi-Eclipse-Cross-PHEV', 'Mitsubishi-Lancer', 'Mitsubishi-Mirage', 'Mitsubishi-Outlander', 'Mitsubishi-Outlander-PHEV', 'Mitsubishi-Outlander-Sport', 'Mitsubishi-Pajero', 'Mitsubishi-RVR', 'Mitsubishi-Triton', 'Nissan', 'Nissan-Altima', 'Nissan-ARIYA', 'Nissan-Armada', 'Nissan-Frontier', 'Nissan-Juke', 'Nissan-Kicks', 'Nissan-Leaf', 'Nissan-Maxima', 'Nissan-Murano', 'Nissan-Navara', 'Nissan-Pathfinder', 'Nissan-Patrol', 'Nissan-Pulsar', 'Nissan-Qashqai', 'Nissan-Rogue', 'Nissan-Rogue-Sport', 'Nissan-Sentra', 'Nissan-Titan', 'Nissan-Versa', 'Nissan-X-Trail', 'Nissan-Xterra', 'NissanInfiniti', 'Omoda', 'Omoda-Omoda-5-EV', 'Perodua-Bezza', 'Peugeot', 'Peugeot-2008', 'Peugeot-205', 'Peugeot-206', 'Peugeot-207', 'Peugeot-208', 'Peugeot-3008', 'Peugeot-307', 'Peugeot-308', 'Peugeot-308-Hybrid', 'Peugeot-407', 'Peugeot-505', 'Peugeot-508', 'Peugeot-e-208', 'Peugeot-Expert', 'Polestar', 'Polestar-2', 'Polestar-3', 'Polestar-4', 'Pontiac-Vibe', 'Porsche', 'Porsche-718', 'Porsche-911', 'Porsche-981-Cayman', 'Porsche-Boxster', 'Porsche-Cayenne', 'Porsche-Cayman', 'Porsche-Macan', 'Porsche-Macan-Electric', 'Porsche-Panamera', 'Porsche-Taycan', 'Ram', 'Ram-1500', 'Ram-2500', 'Ram-3500', 'Renault', 'Renault-Captur', 'Renault-Clio', 'Renault-Clio-III', 'Renault-Clio-V', 'Renault-Kadjar', 'Renault-Koleos', 'Renault-Kwid', 'Renault-Megane', 'Renault-Megane-E-Tech', 'Renault-Symbol', 'Renault-ZOE', 'Rivian', 'Rivian-R1S', 'Rivian-R1T', 'Rolls-Royce', 'Saab', 'Saab-9-3', 'Saab-9-5', 'SAEJ1979', 'Scion', 'Scion-FR-S', 'Scion-iQ', 'Scion-tC', 'Scion-xB', 'SEAT', 'Seat-Alhambra', 'Seat-Altea', 'Seat-Arona', 'Seat-Ateca', 'Seat-Ibiza', 'Seat-Leon', 'Seat-Mii-Electric', 'Seat-Tarraco', 'Skoda', 'Skoda-Elroq', 'Skoda-Enyaq', 'Skoda-Fabia', 'Skoda-Kamiq', 'Skoda-Kodiaq', 'Skoda-Octavia', 'Skoda-Rapid', 'Skoda-Scala', 'Skoda-Superb', 'smart', 'smart-fortwo', 'Smart-Smart-1', 'Subaru', 'Subaru-Ascent', 'Subaru-Baja', 'Subaru-BRZ', 'Subaru-Crosstrek', 'Subaru-Forester', 'Subaru-Impreza', 'Subaru-Legacy', 'Subaru-Outback', 'Subaru-Solterra', 'Subaru-Tribeca', 'Subaru-WRX', 'Subaru-WRX-STI', 'Suzuki', 'Suzuki-Alto', 'Suzuki-Baleno', 'Suzuki-Ignis', 'Suzuki-Jimny', 'Suzuki-Splash', 'Suzuki-Swift', 'Suzuki-SX4', 'Suzuki-Vitara', 'Tata', 'Tata-Harrier', 'Tata-Tiago', 'Tesla', 'Tesla-Cybertruck', 'Tesla-Model-3', 'Tesla-Model-S', 'Tesla-Model-X', 'Tesla-Model-Y', 'Toyota', 'Toyota-4Runner', 'Toyota-Alphard', 'Toyota-Aqua', 'Toyota-Auris', 'Toyota-Avalon', 'Toyota-Aygo', 'Toyota-bZ4X', 'Toyota-C-HR', 'Toyota-Camry', 'Toyota-Camry-Hybrid', 'Toyota-Celica', 'Toyota-Corolla', 'Toyota-Corolla-Cross', 'Toyota-Corolla-Hybrid', 'Toyota-Corolla-iM', 'Toyota-Crown', 'Toyota-Crown-Signia', 'Toyota-FJ-Cruiser', 'Toyota-Fortuner', 'Toyota-GR-Corolla', 'Toyota-GR-Supra', 'Toyota-GR86', 'Toyota-Grand-Highlander', 'Toyota-Grand-Highlander-Hybrid', 'Toyota-Highlander', 'Toyota-Hilux', 'Toyota-Innova', 'Toyota-iQ', 'Toyota-Ist', 'Toyota-Land-Cruiser', 'Toyota-Land-Cruiser-Hybrid', 'Toyota-Matrix', 'Toyota-Mirai', 'Toyota-MR2', 'Toyota-Prius', 'Toyota-Prius-Prime', 'Toyota-Prius-v', 'Toyota-RAV4', 'Toyota-RAV4-Hybrid', 'Toyota-RAV4-Prime', 'Toyota-Rush', 'Toyota-Sequoia', 'Toyota-Sienna', 'Toyota-Sienna-Hybrid', 'Toyota-Tacoma', 'Toyota-Tundra', 'Toyota-Venza', 'Toyota-Venza-Hybrid', 'Toyota-Yaris', 'Toyota-Yaris-Cross', 'Toyota-Yaris-iA', 'Vauxhall-Astra', 'Vauxhall-Mokka-e', 'VauxhallOpel', 'VauxhallOpel-Ampera', 'VauxhallOpel-Astra', 'VauxhallOpel-Corsa-e', 'VauxhallOpel-Crossland', 'VauxhallOpel-Grandland-X', 'VauxhallOpel-Insignia', 'VauxhallOpel-Mokka', 'VauxhallOpel-Zafira-B', 'Volkswagen', 'Volkswagen-Amarok', 'Volkswagen-Arteon', 'Volkswagen-Atlas', 'Volkswagen-Beetle', 'Volkswagen-CC', 'Volkswagen-Crafter', 'Volkswagen-e-Golf', 'Volkswagen-Golf', 'Volkswagen-GTE', 'Volkswagen-ID-Buzz', 'Volkswagen-ID.4', 'Volkswagen-ID3', 'Volkswagen-ID5', 'Volkswagen-ID7-Tourer', 'Volkswagen-Jetta', 'Volkswagen-Jetta-GLI', 'Volkswagen-Nivus', 'Volkswagen-Passat', 'Volkswagen-Passat-B8', 'Volkswagen-Passat-Variant', 'Volkswagen-Polo', 'Volkswagen-Polo-V', 'Volkswagen-R32', 'Volkswagen-Rabbit', 'Volkswagen-Scirocco', 'Volkswagen-Sharan', 'Volkswagen-T-Cross', 'Volkswagen-T-Roc', 'Volkswagen-T5', 'Volkswagen-Taigo', 'Volkswagen-Taos', 'Volkswagen-Tiguan', 'Volkswagen-Touareg', 'Volkswagen-Touran', 'Volkswagen-Up', 'Volkswagen-Virtus', 'Volvo', 'Volvo-C30', 'Volvo-EX30', 'Volvo-S40', 'Volvo-S60', 'Volvo-S70', 'Volvo-S90', 'Volvo-V50', 'Volvo-V60', 'Volvo-V70', 'Volvo-V90-Cross-Country', 'Volvo-V90CC', 'Volvo-XC40', 'Volvo-XC40-Recharge', 'Volvo-XC40-T4-Recharge', 'Volvo-XC60', 'Volvo-XC90', 'Voyah-Free', 'VW-Golf', 'Zeekr-009']
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
    return f"signal_{index}"


def _command_desc(signal, entry):
    parts = []
    for key in ("name", "id", "path"):
        value = signal.get(key)
        if value:
            parts.append(str(value))
            break
    hdr = entry.get("hdr")
    if hdr:
        parts.append(f"hdr={hdr}")
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
    return {
        "service_hex": service_hex,
        "pid_hex": pid_hex,
        "command_hex": service_hex + pid_hex,
        "response_prefix_hex": f"{int(service_hex, 16) + 0x40:02X}{pid_hex}",
    }


def _expected_bytes(signals):
    bit_end = 0
    for signal in signals:
        fmt = signal.get("fmt", {})
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
        raise ValueError(f"bit range out of payload: bix={bix} len={bitlen} total={total_bits}")
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

    aliases = {
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
    }

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
    return f"https://raw.githubusercontent.com/OBDb/{source_name}/master/signalsets/v3/default.json"


def _load_source_data(source_name):
    if source_name not in _SOURCE_NAME_SET:
        raise KeyError(f"unknown OBDb source: {source_name}")

    url = _source_url(source_name)

    try:
        with urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(f"cannot fetch {source_name} signalset from {url}: HTTP {e.code}") from e
    except URLError as e:
        raise RuntimeError(f"cannot fetch {source_name} signalset from {url}: {e.reason}") from e


_ORIGINAL_SOURCE_NAMES = {}
_ORIGINAL_COMMAND_NAMES = {}
_LOADED_SOURCE_COMMANDS = {}


def _build_source_commands(source_name, source_ident):
    cached = _LOADED_SOURCE_COMMANDS.get(source_ident)
    if cached is not None:
        return cached

    data = _load_source_data(source_name)
    commands = {}
    original_names = {}
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
            fmt = signal.get("fmt", {})
            bitlen = int(fmt.get("len", 0))
            if bitlen <= 0:
                continue

            name_original = signal.get("id") or signal.get("name") or signal.get("path") or f"signal_{index}"
            name_ident = _signal_py_name(signal, index)

            if name_ident in used_names:
                suffix = 2
                while f"{name_ident}_{suffix}" in used_names:
                    suffix += 1
                name_ident = f"{name_ident}_{suffix}"
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

            kwargs = {}
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
        raise AttributeError(f"{self._source_ident}.{name}")

    def __dir__(self):
        self._load()
        return sorted(set(super().__dir__()) | set(self.__dict__.keys()))

    def __repr__(self):
        state = "loaded" if self._loaded else "lazy"
        return f"<_LazyNamespace {self._source_ident} ({state})>"

Abarth = _LazyNamespace("Abarth", "Abarth")
_ORIGINAL_SOURCE_NAMES["Abarth"] = "Abarth"
_ORIGINAL_COMMAND_NAMES["Abarth"] = {}

Abarth_500 = _LazyNamespace("Abarth-500", "Abarth_500")
_ORIGINAL_SOURCE_NAMES["Abarth_500"] = "Abarth-500"
_ORIGINAL_COMMAND_NAMES["Abarth_500"] = {}

Abarth_595 = _LazyNamespace("Abarth-595", "Abarth_595")
_ORIGINAL_SOURCE_NAMES["Abarth_595"] = "Abarth-595"
_ORIGINAL_COMMAND_NAMES["Abarth_595"] = {}

Acura = _LazyNamespace("Acura", "Acura")
_ORIGINAL_SOURCE_NAMES["Acura"] = "Acura"
_ORIGINAL_COMMAND_NAMES["Acura"] = {}

Acura_CL = _LazyNamespace("Acura-CL", "Acura_CL")
_ORIGINAL_SOURCE_NAMES["Acura_CL"] = "Acura-CL"
_ORIGINAL_COMMAND_NAMES["Acura_CL"] = {}

Acura_ILX = _LazyNamespace("Acura-ILX", "Acura_ILX")
_ORIGINAL_SOURCE_NAMES["Acura_ILX"] = "Acura-ILX"
_ORIGINAL_COMMAND_NAMES["Acura_ILX"] = {}

Acura_Integra = _LazyNamespace("Acura-Integra", "Acura_Integra")
_ORIGINAL_SOURCE_NAMES["Acura_Integra"] = "Acura-Integra"
_ORIGINAL_COMMAND_NAMES["Acura_Integra"] = {}

Acura_MDX = _LazyNamespace("Acura-MDX", "Acura_MDX")
_ORIGINAL_SOURCE_NAMES["Acura_MDX"] = "Acura-MDX"
_ORIGINAL_COMMAND_NAMES["Acura_MDX"] = {}

Acura_RDX = _LazyNamespace("Acura-RDX", "Acura_RDX")
_ORIGINAL_SOURCE_NAMES["Acura_RDX"] = "Acura-RDX"
_ORIGINAL_COMMAND_NAMES["Acura_RDX"] = {}

Acura_TL = _LazyNamespace("Acura-TL", "Acura_TL")
_ORIGINAL_SOURCE_NAMES["Acura_TL"] = "Acura-TL"
_ORIGINAL_COMMAND_NAMES["Acura_TL"] = {}

Acura_TLX = _LazyNamespace("Acura-TLX", "Acura_TLX")
_ORIGINAL_SOURCE_NAMES["Acura_TLX"] = "Acura-TLX"
_ORIGINAL_COMMAND_NAMES["Acura_TLX"] = {}

Acura_TSX = _LazyNamespace("Acura-TSX", "Acura_TSX")
_ORIGINAL_SOURCE_NAMES["Acura_TSX"] = "Acura-TSX"
_ORIGINAL_COMMAND_NAMES["Acura_TSX"] = {}

Acura_ZDX = _LazyNamespace("Acura-ZDX", "Acura_ZDX")
_ORIGINAL_SOURCE_NAMES["Acura_ZDX"] = "Acura-ZDX"
_ORIGINAL_COMMAND_NAMES["Acura_ZDX"] = {}

Aiways = _LazyNamespace("Aiways", "Aiways")
_ORIGINAL_SOURCE_NAMES["Aiways"] = "Aiways"
_ORIGINAL_COMMAND_NAMES["Aiways"] = {}

Aiways_U5 = _LazyNamespace("Aiways-U5", "Aiways_U5")
_ORIGINAL_SOURCE_NAMES["Aiways_U5"] = "Aiways-U5"
_ORIGINAL_COMMAND_NAMES["Aiways_U5"] = {}

Alfa_Romeo = _LazyNamespace("Alfa-Romeo", "Alfa_Romeo")
_ORIGINAL_SOURCE_NAMES["Alfa_Romeo"] = "Alfa-Romeo"
_ORIGINAL_COMMAND_NAMES["Alfa_Romeo"] = {}

Alfa_Romeo_Giulia = _LazyNamespace("Alfa-Romeo-Giulia", "Alfa_Romeo_Giulia")
_ORIGINAL_SOURCE_NAMES["Alfa_Romeo_Giulia"] = "Alfa-Romeo-Giulia"
_ORIGINAL_COMMAND_NAMES["Alfa_Romeo_Giulia"] = {}

Alfa_Romeo_Giulietta = _LazyNamespace("Alfa-Romeo-Giulietta", "Alfa_Romeo_Giulietta")
_ORIGINAL_SOURCE_NAMES["Alfa_Romeo_Giulietta"] = "Alfa-Romeo-Giulietta"
_ORIGINAL_COMMAND_NAMES["Alfa_Romeo_Giulietta"] = {}

Alfa_Romeo_MiTo = _LazyNamespace("Alfa-Romeo-MiTo", "Alfa_Romeo_MiTo")
_ORIGINAL_SOURCE_NAMES["Alfa_Romeo_MiTo"] = "Alfa-Romeo-MiTo"
_ORIGINAL_COMMAND_NAMES["Alfa_Romeo_MiTo"] = {}

Alfa_Romeo_Tonale = _LazyNamespace("Alfa-Romeo-Tonale", "Alfa_Romeo_Tonale")
_ORIGINAL_SOURCE_NAMES["Alfa_Romeo_Tonale"] = "Alfa-Romeo-Tonale"
_ORIGINAL_COMMAND_NAMES["Alfa_Romeo_Tonale"] = {}

Alpine = _LazyNamespace("Alpine", "Alpine")
_ORIGINAL_SOURCE_NAMES["Alpine"] = "Alpine"
_ORIGINAL_COMMAND_NAMES["Alpine"] = {}

Aston_Martin_Vantage = _LazyNamespace("Aston-Martin-Vantage", "Aston_Martin_Vantage")
_ORIGINAL_SOURCE_NAMES["Aston_Martin_Vantage"] = "Aston-Martin-Vantage"
_ORIGINAL_COMMAND_NAMES["Aston_Martin_Vantage"] = {}

Audi = _LazyNamespace("Audi", "Audi")
_ORIGINAL_SOURCE_NAMES["Audi"] = "Audi"
_ORIGINAL_COMMAND_NAMES["Audi"] = {}

Audi_A1 = _LazyNamespace("Audi-A1", "Audi_A1")
_ORIGINAL_SOURCE_NAMES["Audi_A1"] = "Audi-A1"
_ORIGINAL_COMMAND_NAMES["Audi_A1"] = {}

Audi_A3 = _LazyNamespace("Audi-A3", "Audi_A3")
_ORIGINAL_SOURCE_NAMES["Audi_A3"] = "Audi-A3"
_ORIGINAL_COMMAND_NAMES["Audi_A3"] = {}

Audi_A3_e_tron = _LazyNamespace("Audi-A3-e-tron", "Audi_A3_e_tron")
_ORIGINAL_SOURCE_NAMES["Audi_A3_e_tron"] = "Audi-A3-e-tron"
_ORIGINAL_COMMAND_NAMES["Audi_A3_e_tron"] = {}

Audi_A4 = _LazyNamespace("Audi-A4", "Audi_A4")
_ORIGINAL_SOURCE_NAMES["Audi_A4"] = "Audi-A4"
_ORIGINAL_COMMAND_NAMES["Audi_A4"] = {}

Audi_A5 = _LazyNamespace("Audi-A5", "Audi_A5")
_ORIGINAL_SOURCE_NAMES["Audi_A5"] = "Audi-A5"
_ORIGINAL_COMMAND_NAMES["Audi_A5"] = {}

Audi_A6 = _LazyNamespace("Audi-A6", "Audi_A6")
_ORIGINAL_SOURCE_NAMES["Audi_A6"] = "Audi-A6"
_ORIGINAL_COMMAND_NAMES["Audi_A6"] = {}

Audi_A7 = _LazyNamespace("Audi-A7", "Audi_A7")
_ORIGINAL_SOURCE_NAMES["Audi_A7"] = "Audi-A7"
_ORIGINAL_COMMAND_NAMES["Audi_A7"] = {}

Audi_e_tron = _LazyNamespace("Audi-e-tron", "Audi_e_tron")
_ORIGINAL_SOURCE_NAMES["Audi_e_tron"] = "Audi-e-tron"
_ORIGINAL_COMMAND_NAMES["Audi_e_tron"] = {}

Audi_Q2 = _LazyNamespace("Audi-Q2", "Audi_Q2")
_ORIGINAL_SOURCE_NAMES["Audi_Q2"] = "Audi-Q2"
_ORIGINAL_COMMAND_NAMES["Audi_Q2"] = {}

Audi_Q3 = _LazyNamespace("Audi-Q3", "Audi_Q3")
_ORIGINAL_SOURCE_NAMES["Audi_Q3"] = "Audi-Q3"
_ORIGINAL_COMMAND_NAMES["Audi_Q3"] = {}

Audi_Q4_e_tron = _LazyNamespace("Audi-Q4-e-tron", "Audi_Q4_e_tron")
_ORIGINAL_SOURCE_NAMES["Audi_Q4_e_tron"] = "Audi-Q4-e-tron"
_ORIGINAL_COMMAND_NAMES["Audi_Q4_e_tron"] = {}

Audi_Q5 = _LazyNamespace("Audi-Q5", "Audi_Q5")
_ORIGINAL_SOURCE_NAMES["Audi_Q5"] = "Audi-Q5"
_ORIGINAL_COMMAND_NAMES["Audi_Q5"] = {}

Audi_Q7 = _LazyNamespace("Audi-Q7", "Audi_Q7")
_ORIGINAL_SOURCE_NAMES["Audi_Q7"] = "Audi-Q7"
_ORIGINAL_COMMAND_NAMES["Audi_Q7"] = {}

Audi_Q8 = _LazyNamespace("Audi-Q8", "Audi_Q8")
_ORIGINAL_SOURCE_NAMES["Audi_Q8"] = "Audi-Q8"
_ORIGINAL_COMMAND_NAMES["Audi_Q8"] = {}

Audi_Q8_e_tron = _LazyNamespace("Audi-Q8-e-tron", "Audi_Q8_e_tron")
_ORIGINAL_SOURCE_NAMES["Audi_Q8_e_tron"] = "Audi-Q8-e-tron"
_ORIGINAL_COMMAND_NAMES["Audi_Q8_e_tron"] = {}

Audi_RS_3 = _LazyNamespace("Audi-RS-3", "Audi_RS_3")
_ORIGINAL_SOURCE_NAMES["Audi_RS_3"] = "Audi-RS-3"
_ORIGINAL_COMMAND_NAMES["Audi_RS_3"] = {}

Audi_RS_5 = _LazyNamespace("Audi-RS-5", "Audi_RS_5")
_ORIGINAL_SOURCE_NAMES["Audi_RS_5"] = "Audi-RS-5"
_ORIGINAL_COMMAND_NAMES["Audi_RS_5"] = {}

Audi_RS_e_tron = _LazyNamespace("Audi-RS-e-tron", "Audi_RS_e_tron")
_ORIGINAL_SOURCE_NAMES["Audi_RS_e_tron"] = "Audi-RS-e-tron"
_ORIGINAL_COMMAND_NAMES["Audi_RS_e_tron"] = {}

Audi_S3 = _LazyNamespace("Audi-S3", "Audi_S3")
_ORIGINAL_SOURCE_NAMES["Audi_S3"] = "Audi-S3"
_ORIGINAL_COMMAND_NAMES["Audi_S3"] = {}

Audi_S4 = _LazyNamespace("Audi-S4", "Audi_S4")
_ORIGINAL_SOURCE_NAMES["Audi_S4"] = "Audi-S4"
_ORIGINAL_COMMAND_NAMES["Audi_S4"] = {}

Audi_S5 = _LazyNamespace("Audi-S5", "Audi_S5")
_ORIGINAL_SOURCE_NAMES["Audi_S5"] = "Audi-S5"
_ORIGINAL_COMMAND_NAMES["Audi_S5"] = {}

Audi_S6 = _LazyNamespace("Audi-S6", "Audi_S6")
_ORIGINAL_SOURCE_NAMES["Audi_S6"] = "Audi-S6"
_ORIGINAL_COMMAND_NAMES["Audi_S6"] = {}

Audi_SQ2 = _LazyNamespace("Audi-SQ2", "Audi_SQ2")
_ORIGINAL_SOURCE_NAMES["Audi_SQ2"] = "Audi-SQ2"
_ORIGINAL_COMMAND_NAMES["Audi_SQ2"] = {}

Audi_SQ5 = _LazyNamespace("Audi-SQ5", "Audi_SQ5")
_ORIGINAL_SOURCE_NAMES["Audi_SQ5"] = "Audi-SQ5"
_ORIGINAL_COMMAND_NAMES["Audi_SQ5"] = {}

Audi_SQ7 = _LazyNamespace("Audi-SQ7", "Audi_SQ7")
_ORIGINAL_SOURCE_NAMES["Audi_SQ7"] = "Audi-SQ7"
_ORIGINAL_COMMAND_NAMES["Audi_SQ7"] = {}

Audi_TT = _LazyNamespace("Audi-TT", "Audi_TT")
_ORIGINAL_SOURCE_NAMES["Audi_TT"] = "Audi-TT"
_ORIGINAL_COMMAND_NAMES["Audi_TT"] = {}

Bentley = _LazyNamespace("Bentley", "Bentley")
_ORIGINAL_SOURCE_NAMES["Bentley"] = "Bentley"
_ORIGINAL_COMMAND_NAMES["Bentley"] = {}

Bentley_Bentayga = _LazyNamespace("Bentley-Bentayga", "Bentley_Bentayga")
_ORIGINAL_SOURCE_NAMES["Bentley_Bentayga"] = "Bentley-Bentayga"
_ORIGINAL_COMMAND_NAMES["Bentley_Bentayga"] = {}

BMW = _LazyNamespace("BMW", "BMW")
_ORIGINAL_SOURCE_NAMES["BMW"] = "BMW"
_ORIGINAL_COMMAND_NAMES["BMW"] = {}

BMW_1_Series = _LazyNamespace("BMW-1-Series", "BMW_1_Series")
_ORIGINAL_SOURCE_NAMES["BMW_1_Series"] = "BMW-1-Series"
_ORIGINAL_COMMAND_NAMES["BMW_1_Series"] = {}

BMW_116i = _LazyNamespace("BMW-116i", "BMW_116i")
_ORIGINAL_SOURCE_NAMES["BMW_116i"] = "BMW-116i"
_ORIGINAL_COMMAND_NAMES["BMW_116i"] = {}

BMW_2_Grand_Coupe = _LazyNamespace("BMW-2-Grand-Coupe", "BMW_2_Grand_Coupe")
_ORIGINAL_SOURCE_NAMES["BMW_2_Grand_Coupe"] = "BMW-2-Grand-Coupe"
_ORIGINAL_COMMAND_NAMES["BMW_2_Grand_Coupe"] = {}

BMW_2_Series = _LazyNamespace("BMW-2-Series", "BMW_2_Series")
_ORIGINAL_SOURCE_NAMES["BMW_2_Series"] = "BMW-2-Series"
_ORIGINAL_COMMAND_NAMES["BMW_2_Series"] = {}

BMW_230e = _LazyNamespace("BMW-230e", "BMW_230e")
_ORIGINAL_SOURCE_NAMES["BMW_230e"] = "BMW-230e"
_ORIGINAL_COMMAND_NAMES["BMW_230e"] = {}

BMW_3_Series = _LazyNamespace("BMW-3-Series", "BMW_3_Series")
_ORIGINAL_SOURCE_NAMES["BMW_3_Series"] = "BMW-3-Series"
_ORIGINAL_COMMAND_NAMES["BMW_3_Series"] = {}

BMW_3_Series_eDrive = _LazyNamespace("BMW-3-Series-eDrive", "BMW_3_Series_eDrive")
_ORIGINAL_SOURCE_NAMES["BMW_3_Series_eDrive"] = "BMW-3-Series-eDrive"
_ORIGINAL_COMMAND_NAMES["BMW_3_Series_eDrive"] = {}

BMW_330e = _LazyNamespace("BMW-330e", "BMW_330e")
_ORIGINAL_SOURCE_NAMES["BMW_330e"] = "BMW-330e"
_ORIGINAL_COMMAND_NAMES["BMW_330e"] = {}

BMW_4_Series = _LazyNamespace("BMW-4-Series", "BMW_4_Series")
_ORIGINAL_SOURCE_NAMES["BMW_4_Series"] = "BMW-4-Series"
_ORIGINAL_COMMAND_NAMES["BMW_4_Series"] = {}

BMW_5_Series = _LazyNamespace("BMW-5-Series", "BMW_5_Series")
_ORIGINAL_SOURCE_NAMES["BMW_5_Series"] = "BMW-5-Series"
_ORIGINAL_COMMAND_NAMES["BMW_5_Series"] = {}

BMW_5_Series_xDrive = _LazyNamespace("BMW-5-Series-xDrive", "BMW_5_Series_xDrive")
_ORIGINAL_SOURCE_NAMES["BMW_5_Series_xDrive"] = "BMW-5-Series-xDrive"
_ORIGINAL_COMMAND_NAMES["BMW_5_Series_xDrive"] = {}

BMW_640i_f13 = _LazyNamespace("BMW-640i-f13", "BMW_640i_f13")
_ORIGINAL_SOURCE_NAMES["BMW_640i_f13"] = "BMW-640i-f13"
_ORIGINAL_COMMAND_NAMES["BMW_640i_f13"] = {}

BMW_7_Series = _LazyNamespace("BMW-7-Series", "BMW_7_Series")
_ORIGINAL_SOURCE_NAMES["BMW_7_Series"] = "BMW-7-Series"
_ORIGINAL_COMMAND_NAMES["BMW_7_Series"] = {}

BMW_840i = _LazyNamespace("BMW-840i", "BMW_840i")
_ORIGINAL_SOURCE_NAMES["BMW_840i"] = "BMW-840i"
_ORIGINAL_COMMAND_NAMES["BMW_840i"] = {}

BMW_E91 = _LazyNamespace("BMW-E91", "BMW_E91")
_ORIGINAL_SOURCE_NAMES["BMW_E91"] = "BMW-E91"
_ORIGINAL_COMMAND_NAMES["BMW_E91"] = {}

BMW_E92 = _LazyNamespace("BMW-E92", "BMW_E92")
_ORIGINAL_SOURCE_NAMES["BMW_E92"] = "BMW-E92"
_ORIGINAL_COMMAND_NAMES["BMW_E92"] = {}

BMW_F34 = _LazyNamespace("BMW-F34", "BMW_F34")
_ORIGINAL_SOURCE_NAMES["BMW_F34"] = "BMW-F34"
_ORIGINAL_COMMAND_NAMES["BMW_F34"] = {}

BMW_i3 = _LazyNamespace("BMW-i3", "BMW_i3")
_ORIGINAL_SOURCE_NAMES["BMW_i3"] = "BMW-i3"
_ORIGINAL_COMMAND_NAMES["BMW_i3"] = {}

BMW_i3s = _LazyNamespace("BMW-i3s", "BMW_i3s")
_ORIGINAL_SOURCE_NAMES["BMW_i3s"] = "BMW-i3s"
_ORIGINAL_COMMAND_NAMES["BMW_i3s"] = {}

BMW_i4 = _LazyNamespace("BMW-i4", "BMW_i4")
_ORIGINAL_SOURCE_NAMES["BMW_i4"] = "BMW-i4"
_ORIGINAL_COMMAND_NAMES["BMW_i4"] = {}

BMW_i5 = _LazyNamespace("BMW-i5", "BMW_i5")
_ORIGINAL_SOURCE_NAMES["BMW_i5"] = "BMW-i5"
_ORIGINAL_COMMAND_NAMES["BMW_i5"] = {}

BMW_i8 = _LazyNamespace("BMW-i8", "BMW_i8")
_ORIGINAL_SOURCE_NAMES["BMW_i8"] = "BMW-i8"
_ORIGINAL_COMMAND_NAMES["BMW_i8"] = {}

BMW_iX = _LazyNamespace("BMW-iX", "BMW_iX")
_ORIGINAL_SOURCE_NAMES["BMW_iX"] = "BMW-iX"
_ORIGINAL_COMMAND_NAMES["BMW_iX"] = {}

BMW_iX3 = _LazyNamespace("BMW-iX3", "BMW_iX3")
_ORIGINAL_SOURCE_NAMES["BMW_iX3"] = "BMW-iX3"
_ORIGINAL_COMMAND_NAMES["BMW_iX3"] = {}

BMW_M2 = _LazyNamespace("BMW-M2", "BMW_M2")
_ORIGINAL_SOURCE_NAMES["BMW_M2"] = "BMW-M2"
_ORIGINAL_COMMAND_NAMES["BMW_M2"] = {}

BMW_M3 = _LazyNamespace("BMW-M3", "BMW_M3")
_ORIGINAL_SOURCE_NAMES["BMW_M3"] = "BMW-M3"
_ORIGINAL_COMMAND_NAMES["BMW_M3"] = {}

BMW_M4 = _LazyNamespace("BMW-M4", "BMW_M4")
_ORIGINAL_SOURCE_NAMES["BMW_M4"] = "BMW-M4"
_ORIGINAL_COMMAND_NAMES["BMW_M4"] = {}

BMW_M440i = _LazyNamespace("BMW-M440i", "BMW_M440i")
_ORIGINAL_SOURCE_NAMES["BMW_M440i"] = "BMW-M440i"
_ORIGINAL_COMMAND_NAMES["BMW_M440i"] = {}

BMW_M5 = _LazyNamespace("BMW-M5", "BMW_M5")
_ORIGINAL_SOURCE_NAMES["BMW_M5"] = "BMW-M5"
_ORIGINAL_COMMAND_NAMES["BMW_M5"] = {}

BMW_X1 = _LazyNamespace("BMW-X1", "BMW_X1")
_ORIGINAL_SOURCE_NAMES["BMW_X1"] = "BMW-X1"
_ORIGINAL_COMMAND_NAMES["BMW_X1"] = {}

BMW_X2 = _LazyNamespace("BMW-X2", "BMW_X2")
_ORIGINAL_SOURCE_NAMES["BMW_X2"] = "BMW-X2"
_ORIGINAL_COMMAND_NAMES["BMW_X2"] = {}

BMW_X3 = _LazyNamespace("BMW-X3", "BMW_X3")
_ORIGINAL_SOURCE_NAMES["BMW_X3"] = "BMW-X3"
_ORIGINAL_COMMAND_NAMES["BMW_X3"] = {}

BMW_X4 = _LazyNamespace("BMW-X4", "BMW_X4")
_ORIGINAL_SOURCE_NAMES["BMW_X4"] = "BMW-X4"
_ORIGINAL_COMMAND_NAMES["BMW_X4"] = {}

BMW_X5 = _LazyNamespace("BMW-X5", "BMW_X5")
_ORIGINAL_SOURCE_NAMES["BMW_X5"] = "BMW-X5"
_ORIGINAL_COMMAND_NAMES["BMW_X5"] = {}

BMW_X7 = _LazyNamespace("BMW-X7", "BMW_X7")
_ORIGINAL_SOURCE_NAMES["BMW_X7"] = "BMW-X7"
_ORIGINAL_COMMAND_NAMES["BMW_X7"] = {}

BMW_Z3 = _LazyNamespace("BMW-Z3", "BMW_Z3")
_ORIGINAL_SOURCE_NAMES["BMW_Z3"] = "BMW-Z3"
_ORIGINAL_COMMAND_NAMES["BMW_Z3"] = {}

BMW_Z4 = _LazyNamespace("BMW-Z4", "BMW_Z4")
_ORIGINAL_SOURCE_NAMES["BMW_Z4"] = "BMW-Z4"
_ORIGINAL_COMMAND_NAMES["BMW_Z4"] = {}

Buick = _LazyNamespace("Buick", "Buick")
_ORIGINAL_SOURCE_NAMES["Buick"] = "Buick"
_ORIGINAL_COMMAND_NAMES["Buick"] = {}

Buick_Encore = _LazyNamespace("Buick-Encore", "Buick_Encore")
_ORIGINAL_SOURCE_NAMES["Buick_Encore"] = "Buick-Encore"
_ORIGINAL_COMMAND_NAMES["Buick_Encore"] = {}

Buick_Encore_GX = _LazyNamespace("Buick-Encore-GX", "Buick_Encore_GX")
_ORIGINAL_SOURCE_NAMES["Buick_Encore_GX"] = "Buick-Encore-GX"
_ORIGINAL_COMMAND_NAMES["Buick_Encore_GX"] = {}

Buick_Envision = _LazyNamespace("Buick-Envision", "Buick_Envision")
_ORIGINAL_SOURCE_NAMES["Buick_Envision"] = "Buick-Envision"
_ORIGINAL_COMMAND_NAMES["Buick_Envision"] = {}

Buick_LaCrosse = _LazyNamespace("Buick-LaCrosse", "Buick_LaCrosse")
_ORIGINAL_SOURCE_NAMES["Buick_LaCrosse"] = "Buick-LaCrosse"
_ORIGINAL_COMMAND_NAMES["Buick_LaCrosse"] = {}

BYD = _LazyNamespace("BYD", "BYD")
_ORIGINAL_SOURCE_NAMES["BYD"] = "BYD"
_ORIGINAL_COMMAND_NAMES["BYD"] = {}

BYD_Atto_3 = _LazyNamespace("BYD-Atto-3", "BYD_Atto_3")
_ORIGINAL_SOURCE_NAMES["BYD_Atto_3"] = "BYD-Atto-3"
_ORIGINAL_COMMAND_NAMES["BYD_Atto_3"] = {}

BYD_Dolphin_Mini = _LazyNamespace("BYD-Dolphin-Mini", "BYD_Dolphin_Mini")
_ORIGINAL_SOURCE_NAMES["BYD_Dolphin_Mini"] = "BYD-Dolphin-Mini"
_ORIGINAL_COMMAND_NAMES["BYD_Dolphin_Mini"] = {}

BYD_Sealion_6 = _LazyNamespace("BYD-Sealion-6", "BYD_Sealion_6")
_ORIGINAL_SOURCE_NAMES["BYD_Sealion_6"] = "BYD-Sealion-6"
_ORIGINAL_COMMAND_NAMES["BYD_Sealion_6"] = {}

Cadillac = _LazyNamespace("Cadillac", "Cadillac")
_ORIGINAL_SOURCE_NAMES["Cadillac"] = "Cadillac"
_ORIGINAL_COMMAND_NAMES["Cadillac"] = {}

Cadillac_CT4 = _LazyNamespace("Cadillac-CT4", "Cadillac_CT4")
_ORIGINAL_SOURCE_NAMES["Cadillac_CT4"] = "Cadillac-CT4"
_ORIGINAL_COMMAND_NAMES["Cadillac_CT4"] = {}

Cadillac_CT5 = _LazyNamespace("Cadillac-CT5", "Cadillac_CT5")
_ORIGINAL_SOURCE_NAMES["Cadillac_CT5"] = "Cadillac-CT5"
_ORIGINAL_COMMAND_NAMES["Cadillac_CT5"] = {}

Cadillac_CTS = _LazyNamespace("Cadillac-CTS", "Cadillac_CTS")
_ORIGINAL_SOURCE_NAMES["Cadillac_CTS"] = "Cadillac-CTS"
_ORIGINAL_COMMAND_NAMES["Cadillac_CTS"] = {}

Cadillac_ELR = _LazyNamespace("Cadillac-ELR", "Cadillac_ELR")
_ORIGINAL_SOURCE_NAMES["Cadillac_ELR"] = "Cadillac-ELR"
_ORIGINAL_COMMAND_NAMES["Cadillac_ELR"] = {}

Cadillac_Escalade = _LazyNamespace("Cadillac-Escalade", "Cadillac_Escalade")
_ORIGINAL_SOURCE_NAMES["Cadillac_Escalade"] = "Cadillac-Escalade"
_ORIGINAL_COMMAND_NAMES["Cadillac_Escalade"] = {}

Cadillac_LYRIQ = _LazyNamespace("Cadillac-LYRIQ", "Cadillac_LYRIQ")
_ORIGINAL_SOURCE_NAMES["Cadillac_LYRIQ"] = "Cadillac-LYRIQ"
_ORIGINAL_COMMAND_NAMES["Cadillac_LYRIQ"] = {}

Cadillac_XT5 = _LazyNamespace("Cadillac-XT5", "Cadillac_XT5")
_ORIGINAL_SOURCE_NAMES["Cadillac_XT5"] = "Cadillac-XT5"
_ORIGINAL_COMMAND_NAMES["Cadillac_XT5"] = {}

Changan = _LazyNamespace("Changan", "Changan")
_ORIGINAL_SOURCE_NAMES["Changan"] = "Changan"
_ORIGINAL_COMMAND_NAMES["Changan"] = {}

Chery = _LazyNamespace("Chery", "Chery")
_ORIGINAL_SOURCE_NAMES["Chery"] = "Chery"
_ORIGINAL_COMMAND_NAMES["Chery"] = {}

Chery_Tiggo_7_Pro = _LazyNamespace("Chery-Tiggo-7-Pro", "Chery_Tiggo_7_Pro")
_ORIGINAL_SOURCE_NAMES["Chery_Tiggo_7_Pro"] = "Chery-Tiggo-7-Pro"
_ORIGINAL_COMMAND_NAMES["Chery_Tiggo_7_Pro"] = {}

Chery_Tiggo_8 = _LazyNamespace("Chery-Tiggo-8", "Chery_Tiggo_8")
_ORIGINAL_SOURCE_NAMES["Chery_Tiggo_8"] = "Chery-Tiggo-8"
_ORIGINAL_COMMAND_NAMES["Chery_Tiggo_8"] = {}

Chevrolet = _LazyNamespace("Chevrolet", "Chevrolet")
_ORIGINAL_SOURCE_NAMES["Chevrolet"] = "Chevrolet"
_ORIGINAL_COMMAND_NAMES["Chevrolet"] = {}

Chevrolet_Aveo = _LazyNamespace("Chevrolet-Aveo", "Chevrolet_Aveo")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Aveo"] = "Chevrolet-Aveo"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Aveo"] = {}

Chevrolet_Blazer_EV = _LazyNamespace("Chevrolet-Blazer-EV", "Chevrolet_Blazer_EV")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Blazer_EV"] = "Chevrolet-Blazer-EV"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Blazer_EV"] = {}

Chevrolet_Bolt_EUV = _LazyNamespace("Chevrolet-Bolt-EUV", "Chevrolet_Bolt_EUV")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Bolt_EUV"] = "Chevrolet-Bolt-EUV"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Bolt_EUV"] = {}

Chevrolet_Bolt_EV = _LazyNamespace("Chevrolet-Bolt-EV", "Chevrolet_Bolt_EV")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Bolt_EV"] = "Chevrolet-Bolt-EV"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Bolt_EV"] = {}

Chevrolet_Camaro = _LazyNamespace("Chevrolet-Camaro", "Chevrolet_Camaro")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Camaro"] = "Chevrolet-Camaro"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Camaro"] = {}

Chevrolet_Celta = _LazyNamespace("Chevrolet-Celta", "Chevrolet_Celta")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Celta"] = "Chevrolet-Celta"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Celta"] = {}

Chevrolet_Cobalt = _LazyNamespace("Chevrolet-Cobalt", "Chevrolet_Cobalt")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Cobalt"] = "Chevrolet-Cobalt"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Cobalt"] = {}

Chevrolet_Colorado = _LazyNamespace("Chevrolet-Colorado", "Chevrolet_Colorado")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Colorado"] = "Chevrolet-Colorado"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Colorado"] = {}

Chevrolet_Corvette = _LazyNamespace("Chevrolet-Corvette", "Chevrolet_Corvette")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Corvette"] = "Chevrolet-Corvette"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Corvette"] = {}

Chevrolet_Cruze = _LazyNamespace("Chevrolet-Cruze", "Chevrolet_Cruze")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Cruze"] = "Chevrolet-Cruze"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Cruze"] = {}

Chevrolet_D_Max = _LazyNamespace("Chevrolet-D-Max", "Chevrolet_D_Max")
_ORIGINAL_SOURCE_NAMES["Chevrolet_D_Max"] = "Chevrolet-D-Max"
_ORIGINAL_COMMAND_NAMES["Chevrolet_D_Max"] = {}

Chevrolet_Equinox = _LazyNamespace("Chevrolet-Equinox", "Chevrolet_Equinox")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Equinox"] = "Chevrolet-Equinox"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Equinox"] = {}

Chevrolet_Equinox_EV = _LazyNamespace("Chevrolet-Equinox-EV", "Chevrolet_Equinox_EV")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Equinox_EV"] = "Chevrolet-Equinox-EV"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Equinox_EV"] = {}

Chevrolet_Express_Cargo = _LazyNamespace("Chevrolet-Express-Cargo", "Chevrolet_Express_Cargo")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Express_Cargo"] = "Chevrolet-Express-Cargo"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Express_Cargo"] = {}

Chevrolet_Impala = _LazyNamespace("Chevrolet-Impala", "Chevrolet_Impala")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Impala"] = "Chevrolet-Impala"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Impala"] = {}

Chevrolet_Malibu = _LazyNamespace("Chevrolet-Malibu", "Chevrolet_Malibu")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Malibu"] = "Chevrolet-Malibu"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Malibu"] = {}

Chevrolet_Montana = _LazyNamespace("Chevrolet-Montana", "Chevrolet_Montana")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Montana"] = "Chevrolet-Montana"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Montana"] = {}

Chevrolet_Prizm = _LazyNamespace("Chevrolet-Prizm", "Chevrolet_Prizm")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Prizm"] = "Chevrolet-Prizm"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Prizm"] = {}

Chevrolet_S_10 = _LazyNamespace("Chevrolet-S-10", "Chevrolet_S_10")
_ORIGINAL_SOURCE_NAMES["Chevrolet_S_10"] = "Chevrolet-S-10"
_ORIGINAL_COMMAND_NAMES["Chevrolet_S_10"] = {}

Chevrolet_Silverado = _LazyNamespace("Chevrolet-Silverado", "Chevrolet_Silverado")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Silverado"] = "Chevrolet-Silverado"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Silverado"] = {}

Chevrolet_Silverado_1500 = _LazyNamespace("Chevrolet-Silverado-1500", "Chevrolet_Silverado_1500")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Silverado_1500"] = "Chevrolet-Silverado-1500"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Silverado_1500"] = {}

Chevrolet_Silverado_2500 = _LazyNamespace("Chevrolet-Silverado-2500", "Chevrolet_Silverado_2500")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Silverado_2500"] = "Chevrolet-Silverado-2500"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Silverado_2500"] = {}

Chevrolet_Silverado_3500 = _LazyNamespace("Chevrolet-Silverado-3500", "Chevrolet_Silverado_3500")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Silverado_3500"] = "Chevrolet-Silverado-3500"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Silverado_3500"] = {}

Chevrolet_Silverado_EV = _LazyNamespace("Chevrolet-Silverado-EV", "Chevrolet_Silverado_EV")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Silverado_EV"] = "Chevrolet-Silverado-EV"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Silverado_EV"] = {}

Chevrolet_Sonic = _LazyNamespace("Chevrolet-Sonic", "Chevrolet_Sonic")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Sonic"] = "Chevrolet-Sonic"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Sonic"] = {}

Chevrolet_Spark = _LazyNamespace("Chevrolet-Spark", "Chevrolet_Spark")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Spark"] = "Chevrolet-Spark"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Spark"] = {}

Chevrolet_Tahoe = _LazyNamespace("Chevrolet-Tahoe", "Chevrolet_Tahoe")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Tahoe"] = "Chevrolet-Tahoe"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Tahoe"] = {}

Chevrolet_Trailblazer = _LazyNamespace("Chevrolet-Trailblazer", "Chevrolet_Trailblazer")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Trailblazer"] = "Chevrolet-Trailblazer"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Trailblazer"] = {}

Chevrolet_Traverse = _LazyNamespace("Chevrolet-Traverse", "Chevrolet_Traverse")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Traverse"] = "Chevrolet-Traverse"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Traverse"] = {}

Chevrolet_Trax = _LazyNamespace("Chevrolet-Trax", "Chevrolet_Trax")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Trax"] = "Chevrolet-Trax"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Trax"] = {}

Chevrolet_Volt = _LazyNamespace("Chevrolet-Volt", "Chevrolet_Volt")
_ORIGINAL_SOURCE_NAMES["Chevrolet_Volt"] = "Chevrolet-Volt"
_ORIGINAL_COMMAND_NAMES["Chevrolet_Volt"] = {}

Chrysler = _LazyNamespace("Chrysler", "Chrysler")
_ORIGINAL_SOURCE_NAMES["Chrysler"] = "Chrysler"
_ORIGINAL_COMMAND_NAMES["Chrysler"] = {}

Chrysler_200 = _LazyNamespace("Chrysler-200", "Chrysler_200")
_ORIGINAL_SOURCE_NAMES["Chrysler_200"] = "Chrysler-200"
_ORIGINAL_COMMAND_NAMES["Chrysler_200"] = {}

Chrysler_300 = _LazyNamespace("Chrysler-300", "Chrysler_300")
_ORIGINAL_SOURCE_NAMES["Chrysler_300"] = "Chrysler-300"
_ORIGINAL_COMMAND_NAMES["Chrysler_300"] = {}

Chrysler_Pacifica = _LazyNamespace("Chrysler-Pacifica", "Chrysler_Pacifica")
_ORIGINAL_SOURCE_NAMES["Chrysler_Pacifica"] = "Chrysler-Pacifica"
_ORIGINAL_COMMAND_NAMES["Chrysler_Pacifica"] = {}

Chrysler_Pacifica_Hybrid = _LazyNamespace("Chrysler-Pacifica-Hybrid", "Chrysler_Pacifica_Hybrid")
_ORIGINAL_SOURCE_NAMES["Chrysler_Pacifica_Hybrid"] = "Chrysler-Pacifica-Hybrid"
_ORIGINAL_COMMAND_NAMES["Chrysler_Pacifica_Hybrid"] = {}

Chrysler_Sebring = _LazyNamespace("Chrysler-Sebring", "Chrysler_Sebring")
_ORIGINAL_SOURCE_NAMES["Chrysler_Sebring"] = "Chrysler-Sebring"
_ORIGINAL_COMMAND_NAMES["Chrysler_Sebring"] = {}

Citroen = _LazyNamespace("Citroen", "Citroen")
_ORIGINAL_SOURCE_NAMES["Citroen"] = "Citroen"
_ORIGINAL_COMMAND_NAMES["Citroen"] = {}

Citroen_Basalt = _LazyNamespace("Citroen-Basalt", "Citroen_Basalt")
_ORIGINAL_SOURCE_NAMES["Citroen_Basalt"] = "Citroen-Basalt"
_ORIGINAL_COMMAND_NAMES["Citroen_Basalt"] = {}

Citroen_Berlingo = _LazyNamespace("Citroen-Berlingo", "Citroen_Berlingo")
_ORIGINAL_SOURCE_NAMES["Citroen_Berlingo"] = "Citroen-Berlingo"
_ORIGINAL_COMMAND_NAMES["Citroen_Berlingo"] = {}

Citroen_C3 = _LazyNamespace("Citroen-C3", "Citroen_C3")
_ORIGINAL_SOURCE_NAMES["Citroen_C3"] = "Citroen-C3"
_ORIGINAL_COMMAND_NAMES["Citroen_C3"] = {}

Citroen_C4 = _LazyNamespace("Citroen-C4", "Citroen_C4")
_ORIGINAL_SOURCE_NAMES["Citroen_C4"] = "Citroen-C4"
_ORIGINAL_COMMAND_NAMES["Citroen_C4"] = {}

Citroen_CZero = _LazyNamespace("Citroen-CZero", "Citroen_CZero")
_ORIGINAL_SOURCE_NAMES["Citroen_CZero"] = "Citroen-CZero"
_ORIGINAL_COMMAND_NAMES["Citroen_CZero"] = {}

Citroen_E_C4 = _LazyNamespace("Citroen-E-C4", "Citroen_E_C4")
_ORIGINAL_SOURCE_NAMES["Citroen_E_C4"] = "Citroen-E-C4"
_ORIGINAL_COMMAND_NAMES["Citroen_E_C4"] = {}

Citroen_eC4_X = _LazyNamespace("Citroen-eC4-X", "Citroen_eC4_X")
_ORIGINAL_SOURCE_NAMES["Citroen_eC4_X"] = "Citroen-eC4-X"
_ORIGINAL_COMMAND_NAMES["Citroen_eC4_X"] = {}

Cupra = _LazyNamespace("Cupra", "Cupra")
_ORIGINAL_SOURCE_NAMES["Cupra"] = "Cupra"
_ORIGINAL_COMMAND_NAMES["Cupra"] = {}

Cupra_Born = _LazyNamespace("Cupra-Born", "Cupra_Born")
_ORIGINAL_SOURCE_NAMES["Cupra_Born"] = "Cupra-Born"
_ORIGINAL_COMMAND_NAMES["Cupra_Born"] = {}

Cupra_Formentor = _LazyNamespace("Cupra-Formentor", "Cupra_Formentor")
_ORIGINAL_SOURCE_NAMES["Cupra_Formentor"] = "Cupra-Formentor"
_ORIGINAL_COMMAND_NAMES["Cupra_Formentor"] = {}

Cupra_Leon = _LazyNamespace("Cupra-Leon", "Cupra_Leon")
_ORIGINAL_SOURCE_NAMES["Cupra_Leon"] = "Cupra-Leon"
_ORIGINAL_COMMAND_NAMES["Cupra_Leon"] = {}

Cupra_Leon_Sportstourer = _LazyNamespace("Cupra-Leon-Sportstourer", "Cupra_Leon_Sportstourer")
_ORIGINAL_SOURCE_NAMES["Cupra_Leon_Sportstourer"] = "Cupra-Leon-Sportstourer"
_ORIGINAL_COMMAND_NAMES["Cupra_Leon_Sportstourer"] = {}

Dacia = _LazyNamespace("Dacia", "Dacia")
_ORIGINAL_SOURCE_NAMES["Dacia"] = "Dacia"
_ORIGINAL_COMMAND_NAMES["Dacia"] = {}

Dacia_Duster = _LazyNamespace("Dacia-Duster", "Dacia_Duster")
_ORIGINAL_SOURCE_NAMES["Dacia_Duster"] = "Dacia-Duster"
_ORIGINAL_COMMAND_NAMES["Dacia_Duster"] = {}

Dacia_Lodgy = _LazyNamespace("Dacia-Lodgy", "Dacia_Lodgy")
_ORIGINAL_SOURCE_NAMES["Dacia_Lodgy"] = "Dacia-Lodgy"
_ORIGINAL_COMMAND_NAMES["Dacia_Lodgy"] = {}

Dacia_Sandero = _LazyNamespace("Dacia-Sandero", "Dacia_Sandero")
_ORIGINAL_SOURCE_NAMES["Dacia_Sandero"] = "Dacia-Sandero"
_ORIGINAL_COMMAND_NAMES["Dacia_Sandero"] = {}

Dacia_Spring = _LazyNamespace("Dacia-Spring", "Dacia_Spring")
_ORIGINAL_SOURCE_NAMES["Dacia_Spring"] = "Dacia-Spring"
_ORIGINAL_COMMAND_NAMES["Dacia_Spring"] = {}

Daihatsu = _LazyNamespace("Daihatsu", "Daihatsu")
_ORIGINAL_SOURCE_NAMES["Daihatsu"] = "Daihatsu"
_ORIGINAL_COMMAND_NAMES["Daihatsu"] = {}

Datsun = _LazyNamespace("Datsun", "Datsun")
_ORIGINAL_SOURCE_NAMES["Datsun"] = "Datsun"
_ORIGINAL_COMMAND_NAMES["Datsun"] = {}

Dodge = _LazyNamespace("Dodge", "Dodge")
_ORIGINAL_SOURCE_NAMES["Dodge"] = "Dodge"
_ORIGINAL_COMMAND_NAMES["Dodge"] = {}

Dodge_Challenger = _LazyNamespace("Dodge-Challenger", "Dodge_Challenger")
_ORIGINAL_SOURCE_NAMES["Dodge_Challenger"] = "Dodge-Challenger"
_ORIGINAL_COMMAND_NAMES["Dodge_Challenger"] = {}

Dodge_Charger = _LazyNamespace("Dodge-Charger", "Dodge_Charger")
_ORIGINAL_SOURCE_NAMES["Dodge_Charger"] = "Dodge-Charger"
_ORIGINAL_COMMAND_NAMES["Dodge_Charger"] = {}

Dodge_Dakota = _LazyNamespace("Dodge-Dakota", "Dodge_Dakota")
_ORIGINAL_SOURCE_NAMES["Dodge_Dakota"] = "Dodge-Dakota"
_ORIGINAL_COMMAND_NAMES["Dodge_Dakota"] = {}

Dodge_Durango = _LazyNamespace("Dodge-Durango", "Dodge_Durango")
_ORIGINAL_SOURCE_NAMES["Dodge_Durango"] = "Dodge-Durango"
_ORIGINAL_COMMAND_NAMES["Dodge_Durango"] = {}

Dodge_Grand_Caravan = _LazyNamespace("Dodge-Grand-Caravan", "Dodge_Grand_Caravan")
_ORIGINAL_SOURCE_NAMES["Dodge_Grand_Caravan"] = "Dodge-Grand-Caravan"
_ORIGINAL_COMMAND_NAMES["Dodge_Grand_Caravan"] = {}

Dodge_Hornet = _LazyNamespace("Dodge-Hornet", "Dodge_Hornet")
_ORIGINAL_SOURCE_NAMES["Dodge_Hornet"] = "Dodge-Hornet"
_ORIGINAL_COMMAND_NAMES["Dodge_Hornet"] = {}

Dodge_Journey = _LazyNamespace("Dodge-Journey", "Dodge_Journey")
_ORIGINAL_SOURCE_NAMES["Dodge_Journey"] = "Dodge-Journey"
_ORIGINAL_COMMAND_NAMES["Dodge_Journey"] = {}

Dongfeng = _LazyNamespace("Dongfeng", "Dongfeng")
_ORIGINAL_SOURCE_NAMES["Dongfeng"] = "Dongfeng"
_ORIGINAL_COMMAND_NAMES["Dongfeng"] = {}

DongFeng_Seres_3 = _LazyNamespace("DongFeng-Seres-3", "DongFeng_Seres_3")
_ORIGINAL_SOURCE_NAMES["DongFeng_Seres_3"] = "DongFeng-Seres-3"
_ORIGINAL_COMMAND_NAMES["DongFeng_Seres_3"] = {}

DS = _LazyNamespace("DS", "DS")
_ORIGINAL_SOURCE_NAMES["DS"] = "DS"
_ORIGINAL_COMMAND_NAMES["DS"] = {}

DS_7 = _LazyNamespace("DS-7", "DS_7")
_ORIGINAL_SOURCE_NAMES["DS_7"] = "DS-7"
_ORIGINAL_COMMAND_NAMES["DS_7"] = {}

Ferrari_458_Italia = _LazyNamespace("Ferrari-458-Italia", "Ferrari_458_Italia")
_ORIGINAL_SOURCE_NAMES["Ferrari_458_Italia"] = "Ferrari-458-Italia"
_ORIGINAL_COMMAND_NAMES["Ferrari_458_Italia"] = {}

Fiat = _LazyNamespace("Fiat", "Fiat")
_ORIGINAL_SOURCE_NAMES["Fiat"] = "Fiat"
_ORIGINAL_COMMAND_NAMES["Fiat"] = {}

FIAT_500 = _LazyNamespace("FIAT-500", "FIAT_500")
_ORIGINAL_SOURCE_NAMES["FIAT_500"] = "FIAT-500"
_ORIGINAL_COMMAND_NAMES["FIAT_500"] = {}

FIAT_500e = _LazyNamespace("FIAT-500e", "FIAT_500e")
_ORIGINAL_SOURCE_NAMES["FIAT_500e"] = "FIAT-500e"
_ORIGINAL_COMMAND_NAMES["FIAT_500e"] = {}

FIAT_500X = _LazyNamespace("FIAT-500X", "FIAT_500X")
_ORIGINAL_SOURCE_NAMES["FIAT_500X"] = "FIAT-500X"
_ORIGINAL_COMMAND_NAMES["FIAT_500X"] = {}

FIAT_Fastback = _LazyNamespace("FIAT-Fastback", "FIAT_Fastback")
_ORIGINAL_SOURCE_NAMES["FIAT_Fastback"] = "FIAT-Fastback"
_ORIGINAL_COMMAND_NAMES["FIAT_Fastback"] = {}

Fiat_Grande_Punto = _LazyNamespace("Fiat-Grande-Punto", "Fiat_Grande_Punto")
_ORIGINAL_SOURCE_NAMES["Fiat_Grande_Punto"] = "Fiat-Grande-Punto"
_ORIGINAL_COMMAND_NAMES["Fiat_Grande_Punto"] = {}

FIAT_Panda = _LazyNamespace("FIAT-Panda", "FIAT_Panda")
_ORIGINAL_SOURCE_NAMES["FIAT_Panda"] = "FIAT-Panda"
_ORIGINAL_COMMAND_NAMES["FIAT_Panda"] = {}

Fiat_Punto = _LazyNamespace("Fiat-Punto", "Fiat_Punto")
_ORIGINAL_SOURCE_NAMES["Fiat_Punto"] = "Fiat-Punto"
_ORIGINAL_COMMAND_NAMES["Fiat_Punto"] = {}

Fisker = _LazyNamespace("Fisker", "Fisker")
_ORIGINAL_SOURCE_NAMES["Fisker"] = "Fisker"
_ORIGINAL_COMMAND_NAMES["Fisker"] = {}

Fisker_Ocean = _LazyNamespace("Fisker-Ocean", "Fisker_Ocean")
_ORIGINAL_SOURCE_NAMES["Fisker_Ocean"] = "Fisker-Ocean"
_ORIGINAL_COMMAND_NAMES["Fisker_Ocean"] = {}

Ford = _LazyNamespace("Ford", "Ford")
_ORIGINAL_SOURCE_NAMES["Ford"] = "Ford"
_ORIGINAL_COMMAND_NAMES["Ford"] = {}

Ford_Bronco = _LazyNamespace("Ford-Bronco", "Ford_Bronco")
_ORIGINAL_SOURCE_NAMES["Ford_Bronco"] = "Ford-Bronco"
_ORIGINAL_COMMAND_NAMES["Ford_Bronco"] = {}

Ford_Bronco_Sport = _LazyNamespace("Ford-Bronco-Sport", "Ford_Bronco_Sport")
_ORIGINAL_SOURCE_NAMES["Ford_Bronco_Sport"] = "Ford-Bronco-Sport"
_ORIGINAL_COMMAND_NAMES["Ford_Bronco_Sport"] = {}

Ford_E_Series = _LazyNamespace("Ford-E-Series", "Ford_E_Series")
_ORIGINAL_SOURCE_NAMES["Ford_E_Series"] = "Ford-E-Series"
_ORIGINAL_COMMAND_NAMES["Ford_E_Series"] = {}

Ford_EcoSport = _LazyNamespace("Ford-EcoSport", "Ford_EcoSport")
_ORIGINAL_SOURCE_NAMES["Ford_EcoSport"] = "Ford-EcoSport"
_ORIGINAL_COMMAND_NAMES["Ford_EcoSport"] = {}

Ford_Edge = _LazyNamespace("Ford-Edge", "Ford_Edge")
_ORIGINAL_SOURCE_NAMES["Ford_Edge"] = "Ford-Edge"
_ORIGINAL_COMMAND_NAMES["Ford_Edge"] = {}

Ford_Escape = _LazyNamespace("Ford-Escape", "Ford_Escape")
_ORIGINAL_SOURCE_NAMES["Ford_Escape"] = "Ford-Escape"
_ORIGINAL_COMMAND_NAMES["Ford_Escape"] = {}

Ford_Everest = _LazyNamespace("Ford-Everest", "Ford_Everest")
_ORIGINAL_SOURCE_NAMES["Ford_Everest"] = "Ford-Everest"
_ORIGINAL_COMMAND_NAMES["Ford_Everest"] = {}

Ford_Expedition = _LazyNamespace("Ford-Expedition", "Ford_Expedition")
_ORIGINAL_SOURCE_NAMES["Ford_Expedition"] = "Ford-Expedition"
_ORIGINAL_COMMAND_NAMES["Ford_Expedition"] = {}

Ford_Explorer = _LazyNamespace("Ford-Explorer", "Ford_Explorer")
_ORIGINAL_SOURCE_NAMES["Ford_Explorer"] = "Ford-Explorer"
_ORIGINAL_COMMAND_NAMES["Ford_Explorer"] = {}

Ford_F_150 = _LazyNamespace("Ford-F-150", "Ford_F_150")
_ORIGINAL_SOURCE_NAMES["Ford_F_150"] = "Ford-F-150"
_ORIGINAL_COMMAND_NAMES["Ford_F_150"] = {}

Ford_F_150_Lightning = _LazyNamespace("Ford-F-150-Lightning", "Ford_F_150_Lightning")
_ORIGINAL_SOURCE_NAMES["Ford_F_150_Lightning"] = "Ford-F-150-Lightning"
_ORIGINAL_COMMAND_NAMES["Ford_F_150_Lightning"] = {}

Ford_F_250 = _LazyNamespace("Ford-F-250", "Ford_F_250")
_ORIGINAL_SOURCE_NAMES["Ford_F_250"] = "Ford-F-250"
_ORIGINAL_COMMAND_NAMES["Ford_F_250"] = {}

Ford_F_350 = _LazyNamespace("Ford-F-350", "Ford_F_350")
_ORIGINAL_SOURCE_NAMES["Ford_F_350"] = "Ford-F-350"
_ORIGINAL_COMMAND_NAMES["Ford_F_350"] = {}

Ford_Fiesta = _LazyNamespace("Ford-Fiesta", "Ford_Fiesta")
_ORIGINAL_SOURCE_NAMES["Ford_Fiesta"] = "Ford-Fiesta"
_ORIGINAL_COMMAND_NAMES["Ford_Fiesta"] = {}

Ford_Five_Hundred = _LazyNamespace("Ford-Five-Hundred", "Ford_Five_Hundred")
_ORIGINAL_SOURCE_NAMES["Ford_Five_Hundred"] = "Ford-Five-Hundred"
_ORIGINAL_COMMAND_NAMES["Ford_Five_Hundred"] = {}

Ford_Flex = _LazyNamespace("Ford-Flex", "Ford_Flex")
_ORIGINAL_SOURCE_NAMES["Ford_Flex"] = "Ford-Flex"
_ORIGINAL_COMMAND_NAMES["Ford_Flex"] = {}

Ford_Focus = _LazyNamespace("Ford-Focus", "Ford_Focus")
_ORIGINAL_SOURCE_NAMES["Ford_Focus"] = "Ford-Focus"
_ORIGINAL_COMMAND_NAMES["Ford_Focus"] = {}

Ford_Focus_RS = _LazyNamespace("Ford-Focus-RS", "Ford_Focus_RS")
_ORIGINAL_SOURCE_NAMES["Ford_Focus_RS"] = "Ford-Focus-RS"
_ORIGINAL_COMMAND_NAMES["Ford_Focus_RS"] = {}

Ford_Focus_ST = _LazyNamespace("Ford-Focus-ST", "Ford_Focus_ST")
_ORIGINAL_SOURCE_NAMES["Ford_Focus_ST"] = "Ford-Focus-ST"
_ORIGINAL_COMMAND_NAMES["Ford_Focus_ST"] = {}

Ford_Fusion = _LazyNamespace("Ford-Fusion", "Ford_Fusion")
_ORIGINAL_SOURCE_NAMES["Ford_Fusion"] = "Ford-Fusion"
_ORIGINAL_COMMAND_NAMES["Ford_Fusion"] = {}

Ford_Fusion_Energi = _LazyNamespace("Ford-Fusion-Energi", "Ford_Fusion_Energi")
_ORIGINAL_SOURCE_NAMES["Ford_Fusion_Energi"] = "Ford-Fusion-Energi"
_ORIGINAL_COMMAND_NAMES["Ford_Fusion_Energi"] = {}

Ford_Fusion_Hybrid = _LazyNamespace("Ford-Fusion-Hybrid", "Ford_Fusion_Hybrid")
_ORIGINAL_SOURCE_NAMES["Ford_Fusion_Hybrid"] = "Ford-Fusion-Hybrid"
_ORIGINAL_COMMAND_NAMES["Ford_Fusion_Hybrid"] = {}

Ford_Ka = _LazyNamespace("Ford-Ka", "Ford_Ka")
_ORIGINAL_SOURCE_NAMES["Ford_Ka"] = "Ford-Ka"
_ORIGINAL_COMMAND_NAMES["Ford_Ka"] = {}

Ford_Kuga = _LazyNamespace("Ford-Kuga", "Ford_Kuga")
_ORIGINAL_SOURCE_NAMES["Ford_Kuga"] = "Ford-Kuga"
_ORIGINAL_COMMAND_NAMES["Ford_Kuga"] = {}

Ford_Maverick = _LazyNamespace("Ford-Maverick", "Ford_Maverick")
_ORIGINAL_SOURCE_NAMES["Ford_Maverick"] = "Ford-Maverick"
_ORIGINAL_COMMAND_NAMES["Ford_Maverick"] = {}

Ford_Mondeo = _LazyNamespace("Ford-Mondeo", "Ford_Mondeo")
_ORIGINAL_SOURCE_NAMES["Ford_Mondeo"] = "Ford-Mondeo"
_ORIGINAL_COMMAND_NAMES["Ford_Mondeo"] = {}

Ford_Mustang = _LazyNamespace("Ford-Mustang", "Ford_Mustang")
_ORIGINAL_SOURCE_NAMES["Ford_Mustang"] = "Ford-Mustang"
_ORIGINAL_COMMAND_NAMES["Ford_Mustang"] = {}

Ford_Mustang_Mach_E = _LazyNamespace("Ford-Mustang-Mach-E", "Ford_Mustang_Mach_E")
_ORIGINAL_SOURCE_NAMES["Ford_Mustang_Mach_E"] = "Ford-Mustang-Mach-E"
_ORIGINAL_COMMAND_NAMES["Ford_Mustang_Mach_E"] = {}

Ford_Puma = _LazyNamespace("Ford-Puma", "Ford_Puma")
_ORIGINAL_SOURCE_NAMES["Ford_Puma"] = "Ford-Puma"
_ORIGINAL_COMMAND_NAMES["Ford_Puma"] = {}

Ford_Ranger = _LazyNamespace("Ford-Ranger", "Ford_Ranger")
_ORIGINAL_SOURCE_NAMES["Ford_Ranger"] = "Ford-Ranger"
_ORIGINAL_COMMAND_NAMES["Ford_Ranger"] = {}

Ford_Sierra = _LazyNamespace("Ford-Sierra", "Ford_Sierra")
_ORIGINAL_SOURCE_NAMES["Ford_Sierra"] = "Ford-Sierra"
_ORIGINAL_COMMAND_NAMES["Ford_Sierra"] = {}

Ford_Taurus = _LazyNamespace("Ford-Taurus", "Ford_Taurus")
_ORIGINAL_SOURCE_NAMES["Ford_Taurus"] = "Ford-Taurus"
_ORIGINAL_COMMAND_NAMES["Ford_Taurus"] = {}

Ford_Territory = _LazyNamespace("Ford-Territory", "Ford_Territory")
_ORIGINAL_SOURCE_NAMES["Ford_Territory"] = "Ford-Territory"
_ORIGINAL_COMMAND_NAMES["Ford_Territory"] = {}

Ford_Transit = _LazyNamespace("Ford-Transit", "Ford_Transit")
_ORIGINAL_SOURCE_NAMES["Ford_Transit"] = "Ford-Transit"
_ORIGINAL_COMMAND_NAMES["Ford_Transit"] = {}

Ford_Transit_Connect = _LazyNamespace("Ford-Transit-Connect", "Ford_Transit_Connect")
_ORIGINAL_SOURCE_NAMES["Ford_Transit_Connect"] = "Ford-Transit-Connect"
_ORIGINAL_COMMAND_NAMES["Ford_Transit_Connect"] = {}

FSO_Polonez = _LazyNamespace("FSO-Polonez", "FSO_Polonez")
_ORIGINAL_SOURCE_NAMES["FSO_Polonez"] = "FSO-Polonez"
_ORIGINAL_COMMAND_NAMES["FSO_Polonez"] = {}

Genesis = _LazyNamespace("Genesis", "Genesis")
_ORIGINAL_SOURCE_NAMES["Genesis"] = "Genesis"
_ORIGINAL_COMMAND_NAMES["Genesis"] = {}

Genesis_G70 = _LazyNamespace("Genesis-G70", "Genesis_G70")
_ORIGINAL_SOURCE_NAMES["Genesis_G70"] = "Genesis-G70"
_ORIGINAL_COMMAND_NAMES["Genesis_G70"] = {}

Genesis_G80 = _LazyNamespace("Genesis-G80", "Genesis_G80")
_ORIGINAL_SOURCE_NAMES["Genesis_G80"] = "Genesis-G80"
_ORIGINAL_COMMAND_NAMES["Genesis_G80"] = {}

GMC = _LazyNamespace("GMC", "GMC")
_ORIGINAL_SOURCE_NAMES["GMC"] = "GMC"
_ORIGINAL_COMMAND_NAMES["GMC"] = {}

GMC_Acadia = _LazyNamespace("GMC-Acadia", "GMC_Acadia")
_ORIGINAL_SOURCE_NAMES["GMC_Acadia"] = "GMC-Acadia"
_ORIGINAL_COMMAND_NAMES["GMC_Acadia"] = {}

GMC_Canyon = _LazyNamespace("GMC-Canyon", "GMC_Canyon")
_ORIGINAL_SOURCE_NAMES["GMC_Canyon"] = "GMC-Canyon"
_ORIGINAL_COMMAND_NAMES["GMC_Canyon"] = {}

GMC_Safari = _LazyNamespace("GMC-Safari", "GMC_Safari")
_ORIGINAL_SOURCE_NAMES["GMC_Safari"] = "GMC-Safari"
_ORIGINAL_COMMAND_NAMES["GMC_Safari"] = {}

GMC_Sierra_1500 = _LazyNamespace("GMC-Sierra-1500", "GMC_Sierra_1500")
_ORIGINAL_SOURCE_NAMES["GMC_Sierra_1500"] = "GMC-Sierra-1500"
_ORIGINAL_COMMAND_NAMES["GMC_Sierra_1500"] = {}

GMC_Terrain = _LazyNamespace("GMC-Terrain", "GMC_Terrain")
_ORIGINAL_SOURCE_NAMES["GMC_Terrain"] = "GMC-Terrain"
_ORIGINAL_COMMAND_NAMES["GMC_Terrain"] = {}

GMC_Yukon = _LazyNamespace("GMC-Yukon", "GMC_Yukon")
_ORIGINAL_SOURCE_NAMES["GMC_Yukon"] = "GMC-Yukon"
_ORIGINAL_COMMAND_NAMES["GMC_Yukon"] = {}

GMC_Yukon_XL = _LazyNamespace("GMC-Yukon-XL", "GMC_Yukon_XL")
_ORIGINAL_SOURCE_NAMES["GMC_Yukon_XL"] = "GMC-Yukon-XL"
_ORIGINAL_COMMAND_NAMES["GMC_Yukon_XL"] = {}

Haval = _LazyNamespace("Haval", "Haval")
_ORIGINAL_SOURCE_NAMES["Haval"] = "Haval"
_ORIGINAL_COMMAND_NAMES["Haval"] = {}

Haval_H6_HEV = _LazyNamespace("Haval-H6-HEV", "Haval_H6_HEV")
_ORIGINAL_SOURCE_NAMES["Haval_H6_HEV"] = "Haval-H6-HEV"
_ORIGINAL_COMMAND_NAMES["Haval_H6_HEV"] = {}

Haval_Jolion = _LazyNamespace("Haval-Jolion", "Haval_Jolion")
_ORIGINAL_SOURCE_NAMES["Haval_Jolion"] = "Haval-Jolion"
_ORIGINAL_COMMAND_NAMES["Haval_Jolion"] = {}

Haval_Jolion_HEV = _LazyNamespace("Haval-Jolion-HEV", "Haval_Jolion_HEV")
_ORIGINAL_SOURCE_NAMES["Haval_Jolion_HEV"] = "Haval-Jolion-HEV"
_ORIGINAL_COMMAND_NAMES["Haval_Jolion_HEV"] = {}

Holden = _LazyNamespace("Holden", "Holden")
_ORIGINAL_SOURCE_NAMES["Holden"] = "Holden"
_ORIGINAL_COMMAND_NAMES["Holden"] = {}

Holden_Commodore = _LazyNamespace("Holden-Commodore", "Holden_Commodore")
_ORIGINAL_SOURCE_NAMES["Holden_Commodore"] = "Holden-Commodore"
_ORIGINAL_COMMAND_NAMES["Holden_Commodore"] = {}

Holden_Cruze = _LazyNamespace("Holden-Cruze", "Holden_Cruze")
_ORIGINAL_SOURCE_NAMES["Holden_Cruze"] = "Holden-Cruze"
_ORIGINAL_COMMAND_NAMES["Holden_Cruze"] = {}

Honda = _LazyNamespace("Honda", "Honda")
_ORIGINAL_SOURCE_NAMES["Honda"] = "Honda"
_ORIGINAL_COMMAND_NAMES["Honda"] = {}

Honda_Accord = _LazyNamespace("Honda-Accord", "Honda_Accord")
_ORIGINAL_SOURCE_NAMES["Honda_Accord"] = "Honda-Accord"
_ORIGINAL_COMMAND_NAMES["Honda_Accord"] = {}

Honda_Accord_Hybrid = _LazyNamespace("Honda-Accord-Hybrid", "Honda_Accord_Hybrid")
_ORIGINAL_SOURCE_NAMES["Honda_Accord_Hybrid"] = "Honda-Accord-Hybrid"
_ORIGINAL_COMMAND_NAMES["Honda_Accord_Hybrid"] = {}

Honda_Brio = _LazyNamespace("Honda-Brio", "Honda_Brio")
_ORIGINAL_SOURCE_NAMES["Honda_Brio"] = "Honda-Brio"
_ORIGINAL_COMMAND_NAMES["Honda_Brio"] = {}

Honda_City = _LazyNamespace("Honda-City", "Honda_City")
_ORIGINAL_SOURCE_NAMES["Honda_City"] = "Honda-City"
_ORIGINAL_COMMAND_NAMES["Honda_City"] = {}

Honda_Civic = _LazyNamespace("Honda-Civic", "Honda_Civic")
_ORIGINAL_SOURCE_NAMES["Honda_Civic"] = "Honda-Civic"
_ORIGINAL_COMMAND_NAMES["Honda_Civic"] = {}

Honda_Clarity = _LazyNamespace("Honda-Clarity", "Honda_Clarity")
_ORIGINAL_SOURCE_NAMES["Honda_Clarity"] = "Honda-Clarity"
_ORIGINAL_COMMAND_NAMES["Honda_Clarity"] = {}

Honda_CR_V = _LazyNamespace("Honda-CR-V", "Honda_CR_V")
_ORIGINAL_SOURCE_NAMES["Honda_CR_V"] = "Honda-CR-V"
_ORIGINAL_COMMAND_NAMES["Honda_CR_V"] = {}

Honda_CR_V_Hybrid = _LazyNamespace("Honda-CR-V-Hybrid", "Honda_CR_V_Hybrid")
_ORIGINAL_SOURCE_NAMES["Honda_CR_V_Hybrid"] = "Honda-CR-V-Hybrid"
_ORIGINAL_COMMAND_NAMES["Honda_CR_V_Hybrid"] = {}

Honda_CR_Z = _LazyNamespace("Honda-CR-Z", "Honda_CR_Z")
_ORIGINAL_SOURCE_NAMES["Honda_CR_Z"] = "Honda-CR-Z"
_ORIGINAL_COMMAND_NAMES["Honda_CR_Z"] = {}

Honda_e = _LazyNamespace("Honda-e", "Honda_e")
_ORIGINAL_SOURCE_NAMES["Honda_e"] = "Honda-e"
_ORIGINAL_COMMAND_NAMES["Honda_e"] = {}

Honda_Element = _LazyNamespace("Honda-Element", "Honda_Element")
_ORIGINAL_SOURCE_NAMES["Honda_Element"] = "Honda-Element"
_ORIGINAL_COMMAND_NAMES["Honda_Element"] = {}

Honda_Fit = _LazyNamespace("Honda-Fit", "Honda_Fit")
_ORIGINAL_SOURCE_NAMES["Honda_Fit"] = "Honda-Fit"
_ORIGINAL_COMMAND_NAMES["Honda_Fit"] = {}

Honda_HR_V = _LazyNamespace("Honda-HR-V", "Honda_HR_V")
_ORIGINAL_SOURCE_NAMES["Honda_HR_V"] = "Honda-HR-V"
_ORIGINAL_COMMAND_NAMES["Honda_HR_V"] = {}

Honda_Insight = _LazyNamespace("Honda-Insight", "Honda_Insight")
_ORIGINAL_SOURCE_NAMES["Honda_Insight"] = "Honda-Insight"
_ORIGINAL_COMMAND_NAMES["Honda_Insight"] = {}

Honda_Jazz = _LazyNamespace("Honda-Jazz", "Honda_Jazz")
_ORIGINAL_SOURCE_NAMES["Honda_Jazz"] = "Honda-Jazz"
_ORIGINAL_COMMAND_NAMES["Honda_Jazz"] = {}

Honda_M_NV = _LazyNamespace("Honda-M-NV", "Honda_M_NV")
_ORIGINAL_SOURCE_NAMES["Honda_M_NV"] = "Honda-M-NV"
_ORIGINAL_COMMAND_NAMES["Honda_M_NV"] = {}

Honda_Odyssey = _LazyNamespace("Honda-Odyssey", "Honda_Odyssey")
_ORIGINAL_SOURCE_NAMES["Honda_Odyssey"] = "Honda-Odyssey"
_ORIGINAL_COMMAND_NAMES["Honda_Odyssey"] = {}

Honda_Pilot = _LazyNamespace("Honda-Pilot", "Honda_Pilot")
_ORIGINAL_SOURCE_NAMES["Honda_Pilot"] = "Honda-Pilot"
_ORIGINAL_COMMAND_NAMES["Honda_Pilot"] = {}

Honda_Prologue = _LazyNamespace("Honda-Prologue", "Honda_Prologue")
_ORIGINAL_SOURCE_NAMES["Honda_Prologue"] = "Honda-Prologue"
_ORIGINAL_COMMAND_NAMES["Honda_Prologue"] = {}

Honda_Ridgeline = _LazyNamespace("Honda-Ridgeline", "Honda_Ridgeline")
_ORIGINAL_SOURCE_NAMES["Honda_Ridgeline"] = "Honda-Ridgeline"
_ORIGINAL_COMMAND_NAMES["Honda_Ridgeline"] = {}

Honda_WRV = _LazyNamespace("Honda-WRV", "Honda_WRV")
_ORIGINAL_SOURCE_NAMES["Honda_WRV"] = "Honda-WRV"
_ORIGINAL_COMMAND_NAMES["Honda_WRV"] = {}

Honda_ZR_V = _LazyNamespace("Honda-ZR-V", "Honda_ZR_V")
_ORIGINAL_SOURCE_NAMES["Honda_ZR_V"] = "Honda-ZR-V"
_ORIGINAL_COMMAND_NAMES["Honda_ZR_V"] = {}

Hyundai = _LazyNamespace("Hyundai", "Hyundai")
_ORIGINAL_SOURCE_NAMES["Hyundai"] = "Hyundai"
_ORIGINAL_COMMAND_NAMES["Hyundai"] = {}

Hyundai_Accent = _LazyNamespace("Hyundai-Accent", "Hyundai_Accent")
_ORIGINAL_SOURCE_NAMES["Hyundai_Accent"] = "Hyundai-Accent"
_ORIGINAL_COMMAND_NAMES["Hyundai_Accent"] = {}

Hyundai_Avante = _LazyNamespace("Hyundai-Avante", "Hyundai_Avante")
_ORIGINAL_SOURCE_NAMES["Hyundai_Avante"] = "Hyundai-Avante"
_ORIGINAL_COMMAND_NAMES["Hyundai_Avante"] = {}

Hyundai_Elantra = _LazyNamespace("Hyundai-Elantra", "Hyundai_Elantra")
_ORIGINAL_SOURCE_NAMES["Hyundai_Elantra"] = "Hyundai-Elantra"
_ORIGINAL_COMMAND_NAMES["Hyundai_Elantra"] = {}

Hyundai_Genesis_Coupe = _LazyNamespace("Hyundai-Genesis-Coupe", "Hyundai_Genesis_Coupe")
_ORIGINAL_SOURCE_NAMES["Hyundai_Genesis_Coupe"] = "Hyundai-Genesis-Coupe"
_ORIGINAL_COMMAND_NAMES["Hyundai_Genesis_Coupe"] = {}

Hyundai_i10 = _LazyNamespace("Hyundai-i10", "Hyundai_i10")
_ORIGINAL_SOURCE_NAMES["Hyundai_i10"] = "Hyundai-i10"
_ORIGINAL_COMMAND_NAMES["Hyundai_i10"] = {}

Hyundai_i20 = _LazyNamespace("Hyundai-i20", "Hyundai_i20")
_ORIGINAL_SOURCE_NAMES["Hyundai_i20"] = "Hyundai-i20"
_ORIGINAL_COMMAND_NAMES["Hyundai_i20"] = {}

Hyundai_i30 = _LazyNamespace("Hyundai-i30", "Hyundai_i30")
_ORIGINAL_SOURCE_NAMES["Hyundai_i30"] = "Hyundai-i30"
_ORIGINAL_COMMAND_NAMES["Hyundai_i30"] = {}

Hyundai_IONIQ_5 = _LazyNamespace("Hyundai-IONIQ-5", "Hyundai_IONIQ_5")
_ORIGINAL_SOURCE_NAMES["Hyundai_IONIQ_5"] = "Hyundai-IONIQ-5"
_ORIGINAL_COMMAND_NAMES["Hyundai_IONIQ_5"] = {}

Hyundai_IONIQ_6 = _LazyNamespace("Hyundai-IONIQ-6", "Hyundai_IONIQ_6")
_ORIGINAL_SOURCE_NAMES["Hyundai_IONIQ_6"] = "Hyundai-IONIQ-6"
_ORIGINAL_COMMAND_NAMES["Hyundai_IONIQ_6"] = {}

Hyundai_IONIQ_Electric = _LazyNamespace("Hyundai-IONIQ-Electric", "Hyundai_IONIQ_Electric")
_ORIGINAL_SOURCE_NAMES["Hyundai_IONIQ_Electric"] = "Hyundai-IONIQ-Electric"
_ORIGINAL_COMMAND_NAMES["Hyundai_IONIQ_Electric"] = {}

Hyundai_IONIQ_PlugIn_Hybrid = _LazyNamespace("Hyundai-IONIQ-PlugIn-Hybrid", "Hyundai_IONIQ_PlugIn_Hybrid")
_ORIGINAL_SOURCE_NAMES["Hyundai_IONIQ_PlugIn_Hybrid"] = "Hyundai-IONIQ-PlugIn-Hybrid"
_ORIGINAL_COMMAND_NAMES["Hyundai_IONIQ_PlugIn_Hybrid"] = {}

Hyundai_Kona = _LazyNamespace("Hyundai-Kona", "Hyundai_Kona")
_ORIGINAL_SOURCE_NAMES["Hyundai_Kona"] = "Hyundai-Kona"
_ORIGINAL_COMMAND_NAMES["Hyundai_Kona"] = {}

Hyundai_Kona_Electric = _LazyNamespace("Hyundai-Kona-Electric", "Hyundai_Kona_Electric")
_ORIGINAL_SOURCE_NAMES["Hyundai_Kona_Electric"] = "Hyundai-Kona-Electric"
_ORIGINAL_COMMAND_NAMES["Hyundai_Kona_Electric"] = {}

Hyundai_Palisade = _LazyNamespace("Hyundai-Palisade", "Hyundai_Palisade")
_ORIGINAL_SOURCE_NAMES["Hyundai_Palisade"] = "Hyundai-Palisade"
_ORIGINAL_COMMAND_NAMES["Hyundai_Palisade"] = {}

Hyundai_Santa_Cruz = _LazyNamespace("Hyundai-Santa-Cruz", "Hyundai_Santa_Cruz")
_ORIGINAL_SOURCE_NAMES["Hyundai_Santa_Cruz"] = "Hyundai-Santa-Cruz"
_ORIGINAL_COMMAND_NAMES["Hyundai_Santa_Cruz"] = {}

Hyundai_Santa_Fe = _LazyNamespace("Hyundai-Santa-Fe", "Hyundai_Santa_Fe")
_ORIGINAL_SOURCE_NAMES["Hyundai_Santa_Fe"] = "Hyundai-Santa-Fe"
_ORIGINAL_COMMAND_NAMES["Hyundai_Santa_Fe"] = {}

Hyundai_Santa_Fe_Hybrid = _LazyNamespace("Hyundai-Santa-Fe-Hybrid", "Hyundai_Santa_Fe_Hybrid")
_ORIGINAL_SOURCE_NAMES["Hyundai_Santa_Fe_Hybrid"] = "Hyundai-Santa-Fe-Hybrid"
_ORIGINAL_COMMAND_NAMES["Hyundai_Santa_Fe_Hybrid"] = {}

Hyundai_Sonata = _LazyNamespace("Hyundai-Sonata", "Hyundai_Sonata")
_ORIGINAL_SOURCE_NAMES["Hyundai_Sonata"] = "Hyundai-Sonata"
_ORIGINAL_COMMAND_NAMES["Hyundai_Sonata"] = {}

Hyundai_Tucson = _LazyNamespace("Hyundai-Tucson", "Hyundai_Tucson")
_ORIGINAL_SOURCE_NAMES["Hyundai_Tucson"] = "Hyundai-Tucson"
_ORIGINAL_COMMAND_NAMES["Hyundai_Tucson"] = {}

Hyundai_Tucson_Hybrid = _LazyNamespace("Hyundai-Tucson-Hybrid", "Hyundai_Tucson_Hybrid")
_ORIGINAL_SOURCE_NAMES["Hyundai_Tucson_Hybrid"] = "Hyundai-Tucson-Hybrid"
_ORIGINAL_COMMAND_NAMES["Hyundai_Tucson_Hybrid"] = {}

Hyundai_Veloster = _LazyNamespace("Hyundai-Veloster", "Hyundai_Veloster")
_ORIGINAL_SOURCE_NAMES["Hyundai_Veloster"] = "Hyundai-Veloster"
_ORIGINAL_COMMAND_NAMES["Hyundai_Veloster"] = {}

Hyundai_Venue = _LazyNamespace("Hyundai-Venue", "Hyundai_Venue")
_ORIGINAL_SOURCE_NAMES["Hyundai_Venue"] = "Hyundai-Venue"
_ORIGINAL_COMMAND_NAMES["Hyundai_Venue"] = {}

Hyundai_Verna = _LazyNamespace("Hyundai-Verna", "Hyundai_Verna")
_ORIGINAL_SOURCE_NAMES["Hyundai_Verna"] = "Hyundai-Verna"
_ORIGINAL_COMMAND_NAMES["Hyundai_Verna"] = {}

INFINITI = _LazyNamespace("INFINITI", "INFINITI")
_ORIGINAL_SOURCE_NAMES["INFINITI"] = "INFINITI"
_ORIGINAL_COMMAND_NAMES["INFINITI"] = {}

INFINITI_G_Sedan = _LazyNamespace("INFINITI-G-Sedan", "INFINITI_G_Sedan")
_ORIGINAL_SOURCE_NAMES["INFINITI_G_Sedan"] = "INFINITI-G-Sedan"
_ORIGINAL_COMMAND_NAMES["INFINITI_G_Sedan"] = {}

INFINITI_G35 = _LazyNamespace("INFINITI-G35", "INFINITI_G35")
_ORIGINAL_SOURCE_NAMES["INFINITI_G35"] = "INFINITI-G35"
_ORIGINAL_COMMAND_NAMES["INFINITI_G35"] = {}

INFINITI_G37 = _LazyNamespace("INFINITI-G37", "INFINITI_G37")
_ORIGINAL_SOURCE_NAMES["INFINITI_G37"] = "INFINITI-G37"
_ORIGINAL_COMMAND_NAMES["INFINITI_G37"] = {}

INFINITI_Q45 = _LazyNamespace("INFINITI-Q45", "INFINITI_Q45")
_ORIGINAL_SOURCE_NAMES["INFINITI_Q45"] = "INFINITI-Q45"
_ORIGINAL_COMMAND_NAMES["INFINITI_Q45"] = {}

INFINITI_Q50 = _LazyNamespace("INFINITI-Q50", "INFINITI_Q50")
_ORIGINAL_SOURCE_NAMES["INFINITI_Q50"] = "INFINITI-Q50"
_ORIGINAL_COMMAND_NAMES["INFINITI_Q50"] = {}

INFINITI_Q70 = _LazyNamespace("INFINITI-Q70", "INFINITI_Q70")
_ORIGINAL_SOURCE_NAMES["INFINITI_Q70"] = "INFINITI-Q70"
_ORIGINAL_COMMAND_NAMES["INFINITI_Q70"] = {}

INFINITI_QX55 = _LazyNamespace("INFINITI-QX55", "INFINITI_QX55")
_ORIGINAL_SOURCE_NAMES["INFINITI_QX55"] = "INFINITI-QX55"
_ORIGINAL_COMMAND_NAMES["INFINITI_QX55"] = {}

INFINITI_QX70 = _LazyNamespace("INFINITI-QX70", "INFINITI_QX70")
_ORIGINAL_SOURCE_NAMES["INFINITI_QX70"] = "INFINITI-QX70"
_ORIGINAL_COMMAND_NAMES["INFINITI_QX70"] = {}

JAC_EJ7 = _LazyNamespace("JAC-EJ7", "JAC_EJ7")
_ORIGINAL_SOURCE_NAMES["JAC_EJ7"] = "JAC-EJ7"
_ORIGINAL_COMMAND_NAMES["JAC_EJ7"] = {}

Jaecoo_J7 = _LazyNamespace("Jaecoo-J7", "Jaecoo_J7")
_ORIGINAL_SOURCE_NAMES["Jaecoo_J7"] = "Jaecoo-J7"
_ORIGINAL_COMMAND_NAMES["Jaecoo_J7"] = {}

Jaguar = _LazyNamespace("Jaguar", "Jaguar")
_ORIGINAL_SOURCE_NAMES["Jaguar"] = "Jaguar"
_ORIGINAL_COMMAND_NAMES["Jaguar"] = {}

Jaguar_F_PACE = _LazyNamespace("Jaguar-F-PACE", "Jaguar_F_PACE")
_ORIGINAL_SOURCE_NAMES["Jaguar_F_PACE"] = "Jaguar-F-PACE"
_ORIGINAL_COMMAND_NAMES["Jaguar_F_PACE"] = {}

Jaguar_F_TYPE = _LazyNamespace("Jaguar-F-TYPE", "Jaguar_F_TYPE")
_ORIGINAL_SOURCE_NAMES["Jaguar_F_TYPE"] = "Jaguar-F-TYPE"
_ORIGINAL_COMMAND_NAMES["Jaguar_F_TYPE"] = {}

Jaguar_I_PACE = _LazyNamespace("Jaguar-I-PACE", "Jaguar_I_PACE")
_ORIGINAL_SOURCE_NAMES["Jaguar_I_PACE"] = "Jaguar-I-PACE"
_ORIGINAL_COMMAND_NAMES["Jaguar_I_PACE"] = {}

Jeep = _LazyNamespace("Jeep", "Jeep")
_ORIGINAL_SOURCE_NAMES["Jeep"] = "Jeep"
_ORIGINAL_COMMAND_NAMES["Jeep"] = {}

Jeep_Avenger = _LazyNamespace("Jeep-Avenger", "Jeep_Avenger")
_ORIGINAL_SOURCE_NAMES["Jeep_Avenger"] = "Jeep-Avenger"
_ORIGINAL_COMMAND_NAMES["Jeep_Avenger"] = {}

Jeep_Cherokee = _LazyNamespace("Jeep-Cherokee", "Jeep_Cherokee")
_ORIGINAL_SOURCE_NAMES["Jeep_Cherokee"] = "Jeep-Cherokee"
_ORIGINAL_COMMAND_NAMES["Jeep_Cherokee"] = {}

Jeep_Commander = _LazyNamespace("Jeep-Commander", "Jeep_Commander")
_ORIGINAL_SOURCE_NAMES["Jeep_Commander"] = "Jeep-Commander"
_ORIGINAL_COMMAND_NAMES["Jeep_Commander"] = {}

Jeep_Compass = _LazyNamespace("Jeep-Compass", "Jeep_Compass")
_ORIGINAL_SOURCE_NAMES["Jeep_Compass"] = "Jeep-Compass"
_ORIGINAL_COMMAND_NAMES["Jeep_Compass"] = {}

Jeep_Gladiator = _LazyNamespace("Jeep-Gladiator", "Jeep_Gladiator")
_ORIGINAL_SOURCE_NAMES["Jeep_Gladiator"] = "Jeep-Gladiator"
_ORIGINAL_COMMAND_NAMES["Jeep_Gladiator"] = {}

Jeep_Grand_Cherokee = _LazyNamespace("Jeep-Grand-Cherokee", "Jeep_Grand_Cherokee")
_ORIGINAL_SOURCE_NAMES["Jeep_Grand_Cherokee"] = "Jeep-Grand-Cherokee"
_ORIGINAL_COMMAND_NAMES["Jeep_Grand_Cherokee"] = {}

Jeep_Liberty = _LazyNamespace("Jeep-Liberty", "Jeep_Liberty")
_ORIGINAL_SOURCE_NAMES["Jeep_Liberty"] = "Jeep-Liberty"
_ORIGINAL_COMMAND_NAMES["Jeep_Liberty"] = {}

Jeep_Patriot = _LazyNamespace("Jeep-Patriot", "Jeep_Patriot")
_ORIGINAL_SOURCE_NAMES["Jeep_Patriot"] = "Jeep-Patriot"
_ORIGINAL_COMMAND_NAMES["Jeep_Patriot"] = {}

Jeep_Renegade = _LazyNamespace("Jeep-Renegade", "Jeep_Renegade")
_ORIGINAL_SOURCE_NAMES["Jeep_Renegade"] = "Jeep-Renegade"
_ORIGINAL_COMMAND_NAMES["Jeep_Renegade"] = {}

Jeep_Wagoneer = _LazyNamespace("Jeep-Wagoneer", "Jeep_Wagoneer")
_ORIGINAL_SOURCE_NAMES["Jeep_Wagoneer"] = "Jeep-Wagoneer"
_ORIGINAL_COMMAND_NAMES["Jeep_Wagoneer"] = {}

Jeep_Wrangler = _LazyNamespace("Jeep-Wrangler", "Jeep_Wrangler")
_ORIGINAL_SOURCE_NAMES["Jeep_Wrangler"] = "Jeep-Wrangler"
_ORIGINAL_COMMAND_NAMES["Jeep_Wrangler"] = {}

Jeep_Wrangler_4xe = _LazyNamespace("Jeep-Wrangler-4xe", "Jeep_Wrangler_4xe")
_ORIGINAL_SOURCE_NAMES["Jeep_Wrangler_4xe"] = "Jeep-Wrangler-4xe"
_ORIGINAL_COMMAND_NAMES["Jeep_Wrangler_4xe"] = {}

Jeep_Wrangler_JK = _LazyNamespace("Jeep-Wrangler-JK", "Jeep_Wrangler_JK")
_ORIGINAL_SOURCE_NAMES["Jeep_Wrangler_JK"] = "Jeep-Wrangler-JK"
_ORIGINAL_COMMAND_NAMES["Jeep_Wrangler_JK"] = {}

Kawasaki_W800 = _LazyNamespace("Kawasaki-W800", "Kawasaki_W800")
_ORIGINAL_SOURCE_NAMES["Kawasaki_W800"] = "Kawasaki-W800"
_ORIGINAL_COMMAND_NAMES["Kawasaki_W800"] = {}

Kia = _LazyNamespace("Kia", "Kia")
_ORIGINAL_SOURCE_NAMES["Kia"] = "Kia"
_ORIGINAL_COMMAND_NAMES["Kia"] = {}

Kia_Cadenza = _LazyNamespace("Kia-Cadenza", "Kia_Cadenza")
_ORIGINAL_SOURCE_NAMES["Kia_Cadenza"] = "Kia-Cadenza"
_ORIGINAL_COMMAND_NAMES["Kia_Cadenza"] = {}

Kia_Carens = _LazyNamespace("Kia-Carens", "Kia_Carens")
_ORIGINAL_SOURCE_NAMES["Kia_Carens"] = "Kia-Carens"
_ORIGINAL_COMMAND_NAMES["Kia_Carens"] = {}

Kia_Carnival = _LazyNamespace("Kia-Carnival", "Kia_Carnival")
_ORIGINAL_SOURCE_NAMES["Kia_Carnival"] = "Kia-Carnival"
_ORIGINAL_COMMAND_NAMES["Kia_Carnival"] = {}

Kia_Ceed = _LazyNamespace("Kia-Ceed", "Kia_Ceed")
_ORIGINAL_SOURCE_NAMES["Kia_Ceed"] = "Kia-Ceed"
_ORIGINAL_COMMAND_NAMES["Kia_Ceed"] = {}

Kia_Cerato = _LazyNamespace("Kia-Cerato", "Kia_Cerato")
_ORIGINAL_SOURCE_NAMES["Kia_Cerato"] = "Kia-Cerato"
_ORIGINAL_COMMAND_NAMES["Kia_Cerato"] = {}

Kia_EV3 = _LazyNamespace("Kia-EV3", "Kia_EV3")
_ORIGINAL_SOURCE_NAMES["Kia_EV3"] = "Kia-EV3"
_ORIGINAL_COMMAND_NAMES["Kia_EV3"] = {}

Kia_EV6 = _LazyNamespace("Kia-EV6", "Kia_EV6")
_ORIGINAL_SOURCE_NAMES["Kia_EV6"] = "Kia-EV6"
_ORIGINAL_COMMAND_NAMES["Kia_EV6"] = {}

Kia_EV9 = _LazyNamespace("Kia-EV9", "Kia_EV9")
_ORIGINAL_SOURCE_NAMES["Kia_EV9"] = "Kia-EV9"
_ORIGINAL_COMMAND_NAMES["Kia_EV9"] = {}

Kia_Forte = _LazyNamespace("Kia-Forte", "Kia_Forte")
_ORIGINAL_SOURCE_NAMES["Kia_Forte"] = "Kia-Forte"
_ORIGINAL_COMMAND_NAMES["Kia_Forte"] = {}

Kia_K4 = _LazyNamespace("Kia-K4", "Kia_K4")
_ORIGINAL_SOURCE_NAMES["Kia_K4"] = "Kia-K4"
_ORIGINAL_COMMAND_NAMES["Kia_K4"] = {}

Kia_K5 = _LazyNamespace("Kia-K5", "Kia_K5")
_ORIGINAL_SOURCE_NAMES["Kia_K5"] = "Kia-K5"
_ORIGINAL_COMMAND_NAMES["Kia_K5"] = {}

Kia_Niro = _LazyNamespace("Kia-Niro", "Kia_Niro")
_ORIGINAL_SOURCE_NAMES["Kia_Niro"] = "Kia-Niro"
_ORIGINAL_COMMAND_NAMES["Kia_Niro"] = {}

Kia_Niro_EV = _LazyNamespace("Kia-Niro-EV", "Kia_Niro_EV")
_ORIGINAL_SOURCE_NAMES["Kia_Niro_EV"] = "Kia-Niro-EV"
_ORIGINAL_COMMAND_NAMES["Kia_Niro_EV"] = {}

Kia_Optima = _LazyNamespace("Kia-Optima", "Kia_Optima")
_ORIGINAL_SOURCE_NAMES["Kia_Optima"] = "Kia-Optima"
_ORIGINAL_COMMAND_NAMES["Kia_Optima"] = {}

Kia_Picanto = _LazyNamespace("Kia-Picanto", "Kia_Picanto")
_ORIGINAL_SOURCE_NAMES["Kia_Picanto"] = "Kia-Picanto"
_ORIGINAL_COMMAND_NAMES["Kia_Picanto"] = {}

Kia_Rio = _LazyNamespace("Kia-Rio", "Kia_Rio")
_ORIGINAL_SOURCE_NAMES["Kia_Rio"] = "Kia-Rio"
_ORIGINAL_COMMAND_NAMES["Kia_Rio"] = {}

Kia_Rondo = _LazyNamespace("Kia-Rondo", "Kia_Rondo")
_ORIGINAL_SOURCE_NAMES["Kia_Rondo"] = "Kia-Rondo"
_ORIGINAL_COMMAND_NAMES["Kia_Rondo"] = {}

Kia_Seltos = _LazyNamespace("Kia-Seltos", "Kia_Seltos")
_ORIGINAL_SOURCE_NAMES["Kia_Seltos"] = "Kia-Seltos"
_ORIGINAL_COMMAND_NAMES["Kia_Seltos"] = {}

Kia_Sonet = _LazyNamespace("Kia-Sonet", "Kia_Sonet")
_ORIGINAL_SOURCE_NAMES["Kia_Sonet"] = "Kia-Sonet"
_ORIGINAL_COMMAND_NAMES["Kia_Sonet"] = {}

Kia_Sorento = _LazyNamespace("Kia-Sorento", "Kia_Sorento")
_ORIGINAL_SOURCE_NAMES["Kia_Sorento"] = "Kia-Sorento"
_ORIGINAL_COMMAND_NAMES["Kia_Sorento"] = {}

Kia_Soul = _LazyNamespace("Kia-Soul", "Kia_Soul")
_ORIGINAL_SOURCE_NAMES["Kia_Soul"] = "Kia-Soul"
_ORIGINAL_COMMAND_NAMES["Kia_Soul"] = {}

Kia_Sportage = _LazyNamespace("Kia-Sportage", "Kia_Sportage")
_ORIGINAL_SOURCE_NAMES["Kia_Sportage"] = "Kia-Sportage"
_ORIGINAL_COMMAND_NAMES["Kia_Sportage"] = {}

Kia_Sportage_HEV = _LazyNamespace("Kia-Sportage-HEV", "Kia_Sportage_HEV")
_ORIGINAL_SOURCE_NAMES["Kia_Sportage_HEV"] = "Kia-Sportage-HEV"
_ORIGINAL_COMMAND_NAMES["Kia_Sportage_HEV"] = {}

Kia_Stinger = _LazyNamespace("Kia-Stinger", "Kia_Stinger")
_ORIGINAL_SOURCE_NAMES["Kia_Stinger"] = "Kia-Stinger"
_ORIGINAL_COMMAND_NAMES["Kia_Stinger"] = {}

Kia_Stonic = _LazyNamespace("Kia-Stonic", "Kia_Stonic")
_ORIGINAL_SOURCE_NAMES["Kia_Stonic"] = "Kia-Stonic"
_ORIGINAL_COMMAND_NAMES["Kia_Stonic"] = {}

Kia_Telluride = _LazyNamespace("Kia-Telluride", "Kia_Telluride")
_ORIGINAL_SOURCE_NAMES["Kia_Telluride"] = "Kia-Telluride"
_ORIGINAL_COMMAND_NAMES["Kia_Telluride"] = {}

KTM = _LazyNamespace("KTM", "KTM")
_ORIGINAL_SOURCE_NAMES["KTM"] = "KTM"
_ORIGINAL_COMMAND_NAMES["KTM"] = {}

KTM_RC = _LazyNamespace("KTM-RC", "KTM_RC")
_ORIGINAL_SOURCE_NAMES["KTM_RC"] = "KTM-RC"
_ORIGINAL_COMMAND_NAMES["KTM_RC"] = {}

KTM_RC_390 = _LazyNamespace("KTM-RC-390", "KTM_RC_390")
_ORIGINAL_SOURCE_NAMES["KTM_RC_390"] = "KTM-RC-390"
_ORIGINAL_COMMAND_NAMES["KTM_RC_390"] = {}

Lamborghini = _LazyNamespace("Lamborghini", "Lamborghini")
_ORIGINAL_SOURCE_NAMES["Lamborghini"] = "Lamborghini"
_ORIGINAL_COMMAND_NAMES["Lamborghini"] = {}

Lamborghini_Huracan_evo = _LazyNamespace("Lamborghini-Huracan-evo", "Lamborghini_Huracan_evo")
_ORIGINAL_SOURCE_NAMES["Lamborghini_Huracan_evo"] = "Lamborghini-Huracan-evo"
_ORIGINAL_COMMAND_NAMES["Lamborghini_Huracan_evo"] = {}

Land_Rover = _LazyNamespace("Land-Rover", "Land_Rover")
_ORIGINAL_SOURCE_NAMES["Land_Rover"] = "Land-Rover"
_ORIGINAL_COMMAND_NAMES["Land_Rover"] = {}

Land_Rover_Defender = _LazyNamespace("Land-Rover-Defender", "Land_Rover_Defender")
_ORIGINAL_SOURCE_NAMES["Land_Rover_Defender"] = "Land-Rover-Defender"
_ORIGINAL_COMMAND_NAMES["Land_Rover_Defender"] = {}

Land_Rover_LR4 = _LazyNamespace("Land-Rover-LR4", "Land_Rover_LR4")
_ORIGINAL_SOURCE_NAMES["Land_Rover_LR4"] = "Land-Rover-LR4"
_ORIGINAL_COMMAND_NAMES["Land_Rover_LR4"] = {}

Land_Rover_Range_Rover = _LazyNamespace("Land-Rover-Range-Rover", "Land_Rover_Range_Rover")
_ORIGINAL_SOURCE_NAMES["Land_Rover_Range_Rover"] = "Land-Rover-Range-Rover"
_ORIGINAL_COMMAND_NAMES["Land_Rover_Range_Rover"] = {}

Land_Rover_Range_Rover_Velar = _LazyNamespace("Land-Rover-Range-Rover-Velar", "Land_Rover_Range_Rover_Velar")
_ORIGINAL_SOURCE_NAMES["Land_Rover_Range_Rover_Velar"] = "Land-Rover-Range-Rover-Velar"
_ORIGINAL_COMMAND_NAMES["Land_Rover_Range_Rover_Velar"] = {}

Landrover = _LazyNamespace("Landrover", "Landrover")
_ORIGINAL_SOURCE_NAMES["Landrover"] = "Landrover"
_ORIGINAL_COMMAND_NAMES["Landrover"] = {}

Lexus = _LazyNamespace("Lexus", "Lexus")
_ORIGINAL_SOURCE_NAMES["Lexus"] = "Lexus"
_ORIGINAL_COMMAND_NAMES["Lexus"] = {}

Lexus_CT_200h = _LazyNamespace("Lexus-CT-200h", "Lexus_CT_200h")
_ORIGINAL_SOURCE_NAMES["Lexus_CT_200h"] = "Lexus-CT-200h"
_ORIGINAL_COMMAND_NAMES["Lexus_CT_200h"] = {}

Lexus_ES = _LazyNamespace("Lexus-ES", "Lexus_ES")
_ORIGINAL_SOURCE_NAMES["Lexus_ES"] = "Lexus-ES"
_ORIGINAL_COMMAND_NAMES["Lexus_ES"] = {}

Lexus_ES_300h = _LazyNamespace("Lexus-ES-300h", "Lexus_ES_300h")
_ORIGINAL_SOURCE_NAMES["Lexus_ES_300h"] = "Lexus-ES-300h"
_ORIGINAL_COMMAND_NAMES["Lexus_ES_300h"] = {}

Lexus_GX = _LazyNamespace("Lexus-GX", "Lexus_GX")
_ORIGINAL_SOURCE_NAMES["Lexus_GX"] = "Lexus-GX"
_ORIGINAL_COMMAND_NAMES["Lexus_GX"] = {}

Lexus_GX_460 = _LazyNamespace("Lexus-GX-460", "Lexus_GX_460")
_ORIGINAL_SOURCE_NAMES["Lexus_GX_460"] = "Lexus-GX-460"
_ORIGINAL_COMMAND_NAMES["Lexus_GX_460"] = {}

Lexus_GX_470 = _LazyNamespace("Lexus-GX-470", "Lexus_GX_470")
_ORIGINAL_SOURCE_NAMES["Lexus_GX_470"] = "Lexus-GX-470"
_ORIGINAL_COMMAND_NAMES["Lexus_GX_470"] = {}

Lexus_IS = _LazyNamespace("Lexus-IS", "Lexus_IS")
_ORIGINAL_SOURCE_NAMES["Lexus_IS"] = "Lexus-IS"
_ORIGINAL_COMMAND_NAMES["Lexus_IS"] = {}

Lexus_LC_500 = _LazyNamespace("Lexus-LC-500", "Lexus_LC_500")
_ORIGINAL_SOURCE_NAMES["Lexus_LC_500"] = "Lexus-LC-500"
_ORIGINAL_COMMAND_NAMES["Lexus_LC_500"] = {}

Lexus_LS = _LazyNamespace("Lexus-LS", "Lexus_LS")
_ORIGINAL_SOURCE_NAMES["Lexus_LS"] = "Lexus-LS"
_ORIGINAL_COMMAND_NAMES["Lexus_LS"] = {}

Lexus_NX_350h = _LazyNamespace("Lexus-NX-350h", "Lexus_NX_350h")
_ORIGINAL_SOURCE_NAMES["Lexus_NX_350h"] = "Lexus-NX-350h"
_ORIGINAL_COMMAND_NAMES["Lexus_NX_350h"] = {}

Lexus_RX = _LazyNamespace("Lexus-RX", "Lexus_RX")
_ORIGINAL_SOURCE_NAMES["Lexus_RX"] = "Lexus-RX"
_ORIGINAL_COMMAND_NAMES["Lexus_RX"] = {}

Lexus_RX_350 = _LazyNamespace("Lexus-RX-350", "Lexus_RX_350")
_ORIGINAL_SOURCE_NAMES["Lexus_RX_350"] = "Lexus-RX-350"
_ORIGINAL_COMMAND_NAMES["Lexus_RX_350"] = {}

Lexus_RX_450h = _LazyNamespace("Lexus-RX-450h", "Lexus_RX_450h")
_ORIGINAL_SOURCE_NAMES["Lexus_RX_450h"] = "Lexus-RX-450h"
_ORIGINAL_COMMAND_NAMES["Lexus_RX_450h"] = {}

Lexus_UX = _LazyNamespace("Lexus-UX", "Lexus_UX")
_ORIGINAL_SOURCE_NAMES["Lexus_UX"] = "Lexus-UX"
_ORIGINAL_COMMAND_NAMES["Lexus_UX"] = {}

Lincoln = _LazyNamespace("Lincoln", "Lincoln")
_ORIGINAL_SOURCE_NAMES["Lincoln"] = "Lincoln"
_ORIGINAL_COMMAND_NAMES["Lincoln"] = {}

Lincoln_Aviator = _LazyNamespace("Lincoln-Aviator", "Lincoln_Aviator")
_ORIGINAL_SOURCE_NAMES["Lincoln_Aviator"] = "Lincoln-Aviator"
_ORIGINAL_COMMAND_NAMES["Lincoln_Aviator"] = {}

Lincoln_Corsair = _LazyNamespace("Lincoln-Corsair", "Lincoln_Corsair")
_ORIGINAL_SOURCE_NAMES["Lincoln_Corsair"] = "Lincoln-Corsair"
_ORIGINAL_COMMAND_NAMES["Lincoln_Corsair"] = {}

Lincoln_MKX = _LazyNamespace("Lincoln-MKX", "Lincoln_MKX")
_ORIGINAL_SOURCE_NAMES["Lincoln_MKX"] = "Lincoln-MKX"
_ORIGINAL_COMMAND_NAMES["Lincoln_MKX"] = {}

Lincoln_MKZ = _LazyNamespace("Lincoln-MKZ", "Lincoln_MKZ")
_ORIGINAL_SOURCE_NAMES["Lincoln_MKZ"] = "Lincoln-MKZ"
_ORIGINAL_COMMAND_NAMES["Lincoln_MKZ"] = {}

Lincoln_Nautilus = _LazyNamespace("Lincoln-Nautilus", "Lincoln_Nautilus")
_ORIGINAL_SOURCE_NAMES["Lincoln_Nautilus"] = "Lincoln-Nautilus"
_ORIGINAL_COMMAND_NAMES["Lincoln_Nautilus"] = {}

Lincoln_Navigator = _LazyNamespace("Lincoln-Navigator", "Lincoln_Navigator")
_ORIGINAL_SOURCE_NAMES["Lincoln_Navigator"] = "Lincoln-Navigator"
_ORIGINAL_COMMAND_NAMES["Lincoln_Navigator"] = {}

Lincoln_Town_Car = _LazyNamespace("Lincoln-Town-Car", "Lincoln_Town_Car")
_ORIGINAL_SOURCE_NAMES["Lincoln_Town_Car"] = "Lincoln-Town-Car"
_ORIGINAL_COMMAND_NAMES["Lincoln_Town_Car"] = {}

Lotus = _LazyNamespace("Lotus", "Lotus")
_ORIGINAL_SOURCE_NAMES["Lotus"] = "Lotus"
_ORIGINAL_COMMAND_NAMES["Lotus"] = {}

Lucid_Air = _LazyNamespace("Lucid-Air", "Lucid_Air")
_ORIGINAL_SOURCE_NAMES["Lucid_Air"] = "Lucid-Air"
_ORIGINAL_COMMAND_NAMES["Lucid_Air"] = {}

Maruti = _LazyNamespace("Maruti", "Maruti")
_ORIGINAL_SOURCE_NAMES["Maruti"] = "Maruti"
_ORIGINAL_COMMAND_NAMES["Maruti"] = {}

Maruti_Celerio = _LazyNamespace("Maruti-Celerio", "Maruti_Celerio")
_ORIGINAL_SOURCE_NAMES["Maruti_Celerio"] = "Maruti-Celerio"
_ORIGINAL_COMMAND_NAMES["Maruti_Celerio"] = {}

Maruti_Suzuki_Fronx_Delta = _LazyNamespace("Maruti-Suzuki-Fronx-Delta", "Maruti_Suzuki_Fronx_Delta")
_ORIGINAL_SOURCE_NAMES["Maruti_Suzuki_Fronx_Delta"] = "Maruti-Suzuki-Fronx-Delta"
_ORIGINAL_COMMAND_NAMES["Maruti_Suzuki_Fronx_Delta"] = {}

Maserati = _LazyNamespace("Maserati", "Maserati")
_ORIGINAL_SOURCE_NAMES["Maserati"] = "Maserati"
_ORIGINAL_COMMAND_NAMES["Maserati"] = {}

Maserati_Levante = _LazyNamespace("Maserati-Levante", "Maserati_Levante")
_ORIGINAL_SOURCE_NAMES["Maserati_Levante"] = "Maserati-Levante"
_ORIGINAL_COMMAND_NAMES["Maserati_Levante"] = {}

Maxus = _LazyNamespace("Maxus", "Maxus")
_ORIGINAL_SOURCE_NAMES["Maxus"] = "Maxus"
_ORIGINAL_COMMAND_NAMES["Maxus"] = {}

Maxus_eDeliver_3 = _LazyNamespace("Maxus-eDeliver-3", "Maxus_eDeliver_3")
_ORIGINAL_SOURCE_NAMES["Maxus_eDeliver_3"] = "Maxus-eDeliver-3"
_ORIGINAL_COMMAND_NAMES["Maxus_eDeliver_3"] = {}

Mazda = _LazyNamespace("Mazda", "Mazda")
_ORIGINAL_SOURCE_NAMES["Mazda"] = "Mazda"
_ORIGINAL_COMMAND_NAMES["Mazda"] = {}

Mazda_2 = _LazyNamespace("Mazda-2", "Mazda_2")
_ORIGINAL_SOURCE_NAMES["Mazda_2"] = "Mazda-2"
_ORIGINAL_COMMAND_NAMES["Mazda_2"] = {}

Mazda_3 = _LazyNamespace("Mazda-3", "Mazda_3")
_ORIGINAL_SOURCE_NAMES["Mazda_3"] = "Mazda-3"
_ORIGINAL_COMMAND_NAMES["Mazda_3"] = {}

Mazda_5 = _LazyNamespace("Mazda-5", "Mazda_5")
_ORIGINAL_SOURCE_NAMES["Mazda_5"] = "Mazda-5"
_ORIGINAL_COMMAND_NAMES["Mazda_5"] = {}

Mazda_6 = _LazyNamespace("Mazda-6", "Mazda_6")
_ORIGINAL_SOURCE_NAMES["Mazda_6"] = "Mazda-6"
_ORIGINAL_COMMAND_NAMES["Mazda_6"] = {}

Mazda_BT50 = _LazyNamespace("Mazda-BT50", "Mazda_BT50")
_ORIGINAL_SOURCE_NAMES["Mazda_BT50"] = "Mazda-BT50"
_ORIGINAL_COMMAND_NAMES["Mazda_BT50"] = {}

Mazda_CX_3 = _LazyNamespace("Mazda-CX-3", "Mazda_CX_3")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_3"] = "Mazda-CX-3"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_3"] = {}

Mazda_CX_30 = _LazyNamespace("Mazda-CX-30", "Mazda_CX_30")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_30"] = "Mazda-CX-30"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_30"] = {}

Mazda_CX_5 = _LazyNamespace("Mazda-CX-5", "Mazda_CX_5")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_5"] = "Mazda-CX-5"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_5"] = {}

Mazda_CX_50 = _LazyNamespace("Mazda-CX-50", "Mazda_CX_50")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_50"] = "Mazda-CX-50"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_50"] = {}

Mazda_CX_60 = _LazyNamespace("Mazda-CX-60", "Mazda_CX_60")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_60"] = "Mazda-CX-60"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_60"] = {}

Mazda_CX_7 = _LazyNamespace("Mazda-CX-7", "Mazda_CX_7")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_7"] = "Mazda-CX-7"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_7"] = {}

Mazda_CX_70 = _LazyNamespace("Mazda-CX-70", "Mazda_CX_70")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_70"] = "Mazda-CX-70"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_70"] = {}

Mazda_CX_9 = _LazyNamespace("Mazda-CX-9", "Mazda_CX_9")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_9"] = "Mazda-CX-9"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_9"] = {}

Mazda_CX_90 = _LazyNamespace("Mazda-CX-90", "Mazda_CX_90")
_ORIGINAL_SOURCE_NAMES["Mazda_CX_90"] = "Mazda-CX-90"
_ORIGINAL_COMMAND_NAMES["Mazda_CX_90"] = {}

Mazda_MX_30 = _LazyNamespace("Mazda-MX-30", "Mazda_MX_30")
_ORIGINAL_SOURCE_NAMES["Mazda_MX_30"] = "Mazda-MX-30"
_ORIGINAL_COMMAND_NAMES["Mazda_MX_30"] = {}

Mazda_MX_5 = _LazyNamespace("Mazda-MX-5", "Mazda_MX_5")
_ORIGINAL_SOURCE_NAMES["Mazda_MX_5"] = "Mazda-MX-5"
_ORIGINAL_COMMAND_NAMES["Mazda_MX_5"] = {}

Mazda_RX_7 = _LazyNamespace("Mazda-RX-7", "Mazda_RX_7")
_ORIGINAL_SOURCE_NAMES["Mazda_RX_7"] = "Mazda-RX-7"
_ORIGINAL_COMMAND_NAMES["Mazda_RX_7"] = {}

Mazda_Tribute = _LazyNamespace("Mazda-Tribute", "Mazda_Tribute")
_ORIGINAL_SOURCE_NAMES["Mazda_Tribute"] = "Mazda-Tribute"
_ORIGINAL_COMMAND_NAMES["Mazda_Tribute"] = {}

McLaren_Artura = _LazyNamespace("McLaren-Artura", "McLaren_Artura")
_ORIGINAL_SOURCE_NAMES["McLaren_Artura"] = "McLaren-Artura"
_ORIGINAL_COMMAND_NAMES["McLaren_Artura"] = {}

Mercedes_Benz = _LazyNamespace("Mercedes-Benz", "Mercedes_Benz")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz"] = "Mercedes-Benz"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz"] = {}

Mercedes_Benz_A_180 = _LazyNamespace("Mercedes-Benz-A-180", "Mercedes_Benz_A_180")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_A_180"] = "Mercedes-Benz-A-180"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_A_180"] = {}

Mercedes_Benz_A_200 = _LazyNamespace("Mercedes-Benz-A-200", "Mercedes_Benz_A_200")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_A_200"] = "Mercedes-Benz-A-200"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_A_200"] = {}

Mercedes_Benz_A_220 = _LazyNamespace("Mercedes-Benz-A-220", "Mercedes_Benz_A_220")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_A_220"] = "Mercedes-Benz-A-220"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_A_220"] = {}

Mercedes_Benz_AMG_A_45 = _LazyNamespace("Mercedes-Benz-AMG-A-45", "Mercedes_Benz_AMG_A_45")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_AMG_A_45"] = "Mercedes-Benz-AMG-A-45"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_AMG_A_45"] = {}

Mercedes_Benz_AMG_GT = _LazyNamespace("Mercedes-Benz-AMG-GT", "Mercedes_Benz_AMG_GT")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_AMG_GT"] = "Mercedes-Benz-AMG-GT"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_AMG_GT"] = {}

Mercedes_Benz_C_180 = _LazyNamespace("Mercedes-Benz-C-180", "Mercedes_Benz_C_180")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_C_180"] = "Mercedes-Benz-C-180"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_C_180"] = {}

Mercedes_Benz_C_Class = _LazyNamespace("Mercedes-Benz-C-Class", "Mercedes_Benz_C_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_C_Class"] = "Mercedes-Benz-C-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_C_Class"] = {}

Mercedes_Benz_C200d = _LazyNamespace("Mercedes-Benz-C200d", "Mercedes_Benz_C200d")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_C200d"] = "Mercedes-Benz-C200d"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_C200d"] = {}

Mercedes_Benz_CLA_200 = _LazyNamespace("Mercedes-Benz-CLA-200", "Mercedes_Benz_CLA_200")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_CLA_200"] = "Mercedes-Benz-CLA-200"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_CLA_200"] = {}

Mercedes_Benz_CLA_Class = _LazyNamespace("Mercedes-Benz-CLA-Class", "Mercedes_Benz_CLA_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_CLA_Class"] = "Mercedes-Benz-CLA-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_CLA_Class"] = {}

Mercedes_Benz_CLS = _LazyNamespace("Mercedes-Benz-CLS", "Mercedes_Benz_CLS")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_CLS"] = "Mercedes-Benz-CLS"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_CLS"] = {}

Mercedes_Benz_E_Class = _LazyNamespace("Mercedes-Benz-E-Class", "Mercedes_Benz_E_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_E_Class"] = "Mercedes-Benz-E-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_E_Class"] = {}

Mercedes_Benz_E180 = _LazyNamespace("Mercedes-Benz-E180", "Mercedes_Benz_E180")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_E180"] = "Mercedes-Benz-E180"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_E180"] = {}

Mercedes_Benz_EQA = _LazyNamespace("Mercedes-Benz-EQA", "Mercedes_Benz_EQA")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_EQA"] = "Mercedes-Benz-EQA"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_EQA"] = {}

Mercedes_Benz_EQB = _LazyNamespace("Mercedes-Benz-EQB", "Mercedes_Benz_EQB")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_EQB"] = "Mercedes-Benz-EQB"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_EQB"] = {}

Mercedes_Benz_EQE = _LazyNamespace("Mercedes-Benz-EQE", "Mercedes_Benz_EQE")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_EQE"] = "Mercedes-Benz-EQE"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_EQE"] = {}

Mercedes_Benz_EQS = _LazyNamespace("Mercedes-Benz-EQS", "Mercedes_Benz_EQS")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_EQS"] = "Mercedes-Benz-EQS"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_EQS"] = {}

Mercedes_Benz_EQS_Class_Sedan = _LazyNamespace("Mercedes-Benz-EQS-Class-Sedan", "Mercedes_Benz_EQS_Class_Sedan")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_EQS_Class_Sedan"] = "Mercedes-Benz-EQS-Class-Sedan"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_EQS_Class_Sedan"] = {}

Mercedes_Benz_G_Class = _LazyNamespace("Mercedes-Benz-G-Class", "Mercedes_Benz_G_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_G_Class"] = "Mercedes-Benz-G-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_G_Class"] = {}

Mercedes_Benz_GLA250 = _LazyNamespace("Mercedes-Benz-GLA250", "Mercedes_Benz_GLA250")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_GLA250"] = "Mercedes-Benz-GLA250"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_GLA250"] = {}

Mercedes_Benz_GLB_250 = _LazyNamespace("Mercedes-Benz-GLB-250", "Mercedes_Benz_GLB_250")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_GLB_250"] = "Mercedes-Benz-GLB-250"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_GLB_250"] = {}

Mercedes_Benz_GLC_Class = _LazyNamespace("Mercedes-Benz-GLC-Class", "Mercedes_Benz_GLC_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_GLC_Class"] = "Mercedes-Benz-GLC-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_GLC_Class"] = {}

Mercedes_Benz_Ml63 = _LazyNamespace("Mercedes-Benz-Ml63", "Mercedes_Benz_Ml63")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_Ml63"] = "Mercedes-Benz-Ml63"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_Ml63"] = {}

Mercedes_Benz_S_Class = _LazyNamespace("Mercedes-Benz-S-Class", "Mercedes_Benz_S_Class")
_ORIGINAL_SOURCE_NAMES["Mercedes_Benz_S_Class"] = "Mercedes-Benz-S-Class"
_ORIGINAL_COMMAND_NAMES["Mercedes_Benz_S_Class"] = {}

MG = _LazyNamespace("MG", "MG")
_ORIGINAL_SOURCE_NAMES["MG"] = "MG"
_ORIGINAL_COMMAND_NAMES["MG"] = {}

MG_Comet = _LazyNamespace("MG-Comet", "MG_Comet")
_ORIGINAL_SOURCE_NAMES["MG_Comet"] = "MG-Comet"
_ORIGINAL_COMMAND_NAMES["MG_Comet"] = {}

MG_Hector = _LazyNamespace("MG-Hector", "MG_Hector")
_ORIGINAL_SOURCE_NAMES["MG_Hector"] = "MG-Hector"
_ORIGINAL_COMMAND_NAMES["MG_Hector"] = {}

MG_HS = _LazyNamespace("MG-HS", "MG_HS")
_ORIGINAL_SOURCE_NAMES["MG_HS"] = "MG-HS"
_ORIGINAL_COMMAND_NAMES["MG_HS"] = {}

MG_MG4 = _LazyNamespace("MG-MG4", "MG_MG4")
_ORIGINAL_SOURCE_NAMES["MG_MG4"] = "MG-MG4"
_ORIGINAL_COMMAND_NAMES["MG_MG4"] = {}

MG_One = _LazyNamespace("MG-One", "MG_One")
_ORIGINAL_SOURCE_NAMES["MG_One"] = "MG-One"
_ORIGINAL_COMMAND_NAMES["MG_One"] = {}

MG_ZS = _LazyNamespace("MG-ZS", "MG_ZS")
_ORIGINAL_SOURCE_NAMES["MG_ZS"] = "MG-ZS"
_ORIGINAL_COMMAND_NAMES["MG_ZS"] = {}

MG_ZS_EV = _LazyNamespace("MG-ZS-EV", "MG_ZS_EV")
_ORIGINAL_SOURCE_NAMES["MG_ZS_EV"] = "MG-ZS-EV"
_ORIGINAL_COMMAND_NAMES["MG_ZS_EV"] = {}

MINI = _LazyNamespace("MINI", "MINI")
_ORIGINAL_SOURCE_NAMES["MINI"] = "MINI"
_ORIGINAL_COMMAND_NAMES["MINI"] = {}

MINI_Clubman = _LazyNamespace("MINI-Clubman", "MINI_Clubman")
_ORIGINAL_SOURCE_NAMES["MINI_Clubman"] = "MINI-Clubman"
_ORIGINAL_COMMAND_NAMES["MINI_Clubman"] = {}

MINI_Cooper = _LazyNamespace("MINI-Cooper", "MINI_Cooper")
_ORIGINAL_SOURCE_NAMES["MINI_Cooper"] = "MINI-Cooper"
_ORIGINAL_COMMAND_NAMES["MINI_Cooper"] = {}

MINI_Cooper_S = _LazyNamespace("MINI-Cooper-S", "MINI_Cooper_S")
_ORIGINAL_SOURCE_NAMES["MINI_Cooper_S"] = "MINI-Cooper-S"
_ORIGINAL_COMMAND_NAMES["MINI_Cooper_S"] = {}

MINI_Cooper_SE = _LazyNamespace("MINI-Cooper-SE", "MINI_Cooper_SE")
_ORIGINAL_SOURCE_NAMES["MINI_Cooper_SE"] = "MINI-Cooper-SE"
_ORIGINAL_COMMAND_NAMES["MINI_Cooper_SE"] = {}

MINI_Countryman = _LazyNamespace("MINI-Countryman", "MINI_Countryman")
_ORIGINAL_SOURCE_NAMES["MINI_Countryman"] = "MINI-Countryman"
_ORIGINAL_COMMAND_NAMES["MINI_Countryman"] = {}

MINI_Hardtop = _LazyNamespace("MINI-Hardtop", "MINI_Hardtop")
_ORIGINAL_SOURCE_NAMES["MINI_Hardtop"] = "MINI-Hardtop"
_ORIGINAL_COMMAND_NAMES["MINI_Hardtop"] = {}

MINI_JCW = _LazyNamespace("MINI-JCW", "MINI_JCW")
_ORIGINAL_SOURCE_NAMES["MINI_JCW"] = "MINI-JCW"
_ORIGINAL_COMMAND_NAMES["MINI_JCW"] = {}

Mitsubishi = _LazyNamespace("Mitsubishi", "Mitsubishi")
_ORIGINAL_SOURCE_NAMES["Mitsubishi"] = "Mitsubishi"
_ORIGINAL_COMMAND_NAMES["Mitsubishi"] = {}

Mitsubishi_ASX = _LazyNamespace("Mitsubishi-ASX", "Mitsubishi_ASX")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_ASX"] = "Mitsubishi-ASX"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_ASX"] = {}

Mitsubishi_Challenger = _LazyNamespace("Mitsubishi-Challenger", "Mitsubishi_Challenger")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Challenger"] = "Mitsubishi-Challenger"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Challenger"] = {}

Mitsubishi_Eclipse_Cross = _LazyNamespace("Mitsubishi-Eclipse-Cross", "Mitsubishi_Eclipse_Cross")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Eclipse_Cross"] = "Mitsubishi-Eclipse-Cross"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Eclipse_Cross"] = {}

Mitsubishi_Eclipse_Cross_PHEV = _LazyNamespace("Mitsubishi-Eclipse-Cross-PHEV", "Mitsubishi_Eclipse_Cross_PHEV")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Eclipse_Cross_PHEV"] = "Mitsubishi-Eclipse-Cross-PHEV"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Eclipse_Cross_PHEV"] = {}

Mitsubishi_Lancer = _LazyNamespace("Mitsubishi-Lancer", "Mitsubishi_Lancer")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Lancer"] = "Mitsubishi-Lancer"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Lancer"] = {}

Mitsubishi_Mirage = _LazyNamespace("Mitsubishi-Mirage", "Mitsubishi_Mirage")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Mirage"] = "Mitsubishi-Mirage"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Mirage"] = {}

Mitsubishi_Outlander = _LazyNamespace("Mitsubishi-Outlander", "Mitsubishi_Outlander")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Outlander"] = "Mitsubishi-Outlander"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Outlander"] = {}

Mitsubishi_Outlander_PHEV = _LazyNamespace("Mitsubishi-Outlander-PHEV", "Mitsubishi_Outlander_PHEV")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Outlander_PHEV"] = "Mitsubishi-Outlander-PHEV"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Outlander_PHEV"] = {}

Mitsubishi_Outlander_Sport = _LazyNamespace("Mitsubishi-Outlander-Sport", "Mitsubishi_Outlander_Sport")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Outlander_Sport"] = "Mitsubishi-Outlander-Sport"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Outlander_Sport"] = {}

Mitsubishi_Pajero = _LazyNamespace("Mitsubishi-Pajero", "Mitsubishi_Pajero")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Pajero"] = "Mitsubishi-Pajero"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Pajero"] = {}

Mitsubishi_RVR = _LazyNamespace("Mitsubishi-RVR", "Mitsubishi_RVR")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_RVR"] = "Mitsubishi-RVR"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_RVR"] = {}

Mitsubishi_Triton = _LazyNamespace("Mitsubishi-Triton", "Mitsubishi_Triton")
_ORIGINAL_SOURCE_NAMES["Mitsubishi_Triton"] = "Mitsubishi-Triton"
_ORIGINAL_COMMAND_NAMES["Mitsubishi_Triton"] = {}

Nissan = _LazyNamespace("Nissan", "Nissan")
_ORIGINAL_SOURCE_NAMES["Nissan"] = "Nissan"
_ORIGINAL_COMMAND_NAMES["Nissan"] = {}

Nissan_Altima = _LazyNamespace("Nissan-Altima", "Nissan_Altima")
_ORIGINAL_SOURCE_NAMES["Nissan_Altima"] = "Nissan-Altima"
_ORIGINAL_COMMAND_NAMES["Nissan_Altima"] = {}

Nissan_ARIYA = _LazyNamespace("Nissan-ARIYA", "Nissan_ARIYA")
_ORIGINAL_SOURCE_NAMES["Nissan_ARIYA"] = "Nissan-ARIYA"
_ORIGINAL_COMMAND_NAMES["Nissan_ARIYA"] = {}

Nissan_Armada = _LazyNamespace("Nissan-Armada", "Nissan_Armada")
_ORIGINAL_SOURCE_NAMES["Nissan_Armada"] = "Nissan-Armada"
_ORIGINAL_COMMAND_NAMES["Nissan_Armada"] = {}

Nissan_Frontier = _LazyNamespace("Nissan-Frontier", "Nissan_Frontier")
_ORIGINAL_SOURCE_NAMES["Nissan_Frontier"] = "Nissan-Frontier"
_ORIGINAL_COMMAND_NAMES["Nissan_Frontier"] = {}

Nissan_Juke = _LazyNamespace("Nissan-Juke", "Nissan_Juke")
_ORIGINAL_SOURCE_NAMES["Nissan_Juke"] = "Nissan-Juke"
_ORIGINAL_COMMAND_NAMES["Nissan_Juke"] = {}

Nissan_Kicks = _LazyNamespace("Nissan-Kicks", "Nissan_Kicks")
_ORIGINAL_SOURCE_NAMES["Nissan_Kicks"] = "Nissan-Kicks"
_ORIGINAL_COMMAND_NAMES["Nissan_Kicks"] = {}

Nissan_Leaf = _LazyNamespace("Nissan-Leaf", "Nissan_Leaf")
_ORIGINAL_SOURCE_NAMES["Nissan_Leaf"] = "Nissan-Leaf"
_ORIGINAL_COMMAND_NAMES["Nissan_Leaf"] = {}

Nissan_Maxima = _LazyNamespace("Nissan-Maxima", "Nissan_Maxima")
_ORIGINAL_SOURCE_NAMES["Nissan_Maxima"] = "Nissan-Maxima"
_ORIGINAL_COMMAND_NAMES["Nissan_Maxima"] = {}

Nissan_Murano = _LazyNamespace("Nissan-Murano", "Nissan_Murano")
_ORIGINAL_SOURCE_NAMES["Nissan_Murano"] = "Nissan-Murano"
_ORIGINAL_COMMAND_NAMES["Nissan_Murano"] = {}

Nissan_Navara = _LazyNamespace("Nissan-Navara", "Nissan_Navara")
_ORIGINAL_SOURCE_NAMES["Nissan_Navara"] = "Nissan-Navara"
_ORIGINAL_COMMAND_NAMES["Nissan_Navara"] = {}

Nissan_Pathfinder = _LazyNamespace("Nissan-Pathfinder", "Nissan_Pathfinder")
_ORIGINAL_SOURCE_NAMES["Nissan_Pathfinder"] = "Nissan-Pathfinder"
_ORIGINAL_COMMAND_NAMES["Nissan_Pathfinder"] = {}

Nissan_Patrol = _LazyNamespace("Nissan-Patrol", "Nissan_Patrol")
_ORIGINAL_SOURCE_NAMES["Nissan_Patrol"] = "Nissan-Patrol"
_ORIGINAL_COMMAND_NAMES["Nissan_Patrol"] = {}

Nissan_Pulsar = _LazyNamespace("Nissan-Pulsar", "Nissan_Pulsar")
_ORIGINAL_SOURCE_NAMES["Nissan_Pulsar"] = "Nissan-Pulsar"
_ORIGINAL_COMMAND_NAMES["Nissan_Pulsar"] = {}

Nissan_Qashqai = _LazyNamespace("Nissan-Qashqai", "Nissan_Qashqai")
_ORIGINAL_SOURCE_NAMES["Nissan_Qashqai"] = "Nissan-Qashqai"
_ORIGINAL_COMMAND_NAMES["Nissan_Qashqai"] = {}

Nissan_Rogue = _LazyNamespace("Nissan-Rogue", "Nissan_Rogue")
_ORIGINAL_SOURCE_NAMES["Nissan_Rogue"] = "Nissan-Rogue"
_ORIGINAL_COMMAND_NAMES["Nissan_Rogue"] = {}

Nissan_Rogue_Sport = _LazyNamespace("Nissan-Rogue-Sport", "Nissan_Rogue_Sport")
_ORIGINAL_SOURCE_NAMES["Nissan_Rogue_Sport"] = "Nissan-Rogue-Sport"
_ORIGINAL_COMMAND_NAMES["Nissan_Rogue_Sport"] = {}

Nissan_Sentra = _LazyNamespace("Nissan-Sentra", "Nissan_Sentra")
_ORIGINAL_SOURCE_NAMES["Nissan_Sentra"] = "Nissan-Sentra"
_ORIGINAL_COMMAND_NAMES["Nissan_Sentra"] = {}

Nissan_Titan = _LazyNamespace("Nissan-Titan", "Nissan_Titan")
_ORIGINAL_SOURCE_NAMES["Nissan_Titan"] = "Nissan-Titan"
_ORIGINAL_COMMAND_NAMES["Nissan_Titan"] = {}

Nissan_Versa = _LazyNamespace("Nissan-Versa", "Nissan_Versa")
_ORIGINAL_SOURCE_NAMES["Nissan_Versa"] = "Nissan-Versa"
_ORIGINAL_COMMAND_NAMES["Nissan_Versa"] = {}

Nissan_X_Trail = _LazyNamespace("Nissan-X-Trail", "Nissan_X_Trail")
_ORIGINAL_SOURCE_NAMES["Nissan_X_Trail"] = "Nissan-X-Trail"
_ORIGINAL_COMMAND_NAMES["Nissan_X_Trail"] = {}

Nissan_Xterra = _LazyNamespace("Nissan-Xterra", "Nissan_Xterra")
_ORIGINAL_SOURCE_NAMES["Nissan_Xterra"] = "Nissan-Xterra"
_ORIGINAL_COMMAND_NAMES["Nissan_Xterra"] = {}

NissanInfiniti = _LazyNamespace("NissanInfiniti", "NissanInfiniti")
_ORIGINAL_SOURCE_NAMES["NissanInfiniti"] = "NissanInfiniti"
_ORIGINAL_COMMAND_NAMES["NissanInfiniti"] = {}

Omoda = _LazyNamespace("Omoda", "Omoda")
_ORIGINAL_SOURCE_NAMES["Omoda"] = "Omoda"
_ORIGINAL_COMMAND_NAMES["Omoda"] = {}

Omoda_Omoda_5_EV = _LazyNamespace("Omoda-Omoda-5-EV", "Omoda_Omoda_5_EV")
_ORIGINAL_SOURCE_NAMES["Omoda_Omoda_5_EV"] = "Omoda-Omoda-5-EV"
_ORIGINAL_COMMAND_NAMES["Omoda_Omoda_5_EV"] = {}

Perodua_Bezza = _LazyNamespace("Perodua-Bezza", "Perodua_Bezza")
_ORIGINAL_SOURCE_NAMES["Perodua_Bezza"] = "Perodua-Bezza"
_ORIGINAL_COMMAND_NAMES["Perodua_Bezza"] = {}

Peugeot = _LazyNamespace("Peugeot", "Peugeot")
_ORIGINAL_SOURCE_NAMES["Peugeot"] = "Peugeot"
_ORIGINAL_COMMAND_NAMES["Peugeot"] = {}

Peugeot_2008 = _LazyNamespace("Peugeot-2008", "Peugeot_2008")
_ORIGINAL_SOURCE_NAMES["Peugeot_2008"] = "Peugeot-2008"
_ORIGINAL_COMMAND_NAMES["Peugeot_2008"] = {}

Peugeot_205 = _LazyNamespace("Peugeot-205", "Peugeot_205")
_ORIGINAL_SOURCE_NAMES["Peugeot_205"] = "Peugeot-205"
_ORIGINAL_COMMAND_NAMES["Peugeot_205"] = {}

Peugeot_206 = _LazyNamespace("Peugeot-206", "Peugeot_206")
_ORIGINAL_SOURCE_NAMES["Peugeot_206"] = "Peugeot-206"
_ORIGINAL_COMMAND_NAMES["Peugeot_206"] = {}

Peugeot_207 = _LazyNamespace("Peugeot-207", "Peugeot_207")
_ORIGINAL_SOURCE_NAMES["Peugeot_207"] = "Peugeot-207"
_ORIGINAL_COMMAND_NAMES["Peugeot_207"] = {}

Peugeot_208 = _LazyNamespace("Peugeot-208", "Peugeot_208")
_ORIGINAL_SOURCE_NAMES["Peugeot_208"] = "Peugeot-208"
_ORIGINAL_COMMAND_NAMES["Peugeot_208"] = {}

Peugeot_3008 = _LazyNamespace("Peugeot-3008", "Peugeot_3008")
_ORIGINAL_SOURCE_NAMES["Peugeot_3008"] = "Peugeot-3008"
_ORIGINAL_COMMAND_NAMES["Peugeot_3008"] = {}

Peugeot_307 = _LazyNamespace("Peugeot-307", "Peugeot_307")
_ORIGINAL_SOURCE_NAMES["Peugeot_307"] = "Peugeot-307"
_ORIGINAL_COMMAND_NAMES["Peugeot_307"] = {}

Peugeot_308 = _LazyNamespace("Peugeot-308", "Peugeot_308")
_ORIGINAL_SOURCE_NAMES["Peugeot_308"] = "Peugeot-308"
_ORIGINAL_COMMAND_NAMES["Peugeot_308"] = {}

Peugeot_308_Hybrid = _LazyNamespace("Peugeot-308-Hybrid", "Peugeot_308_Hybrid")
_ORIGINAL_SOURCE_NAMES["Peugeot_308_Hybrid"] = "Peugeot-308-Hybrid"
_ORIGINAL_COMMAND_NAMES["Peugeot_308_Hybrid"] = {}

Peugeot_407 = _LazyNamespace("Peugeot-407", "Peugeot_407")
_ORIGINAL_SOURCE_NAMES["Peugeot_407"] = "Peugeot-407"
_ORIGINAL_COMMAND_NAMES["Peugeot_407"] = {}

Peugeot_505 = _LazyNamespace("Peugeot-505", "Peugeot_505")
_ORIGINAL_SOURCE_NAMES["Peugeot_505"] = "Peugeot-505"
_ORIGINAL_COMMAND_NAMES["Peugeot_505"] = {}

Peugeot_508 = _LazyNamespace("Peugeot-508", "Peugeot_508")
_ORIGINAL_SOURCE_NAMES["Peugeot_508"] = "Peugeot-508"
_ORIGINAL_COMMAND_NAMES["Peugeot_508"] = {}

Peugeot_e_208 = _LazyNamespace("Peugeot-e-208", "Peugeot_e_208")
_ORIGINAL_SOURCE_NAMES["Peugeot_e_208"] = "Peugeot-e-208"
_ORIGINAL_COMMAND_NAMES["Peugeot_e_208"] = {}

Peugeot_Expert = _LazyNamespace("Peugeot-Expert", "Peugeot_Expert")
_ORIGINAL_SOURCE_NAMES["Peugeot_Expert"] = "Peugeot-Expert"
_ORIGINAL_COMMAND_NAMES["Peugeot_Expert"] = {}

Polestar = _LazyNamespace("Polestar", "Polestar")
_ORIGINAL_SOURCE_NAMES["Polestar"] = "Polestar"
_ORIGINAL_COMMAND_NAMES["Polestar"] = {}

Polestar_2 = _LazyNamespace("Polestar-2", "Polestar_2")
_ORIGINAL_SOURCE_NAMES["Polestar_2"] = "Polestar-2"
_ORIGINAL_COMMAND_NAMES["Polestar_2"] = {}

Polestar_3 = _LazyNamespace("Polestar-3", "Polestar_3")
_ORIGINAL_SOURCE_NAMES["Polestar_3"] = "Polestar-3"
_ORIGINAL_COMMAND_NAMES["Polestar_3"] = {}

Polestar_4 = _LazyNamespace("Polestar-4", "Polestar_4")
_ORIGINAL_SOURCE_NAMES["Polestar_4"] = "Polestar-4"
_ORIGINAL_COMMAND_NAMES["Polestar_4"] = {}

Pontiac_Vibe = _LazyNamespace("Pontiac-Vibe", "Pontiac_Vibe")
_ORIGINAL_SOURCE_NAMES["Pontiac_Vibe"] = "Pontiac-Vibe"
_ORIGINAL_COMMAND_NAMES["Pontiac_Vibe"] = {}

Porsche = _LazyNamespace("Porsche", "Porsche")
_ORIGINAL_SOURCE_NAMES["Porsche"] = "Porsche"
_ORIGINAL_COMMAND_NAMES["Porsche"] = {}

Porsche_718 = _LazyNamespace("Porsche-718", "Porsche_718")
_ORIGINAL_SOURCE_NAMES["Porsche_718"] = "Porsche-718"
_ORIGINAL_COMMAND_NAMES["Porsche_718"] = {}

Porsche_911 = _LazyNamespace("Porsche-911", "Porsche_911")
_ORIGINAL_SOURCE_NAMES["Porsche_911"] = "Porsche-911"
_ORIGINAL_COMMAND_NAMES["Porsche_911"] = {}

Porsche_981_Cayman = _LazyNamespace("Porsche-981-Cayman", "Porsche_981_Cayman")
_ORIGINAL_SOURCE_NAMES["Porsche_981_Cayman"] = "Porsche-981-Cayman"
_ORIGINAL_COMMAND_NAMES["Porsche_981_Cayman"] = {}

Porsche_Boxster = _LazyNamespace("Porsche-Boxster", "Porsche_Boxster")
_ORIGINAL_SOURCE_NAMES["Porsche_Boxster"] = "Porsche-Boxster"
_ORIGINAL_COMMAND_NAMES["Porsche_Boxster"] = {}

Porsche_Cayenne = _LazyNamespace("Porsche-Cayenne", "Porsche_Cayenne")
_ORIGINAL_SOURCE_NAMES["Porsche_Cayenne"] = "Porsche-Cayenne"
_ORIGINAL_COMMAND_NAMES["Porsche_Cayenne"] = {}

Porsche_Cayman = _LazyNamespace("Porsche-Cayman", "Porsche_Cayman")
_ORIGINAL_SOURCE_NAMES["Porsche_Cayman"] = "Porsche-Cayman"
_ORIGINAL_COMMAND_NAMES["Porsche_Cayman"] = {}

Porsche_Macan = _LazyNamespace("Porsche-Macan", "Porsche_Macan")
_ORIGINAL_SOURCE_NAMES["Porsche_Macan"] = "Porsche-Macan"
_ORIGINAL_COMMAND_NAMES["Porsche_Macan"] = {}

Porsche_Macan_Electric = _LazyNamespace("Porsche-Macan-Electric", "Porsche_Macan_Electric")
_ORIGINAL_SOURCE_NAMES["Porsche_Macan_Electric"] = "Porsche-Macan-Electric"
_ORIGINAL_COMMAND_NAMES["Porsche_Macan_Electric"] = {}

Porsche_Panamera = _LazyNamespace("Porsche-Panamera", "Porsche_Panamera")
_ORIGINAL_SOURCE_NAMES["Porsche_Panamera"] = "Porsche-Panamera"
_ORIGINAL_COMMAND_NAMES["Porsche_Panamera"] = {}

Porsche_Taycan = _LazyNamespace("Porsche-Taycan", "Porsche_Taycan")
_ORIGINAL_SOURCE_NAMES["Porsche_Taycan"] = "Porsche-Taycan"
_ORIGINAL_COMMAND_NAMES["Porsche_Taycan"] = {}

Ram = _LazyNamespace("Ram", "Ram")
_ORIGINAL_SOURCE_NAMES["Ram"] = "Ram"
_ORIGINAL_COMMAND_NAMES["Ram"] = {}

Ram_1500 = _LazyNamespace("Ram-1500", "Ram_1500")
_ORIGINAL_SOURCE_NAMES["Ram_1500"] = "Ram-1500"
_ORIGINAL_COMMAND_NAMES["Ram_1500"] = {}

Ram_2500 = _LazyNamespace("Ram-2500", "Ram_2500")
_ORIGINAL_SOURCE_NAMES["Ram_2500"] = "Ram-2500"
_ORIGINAL_COMMAND_NAMES["Ram_2500"] = {}

Ram_3500 = _LazyNamespace("Ram-3500", "Ram_3500")
_ORIGINAL_SOURCE_NAMES["Ram_3500"] = "Ram-3500"
_ORIGINAL_COMMAND_NAMES["Ram_3500"] = {}

Renault = _LazyNamespace("Renault", "Renault")
_ORIGINAL_SOURCE_NAMES["Renault"] = "Renault"
_ORIGINAL_COMMAND_NAMES["Renault"] = {}

Renault_Captur = _LazyNamespace("Renault-Captur", "Renault_Captur")
_ORIGINAL_SOURCE_NAMES["Renault_Captur"] = "Renault-Captur"
_ORIGINAL_COMMAND_NAMES["Renault_Captur"] = {}

Renault_Clio = _LazyNamespace("Renault-Clio", "Renault_Clio")
_ORIGINAL_SOURCE_NAMES["Renault_Clio"] = "Renault-Clio"
_ORIGINAL_COMMAND_NAMES["Renault_Clio"] = {}

Renault_Clio_III = _LazyNamespace("Renault-Clio-III", "Renault_Clio_III")
_ORIGINAL_SOURCE_NAMES["Renault_Clio_III"] = "Renault-Clio-III"
_ORIGINAL_COMMAND_NAMES["Renault_Clio_III"] = {}

Renault_Clio_V = _LazyNamespace("Renault-Clio-V", "Renault_Clio_V")
_ORIGINAL_SOURCE_NAMES["Renault_Clio_V"] = "Renault-Clio-V"
_ORIGINAL_COMMAND_NAMES["Renault_Clio_V"] = {}

Renault_Kadjar = _LazyNamespace("Renault-Kadjar", "Renault_Kadjar")
_ORIGINAL_SOURCE_NAMES["Renault_Kadjar"] = "Renault-Kadjar"
_ORIGINAL_COMMAND_NAMES["Renault_Kadjar"] = {}

Renault_Koleos = _LazyNamespace("Renault-Koleos", "Renault_Koleos")
_ORIGINAL_SOURCE_NAMES["Renault_Koleos"] = "Renault-Koleos"
_ORIGINAL_COMMAND_NAMES["Renault_Koleos"] = {}

Renault_Kwid = _LazyNamespace("Renault-Kwid", "Renault_Kwid")
_ORIGINAL_SOURCE_NAMES["Renault_Kwid"] = "Renault-Kwid"
_ORIGINAL_COMMAND_NAMES["Renault_Kwid"] = {}

Renault_Megane = _LazyNamespace("Renault-Megane", "Renault_Megane")
_ORIGINAL_SOURCE_NAMES["Renault_Megane"] = "Renault-Megane"
_ORIGINAL_COMMAND_NAMES["Renault_Megane"] = {}

Renault_Megane_E_Tech = _LazyNamespace("Renault-Megane-E-Tech", "Renault_Megane_E_Tech")
_ORIGINAL_SOURCE_NAMES["Renault_Megane_E_Tech"] = "Renault-Megane-E-Tech"
_ORIGINAL_COMMAND_NAMES["Renault_Megane_E_Tech"] = {}

Renault_Symbol = _LazyNamespace("Renault-Symbol", "Renault_Symbol")
_ORIGINAL_SOURCE_NAMES["Renault_Symbol"] = "Renault-Symbol"
_ORIGINAL_COMMAND_NAMES["Renault_Symbol"] = {}

Renault_ZOE = _LazyNamespace("Renault-ZOE", "Renault_ZOE")
_ORIGINAL_SOURCE_NAMES["Renault_ZOE"] = "Renault-ZOE"
_ORIGINAL_COMMAND_NAMES["Renault_ZOE"] = {}

Rivian = _LazyNamespace("Rivian", "Rivian")
_ORIGINAL_SOURCE_NAMES["Rivian"] = "Rivian"
_ORIGINAL_COMMAND_NAMES["Rivian"] = {}

Rivian_R1S = _LazyNamespace("Rivian-R1S", "Rivian_R1S")
_ORIGINAL_SOURCE_NAMES["Rivian_R1S"] = "Rivian-R1S"
_ORIGINAL_COMMAND_NAMES["Rivian_R1S"] = {}

Rivian_R1T = _LazyNamespace("Rivian-R1T", "Rivian_R1T")
_ORIGINAL_SOURCE_NAMES["Rivian_R1T"] = "Rivian-R1T"
_ORIGINAL_COMMAND_NAMES["Rivian_R1T"] = {}

Rolls_Royce = _LazyNamespace("Rolls-Royce", "Rolls_Royce")
_ORIGINAL_SOURCE_NAMES["Rolls_Royce"] = "Rolls-Royce"
_ORIGINAL_COMMAND_NAMES["Rolls_Royce"] = {}

Saab = _LazyNamespace("Saab", "Saab")
_ORIGINAL_SOURCE_NAMES["Saab"] = "Saab"
_ORIGINAL_COMMAND_NAMES["Saab"] = {}

Saab_9_3 = _LazyNamespace("Saab-9-3", "Saab_9_3")
_ORIGINAL_SOURCE_NAMES["Saab_9_3"] = "Saab-9-3"
_ORIGINAL_COMMAND_NAMES["Saab_9_3"] = {}

Saab_9_5 = _LazyNamespace("Saab-9-5", "Saab_9_5")
_ORIGINAL_SOURCE_NAMES["Saab_9_5"] = "Saab-9-5"
_ORIGINAL_COMMAND_NAMES["Saab_9_5"] = {}

SAEJ1979 = _LazyNamespace("SAEJ1979", "SAEJ1979")
_ORIGINAL_SOURCE_NAMES["SAEJ1979"] = "SAEJ1979"
_ORIGINAL_COMMAND_NAMES["SAEJ1979"] = {}

Scion = _LazyNamespace("Scion", "Scion")
_ORIGINAL_SOURCE_NAMES["Scion"] = "Scion"
_ORIGINAL_COMMAND_NAMES["Scion"] = {}

Scion_FR_S = _LazyNamespace("Scion-FR-S", "Scion_FR_S")
_ORIGINAL_SOURCE_NAMES["Scion_FR_S"] = "Scion-FR-S"
_ORIGINAL_COMMAND_NAMES["Scion_FR_S"] = {}

Scion_iQ = _LazyNamespace("Scion-iQ", "Scion_iQ")
_ORIGINAL_SOURCE_NAMES["Scion_iQ"] = "Scion-iQ"
_ORIGINAL_COMMAND_NAMES["Scion_iQ"] = {}

Scion_tC = _LazyNamespace("Scion-tC", "Scion_tC")
_ORIGINAL_SOURCE_NAMES["Scion_tC"] = "Scion-tC"
_ORIGINAL_COMMAND_NAMES["Scion_tC"] = {}

Scion_xB = _LazyNamespace("Scion-xB", "Scion_xB")
_ORIGINAL_SOURCE_NAMES["Scion_xB"] = "Scion-xB"
_ORIGINAL_COMMAND_NAMES["Scion_xB"] = {}

SEAT = _LazyNamespace("SEAT", "SEAT")
_ORIGINAL_SOURCE_NAMES["SEAT"] = "SEAT"
_ORIGINAL_COMMAND_NAMES["SEAT"] = {}

Seat_Alhambra = _LazyNamespace("Seat-Alhambra", "Seat_Alhambra")
_ORIGINAL_SOURCE_NAMES["Seat_Alhambra"] = "Seat-Alhambra"
_ORIGINAL_COMMAND_NAMES["Seat_Alhambra"] = {}

Seat_Altea = _LazyNamespace("Seat-Altea", "Seat_Altea")
_ORIGINAL_SOURCE_NAMES["Seat_Altea"] = "Seat-Altea"
_ORIGINAL_COMMAND_NAMES["Seat_Altea"] = {}

Seat_Arona = _LazyNamespace("Seat-Arona", "Seat_Arona")
_ORIGINAL_SOURCE_NAMES["Seat_Arona"] = "Seat-Arona"
_ORIGINAL_COMMAND_NAMES["Seat_Arona"] = {}

Seat_Ateca = _LazyNamespace("Seat-Ateca", "Seat_Ateca")
_ORIGINAL_SOURCE_NAMES["Seat_Ateca"] = "Seat-Ateca"
_ORIGINAL_COMMAND_NAMES["Seat_Ateca"] = {}

Seat_Ibiza = _LazyNamespace("Seat-Ibiza", "Seat_Ibiza")
_ORIGINAL_SOURCE_NAMES["Seat_Ibiza"] = "Seat-Ibiza"
_ORIGINAL_COMMAND_NAMES["Seat_Ibiza"] = {}

Seat_Leon = _LazyNamespace("Seat-Leon", "Seat_Leon")
_ORIGINAL_SOURCE_NAMES["Seat_Leon"] = "Seat-Leon"
_ORIGINAL_COMMAND_NAMES["Seat_Leon"] = {}

Seat_Mii_Electric = _LazyNamespace("Seat-Mii-Electric", "Seat_Mii_Electric")
_ORIGINAL_SOURCE_NAMES["Seat_Mii_Electric"] = "Seat-Mii-Electric"
_ORIGINAL_COMMAND_NAMES["Seat_Mii_Electric"] = {}

Seat_Tarraco = _LazyNamespace("Seat-Tarraco", "Seat_Tarraco")
_ORIGINAL_SOURCE_NAMES["Seat_Tarraco"] = "Seat-Tarraco"
_ORIGINAL_COMMAND_NAMES["Seat_Tarraco"] = {}

Skoda = _LazyNamespace("Skoda", "Skoda")
_ORIGINAL_SOURCE_NAMES["Skoda"] = "Skoda"
_ORIGINAL_COMMAND_NAMES["Skoda"] = {}

Skoda_Elroq = _LazyNamespace("Skoda-Elroq", "Skoda_Elroq")
_ORIGINAL_SOURCE_NAMES["Skoda_Elroq"] = "Skoda-Elroq"
_ORIGINAL_COMMAND_NAMES["Skoda_Elroq"] = {}

Skoda_Enyaq = _LazyNamespace("Skoda-Enyaq", "Skoda_Enyaq")
_ORIGINAL_SOURCE_NAMES["Skoda_Enyaq"] = "Skoda-Enyaq"
_ORIGINAL_COMMAND_NAMES["Skoda_Enyaq"] = {}

Skoda_Fabia = _LazyNamespace("Skoda-Fabia", "Skoda_Fabia")
_ORIGINAL_SOURCE_NAMES["Skoda_Fabia"] = "Skoda-Fabia"
_ORIGINAL_COMMAND_NAMES["Skoda_Fabia"] = {}

Skoda_Kamiq = _LazyNamespace("Skoda-Kamiq", "Skoda_Kamiq")
_ORIGINAL_SOURCE_NAMES["Skoda_Kamiq"] = "Skoda-Kamiq"
_ORIGINAL_COMMAND_NAMES["Skoda_Kamiq"] = {}

Skoda_Kodiaq = _LazyNamespace("Skoda-Kodiaq", "Skoda_Kodiaq")
_ORIGINAL_SOURCE_NAMES["Skoda_Kodiaq"] = "Skoda-Kodiaq"
_ORIGINAL_COMMAND_NAMES["Skoda_Kodiaq"] = {}

Skoda_Octavia = _LazyNamespace("Skoda-Octavia", "Skoda_Octavia")
_ORIGINAL_SOURCE_NAMES["Skoda_Octavia"] = "Skoda-Octavia"
_ORIGINAL_COMMAND_NAMES["Skoda_Octavia"] = {}

Skoda_Rapid = _LazyNamespace("Skoda-Rapid", "Skoda_Rapid")
_ORIGINAL_SOURCE_NAMES["Skoda_Rapid"] = "Skoda-Rapid"
_ORIGINAL_COMMAND_NAMES["Skoda_Rapid"] = {}

Skoda_Scala = _LazyNamespace("Skoda-Scala", "Skoda_Scala")
_ORIGINAL_SOURCE_NAMES["Skoda_Scala"] = "Skoda-Scala"
_ORIGINAL_COMMAND_NAMES["Skoda_Scala"] = {}

Skoda_Superb = _LazyNamespace("Skoda-Superb", "Skoda_Superb")
_ORIGINAL_SOURCE_NAMES["Skoda_Superb"] = "Skoda-Superb"
_ORIGINAL_COMMAND_NAMES["Skoda_Superb"] = {}

smart = _LazyNamespace("smart", "smart")
_ORIGINAL_SOURCE_NAMES["smart"] = "smart"
_ORIGINAL_COMMAND_NAMES["smart"] = {}

smart_fortwo = _LazyNamespace("smart-fortwo", "smart_fortwo")
_ORIGINAL_SOURCE_NAMES["smart_fortwo"] = "smart-fortwo"
_ORIGINAL_COMMAND_NAMES["smart_fortwo"] = {}

Smart_Smart_1 = _LazyNamespace("Smart-Smart-1", "Smart_Smart_1")
_ORIGINAL_SOURCE_NAMES["Smart_Smart_1"] = "Smart-Smart-1"
_ORIGINAL_COMMAND_NAMES["Smart_Smart_1"] = {}

Subaru = _LazyNamespace("Subaru", "Subaru")
_ORIGINAL_SOURCE_NAMES["Subaru"] = "Subaru"
_ORIGINAL_COMMAND_NAMES["Subaru"] = {}

Subaru_Ascent = _LazyNamespace("Subaru-Ascent", "Subaru_Ascent")
_ORIGINAL_SOURCE_NAMES["Subaru_Ascent"] = "Subaru-Ascent"
_ORIGINAL_COMMAND_NAMES["Subaru_Ascent"] = {}

Subaru_Baja = _LazyNamespace("Subaru-Baja", "Subaru_Baja")
_ORIGINAL_SOURCE_NAMES["Subaru_Baja"] = "Subaru-Baja"
_ORIGINAL_COMMAND_NAMES["Subaru_Baja"] = {}

Subaru_BRZ = _LazyNamespace("Subaru-BRZ", "Subaru_BRZ")
_ORIGINAL_SOURCE_NAMES["Subaru_BRZ"] = "Subaru-BRZ"
_ORIGINAL_COMMAND_NAMES["Subaru_BRZ"] = {}

Subaru_Crosstrek = _LazyNamespace("Subaru-Crosstrek", "Subaru_Crosstrek")
_ORIGINAL_SOURCE_NAMES["Subaru_Crosstrek"] = "Subaru-Crosstrek"
_ORIGINAL_COMMAND_NAMES["Subaru_Crosstrek"] = {}

Subaru_Forester = _LazyNamespace("Subaru-Forester", "Subaru_Forester")
_ORIGINAL_SOURCE_NAMES["Subaru_Forester"] = "Subaru-Forester"
_ORIGINAL_COMMAND_NAMES["Subaru_Forester"] = {}

Subaru_Impreza = _LazyNamespace("Subaru-Impreza", "Subaru_Impreza")
_ORIGINAL_SOURCE_NAMES["Subaru_Impreza"] = "Subaru-Impreza"
_ORIGINAL_COMMAND_NAMES["Subaru_Impreza"] = {}

Subaru_Legacy = _LazyNamespace("Subaru-Legacy", "Subaru_Legacy")
_ORIGINAL_SOURCE_NAMES["Subaru_Legacy"] = "Subaru-Legacy"
_ORIGINAL_COMMAND_NAMES["Subaru_Legacy"] = {}

Subaru_Outback = _LazyNamespace("Subaru-Outback", "Subaru_Outback")
_ORIGINAL_SOURCE_NAMES["Subaru_Outback"] = "Subaru-Outback"
_ORIGINAL_COMMAND_NAMES["Subaru_Outback"] = {}

Subaru_Solterra = _LazyNamespace("Subaru-Solterra", "Subaru_Solterra")
_ORIGINAL_SOURCE_NAMES["Subaru_Solterra"] = "Subaru-Solterra"
_ORIGINAL_COMMAND_NAMES["Subaru_Solterra"] = {}

Subaru_Tribeca = _LazyNamespace("Subaru-Tribeca", "Subaru_Tribeca")
_ORIGINAL_SOURCE_NAMES["Subaru_Tribeca"] = "Subaru-Tribeca"
_ORIGINAL_COMMAND_NAMES["Subaru_Tribeca"] = {}

Subaru_WRX = _LazyNamespace("Subaru-WRX", "Subaru_WRX")
_ORIGINAL_SOURCE_NAMES["Subaru_WRX"] = "Subaru-WRX"
_ORIGINAL_COMMAND_NAMES["Subaru_WRX"] = {}

Subaru_WRX_STI = _LazyNamespace("Subaru-WRX-STI", "Subaru_WRX_STI")
_ORIGINAL_SOURCE_NAMES["Subaru_WRX_STI"] = "Subaru-WRX-STI"
_ORIGINAL_COMMAND_NAMES["Subaru_WRX_STI"] = {}

Suzuki = _LazyNamespace("Suzuki", "Suzuki")
_ORIGINAL_SOURCE_NAMES["Suzuki"] = "Suzuki"
_ORIGINAL_COMMAND_NAMES["Suzuki"] = {}

Suzuki_Alto = _LazyNamespace("Suzuki-Alto", "Suzuki_Alto")
_ORIGINAL_SOURCE_NAMES["Suzuki_Alto"] = "Suzuki-Alto"
_ORIGINAL_COMMAND_NAMES["Suzuki_Alto"] = {}

Suzuki_Baleno = _LazyNamespace("Suzuki-Baleno", "Suzuki_Baleno")
_ORIGINAL_SOURCE_NAMES["Suzuki_Baleno"] = "Suzuki-Baleno"
_ORIGINAL_COMMAND_NAMES["Suzuki_Baleno"] = {}

Suzuki_Ignis = _LazyNamespace("Suzuki-Ignis", "Suzuki_Ignis")
_ORIGINAL_SOURCE_NAMES["Suzuki_Ignis"] = "Suzuki-Ignis"
_ORIGINAL_COMMAND_NAMES["Suzuki_Ignis"] = {}

Suzuki_Jimny = _LazyNamespace("Suzuki-Jimny", "Suzuki_Jimny")
_ORIGINAL_SOURCE_NAMES["Suzuki_Jimny"] = "Suzuki-Jimny"
_ORIGINAL_COMMAND_NAMES["Suzuki_Jimny"] = {}

Suzuki_Splash = _LazyNamespace("Suzuki-Splash", "Suzuki_Splash")
_ORIGINAL_SOURCE_NAMES["Suzuki_Splash"] = "Suzuki-Splash"
_ORIGINAL_COMMAND_NAMES["Suzuki_Splash"] = {}

Suzuki_Swift = _LazyNamespace("Suzuki-Swift", "Suzuki_Swift")
_ORIGINAL_SOURCE_NAMES["Suzuki_Swift"] = "Suzuki-Swift"
_ORIGINAL_COMMAND_NAMES["Suzuki_Swift"] = {}

Suzuki_SX4 = _LazyNamespace("Suzuki-SX4", "Suzuki_SX4")
_ORIGINAL_SOURCE_NAMES["Suzuki_SX4"] = "Suzuki-SX4"
_ORIGINAL_COMMAND_NAMES["Suzuki_SX4"] = {}

Suzuki_Vitara = _LazyNamespace("Suzuki-Vitara", "Suzuki_Vitara")
_ORIGINAL_SOURCE_NAMES["Suzuki_Vitara"] = "Suzuki-Vitara"
_ORIGINAL_COMMAND_NAMES["Suzuki_Vitara"] = {}

Tata = _LazyNamespace("Tata", "Tata")
_ORIGINAL_SOURCE_NAMES["Tata"] = "Tata"
_ORIGINAL_COMMAND_NAMES["Tata"] = {}

Tata_Harrier = _LazyNamespace("Tata-Harrier", "Tata_Harrier")
_ORIGINAL_SOURCE_NAMES["Tata_Harrier"] = "Tata-Harrier"
_ORIGINAL_COMMAND_NAMES["Tata_Harrier"] = {}

Tata_Tiago = _LazyNamespace("Tata-Tiago", "Tata_Tiago")
_ORIGINAL_SOURCE_NAMES["Tata_Tiago"] = "Tata-Tiago"
_ORIGINAL_COMMAND_NAMES["Tata_Tiago"] = {}

Tesla = _LazyNamespace("Tesla", "Tesla")
_ORIGINAL_SOURCE_NAMES["Tesla"] = "Tesla"
_ORIGINAL_COMMAND_NAMES["Tesla"] = {}

Tesla_Cybertruck = _LazyNamespace("Tesla-Cybertruck", "Tesla_Cybertruck")
_ORIGINAL_SOURCE_NAMES["Tesla_Cybertruck"] = "Tesla-Cybertruck"
_ORIGINAL_COMMAND_NAMES["Tesla_Cybertruck"] = {}

Tesla_Model_3 = _LazyNamespace("Tesla-Model-3", "Tesla_Model_3")
_ORIGINAL_SOURCE_NAMES["Tesla_Model_3"] = "Tesla-Model-3"
_ORIGINAL_COMMAND_NAMES["Tesla_Model_3"] = {}

Tesla_Model_S = _LazyNamespace("Tesla-Model-S", "Tesla_Model_S")
_ORIGINAL_SOURCE_NAMES["Tesla_Model_S"] = "Tesla-Model-S"
_ORIGINAL_COMMAND_NAMES["Tesla_Model_S"] = {}

Tesla_Model_X = _LazyNamespace("Tesla-Model-X", "Tesla_Model_X")
_ORIGINAL_SOURCE_NAMES["Tesla_Model_X"] = "Tesla-Model-X"
_ORIGINAL_COMMAND_NAMES["Tesla_Model_X"] = {}

Tesla_Model_Y = _LazyNamespace("Tesla-Model-Y", "Tesla_Model_Y")
_ORIGINAL_SOURCE_NAMES["Tesla_Model_Y"] = "Tesla-Model-Y"
_ORIGINAL_COMMAND_NAMES["Tesla_Model_Y"] = {}

Toyota = _LazyNamespace("Toyota", "Toyota")
_ORIGINAL_SOURCE_NAMES["Toyota"] = "Toyota"
_ORIGINAL_COMMAND_NAMES["Toyota"] = {}

Toyota_4Runner = _LazyNamespace("Toyota-4Runner", "Toyota_4Runner")
_ORIGINAL_SOURCE_NAMES["Toyota_4Runner"] = "Toyota-4Runner"
_ORIGINAL_COMMAND_NAMES["Toyota_4Runner"] = {}

Toyota_Alphard = _LazyNamespace("Toyota-Alphard", "Toyota_Alphard")
_ORIGINAL_SOURCE_NAMES["Toyota_Alphard"] = "Toyota-Alphard"
_ORIGINAL_COMMAND_NAMES["Toyota_Alphard"] = {}

Toyota_Aqua = _LazyNamespace("Toyota-Aqua", "Toyota_Aqua")
_ORIGINAL_SOURCE_NAMES["Toyota_Aqua"] = "Toyota-Aqua"
_ORIGINAL_COMMAND_NAMES["Toyota_Aqua"] = {}

Toyota_Auris = _LazyNamespace("Toyota-Auris", "Toyota_Auris")
_ORIGINAL_SOURCE_NAMES["Toyota_Auris"] = "Toyota-Auris"
_ORIGINAL_COMMAND_NAMES["Toyota_Auris"] = {}

Toyota_Avalon = _LazyNamespace("Toyota-Avalon", "Toyota_Avalon")
_ORIGINAL_SOURCE_NAMES["Toyota_Avalon"] = "Toyota-Avalon"
_ORIGINAL_COMMAND_NAMES["Toyota_Avalon"] = {}

Toyota_Aygo = _LazyNamespace("Toyota-Aygo", "Toyota_Aygo")
_ORIGINAL_SOURCE_NAMES["Toyota_Aygo"] = "Toyota-Aygo"
_ORIGINAL_COMMAND_NAMES["Toyota_Aygo"] = {}

Toyota_bZ4X = _LazyNamespace("Toyota-bZ4X", "Toyota_bZ4X")
_ORIGINAL_SOURCE_NAMES["Toyota_bZ4X"] = "Toyota-bZ4X"
_ORIGINAL_COMMAND_NAMES["Toyota_bZ4X"] = {}

Toyota_C_HR = _LazyNamespace("Toyota-C-HR", "Toyota_C_HR")
_ORIGINAL_SOURCE_NAMES["Toyota_C_HR"] = "Toyota-C-HR"
_ORIGINAL_COMMAND_NAMES["Toyota_C_HR"] = {}

Toyota_Camry = _LazyNamespace("Toyota-Camry", "Toyota_Camry")
_ORIGINAL_SOURCE_NAMES["Toyota_Camry"] = "Toyota-Camry"
_ORIGINAL_COMMAND_NAMES["Toyota_Camry"] = {}

Toyota_Camry_Hybrid = _LazyNamespace("Toyota-Camry-Hybrid", "Toyota_Camry_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Camry_Hybrid"] = "Toyota-Camry-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Camry_Hybrid"] = {}

Toyota_Celica = _LazyNamespace("Toyota-Celica", "Toyota_Celica")
_ORIGINAL_SOURCE_NAMES["Toyota_Celica"] = "Toyota-Celica"
_ORIGINAL_COMMAND_NAMES["Toyota_Celica"] = {}

Toyota_Corolla = _LazyNamespace("Toyota-Corolla", "Toyota_Corolla")
_ORIGINAL_SOURCE_NAMES["Toyota_Corolla"] = "Toyota-Corolla"
_ORIGINAL_COMMAND_NAMES["Toyota_Corolla"] = {}

Toyota_Corolla_Cross = _LazyNamespace("Toyota-Corolla-Cross", "Toyota_Corolla_Cross")
_ORIGINAL_SOURCE_NAMES["Toyota_Corolla_Cross"] = "Toyota-Corolla-Cross"
_ORIGINAL_COMMAND_NAMES["Toyota_Corolla_Cross"] = {}

Toyota_Corolla_Hybrid = _LazyNamespace("Toyota-Corolla-Hybrid", "Toyota_Corolla_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Corolla_Hybrid"] = "Toyota-Corolla-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Corolla_Hybrid"] = {}

Toyota_Corolla_iM = _LazyNamespace("Toyota-Corolla-iM", "Toyota_Corolla_iM")
_ORIGINAL_SOURCE_NAMES["Toyota_Corolla_iM"] = "Toyota-Corolla-iM"
_ORIGINAL_COMMAND_NAMES["Toyota_Corolla_iM"] = {}

Toyota_Crown = _LazyNamespace("Toyota-Crown", "Toyota_Crown")
_ORIGINAL_SOURCE_NAMES["Toyota_Crown"] = "Toyota-Crown"
_ORIGINAL_COMMAND_NAMES["Toyota_Crown"] = {}

Toyota_Crown_Signia = _LazyNamespace("Toyota-Crown-Signia", "Toyota_Crown_Signia")
_ORIGINAL_SOURCE_NAMES["Toyota_Crown_Signia"] = "Toyota-Crown-Signia"
_ORIGINAL_COMMAND_NAMES["Toyota_Crown_Signia"] = {}

Toyota_FJ_Cruiser = _LazyNamespace("Toyota-FJ-Cruiser", "Toyota_FJ_Cruiser")
_ORIGINAL_SOURCE_NAMES["Toyota_FJ_Cruiser"] = "Toyota-FJ-Cruiser"
_ORIGINAL_COMMAND_NAMES["Toyota_FJ_Cruiser"] = {}

Toyota_Fortuner = _LazyNamespace("Toyota-Fortuner", "Toyota_Fortuner")
_ORIGINAL_SOURCE_NAMES["Toyota_Fortuner"] = "Toyota-Fortuner"
_ORIGINAL_COMMAND_NAMES["Toyota_Fortuner"] = {}

Toyota_GR_Corolla = _LazyNamespace("Toyota-GR-Corolla", "Toyota_GR_Corolla")
_ORIGINAL_SOURCE_NAMES["Toyota_GR_Corolla"] = "Toyota-GR-Corolla"
_ORIGINAL_COMMAND_NAMES["Toyota_GR_Corolla"] = {}

Toyota_GR_Supra = _LazyNamespace("Toyota-GR-Supra", "Toyota_GR_Supra")
_ORIGINAL_SOURCE_NAMES["Toyota_GR_Supra"] = "Toyota-GR-Supra"
_ORIGINAL_COMMAND_NAMES["Toyota_GR_Supra"] = {}

Toyota_GR86 = _LazyNamespace("Toyota-GR86", "Toyota_GR86")
_ORIGINAL_SOURCE_NAMES["Toyota_GR86"] = "Toyota-GR86"
_ORIGINAL_COMMAND_NAMES["Toyota_GR86"] = {}

Toyota_Grand_Highlander = _LazyNamespace("Toyota-Grand-Highlander", "Toyota_Grand_Highlander")
_ORIGINAL_SOURCE_NAMES["Toyota_Grand_Highlander"] = "Toyota-Grand-Highlander"
_ORIGINAL_COMMAND_NAMES["Toyota_Grand_Highlander"] = {}

Toyota_Grand_Highlander_Hybrid = _LazyNamespace("Toyota-Grand-Highlander-Hybrid", "Toyota_Grand_Highlander_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Grand_Highlander_Hybrid"] = "Toyota-Grand-Highlander-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Grand_Highlander_Hybrid"] = {}

Toyota_Highlander = _LazyNamespace("Toyota-Highlander", "Toyota_Highlander")
_ORIGINAL_SOURCE_NAMES["Toyota_Highlander"] = "Toyota-Highlander"
_ORIGINAL_COMMAND_NAMES["Toyota_Highlander"] = {}

Toyota_Hilux = _LazyNamespace("Toyota-Hilux", "Toyota_Hilux")
_ORIGINAL_SOURCE_NAMES["Toyota_Hilux"] = "Toyota-Hilux"
_ORIGINAL_COMMAND_NAMES["Toyota_Hilux"] = {}

Toyota_Innova = _LazyNamespace("Toyota-Innova", "Toyota_Innova")
_ORIGINAL_SOURCE_NAMES["Toyota_Innova"] = "Toyota-Innova"
_ORIGINAL_COMMAND_NAMES["Toyota_Innova"] = {}

Toyota_iQ = _LazyNamespace("Toyota-iQ", "Toyota_iQ")
_ORIGINAL_SOURCE_NAMES["Toyota_iQ"] = "Toyota-iQ"
_ORIGINAL_COMMAND_NAMES["Toyota_iQ"] = {}

Toyota_Ist = _LazyNamespace("Toyota-Ist", "Toyota_Ist")
_ORIGINAL_SOURCE_NAMES["Toyota_Ist"] = "Toyota-Ist"
_ORIGINAL_COMMAND_NAMES["Toyota_Ist"] = {}

Toyota_Land_Cruiser = _LazyNamespace("Toyota-Land-Cruiser", "Toyota_Land_Cruiser")
_ORIGINAL_SOURCE_NAMES["Toyota_Land_Cruiser"] = "Toyota-Land-Cruiser"
_ORIGINAL_COMMAND_NAMES["Toyota_Land_Cruiser"] = {}

Toyota_Land_Cruiser_Hybrid = _LazyNamespace("Toyota-Land-Cruiser-Hybrid", "Toyota_Land_Cruiser_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Land_Cruiser_Hybrid"] = "Toyota-Land-Cruiser-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Land_Cruiser_Hybrid"] = {}

Toyota_Matrix = _LazyNamespace("Toyota-Matrix", "Toyota_Matrix")
_ORIGINAL_SOURCE_NAMES["Toyota_Matrix"] = "Toyota-Matrix"
_ORIGINAL_COMMAND_NAMES["Toyota_Matrix"] = {}

Toyota_Mirai = _LazyNamespace("Toyota-Mirai", "Toyota_Mirai")
_ORIGINAL_SOURCE_NAMES["Toyota_Mirai"] = "Toyota-Mirai"
_ORIGINAL_COMMAND_NAMES["Toyota_Mirai"] = {}

Toyota_MR2 = _LazyNamespace("Toyota-MR2", "Toyota_MR2")
_ORIGINAL_SOURCE_NAMES["Toyota_MR2"] = "Toyota-MR2"
_ORIGINAL_COMMAND_NAMES["Toyota_MR2"] = {}

Toyota_Prius = _LazyNamespace("Toyota-Prius", "Toyota_Prius")
_ORIGINAL_SOURCE_NAMES["Toyota_Prius"] = "Toyota-Prius"
_ORIGINAL_COMMAND_NAMES["Toyota_Prius"] = {}

Toyota_Prius_Prime = _LazyNamespace("Toyota-Prius-Prime", "Toyota_Prius_Prime")
_ORIGINAL_SOURCE_NAMES["Toyota_Prius_Prime"] = "Toyota-Prius-Prime"
_ORIGINAL_COMMAND_NAMES["Toyota_Prius_Prime"] = {}

Toyota_Prius_v = _LazyNamespace("Toyota-Prius-v", "Toyota_Prius_v")
_ORIGINAL_SOURCE_NAMES["Toyota_Prius_v"] = "Toyota-Prius-v"
_ORIGINAL_COMMAND_NAMES["Toyota_Prius_v"] = {}

Toyota_RAV4 = _LazyNamespace("Toyota-RAV4", "Toyota_RAV4")
_ORIGINAL_SOURCE_NAMES["Toyota_RAV4"] = "Toyota-RAV4"
_ORIGINAL_COMMAND_NAMES["Toyota_RAV4"] = {}

Toyota_RAV4_Hybrid = _LazyNamespace("Toyota-RAV4-Hybrid", "Toyota_RAV4_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_RAV4_Hybrid"] = "Toyota-RAV4-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_RAV4_Hybrid"] = {}

Toyota_RAV4_Prime = _LazyNamespace("Toyota-RAV4-Prime", "Toyota_RAV4_Prime")
_ORIGINAL_SOURCE_NAMES["Toyota_RAV4_Prime"] = "Toyota-RAV4-Prime"
_ORIGINAL_COMMAND_NAMES["Toyota_RAV4_Prime"] = {}

Toyota_Rush = _LazyNamespace("Toyota-Rush", "Toyota_Rush")
_ORIGINAL_SOURCE_NAMES["Toyota_Rush"] = "Toyota-Rush"
_ORIGINAL_COMMAND_NAMES["Toyota_Rush"] = {}

Toyota_Sequoia = _LazyNamespace("Toyota-Sequoia", "Toyota_Sequoia")
_ORIGINAL_SOURCE_NAMES["Toyota_Sequoia"] = "Toyota-Sequoia"
_ORIGINAL_COMMAND_NAMES["Toyota_Sequoia"] = {}

Toyota_Sienna = _LazyNamespace("Toyota-Sienna", "Toyota_Sienna")
_ORIGINAL_SOURCE_NAMES["Toyota_Sienna"] = "Toyota-Sienna"
_ORIGINAL_COMMAND_NAMES["Toyota_Sienna"] = {}

Toyota_Sienna_Hybrid = _LazyNamespace("Toyota-Sienna-Hybrid", "Toyota_Sienna_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Sienna_Hybrid"] = "Toyota-Sienna-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Sienna_Hybrid"] = {}

Toyota_Tacoma = _LazyNamespace("Toyota-Tacoma", "Toyota_Tacoma")
_ORIGINAL_SOURCE_NAMES["Toyota_Tacoma"] = "Toyota-Tacoma"
_ORIGINAL_COMMAND_NAMES["Toyota_Tacoma"] = {}

Toyota_Tundra = _LazyNamespace("Toyota-Tundra", "Toyota_Tundra")
_ORIGINAL_SOURCE_NAMES["Toyota_Tundra"] = "Toyota-Tundra"
_ORIGINAL_COMMAND_NAMES["Toyota_Tundra"] = {}

Toyota_Venza = _LazyNamespace("Toyota-Venza", "Toyota_Venza")
_ORIGINAL_SOURCE_NAMES["Toyota_Venza"] = "Toyota-Venza"
_ORIGINAL_COMMAND_NAMES["Toyota_Venza"] = {}

Toyota_Venza_Hybrid = _LazyNamespace("Toyota-Venza-Hybrid", "Toyota_Venza_Hybrid")
_ORIGINAL_SOURCE_NAMES["Toyota_Venza_Hybrid"] = "Toyota-Venza-Hybrid"
_ORIGINAL_COMMAND_NAMES["Toyota_Venza_Hybrid"] = {}

Toyota_Yaris = _LazyNamespace("Toyota-Yaris", "Toyota_Yaris")
_ORIGINAL_SOURCE_NAMES["Toyota_Yaris"] = "Toyota-Yaris"
_ORIGINAL_COMMAND_NAMES["Toyota_Yaris"] = {}

Toyota_Yaris_Cross = _LazyNamespace("Toyota-Yaris-Cross", "Toyota_Yaris_Cross")
_ORIGINAL_SOURCE_NAMES["Toyota_Yaris_Cross"] = "Toyota-Yaris-Cross"
_ORIGINAL_COMMAND_NAMES["Toyota_Yaris_Cross"] = {}

Toyota_Yaris_iA = _LazyNamespace("Toyota-Yaris-iA", "Toyota_Yaris_iA")
_ORIGINAL_SOURCE_NAMES["Toyota_Yaris_iA"] = "Toyota-Yaris-iA"
_ORIGINAL_COMMAND_NAMES["Toyota_Yaris_iA"] = {}

Vauxhall_Astra = _LazyNamespace("Vauxhall-Astra", "Vauxhall_Astra")
_ORIGINAL_SOURCE_NAMES["Vauxhall_Astra"] = "Vauxhall-Astra"
_ORIGINAL_COMMAND_NAMES["Vauxhall_Astra"] = {}

Vauxhall_Mokka_e = _LazyNamespace("Vauxhall-Mokka-e", "Vauxhall_Mokka_e")
_ORIGINAL_SOURCE_NAMES["Vauxhall_Mokka_e"] = "Vauxhall-Mokka-e"
_ORIGINAL_COMMAND_NAMES["Vauxhall_Mokka_e"] = {}

VauxhallOpel = _LazyNamespace("VauxhallOpel", "VauxhallOpel")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel"] = "VauxhallOpel"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel"] = {}

VauxhallOpel_Ampera = _LazyNamespace("VauxhallOpel-Ampera", "VauxhallOpel_Ampera")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Ampera"] = "VauxhallOpel-Ampera"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Ampera"] = {}

VauxhallOpel_Astra = _LazyNamespace("VauxhallOpel-Astra", "VauxhallOpel_Astra")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Astra"] = "VauxhallOpel-Astra"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Astra"] = {}

VauxhallOpel_Corsa_e = _LazyNamespace("VauxhallOpel-Corsa-e", "VauxhallOpel_Corsa_e")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Corsa_e"] = "VauxhallOpel-Corsa-e"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Corsa_e"] = {}

VauxhallOpel_Crossland = _LazyNamespace("VauxhallOpel-Crossland", "VauxhallOpel_Crossland")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Crossland"] = "VauxhallOpel-Crossland"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Crossland"] = {}

VauxhallOpel_Grandland_X = _LazyNamespace("VauxhallOpel-Grandland-X", "VauxhallOpel_Grandland_X")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Grandland_X"] = "VauxhallOpel-Grandland-X"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Grandland_X"] = {}

VauxhallOpel_Insignia = _LazyNamespace("VauxhallOpel-Insignia", "VauxhallOpel_Insignia")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Insignia"] = "VauxhallOpel-Insignia"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Insignia"] = {}

VauxhallOpel_Mokka = _LazyNamespace("VauxhallOpel-Mokka", "VauxhallOpel_Mokka")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Mokka"] = "VauxhallOpel-Mokka"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Mokka"] = {}

VauxhallOpel_Zafira_B = _LazyNamespace("VauxhallOpel-Zafira-B", "VauxhallOpel_Zafira_B")
_ORIGINAL_SOURCE_NAMES["VauxhallOpel_Zafira_B"] = "VauxhallOpel-Zafira-B"
_ORIGINAL_COMMAND_NAMES["VauxhallOpel_Zafira_B"] = {}

Volkswagen = _LazyNamespace("Volkswagen", "Volkswagen")
_ORIGINAL_SOURCE_NAMES["Volkswagen"] = "Volkswagen"
_ORIGINAL_COMMAND_NAMES["Volkswagen"] = {}

Volkswagen_Amarok = _LazyNamespace("Volkswagen-Amarok", "Volkswagen_Amarok")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Amarok"] = "Volkswagen-Amarok"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Amarok"] = {}

Volkswagen_Arteon = _LazyNamespace("Volkswagen-Arteon", "Volkswagen_Arteon")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Arteon"] = "Volkswagen-Arteon"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Arteon"] = {}

Volkswagen_Atlas = _LazyNamespace("Volkswagen-Atlas", "Volkswagen_Atlas")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Atlas"] = "Volkswagen-Atlas"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Atlas"] = {}

Volkswagen_Beetle = _LazyNamespace("Volkswagen-Beetle", "Volkswagen_Beetle")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Beetle"] = "Volkswagen-Beetle"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Beetle"] = {}

Volkswagen_CC = _LazyNamespace("Volkswagen-CC", "Volkswagen_CC")
_ORIGINAL_SOURCE_NAMES["Volkswagen_CC"] = "Volkswagen-CC"
_ORIGINAL_COMMAND_NAMES["Volkswagen_CC"] = {}

Volkswagen_Crafter = _LazyNamespace("Volkswagen-Crafter", "Volkswagen_Crafter")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Crafter"] = "Volkswagen-Crafter"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Crafter"] = {}

Volkswagen_e_Golf = _LazyNamespace("Volkswagen-e-Golf", "Volkswagen_e_Golf")
_ORIGINAL_SOURCE_NAMES["Volkswagen_e_Golf"] = "Volkswagen-e-Golf"
_ORIGINAL_COMMAND_NAMES["Volkswagen_e_Golf"] = {}

Volkswagen_Golf = _LazyNamespace("Volkswagen-Golf", "Volkswagen_Golf")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Golf"] = "Volkswagen-Golf"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Golf"] = {}

Volkswagen_GTE = _LazyNamespace("Volkswagen-GTE", "Volkswagen_GTE")
_ORIGINAL_SOURCE_NAMES["Volkswagen_GTE"] = "Volkswagen-GTE"
_ORIGINAL_COMMAND_NAMES["Volkswagen_GTE"] = {}

Volkswagen_ID_Buzz = _LazyNamespace("Volkswagen-ID-Buzz", "Volkswagen_ID_Buzz")
_ORIGINAL_SOURCE_NAMES["Volkswagen_ID_Buzz"] = "Volkswagen-ID-Buzz"
_ORIGINAL_COMMAND_NAMES["Volkswagen_ID_Buzz"] = {}

Volkswagen_ID_4 = _LazyNamespace("Volkswagen-ID.4", "Volkswagen_ID_4")
_ORIGINAL_SOURCE_NAMES["Volkswagen_ID_4"] = "Volkswagen-ID.4"
_ORIGINAL_COMMAND_NAMES["Volkswagen_ID_4"] = {}

Volkswagen_ID3 = _LazyNamespace("Volkswagen-ID3", "Volkswagen_ID3")
_ORIGINAL_SOURCE_NAMES["Volkswagen_ID3"] = "Volkswagen-ID3"
_ORIGINAL_COMMAND_NAMES["Volkswagen_ID3"] = {}

Volkswagen_ID5 = _LazyNamespace("Volkswagen-ID5", "Volkswagen_ID5")
_ORIGINAL_SOURCE_NAMES["Volkswagen_ID5"] = "Volkswagen-ID5"
_ORIGINAL_COMMAND_NAMES["Volkswagen_ID5"] = {}

Volkswagen_ID7_Tourer = _LazyNamespace("Volkswagen-ID7-Tourer", "Volkswagen_ID7_Tourer")
_ORIGINAL_SOURCE_NAMES["Volkswagen_ID7_Tourer"] = "Volkswagen-ID7-Tourer"
_ORIGINAL_COMMAND_NAMES["Volkswagen_ID7_Tourer"] = {}

Volkswagen_Jetta = _LazyNamespace("Volkswagen-Jetta", "Volkswagen_Jetta")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Jetta"] = "Volkswagen-Jetta"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Jetta"] = {}

Volkswagen_Jetta_GLI = _LazyNamespace("Volkswagen-Jetta-GLI", "Volkswagen_Jetta_GLI")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Jetta_GLI"] = "Volkswagen-Jetta-GLI"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Jetta_GLI"] = {}

Volkswagen_Nivus = _LazyNamespace("Volkswagen-Nivus", "Volkswagen_Nivus")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Nivus"] = "Volkswagen-Nivus"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Nivus"] = {}

Volkswagen_Passat = _LazyNamespace("Volkswagen-Passat", "Volkswagen_Passat")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Passat"] = "Volkswagen-Passat"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Passat"] = {}

Volkswagen_Passat_B8 = _LazyNamespace("Volkswagen-Passat-B8", "Volkswagen_Passat_B8")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Passat_B8"] = "Volkswagen-Passat-B8"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Passat_B8"] = {}

Volkswagen_Passat_Variant = _LazyNamespace("Volkswagen-Passat-Variant", "Volkswagen_Passat_Variant")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Passat_Variant"] = "Volkswagen-Passat-Variant"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Passat_Variant"] = {}

Volkswagen_Polo = _LazyNamespace("Volkswagen-Polo", "Volkswagen_Polo")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Polo"] = "Volkswagen-Polo"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Polo"] = {}

Volkswagen_Polo_V = _LazyNamespace("Volkswagen-Polo-V", "Volkswagen_Polo_V")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Polo_V"] = "Volkswagen-Polo-V"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Polo_V"] = {}

Volkswagen_R32 = _LazyNamespace("Volkswagen-R32", "Volkswagen_R32")
_ORIGINAL_SOURCE_NAMES["Volkswagen_R32"] = "Volkswagen-R32"
_ORIGINAL_COMMAND_NAMES["Volkswagen_R32"] = {}

Volkswagen_Rabbit = _LazyNamespace("Volkswagen-Rabbit", "Volkswagen_Rabbit")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Rabbit"] = "Volkswagen-Rabbit"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Rabbit"] = {}

Volkswagen_Scirocco = _LazyNamespace("Volkswagen-Scirocco", "Volkswagen_Scirocco")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Scirocco"] = "Volkswagen-Scirocco"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Scirocco"] = {}

Volkswagen_Sharan = _LazyNamespace("Volkswagen-Sharan", "Volkswagen_Sharan")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Sharan"] = "Volkswagen-Sharan"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Sharan"] = {}

Volkswagen_T_Cross = _LazyNamespace("Volkswagen-T-Cross", "Volkswagen_T_Cross")
_ORIGINAL_SOURCE_NAMES["Volkswagen_T_Cross"] = "Volkswagen-T-Cross"
_ORIGINAL_COMMAND_NAMES["Volkswagen_T_Cross"] = {}

Volkswagen_T_Roc = _LazyNamespace("Volkswagen-T-Roc", "Volkswagen_T_Roc")
_ORIGINAL_SOURCE_NAMES["Volkswagen_T_Roc"] = "Volkswagen-T-Roc"
_ORIGINAL_COMMAND_NAMES["Volkswagen_T_Roc"] = {}

Volkswagen_T5 = _LazyNamespace("Volkswagen-T5", "Volkswagen_T5")
_ORIGINAL_SOURCE_NAMES["Volkswagen_T5"] = "Volkswagen-T5"
_ORIGINAL_COMMAND_NAMES["Volkswagen_T5"] = {}

Volkswagen_Taigo = _LazyNamespace("Volkswagen-Taigo", "Volkswagen_Taigo")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Taigo"] = "Volkswagen-Taigo"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Taigo"] = {}

Volkswagen_Taos = _LazyNamespace("Volkswagen-Taos", "Volkswagen_Taos")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Taos"] = "Volkswagen-Taos"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Taos"] = {}

Volkswagen_Tiguan = _LazyNamespace("Volkswagen-Tiguan", "Volkswagen_Tiguan")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Tiguan"] = "Volkswagen-Tiguan"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Tiguan"] = {}

Volkswagen_Touareg = _LazyNamespace("Volkswagen-Touareg", "Volkswagen_Touareg")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Touareg"] = "Volkswagen-Touareg"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Touareg"] = {}

Volkswagen_Touran = _LazyNamespace("Volkswagen-Touran", "Volkswagen_Touran")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Touran"] = "Volkswagen-Touran"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Touran"] = {}

Volkswagen_Up = _LazyNamespace("Volkswagen-Up", "Volkswagen_Up")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Up"] = "Volkswagen-Up"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Up"] = {}

Volkswagen_Virtus = _LazyNamespace("Volkswagen-Virtus", "Volkswagen_Virtus")
_ORIGINAL_SOURCE_NAMES["Volkswagen_Virtus"] = "Volkswagen-Virtus"
_ORIGINAL_COMMAND_NAMES["Volkswagen_Virtus"] = {}

Volvo = _LazyNamespace("Volvo", "Volvo")
_ORIGINAL_SOURCE_NAMES["Volvo"] = "Volvo"
_ORIGINAL_COMMAND_NAMES["Volvo"] = {}

Volvo_C30 = _LazyNamespace("Volvo-C30", "Volvo_C30")
_ORIGINAL_SOURCE_NAMES["Volvo_C30"] = "Volvo-C30"
_ORIGINAL_COMMAND_NAMES["Volvo_C30"] = {}

Volvo_EX30 = _LazyNamespace("Volvo-EX30", "Volvo_EX30")
_ORIGINAL_SOURCE_NAMES["Volvo_EX30"] = "Volvo-EX30"
_ORIGINAL_COMMAND_NAMES["Volvo_EX30"] = {}

Volvo_S40 = _LazyNamespace("Volvo-S40", "Volvo_S40")
_ORIGINAL_SOURCE_NAMES["Volvo_S40"] = "Volvo-S40"
_ORIGINAL_COMMAND_NAMES["Volvo_S40"] = {}

Volvo_S60 = _LazyNamespace("Volvo-S60", "Volvo_S60")
_ORIGINAL_SOURCE_NAMES["Volvo_S60"] = "Volvo-S60"
_ORIGINAL_COMMAND_NAMES["Volvo_S60"] = {}

Volvo_S70 = _LazyNamespace("Volvo-S70", "Volvo_S70")
_ORIGINAL_SOURCE_NAMES["Volvo_S70"] = "Volvo-S70"
_ORIGINAL_COMMAND_NAMES["Volvo_S70"] = {}

Volvo_S90 = _LazyNamespace("Volvo-S90", "Volvo_S90")
_ORIGINAL_SOURCE_NAMES["Volvo_S90"] = "Volvo-S90"
_ORIGINAL_COMMAND_NAMES["Volvo_S90"] = {}

Volvo_V50 = _LazyNamespace("Volvo-V50", "Volvo_V50")
_ORIGINAL_SOURCE_NAMES["Volvo_V50"] = "Volvo-V50"
_ORIGINAL_COMMAND_NAMES["Volvo_V50"] = {}

Volvo_V60 = _LazyNamespace("Volvo-V60", "Volvo_V60")
_ORIGINAL_SOURCE_NAMES["Volvo_V60"] = "Volvo-V60"
_ORIGINAL_COMMAND_NAMES["Volvo_V60"] = {}

Volvo_V70 = _LazyNamespace("Volvo-V70", "Volvo_V70")
_ORIGINAL_SOURCE_NAMES["Volvo_V70"] = "Volvo-V70"
_ORIGINAL_COMMAND_NAMES["Volvo_V70"] = {}

Volvo_V90_Cross_Country = _LazyNamespace("Volvo-V90-Cross-Country", "Volvo_V90_Cross_Country")
_ORIGINAL_SOURCE_NAMES["Volvo_V90_Cross_Country"] = "Volvo-V90-Cross-Country"
_ORIGINAL_COMMAND_NAMES["Volvo_V90_Cross_Country"] = {}

Volvo_V90CC = _LazyNamespace("Volvo-V90CC", "Volvo_V90CC")
_ORIGINAL_SOURCE_NAMES["Volvo_V90CC"] = "Volvo-V90CC"
_ORIGINAL_COMMAND_NAMES["Volvo_V90CC"] = {}

Volvo_XC40 = _LazyNamespace("Volvo-XC40", "Volvo_XC40")
_ORIGINAL_SOURCE_NAMES["Volvo_XC40"] = "Volvo-XC40"
_ORIGINAL_COMMAND_NAMES["Volvo_XC40"] = {}

Volvo_XC40_Recharge = _LazyNamespace("Volvo-XC40-Recharge", "Volvo_XC40_Recharge")
_ORIGINAL_SOURCE_NAMES["Volvo_XC40_Recharge"] = "Volvo-XC40-Recharge"
_ORIGINAL_COMMAND_NAMES["Volvo_XC40_Recharge"] = {}

Volvo_XC40_T4_Recharge = _LazyNamespace("Volvo-XC40-T4-Recharge", "Volvo_XC40_T4_Recharge")
_ORIGINAL_SOURCE_NAMES["Volvo_XC40_T4_Recharge"] = "Volvo-XC40-T4-Recharge"
_ORIGINAL_COMMAND_NAMES["Volvo_XC40_T4_Recharge"] = {}

Volvo_XC60 = _LazyNamespace("Volvo-XC60", "Volvo_XC60")
_ORIGINAL_SOURCE_NAMES["Volvo_XC60"] = "Volvo-XC60"
_ORIGINAL_COMMAND_NAMES["Volvo_XC60"] = {}

Volvo_XC90 = _LazyNamespace("Volvo-XC90", "Volvo_XC90")
_ORIGINAL_SOURCE_NAMES["Volvo_XC90"] = "Volvo-XC90"
_ORIGINAL_COMMAND_NAMES["Volvo_XC90"] = {}

Voyah_Free = _LazyNamespace("Voyah-Free", "Voyah_Free")
_ORIGINAL_SOURCE_NAMES["Voyah_Free"] = "Voyah-Free"
_ORIGINAL_COMMAND_NAMES["Voyah_Free"] = {}

VW_Golf = _LazyNamespace("VW-Golf", "VW_Golf")
_ORIGINAL_SOURCE_NAMES["VW_Golf"] = "VW-Golf"
_ORIGINAL_COMMAND_NAMES["VW_Golf"] = {}

Zeekr_009 = _LazyNamespace("Zeekr-009", "Zeekr_009")
_ORIGINAL_SOURCE_NAMES["Zeekr_009"] = "Zeekr-009"
_ORIGINAL_COMMAND_NAMES["Zeekr_009"] = {}

__all__ = [
    'Abarth',
    'Abarth_500',
    'Abarth_595',
    'Acura',
    'Acura_CL',
    'Acura_ILX',
    'Acura_Integra',
    'Acura_MDX',
    'Acura_RDX',
    'Acura_TL',
    'Acura_TLX',
    'Acura_TSX',
    'Acura_ZDX',
    'Aiways',
    'Aiways_U5',
    'Alfa_Romeo',
    'Alfa_Romeo_Giulia',
    'Alfa_Romeo_Giulietta',
    'Alfa_Romeo_MiTo',
    'Alfa_Romeo_Tonale',
    'Alpine',
    'Aston_Martin_Vantage',
    'Audi',
    'Audi_A1',
    'Audi_A3',
    'Audi_A3_e_tron',
    'Audi_A4',
    'Audi_A5',
    'Audi_A6',
    'Audi_A7',
    'Audi_e_tron',
    'Audi_Q2',
    'Audi_Q3',
    'Audi_Q4_e_tron',
    'Audi_Q5',
    'Audi_Q7',
    'Audi_Q8',
    'Audi_Q8_e_tron',
    'Audi_RS_3',
    'Audi_RS_5',
    'Audi_RS_e_tron',
    'Audi_S3',
    'Audi_S4',
    'Audi_S5',
    'Audi_S6',
    'Audi_SQ2',
    'Audi_SQ5',
    'Audi_SQ7',
    'Audi_TT',
    'Bentley',
    'Bentley_Bentayga',
    'BMW',
    'BMW_1_Series',
    'BMW_116i',
    'BMW_2_Grand_Coupe',
    'BMW_2_Series',
    'BMW_230e',
    'BMW_3_Series',
    'BMW_3_Series_eDrive',
    'BMW_330e',
    'BMW_4_Series',
    'BMW_5_Series',
    'BMW_5_Series_xDrive',
    'BMW_640i_f13',
    'BMW_7_Series',
    'BMW_840i',
    'BMW_E91',
    'BMW_E92',
    'BMW_F34',
    'BMW_i3',
    'BMW_i3s',
    'BMW_i4',
    'BMW_i5',
    'BMW_i8',
    'BMW_iX',
    'BMW_iX3',
    'BMW_M2',
    'BMW_M3',
    'BMW_M4',
    'BMW_M440i',
    'BMW_M5',
    'BMW_X1',
    'BMW_X2',
    'BMW_X3',
    'BMW_X4',
    'BMW_X5',
    'BMW_X7',
    'BMW_Z3',
    'BMW_Z4',
    'Buick',
    'Buick_Encore',
    'Buick_Encore_GX',
    'Buick_Envision',
    'Buick_LaCrosse',
    'BYD',
    'BYD_Atto_3',
    'BYD_Dolphin_Mini',
    'BYD_Sealion_6',
    'Cadillac',
    'Cadillac_CT4',
    'Cadillac_CT5',
    'Cadillac_CTS',
    'Cadillac_ELR',
    'Cadillac_Escalade',
    'Cadillac_LYRIQ',
    'Cadillac_XT5',
    'Changan',
    'Chery',
    'Chery_Tiggo_7_Pro',
    'Chery_Tiggo_8',
    'Chevrolet',
    'Chevrolet_Aveo',
    'Chevrolet_Blazer_EV',
    'Chevrolet_Bolt_EUV',
    'Chevrolet_Bolt_EV',
    'Chevrolet_Camaro',
    'Chevrolet_Celta',
    'Chevrolet_Cobalt',
    'Chevrolet_Colorado',
    'Chevrolet_Corvette',
    'Chevrolet_Cruze',
    'Chevrolet_D_Max',
    'Chevrolet_Equinox',
    'Chevrolet_Equinox_EV',
    'Chevrolet_Express_Cargo',
    'Chevrolet_Impala',
    'Chevrolet_Malibu',
    'Chevrolet_Montana',
    'Chevrolet_Prizm',
    'Chevrolet_S_10',
    'Chevrolet_Silverado',
    'Chevrolet_Silverado_1500',
    'Chevrolet_Silverado_2500',
    'Chevrolet_Silverado_3500',
    'Chevrolet_Silverado_EV',
    'Chevrolet_Sonic',
    'Chevrolet_Spark',
    'Chevrolet_Tahoe',
    'Chevrolet_Trailblazer',
    'Chevrolet_Traverse',
    'Chevrolet_Trax',
    'Chevrolet_Volt',
    'Chrysler',
    'Chrysler_200',
    'Chrysler_300',
    'Chrysler_Pacifica',
    'Chrysler_Pacifica_Hybrid',
    'Chrysler_Sebring',
    'Citroen',
    'Citroen_Basalt',
    'Citroen_Berlingo',
    'Citroen_C3',
    'Citroen_C4',
    'Citroen_CZero',
    'Citroen_E_C4',
    'Citroen_eC4_X',
    'Cupra',
    'Cupra_Born',
    'Cupra_Formentor',
    'Cupra_Leon',
    'Cupra_Leon_Sportstourer',
    'Dacia',
    'Dacia_Duster',
    'Dacia_Lodgy',
    'Dacia_Sandero',
    'Dacia_Spring',
    'Daihatsu',
    'Datsun',
    'Dodge',
    'Dodge_Challenger',
    'Dodge_Charger',
    'Dodge_Dakota',
    'Dodge_Durango',
    'Dodge_Grand_Caravan',
    'Dodge_Hornet',
    'Dodge_Journey',
    'Dongfeng',
    'DongFeng_Seres_3',
    'DS',
    'DS_7',
    'Ferrari_458_Italia',
    'Fiat',
    'FIAT_500',
    'FIAT_500e',
    'FIAT_500X',
    'FIAT_Fastback',
    'Fiat_Grande_Punto',
    'FIAT_Panda',
    'Fiat_Punto',
    'Fisker',
    'Fisker_Ocean',
    'Ford',
    'Ford_Bronco',
    'Ford_Bronco_Sport',
    'Ford_E_Series',
    'Ford_EcoSport',
    'Ford_Edge',
    'Ford_Escape',
    'Ford_Everest',
    'Ford_Expedition',
    'Ford_Explorer',
    'Ford_F_150',
    'Ford_F_150_Lightning',
    'Ford_F_250',
    'Ford_F_350',
    'Ford_Fiesta',
    'Ford_Five_Hundred',
    'Ford_Flex',
    'Ford_Focus',
    'Ford_Focus_RS',
    'Ford_Focus_ST',
    'Ford_Fusion',
    'Ford_Fusion_Energi',
    'Ford_Fusion_Hybrid',
    'Ford_Ka',
    'Ford_Kuga',
    'Ford_Maverick',
    'Ford_Mondeo',
    'Ford_Mustang',
    'Ford_Mustang_Mach_E',
    'Ford_Puma',
    'Ford_Ranger',
    'Ford_Sierra',
    'Ford_Taurus',
    'Ford_Territory',
    'Ford_Transit',
    'Ford_Transit_Connect',
    'FSO_Polonez',
    'Genesis',
    'Genesis_G70',
    'Genesis_G80',
    'GMC',
    'GMC_Acadia',
    'GMC_Canyon',
    'GMC_Safari',
    'GMC_Sierra_1500',
    'GMC_Terrain',
    'GMC_Yukon',
    'GMC_Yukon_XL',
    'Haval',
    'Haval_H6_HEV',
    'Haval_Jolion',
    'Haval_Jolion_HEV',
    'Holden',
    'Holden_Commodore',
    'Holden_Cruze',
    'Honda',
    'Honda_Accord',
    'Honda_Accord_Hybrid',
    'Honda_Brio',
    'Honda_City',
    'Honda_Civic',
    'Honda_Clarity',
    'Honda_CR_V',
    'Honda_CR_V_Hybrid',
    'Honda_CR_Z',
    'Honda_e',
    'Honda_Element',
    'Honda_Fit',
    'Honda_HR_V',
    'Honda_Insight',
    'Honda_Jazz',
    'Honda_M_NV',
    'Honda_Odyssey',
    'Honda_Pilot',
    'Honda_Prologue',
    'Honda_Ridgeline',
    'Honda_WRV',
    'Honda_ZR_V',
    'Hyundai',
    'Hyundai_Accent',
    'Hyundai_Avante',
    'Hyundai_Elantra',
    'Hyundai_Genesis_Coupe',
    'Hyundai_i10',
    'Hyundai_i20',
    'Hyundai_i30',
    'Hyundai_IONIQ_5',
    'Hyundai_IONIQ_6',
    'Hyundai_IONIQ_Electric',
    'Hyundai_IONIQ_PlugIn_Hybrid',
    'Hyundai_Kona',
    'Hyundai_Kona_Electric',
    'Hyundai_Palisade',
    'Hyundai_Santa_Cruz',
    'Hyundai_Santa_Fe',
    'Hyundai_Santa_Fe_Hybrid',
    'Hyundai_Sonata',
    'Hyundai_Tucson',
    'Hyundai_Tucson_Hybrid',
    'Hyundai_Veloster',
    'Hyundai_Venue',
    'Hyundai_Verna',
    'INFINITI',
    'INFINITI_G_Sedan',
    'INFINITI_G35',
    'INFINITI_G37',
    'INFINITI_Q45',
    'INFINITI_Q50',
    'INFINITI_Q70',
    'INFINITI_QX55',
    'INFINITI_QX70',
    'JAC_EJ7',
    'Jaecoo_J7',
    'Jaguar',
    'Jaguar_F_PACE',
    'Jaguar_F_TYPE',
    'Jaguar_I_PACE',
    'Jeep',
    'Jeep_Avenger',
    'Jeep_Cherokee',
    'Jeep_Commander',
    'Jeep_Compass',
    'Jeep_Gladiator',
    'Jeep_Grand_Cherokee',
    'Jeep_Liberty',
    'Jeep_Patriot',
    'Jeep_Renegade',
    'Jeep_Wagoneer',
    'Jeep_Wrangler',
    'Jeep_Wrangler_4xe',
    'Jeep_Wrangler_JK',
    'Kawasaki_W800',
    'Kia',
    'Kia_Cadenza',
    'Kia_Carens',
    'Kia_Carnival',
    'Kia_Ceed',
    'Kia_Cerato',
    'Kia_EV3',
    'Kia_EV6',
    'Kia_EV9',
    'Kia_Forte',
    'Kia_K4',
    'Kia_K5',
    'Kia_Niro',
    'Kia_Niro_EV',
    'Kia_Optima',
    'Kia_Picanto',
    'Kia_Rio',
    'Kia_Rondo',
    'Kia_Seltos',
    'Kia_Sonet',
    'Kia_Sorento',
    'Kia_Soul',
    'Kia_Sportage',
    'Kia_Sportage_HEV',
    'Kia_Stinger',
    'Kia_Stonic',
    'Kia_Telluride',
    'KTM',
    'KTM_RC',
    'KTM_RC_390',
    'Lamborghini',
    'Lamborghini_Huracan_evo',
    'Land_Rover',
    'Land_Rover_Defender',
    'Land_Rover_LR4',
    'Land_Rover_Range_Rover',
    'Land_Rover_Range_Rover_Velar',
    'Landrover',
    'Lexus',
    'Lexus_CT_200h',
    'Lexus_ES',
    'Lexus_ES_300h',
    'Lexus_GX',
    'Lexus_GX_460',
    'Lexus_GX_470',
    'Lexus_IS',
    'Lexus_LC_500',
    'Lexus_LS',
    'Lexus_NX_350h',
    'Lexus_RX',
    'Lexus_RX_350',
    'Lexus_RX_450h',
    'Lexus_UX',
    'Lincoln',
    'Lincoln_Aviator',
    'Lincoln_Corsair',
    'Lincoln_MKX',
    'Lincoln_MKZ',
    'Lincoln_Nautilus',
    'Lincoln_Navigator',
    'Lincoln_Town_Car',
    'Lotus',
    'Lucid_Air',
    'Maruti',
    'Maruti_Celerio',
    'Maruti_Suzuki_Fronx_Delta',
    'Maserati',
    'Maserati_Levante',
    'Maxus',
    'Maxus_eDeliver_3',
    'Mazda',
    'Mazda_2',
    'Mazda_3',
    'Mazda_5',
    'Mazda_6',
    'Mazda_BT50',
    'Mazda_CX_3',
    'Mazda_CX_30',
    'Mazda_CX_5',
    'Mazda_CX_50',
    'Mazda_CX_60',
    'Mazda_CX_7',
    'Mazda_CX_70',
    'Mazda_CX_9',
    'Mazda_CX_90',
    'Mazda_MX_30',
    'Mazda_MX_5',
    'Mazda_RX_7',
    'Mazda_Tribute',
    'McLaren_Artura',
    'Mercedes_Benz',
    'Mercedes_Benz_A_180',
    'Mercedes_Benz_A_200',
    'Mercedes_Benz_A_220',
    'Mercedes_Benz_AMG_A_45',
    'Mercedes_Benz_AMG_GT',
    'Mercedes_Benz_C_180',
    'Mercedes_Benz_C_Class',
    'Mercedes_Benz_C200d',
    'Mercedes_Benz_CLA_200',
    'Mercedes_Benz_CLA_Class',
    'Mercedes_Benz_CLS',
    'Mercedes_Benz_E_Class',
    'Mercedes_Benz_E180',
    'Mercedes_Benz_EQA',
    'Mercedes_Benz_EQB',
    'Mercedes_Benz_EQE',
    'Mercedes_Benz_EQS',
    'Mercedes_Benz_EQS_Class_Sedan',
    'Mercedes_Benz_G_Class',
    'Mercedes_Benz_GLA250',
    'Mercedes_Benz_GLB_250',
    'Mercedes_Benz_GLC_Class',
    'Mercedes_Benz_Ml63',
    'Mercedes_Benz_S_Class',
    'MG',
    'MG_Comet',
    'MG_Hector',
    'MG_HS',
    'MG_MG4',
    'MG_One',
    'MG_ZS',
    'MG_ZS_EV',
    'MINI',
    'MINI_Clubman',
    'MINI_Cooper',
    'MINI_Cooper_S',
    'MINI_Cooper_SE',
    'MINI_Countryman',
    'MINI_Hardtop',
    'MINI_JCW',
    'Mitsubishi',
    'Mitsubishi_ASX',
    'Mitsubishi_Challenger',
    'Mitsubishi_Eclipse_Cross',
    'Mitsubishi_Eclipse_Cross_PHEV',
    'Mitsubishi_Lancer',
    'Mitsubishi_Mirage',
    'Mitsubishi_Outlander',
    'Mitsubishi_Outlander_PHEV',
    'Mitsubishi_Outlander_Sport',
    'Mitsubishi_Pajero',
    'Mitsubishi_RVR',
    'Mitsubishi_Triton',
    'Nissan',
    'Nissan_Altima',
    'Nissan_ARIYA',
    'Nissan_Armada',
    'Nissan_Frontier',
    'Nissan_Juke',
    'Nissan_Kicks',
    'Nissan_Leaf',
    'Nissan_Maxima',
    'Nissan_Murano',
    'Nissan_Navara',
    'Nissan_Pathfinder',
    'Nissan_Patrol',
    'Nissan_Pulsar',
    'Nissan_Qashqai',
    'Nissan_Rogue',
    'Nissan_Rogue_Sport',
    'Nissan_Sentra',
    'Nissan_Titan',
    'Nissan_Versa',
    'Nissan_X_Trail',
    'Nissan_Xterra',
    'NissanInfiniti',
    'Omoda',
    'Omoda_Omoda_5_EV',
    'Perodua_Bezza',
    'Peugeot',
    'Peugeot_2008',
    'Peugeot_205',
    'Peugeot_206',
    'Peugeot_207',
    'Peugeot_208',
    'Peugeot_3008',
    'Peugeot_307',
    'Peugeot_308',
    'Peugeot_308_Hybrid',
    'Peugeot_407',
    'Peugeot_505',
    'Peugeot_508',
    'Peugeot_e_208',
    'Peugeot_Expert',
    'Polestar',
    'Polestar_2',
    'Polestar_3',
    'Polestar_4',
    'Pontiac_Vibe',
    'Porsche',
    'Porsche_718',
    'Porsche_911',
    'Porsche_981_Cayman',
    'Porsche_Boxster',
    'Porsche_Cayenne',
    'Porsche_Cayman',
    'Porsche_Macan',
    'Porsche_Macan_Electric',
    'Porsche_Panamera',
    'Porsche_Taycan',
    'Ram',
    'Ram_1500',
    'Ram_2500',
    'Ram_3500',
    'Renault',
    'Renault_Captur',
    'Renault_Clio',
    'Renault_Clio_III',
    'Renault_Clio_V',
    'Renault_Kadjar',
    'Renault_Koleos',
    'Renault_Kwid',
    'Renault_Megane',
    'Renault_Megane_E_Tech',
    'Renault_Symbol',
    'Renault_ZOE',
    'Rivian',
    'Rivian_R1S',
    'Rivian_R1T',
    'Rolls_Royce',
    'Saab',
    'Saab_9_3',
    'Saab_9_5',
    'SAEJ1979',
    'Scion',
    'Scion_FR_S',
    'Scion_iQ',
    'Scion_tC',
    'Scion_xB',
    'SEAT',
    'Seat_Alhambra',
    'Seat_Altea',
    'Seat_Arona',
    'Seat_Ateca',
    'Seat_Ibiza',
    'Seat_Leon',
    'Seat_Mii_Electric',
    'Seat_Tarraco',
    'Skoda',
    'Skoda_Elroq',
    'Skoda_Enyaq',
    'Skoda_Fabia',
    'Skoda_Kamiq',
    'Skoda_Kodiaq',
    'Skoda_Octavia',
    'Skoda_Rapid',
    'Skoda_Scala',
    'Skoda_Superb',
    'smart',
    'smart_fortwo',
    'Smart_Smart_1',
    'Subaru',
    'Subaru_Ascent',
    'Subaru_Baja',
    'Subaru_BRZ',
    'Subaru_Crosstrek',
    'Subaru_Forester',
    'Subaru_Impreza',
    'Subaru_Legacy',
    'Subaru_Outback',
    'Subaru_Solterra',
    'Subaru_Tribeca',
    'Subaru_WRX',
    'Subaru_WRX_STI',
    'Suzuki',
    'Suzuki_Alto',
    'Suzuki_Baleno',
    'Suzuki_Ignis',
    'Suzuki_Jimny',
    'Suzuki_Splash',
    'Suzuki_Swift',
    'Suzuki_SX4',
    'Suzuki_Vitara',
    'Tata',
    'Tata_Harrier',
    'Tata_Tiago',
    'Tesla',
    'Tesla_Cybertruck',
    'Tesla_Model_3',
    'Tesla_Model_S',
    'Tesla_Model_X',
    'Tesla_Model_Y',
    'Toyota',
    'Toyota_4Runner',
    'Toyota_Alphard',
    'Toyota_Aqua',
    'Toyota_Auris',
    'Toyota_Avalon',
    'Toyota_Aygo',
    'Toyota_bZ4X',
    'Toyota_C_HR',
    'Toyota_Camry',
    'Toyota_Camry_Hybrid',
    'Toyota_Celica',
    'Toyota_Corolla',
    'Toyota_Corolla_Cross',
    'Toyota_Corolla_Hybrid',
    'Toyota_Corolla_iM',
    'Toyota_Crown',
    'Toyota_Crown_Signia',
    'Toyota_FJ_Cruiser',
    'Toyota_Fortuner',
    'Toyota_GR_Corolla',
    'Toyota_GR_Supra',
    'Toyota_GR86',
    'Toyota_Grand_Highlander',
    'Toyota_Grand_Highlander_Hybrid',
    'Toyota_Highlander',
    'Toyota_Hilux',
    'Toyota_Innova',
    'Toyota_iQ',
    'Toyota_Ist',
    'Toyota_Land_Cruiser',
    'Toyota_Land_Cruiser_Hybrid',
    'Toyota_Matrix',
    'Toyota_Mirai',
    'Toyota_MR2',
    'Toyota_Prius',
    'Toyota_Prius_Prime',
    'Toyota_Prius_v',
    'Toyota_RAV4',
    'Toyota_RAV4_Hybrid',
    'Toyota_RAV4_Prime',
    'Toyota_Rush',
    'Toyota_Sequoia',
    'Toyota_Sienna',
    'Toyota_Sienna_Hybrid',
    'Toyota_Tacoma',
    'Toyota_Tundra',
    'Toyota_Venza',
    'Toyota_Venza_Hybrid',
    'Toyota_Yaris',
    'Toyota_Yaris_Cross',
    'Toyota_Yaris_iA',
    'Vauxhall_Astra',
    'Vauxhall_Mokka_e',
    'VauxhallOpel',
    'VauxhallOpel_Ampera',
    'VauxhallOpel_Astra',
    'VauxhallOpel_Corsa_e',
    'VauxhallOpel_Crossland',
    'VauxhallOpel_Grandland_X',
    'VauxhallOpel_Insignia',
    'VauxhallOpel_Mokka',
    'VauxhallOpel_Zafira_B',
    'Volkswagen',
    'Volkswagen_Amarok',
    'Volkswagen_Arteon',
    'Volkswagen_Atlas',
    'Volkswagen_Beetle',
    'Volkswagen_CC',
    'Volkswagen_Crafter',
    'Volkswagen_e_Golf',
    'Volkswagen_Golf',
    'Volkswagen_GTE',
    'Volkswagen_ID_Buzz',
    'Volkswagen_ID_4',
    'Volkswagen_ID3',
    'Volkswagen_ID5',
    'Volkswagen_ID7_Tourer',
    'Volkswagen_Jetta',
    'Volkswagen_Jetta_GLI',
    'Volkswagen_Nivus',
    'Volkswagen_Passat',
    'Volkswagen_Passat_B8',
    'Volkswagen_Passat_Variant',
    'Volkswagen_Polo',
    'Volkswagen_Polo_V',
    'Volkswagen_R32',
    'Volkswagen_Rabbit',
    'Volkswagen_Scirocco',
    'Volkswagen_Sharan',
    'Volkswagen_T_Cross',
    'Volkswagen_T_Roc',
    'Volkswagen_T5',
    'Volkswagen_Taigo',
    'Volkswagen_Taos',
    'Volkswagen_Tiguan',
    'Volkswagen_Touareg',
    'Volkswagen_Touran',
    'Volkswagen_Up',
    'Volkswagen_Virtus',
    'Volvo',
    'Volvo_C30',
    'Volvo_EX30',
    'Volvo_S40',
    'Volvo_S60',
    'Volvo_S70',
    'Volvo_S90',
    'Volvo_V50',
    'Volvo_V60',
    'Volvo_V70',
    'Volvo_V90_Cross_Country',
    'Volvo_V90CC',
    'Volvo_XC40',
    'Volvo_XC40_Recharge',
    'Volvo_XC40_T4_Recharge',
    'Volvo_XC60',
    'Volvo_XC90',
    'Voyah_Free',
    'VW_Golf',
    'Zeekr_009',
    '_ORIGINAL_SOURCE_NAMES',
    '_ORIGINAL_COMMAND_NAMES'
]
