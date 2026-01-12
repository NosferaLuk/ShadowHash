import os
import random
import string
import hashlib
import subprocess
import argparse
import sys
import shutil
from pathlib import Path

# Cores para o terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def get_ffmpeg_path(custom_path=None):
    """Verifica se o FFMPEG existe no PATH ou no caminho informado."""
    if custom_path:
        if os.path.isfile(custom_path):
            return custom_path
        print(f"{Colors.FAIL}[X] Caminho customizado do FFMPEG inválido.{Colors.ENDC}")
        sys.exit(1)
    
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        # Tenta procurar na pasta local caso o usuário tenha jogado o .exe junto
        if os.path.isfile("ffmpeg.exe"):
            return os.path.abspath("ffmpeg.exe")
        print(f"{Colors.FAIL}[X] FFMPEG não encontrado no PATH. Instale ou especifique o caminho.{Colors.ENDC}")
        sys.exit(1)
    return ffmpeg

def generate_random_name(length=12):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def get_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def process_videos(input_dir, output_dir, ffmpeg_path):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"{Colors.FAIL}[!] Diretório de entrada não existe: {input_dir}{Colors.ENDC}")
        return

    if not output_path.exists():
        os.makedirs(output_path)

    files = [f for f in input_path.glob('*.mp4')]
    
    if not files:
        print(f"{Colors.WARNING}[!] Nenhum arquivo .mp4 encontrado em {input_dir}{Colors.ENDC}")
        return

    print(f"{Colors.HEADER}=== Iniciando Processamento de {len(files)} vídeos ==={Colors.ENDC}\n")

    for file in files:
        random_name = generate_random_name() + ".mp4"
        target_file = output_path / random_name
        
        print(f"{Colors.OKBLUE}[*] Processando: {file.name}{Colors.ENDC}")
        
        try:
            # Comando FFmpeg otimizado
            command = [
                ffmpeg_path,
                '-i', str(file),
                '-vf', 'eq=brightness=0.005:contrast=1.005', # Alteração imperceptível nos pixels
                '-map_metadata', '-1',                       # Remove metadados (EXIF, etc)
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                '-crf', '22',
                '-c:a', 'copy',                              # Não recodifica áudio (mais rápido)
                '-y',
                str(target_file)
            ]
            
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(f"{Colors.OKGREEN}[V] Sucesso: {random_name}")
            print(f"    Hash Novo: {get_md5(target_file)}{Colors.ENDC}")
            print("-" * 30)
            
        except subprocess.CalledProcessError:
            print(f"{Colors.FAIL}[X] Erro de codificação no FFmpeg para {file.name}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}[X] Erro inesperado: {e}{Colors.ENDC}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alterador de Hash de Vídeo para Uploads Únicos")
    
    parser.add_argument('--input', '-i', default='input', help='Pasta de entrada dos vídeos (Padrão: ./input)')
    parser.add_argument('--output', '-o', default='output', help='Pasta de saída (Padrão: ./output)')
    parser.add_argument('--ffmpeg', '-f', help='Caminho manual para o executável do ffmpeg')

    args = parser.parse_args()

    # Cria pasta input se não existir (facilita pro usuário)
    if not os.path.exists(args.input):
        os.makedirs(args.input)
        print(f"{Colors.WARNING}[!] Pasta '{args.input}' criada. Coloque seus vídeos lá.{Colors.ENDC}")
    else:
        ff_path = get_ffmpeg_path(args.ffmpeg)
        process_videos(args.input, args.output, ff_path)