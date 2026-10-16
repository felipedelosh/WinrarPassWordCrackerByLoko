"""
FelipedelosH
2026

Enter a winrar file '.rar' and usages characters.txt to generate a brute force attack.
"""
import os
from src.controllers.Controller import Controller

path = str(os.path.dirname(os.path.abspath(__file__)))
c = Controller(path)
c.bruteForce()

try:
    c.bruteForce()
finally:
    c.saveLogs()
