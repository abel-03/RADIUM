# Тестовое задание

Напишите скрипт, асинхронно, в 3 одновременных задачи, скачивающий содержимое HEAD репозитория https://gitea.radium.group/radium/project-configuration во временную папку.
После выполнения всех асинхронных задач скрипт должен посчитать sha256 хэши от каждого файла.
Код должен проходить без замечаний проверку линтером wemake-python-styleguide. Конфигурация nitpick - https://gitea.radium.group/radium/project-configuration. (https://gitea.radium.group/radium/project-configuration)
Обязательно 100% покрытие тестами.



# Как запустить

1. Клонировать репозиторий
```
git clone <repository>
```

2. Запускаем скрипт
```
python3 main.py
```

# Как запустить тесты
1. pytest