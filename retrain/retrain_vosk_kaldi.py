import os
import subprocess
import shutil
import argparse
# from pathlib import Path

# Конфигурация
KALDI_REPO = "https://github.com/kaldi-asr/kaldi.git"
VOSK_MODEL_TOOLS = "https://github.com/alphacep/vosk-model-tools.git"

def create_venv():
    print("Создаю виртуальное окружение...")
    subprocess.run(["python", "-m", "venv", ".venvretr"], check=True)

def install_dependencies():
    print("Устанавливаю зависимости...")
    pip = get_venv_pip()
    subprocess.run([pip, "install", "vosk", "numpy", "scipy", "soundfile", "tqdm", "gitpython"], check=True)

def get_venv_pip():
    return (
        os.path.join(".venvretr", "Scripts", "pip") 
        if os.name == "nt" 
        else os.path.join(".venvretr", "bin", "pip")
    )

def clone_repos():
    print("Клонирую Kaldi и Vosk-model-tools...")
    if not os.path.exists("kaldi"):
        subprocess.run(["git", "clone", KALDI_REPO], check=True)
    if not os.path.exists("vosk-model-tools"):
        subprocess.run(["git", "clone", VOSK_MODEL_TOOLS], check=True)

def prepare_data(input_file, output_dir="data"):
    print("Подготавливаю данные...")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(input_file, "r", encoding="utf-8") as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    # Сохраняем фразы в текстовый файл
    with open(f"{output_dir}/text", "w", encoding="utf-8") as f:
        for i, phrase in enumerate(phrases, 1):
            f.write(f"utt-{i} {phrase}\n")
    
    # Создаём файлы для Kaldi
    with open(f"{output_dir}/wav.scp", "w") as f:
        for i in range(1, len(phrases) + 1):
            f.write(f"utt-{i} null\n")
    
    with open(f"{output_dir}/utt2spk", "w") as f:
        for i in range(1, len(phrases) + 1):
            f.write(f"utt-{i} spk-{i}\n")

def retrain_kaldi(model_path, data_dir="data"):
    print("Дообучаю модель через Kaldi...")
    
    # 1. Подготовка данных
    subprocess.run([
        "bash", "kaldi/egs/wsj/s5/utils/data/prepare_data.sh",
        data_dir,
        "data/lang",
        "exp/data"
    ], check=True)
    
    # 2. Дообучение (упрощённый пример)
    subprocess.run([
        "bash", "kaldi/egs/wsj/s5/steps/train_mono.sh",
        "--nj", "1",
        "data/lang",
        "exp/data",
        "exp/mono"
    ], check=True)
    
    # 3. Конвертация в Vosk-формат
    subprocess.run([
        "python", "vosk-model-tools/src/vosk_import.py",
        "exp/mono",
        "model_new"
    ], check=True)

def cleanup():
    print("Удаляю временные файлы...")
    shutil.rmtree(".venvretr", ignore_errors=True)
    shutil.rmtree("kaldi", ignore_errors=True)

def main():
    parser = argparse.ArgumentParser(description="Дообучение Vosk через Kaldi")
    parser.add_argument("--input", default="./phrases.txt", help="Файл с фразами")
    parser.add_argument("--model", default="../model", help="Путь к исходной модели")
    args = parser.parse_args()

    try:
        create_venv()
        install_dependencies()
        clone_repos()
        prepare_data(args.input)
        retrain_kaldi(args.model)
        print("Готово! Новая модель сохранена в model_new/")
    finally:
        cleanup()

if __name__ == "__main__":
    main()