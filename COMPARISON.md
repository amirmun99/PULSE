# PULSE Family – Core vs Stratus  
*A complete side‑by‑side specification sheet*

| Category | **PULSE CORE** | **PULSE STRATUS** |
|----------|---------------|-------------------|
| **Target User** | Track‑day & hobby diagnostics | Professional motorsport, R&D, industrial |
| **MCU** | RP2040 (133 MHz) | RP2040 (133 MHz) |
| **IMU** | LSM6DSO32 – 6‑DoF, ±32 g, 4 k dps | Same as CORE |
| **Magnetometer** | MMC5603 3‑axis | Same as CORE |
| **Environmental Sensor** | — | AHT20 Temp / Humidity |
| **Display** | — | 1.12″ SH1107 OLED |
| **Logging Medium** | microSD (CSV) | microSD (CSV) |
| **Battery** | 1800 mAh Li‑ion (≈ 25‑30 h) | 1800 mAh Li‑ion (≈ 20‑24 h) |
| **User Input** | Single tactile button | Single tactile button + on‑screen prompts |
| **Enclosure** | Small PA6‑GF, weather‑resistant | Larger PA6‑GF, mountable flanges |
| **Dimensions** | ... | ... |
| **Weight** | ... | ... |
| **Firmware Features** | • IMU + MAG logging<br>• CSV output | All CORE features **plus**:<br>• Temp/Humi logging<br>• OLED live view<br>• Battery monitor |
| **Modular Mounting** | *Planned* (roadmap) | *Planned* (roadmap) |
| **Ideal Scenarios** | Autocross, weekend tuning, MTB, UAV | Endurance racing, dyno validation, industrial machinery |

---

## 1. Hardware Breakdown

### Shared Components
- **RP2040 MCU** for deterministic timing and UF2 boot‑loader ease.
- **LSM6DSO32 IMU** at up to **6.7 kHz** sample rate (software selectable).
- **MMC5603 Magnetometer** for drift‑free yaw / heading.

### Stratus Add‑Ons
- **AHT20** adds ±0.3 °C / ±2 % RH context.
- **1.12″ OLED** gives immediate feedback: logging state, battery level, live g‑meter.

---

## 2. Power & Runtime

| Mode | CORE Runtime | STRATUS Runtime |
|------|--------------|-----------------|
| Low‑rate (100 Hz) | ≈ 30 h | ≈ 24 h |
| High‑rate (400 Hz) | ≈ 26 h | ≈ 20 h |
| Max‑rate IMU (1 kHz) | ≈ 22 h | ≈ 17 h |

*All runtimes measured with freshly‑charged 1800 mAh cell, OLED at 20 % brightness.*

---

## 3. Enclosure & Mounting

| Aspect | CORE | STRATUS |
|--------|------|---------|
| Material | PA6‑GF | PA6‑GF |
| Ingress (unrated) | Splash‑resistant seals (Coming Soon) | Same (Coming Soon) |
| Mounting | **Roadmap:** modular shoe + adhesive pads | **Roadmap:** flange brackets + shoe |

---

## 4. Roadmap Feature Matrix

| Feature | Status | CORE | STRATUS |
|---------|--------|------|---------|
| Modular mounting kit | **Design** | 🔜 | 🔜 |
| Bluetooth LE streaming | **Research** | 🔜 | — |
| LTE / 4G telemetry | **Research** | — | 🔜 |
| Desktop dashboard | **Research** | 🔜 | 🔜 |
| OTA firmware update | **Research** | 🔜 | 🔜 |

---

## 5. Which One Should I Build?

| If you need… | Choose |
|--------------|--------|
| *Light weight, minimal cost, longest battery life* | **PULSE CORE** |
| *On‑device display, environmental context, installation mounts* | **PULSE STRATUS** |

