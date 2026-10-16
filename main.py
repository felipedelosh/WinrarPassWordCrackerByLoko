"""
FelipedelosH
2026

Enter a winrar file '.rar' and usages characters.txt to generate a brute force attack.
"""
import os
from src.CORE.Config import Config
from src.controllers.Controller import Controller
from src.CORE.DependencyInjector import DependencyInjector


path = str(os.path.dirname(os.path.abspath(__file__)))
config = Config()
dependencies = DependencyInjector.build_dependencies(
    path=path,
    config=config
)
c = Controller(path, config, dependencies)

try:
    c.bruteForce()
finally:
    c.saveLogs()
