from setuptools import setup, find_packages


# Читаем содержимое файла README.md для использования в long_description
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


# Функция для чтения зависимостей из requirements.txt
def parse_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith('#')]


setup(
    name='postgresintegration',  # Название вашей библиотеки
    version='0.1.0',  # Версия библиотеки
    author='noName',  # Имя автора
    author_email='noName@gmail.com',  # Email автора
    description='...',  # Краткое описание библиотеки
    long_description=long_description,  # Длинное описание из README.md
    url='https://github.com/AMarsel2551/postgresintegration.git',  # URL проекта (например, ссылка на репозиторий GitHub)
    packages=find_packages(),  # Автоматический поиск всех пакетов и подпакетов
    classifiers=[
        'Programming Language :: Python :: 3.10',  # Указываем, что библиотека написана на Python 3
        'License :: OSI Approved :: MIT License',  # Лицензия
        'Operating System :: OS Independent',  # ОС, на которых может работать библиотека
    ],
    python_requires='>=3.6',  # Требуемая версия Python
    install_requires=parse_requirements('requirements.txt'),
    include_package_data=False,
)

