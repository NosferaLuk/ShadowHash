# ShadowHash: Video Uniquifier & Metadata Scrubber 🎥

A specialized Python tool designed for content creators and social media managers. It processes video files to alter their cryptographic hash (MD5) without visibly affecting quality, making them unique to algorithms.

## 🚀 Features

- **Hash Mutation:** Applies imperceptible brightness/contrast adjustments (`0.005`) to change pixel data.
- **Metadata Scrub:** Completely wipes original metadata.
- **High Performance:** Uses `ffmpeg` with `ultrafast` preset for bulk processing.
- **Privacy:** Randomizes output filenames.
- **Audio Passthrough:** Keeps original audio quality without re-encoding.

## 🛠️ Requirements

1. **Python 3.x**
2. **FFmpeg** installed and added to your system PATH (or placed in the script folder).

## ⚡ Quick Start

1. Clone the repo:
   ```bash
   git clone https://github.com/NosferaLuk/ShadowHash.git