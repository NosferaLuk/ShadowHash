# ShadowHash Pro 🎥

ShadowHash is a Python automation tool designed for content creators, agencies, and social media managers. It processes video files to alter their digital fingerprints (MD5, Metadata, Visual & Audio Signals) to mitigate algorithm duplication detection.

## 🚀 Features (v3.1)

### Advanced Evasion Mode (Default):
* **Visual Noise Injection:** Adds imperceptible film grain to alter compression structure.
* **Smart Crop:** Zooms in 1-4% (configurable) to break geometric edge detection.
* **Audio Scrambling:** Re-encodes audio with micro-volume shifts to change the audio stream hash.

### General Features:
* **Multi-Format Support:** Works with .mp4, .mov, .avi, .mkv, .webm.
* **Multi-Threading:** Processes multiple videos simultaneously for high throughput.
* **Audit Logging:** Automatically maintains a `processing_log.txt` history.
* **Metadata Wipe:** Completely strips global metadata.
* **Cross-Platform:** Works natively on Windows, Linux, and macOS.

## 🛠️ Installation

Clone the repository:

```bash
git clone [https://github.com/NosferaLuk/ShadowHash.git](https://github.com/NosferaLuk/ShadowHash.git)
cd ShadowHash

```

**Requirements:**

* Python 3.8+
* FFmpeg (Installed in system PATH or placed in the project folder)

## ⚡ Usage

Run the script directly via terminal:

```bash
# Standard Run (Advanced Mode + Medium Intensity)
python video_hasher.py

# High Intensity (More noise, 4% crop - Better evasion, slightly visible)
python video_hasher.py --intensity high

# Fast Mode (Only Metadata/MD5 - No heavy filters)
python video_hasher.py --mode fast

# Custom Input/Output folders
python video_hasher.py -i ./raw_footage -o ./ready_to_upload

# Maximize Performance (Increase threads)
python video_hasher.py --threads 8

```

## ⚙️ Filter Intensity Settings

| Setting | Noise Level | Crop (Zoom) | Use Case |
| --- | --- | --- | --- |
| **Low** | 2 | 1% | High quality requirements, YouTube 4K |
| **Medium** (Default) | 5 | 2% | General usage (TikTok, Reels, Shorts) |
| **High** | 8 | 4% | Aggressive repurposing, avoiding strict flags |

## ⚠️ Disclaimer

This tool is intended for content management, archiving, and legitimate testing purposes. The effectiveness of algorithm evasion varies by platform and updates frequently. Use responsibly.