## STT-text-editor

### Установка

1. Скачать архив или клонировать репозиторий
2. `pip install requirements.txt`

Запуск через `main.py`

### Изменения

Для замены модели (например для другого языка) заменить содержимое папки model. Модели можно найти на официальном сайте [Vosk](https://alphacephei.com/vosk/models)

Для дообучения модели (например чтобы использовать медицинские термины): 
1. Перейти в папку `retrain`
2. Записать в файл `phrases.txt` словарь терминов и словосочетаний в формате
    > транквилизация  
    > перелом костей  
    > перелом кости
    > надавливание
3. Запустить файл `retrain_vosk_model.py`
4. Удалить папку `model` и переименовать `model_new` в `model`
