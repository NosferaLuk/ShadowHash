import os
import random
import string
import hashlib
import subprocess
import argparse
import sys
import shutil
from pathlib import Path

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def get_ffmpeg_path(custom_path=None):
    """
    Checks if FFMPEG exists in PATH or at the provided custom path.
    Improved to be Cross-Platform (handles non-.exe binaries on Linux/Mac).
    """
    if custom_path:
        path = Path(custom_path)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        print(f"{Colors.FAIL}[X] Invalid or non-executable custom FFMPEG path.{Colors.ENDC}")
        sys.exit(1)
    
    # shutil.which handles .exe on Windows and binaries without extension on Linux/Mac
    ffmpeg = shutil.which("ffmpeg")
    
    if not ffmpeg:
        # Local fallback: checks current directory in an OS-agnostic way
        local_ffmpeg = Path("ffmpeg.exe") if os.name == 'nt' else Path("./ffmpeg")
        if local_ffmpeg.is_file():
            return str(local_ffmpeg.resolve())
            
        print(f"{Colors.FAIL}[X] FFMPEG not found in PATH. Please install it or place the executable in this folder.{Colors.ENDC}")
        sys.exit(1)
        
    return ffmpeg

def generate_random_name(length=12):
    """Generates a random alphanumeric string for filenames."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_md5(file_path):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    # Larger buffer (64kb) for slightly more efficient reading on modern disks
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def process_videos(input_dir, output_dir, ffmpeg_path, audio_mode='copy'):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"{Colors.FAIL}[!] Input directory does not exist: {input_dir}{Colors.ENDC}")
        return

    output_path.mkdir(parents=True, exist_ok=True)

    # Case-insensitive search for mp4 files
    files = [f for f in input_path.iterdir() if f.suffix.lower() == '.mp4']
    
    if not files:
        print(f"{Colors.WARNING}[!] No .mp4 files found in {input_dir}{Colors.ENDC}")
        return

    print(f"{Colors.HEADER}=== Starting Processing of {len(files)} videos ==={Colors.ENDC}")
    print(f"{Colors.HEADER}=== Audio Mode: {audio_mode} ==={Colors.ENDC}\n")

    for file in files:
        random_name = generate_random_name() + ".mp4"
        target_file = output_path / random_name
        
        print(f"{Colors.OKBLUE}[*] Processing: {file.name}{Colors.ENDC}")
        
        # Constructing FFmpeg command
        command = [
            ffmpeg_path,
            '-v', 'error',          # Less verbosity, shows only real errors
            '-i', str(file),
            '-vf', 'eq=brightness=0.005:contrast=1.005', # Minimal visual adjustment
            '-map_metadata', '-1',  # Remove global metadata
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '22',
        ]

        # Improved Audio Logic
        if audio_mode == 'scramble':
            # Re-encodes audio with an imperceptible volume change
            # This changes the audio stream hash, unlike 'copy'
            command.extend(['-af', 'volume=1.001', '-c:a', 'aac', '-b:a', '128k'])
        else:
            command.extend(['-c:a', 'copy'])

        command.extend(['-y', str(target_file)])
            
        try:
            subprocess.run(command, check=True)
            
            new_hash = get_md5(target_file)
            print(f"{Colors.OKGREEN}[V] Success: {random_name}")
            print(f"    New Hash: {new_hash}{Colors.ENDC}")
            print("-" * 30)
            
        except subprocess.CalledProcessError:
            print(f"{Colors.FAIL}[X] FFmpeg encoding error for {file.name}{Colors.ENDC}")
        except PermissionError:
            print(f"{Colors.FAIL}[X] Permission error accessing {file.name}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[X] Unexpected error: {e}{Colors.ENDC}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowHash Video Hash Changer (Improved)")
    
    parser.add_argument('--input', '-i', default='input', help='Input folder (Default: ./input)')
    parser.add_argument('--output', '-o', default='output', help='Output folder (Default: ./output)')
    parser.add_argument('--ffmpeg', '-f', help='Manual path to ffmpeg executable')
    # New argument to attempt breaking audio hash as well
    parser.add_argument('--scramble-audio', '-s', action='store_true', 
                        help='Re-encodes audio with slight alteration to change the sound stream hash')

    args = parser.parse_args()

    # Create input folder if it doesn't exist
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"{Colors.WARNING}[!] Folder '{args.input}' created. Place your videos there.{Colors.ENDC}")
    else:
        ff_path = get_ffmpeg_path(args.ffmpeg)
        mode = 'scramble' if args.scramble_audio else 'copy'
        process_videos(args.input, args.output, ff_path, audio_mode=mode)