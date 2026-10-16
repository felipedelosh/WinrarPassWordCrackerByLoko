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


- `Function 1`: **Sequential Brute Force Attack** - Generates and tests password combinations sequentially to recover passwords from RAR archives.<br>
- `Function 2`: **Termite Colony System** - Creates termite colonies represented by `.txt` files, each containing a password candidate.<br>
- `Function 3`: **Termite Lifecycle Management** - Generates, reads, removes, and preserves termite files based on password validation results.<br>
- `Function 4`: **Custom Character Set** - Loads password characters from `characters.txt`, removing separators and duplicates.<br>
- `Function 5`: **Configurable Password Length** - Supports minimum and maximum password lengths through `.env` configuration.<br>
- `Function 6`: **RAR Password Validation** - Uses `UnRAR.exe` to test generated passwords against protected RAR archives.<br>
- `Function 7`: **Automatic File Extraction** - Extracts archive contents to the output directory when a valid password is found.<br>
- `Function 8`: **Real-Time Progress Tracking** - Displays tested combinations, execution time, and processing speed in the console.<br>
- `Function 9`: **Execution Logging** - Records application events, errors, and results in log files.<br>
- `Function 10`: **Attack Strategy Configuration** - Provides configuration for sequential and random attack modes. Currently, only sequential mode is implemented.<br>
- `Function 11`: **Dependency Injection** - Uses a centralized dependency injector to initialize and connect application services.<br>
- `Function 12`: **Hexagonal Architecture** - Separates application contracts from infrastructure implementations to improve maintainability and extensibility.<br>
- `Function 13`: **Graceful Interruption** - Allows users to stop execution using `Ctrl+C`.<br>


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
│   ├── un_rar_files
│   └── log.log
├── TEMP/
└── src/
    ├── Application/
    │   └── services/
    │       └── CRACKER/
    │           └── IBruteForceService.py
    ├── Infrastructure/
    │   └── services/
    │       ├── CRACKER/
    │       │   └── SequentialBruteForceService.py
    │       ├── BeautifulPrinter.py
    │       ├── PasswordCombinationGenerator.py
    │       ├── TermiteService.py
    │       └── WinrarService.py
    ├── CORE/
    │   ├── Config.py
    │   ├── DependencyInjector.py
    │   ├── FolderController.py
    │   └── Logger.py
    ├── Models/
    │   └── Enums/
    │       └── Attack.py
    └── controllers/
        └── Controller.py
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
