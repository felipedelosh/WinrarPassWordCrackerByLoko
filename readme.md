<h1 align="center"> FelipedelosH </h1>
<br>
<h4>WinrarPassWordCrackerByLoko</h4>

![Banner](Docs/banner.png)
<br>
:construction: In Contruction :construction:
<br><br>
This program is a simple RAR password recovery tool written in Python.

It tries to guess the password of a .rar file by brute force.
That means it generates many possible passwords and tests them one by one.

## :hammer:Funtions:

- `Function 1`: Neque porro quisquam est qui dolorem ipsum quia dolor sit amet.<br>
- `Function 2`: Neque porro quisquam est qui dolorem ipsum quia dolor sit amet.<br>
- `Function 3`: Neque porro quisquam est qui dolorem ipsum quia dolor sit amet.<br>
- `Function 3a`: Neque porro quisquam est qui dolorem ipsum quia dolor sit amet.<br>
- `Function 4`: Neque porro quisquam est qui dolorem ipsum quia dolor sit amet.<br>

## Architecture

```
WinrarPassWordCrackerByLoko/
├── main.py
├── characters.txt
├── .env
├── UnRAR.exe
├── Docs/
├── INPUT/
│   └── rar.rar
├── OUTPUT/
│   ├── files
│   └── log
├── TEMP/
└── src/
    ├── __init__.py
    ├── controllers/
    │   ├── ConfigController.py
    │   ├── FolderController.py
    │   ├── LoggerController.py
    │   └── Controller.py
    └── services/
        ├── CRACKER/
        │   └── SequentialBruteForceService.py
        ├── BeautifulPrinter.py
        ├── PasswordCombinationGenerator.py
        ├── TermiteService.py
        └── WinrarService.py
```

## ⚙️ Requirements

1. Install WinRAR

To use this program, you need to install WinRAR on your computer.

WinRAR comes with a small command-line tool called UnRAR.exe, which is the program that actually tests and extracts the RAR file. This project does not include it, so you must get it from your WinRAR installation.

You can download WinRAR for free from the official website:
https://winrar.es/descargas

2. Copy UnRAR.exe to the project root

After installing WinRAR, find the file UnRAR.exe in the WinRAR installation folder. By default it is located at:

C:\Program Files\WinRAR\UnRAR.exe

Copy that file and paste it into the root folder of this project, next to main.py:
```
WinrarPassWordCrackerByLoko/
├── main.py
├── characters.txt
├── UnRAR.exe        👈 here
├── Docs/
└── src/
```

3. Python 3

Make sure you have Python 3 installed. You can check with:

```
python --version
```

4. Install dependencies

```
python -m pip install -r requirements.txt
```


## :play_or_pause_button:How to execute a project

```
Double click main.py
```

```
C:\Users\docto\AppData\Local\Python\pythoncore-3.14-64\python.exe d:/PYTHON/WinrarPassWordCrackerByLoko/main.py
```


## :hammer_and_wrench:Tech.

- code programing
- framework

## :warning:Warning.

- limitations.

## Autor

| [<img src="https://avatars.githubusercontent.com/u/38327255?v=4" width=115><br><sub>Andrés Felipe Hernánez</sub>](https://github.com/felipedelosh)|
| :---: |
