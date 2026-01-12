import os
import random
import string
import hashlib
import subprocess
import argparse
import sys
import shutil
import time
import concurrent.futures
from pathlib import Path
from datetime import datetime

# Terminal colors for better UX
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Supported video formats
SUPPORTED_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def get_ffmpeg_path(custom_path=None):
    """
    Checks if FFMPEG exists in PATH or at the provided custom path.
    Cross-Platform compatible.
    """
    if custom_path:
        path = Path(custom_path)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        print(f"{Colors.FAIL}[X] Invalid or non-executable custom FFMPEG path.{Colors.ENDC}")
        sys.exit(1)
    
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        local_ffmpeg = Path("ffmpeg.exe") if os.name == 'nt' else Path("./ffmpeg")
        if local_ffmpeg.is_file():
            return str(local_ffmpeg.resolve())
        print(f"{Colors.FAIL}[X] FFMPEG not found. Install it or place executable here.{Colors.ENDC}")
        sys.exit(1)
    return ffmpeg

def generate_random_name(length=12, extension='.mp4'):
    """Generates random filename to avoid filename-based flagging."""
    letters = string.ascii_letters + string.digits
    name = ''.join(random.choice(letters) for _ in range(length))
    return f"{name}{extension}"

def get_md5(file_path):
    """Calculates file MD5 hash."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def build_filter_chain(intensity='medium'):
    """
    Builds a robust FFmpeg filter chain to break visual fingerprinting.
    Strategies: EQ Shift + Noise Injection + Smart Crop.
    """
    # 1. Randomize EQ slightly
    contrast = round(random.uniform(1.01, 1.04), 3)
    brightness = round(random.uniform(0.005, 0.015), 3)
    
    # 2. Noise intensity configuration
    if intensity == 'low':
        noise_amount = 2
        crop_factor = 0.99 # 1% zoom
    elif intensity == 'high':
        noise_amount = 8
        crop_factor = 0.96 # 4% zoom (aggressivo)
    else: # medium
        noise_amount = 5
        crop_factor = 0.98 # 2% zoom
    
    filters = [
        f"eq=brightness={brightness}:contrast={contrast}",
        f"noise=alls={noise_amount}:allf=t+u",
        f"crop=iw*{crop_factor}:ih*{crop_factor}"
    ]
    
    return ",".join(filters)

def process_single_video(file_path, output_dir, ffmpeg_path, mode, intensity):
    """
    Worker function to process a single video.
    """
    try:
        # Maintain original extension or standardize to mp4? 
        # Ideally standardize to mp4 for social media compatibility.
        random_name = generate_random_name(extension='.mp4')
        target_file = output_dir / random_name
        
        command = [ffmpeg_path, '-v', 'error', '-i', str(file_path)]

        # --- Filter Logic ---
        if mode == 'fast':
            # Minimal change: Metadata scrub + slight EQ
            command.extend(['-vf', 'eq=brightness=0.005:contrast=1.005'])
            command.extend(['-c:a', 'copy'])
        else:
            # Advanced Mode: Noise, Crop, Audio Scramble
            vf_string = build_filter_chain(intensity)
            command.extend(['-vf', vf_string])
            command.extend(['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22'])
            # Audio scramble (volume shift + re-encode)
            command.extend(['-af', 'volume=1.01', '-c:a', 'aac', '-b:a', '128k'])

        # Common flags
        command.extend(['-map_metadata', '-1', '-y', str(target_file)])
        
        # Execute
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        # Post-processing
        new_hash = get_md5(target_file)
        
        # Return success data
        return {
            "status": "success",
            "original": file_path.name,
            "new": random_name,
            "hash": new_hash
        }

    except subprocess.CalledProcessError as e:
        return {"status": "error", "file": file_path.name, "msg": "FFmpeg Error"}
    except Exception as e:
        return {"status": "error", "file": file_path.name, "msg": str(e)}

def main():
    parser = argparse.ArgumentParser(description="ShadowHash Pro: Advanced Algorithm Evasion Tool")
    
    parser.add_argument('--input', '-i', default='input', help='Input folder')
    parser.add_argument('--output', '-o', default='output', help='Output folder')
    parser.add_argument('--mode', '-m', choices=['fast', 'advanced'], default='advanced', 
                        help='Fast: Metadata scrub only. Advanced: Adds noise/crop/audio scramble.')
    parser.add_argument('--intensity', choices=['low', 'medium', 'high'], default='medium',
                        help='Intensity of visual filters (only for advanced mode).')
    parser.add_argument('--threads', '-t', type=int, default=3, help='Number of parallel threads.')
    
    args = parser.parse_args()

    # Setup directories
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        input_path.mkdir()
        print(f"{Colors.WARNING}[!] Created '{args.input}'. Place videos there and run again.{Colors.ENDC}")
        return

    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get Files (Multi-format support)
    files = [f for f in input_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTS]
    
    if not files:
        print(f"{Colors.WARNING}[!] No supported video files found in {input_path}{Colors.ENDC}")
        print(f"Supported formats: {', '.join(SUPPORTED_EXTS)}")
        return

    ffmpeg_path = get_ffmpeg_path()
    
    print(f"{Colors.HEADER}=== ShadowHash Pro v3.1 ==={Colors.ENDC}")
    print(f"Mode: {args.mode.upper()} | Intensity: {args.intensity.upper()}")
    print(f"Threads: {args.threads}")
    print(f"Queue: {len(files)} videos\n")

    # Audit Log Header
    log_file = output_path / "processing_log.txt"
    with open(log_file, "a", encoding="utf-8") as f: # Changed to 'a' (append) to not overwrite history
        if f.tell() == 0:
            f.write(f"timestamp,original_name,new_name,new_md5,mode\n")

    # Parallel Processing Loop
    start_time = time.time()
    processed_count = 0
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Create futures
            futures = {
                executor.submit(process_single_video, f, output_path, ffmpeg_path, args.mode, args.intensity): f 
                for f in files
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                processed_count += 1
                progress = f"[{processed_count}/{len(files)}]"
                
                if result['status'] == 'success':
                    print(f"{Colors.OKGREEN}{progress} Processed: {result['original']} -> {result['new']}{Colors.ENDC}")
                    # Log to file
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now()},{result['original']},{result['new']},{result['hash']},{args.mode}\n")
                else:
                    print(f"{Colors.FAIL}{progress} Failed: {result['file']} ({result['msg']}){Colors.ENDC}")

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Aborted by user. Finishing pending tasks...{Colors.ENDC}")
        # ThreadPoolExecutor handles cleanup automatically on exit context, 
        # but we acknowledge the interruption.
        
    duration = time.time() - start_time
    print(f"\n{Colors.HEADER}=== Done in {duration:.2f}s ==={Colors.ENDC}")
    print(f"Log updated: {log_file}")

if __name__ == "__main__":
    main()