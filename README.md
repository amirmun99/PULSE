![pulse_logo](https://github.com/user-attachments/assets/2695f727-d486-4fb1-ab4e-1725e0075b3e)

# PULSE – Open‑Source Vehicle & Motion Data Loggers  
*Precision • Utility • Logging • Sensors • Events*


> Two hardware variants, one unified platform – everything you need to capture motion, vibration, and environmental data in the field.

---

## 1. Project at a Glance
| Model            | Designed For                                          | Key Differentiator |
|------------------|-------------------------------------------------------|--------------------|
| **PULSE CORE**   | Enthusiasts, weekend track days, quick diagnostics    | Ultra‑compact, entry cost, longest runtime |
| **PULSE STRATUS**| Professional motorsport, R&D, industrial monitoring   | Full sensor suite, OLED feedback, installation‑grade enclosure |

This repository contains **everything** you need to build either logger yourself:
* firmware (RP2040/CircuitPython)
* 3‑D printed case files
* documented Bills of Materials
* a cross‑platform Python tool to visualize the data

---

## 2. Why PULSE?
Professional data loggers can be expensive, proprietary, or over‑complicated. PULSE bridges that gap:

* **Accurate** – ±32 g IMU plus 3‑axis magnetometer (both models)  
* **Robust** – PA6‑GF printed enclosures built for real‑world abuse  
* **Simple** – one‑button logging, CSV output, microSD storage  
* **Hackable** – Apache‑2.0 licensed hardware *and* firmware

---

## 3. How It Works
1. **Power‑on**  
2. **Press the button** – a new CSV file is created on the microSD card.  
3. **Drive / test / experiment** – data streams at up to 400 Hz (configurable).  
4. **Press again** – file is closed safely.  
5. **Analyze** – copy the CSV to your PC and run  

---

## 4. Hardware Highlights
| Component             | CORE | STRATUS | Purpose / Notes                                   |
|-----------------------|:----:|:-------:|---------------------------------------------------|
| **RP2040 MCU**        | ✅   | ✅      | 133 MHz dual‑core, 264 kB SRAM, USB‑C bootloader  |
| **LSM6DSO32 (IMU)**   | ✅   | ✅      | 6‑DoF, ±32 g accelerometer + 4000 dps gyro        |
| **MMC5603 Magnetometer** | ✅ | ✅      | 3‑axis heading for absolute orientation           |
| **AHT20 Temp/Humidity** | —   | ✅      | Ambient conditions (±0.3 °C / ±2 % RH)            |
| **1.12″ OLED (SH1107)** | —   | ✅      | Live data, battery, file status                   |
| **Li‑ion 1800 mAh**   | ✅   | ✅      | 20 – 30 h continuous logging (mode‑dependent)      |
| **Printed Enclosure** | Small PA6‑GF | Mountable PA6‑GF | Impact‑ and heat‑resistant                        |

---

## 5. Current Features
* One‑button **start / stop / file‑rotate** workflow  
* **CSV** logging on microSD – instant spreadsheet‐friendly data  
* Timestamped **acceleration, rotation, heading** (both models)  
* **Battery voltage read‑back** and low‑voltage safe‑stop (STRATUS)  
* Cross‑platform **`visualize_logs.py`** tool (matplotlib + pandas)  
* Comprehensive build docs with exploded renders & wiring diagrams  

---

## 6. Roadmap
*  **Custom PCB**
*  **Modular mounting system** – universal shoe & adhesive brackets (in design)  
*  **Bluetooth LE live streaming** for CORE (mobile telemetry app)  
*  **LTE / 4G telemetry** for STRATUS – cloud dashboard & alerts  
*  **session dashboard** (PySide + Plotly) with lap overlays  
*  **OTA firmware updates** via UF2 drag‑and‑drop or BLE

