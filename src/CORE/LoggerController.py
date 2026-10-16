"""
FelipedelosH
2026

LOGs By FelipedelosH
"""
class Logger:
    def __init__(self, isPrintable = False):
        self.log = ""
        self.print = isPrintable

    def info(self, data):
        _newData = f"INFO::{data}"
        if self.print:
            print(_newData)
        self.log = self.log + _newData + "\n"


    def warn(self, data):
        _newData = f"WARN::{data}"
        if self.print:
            print(_newData)
        self.log = self.log + _newData + "\n"

    def error(self, data):
        _newData = f"ERROR::{data}"
        if self.print:
            print(_newData)
        self.log = self.log + _newData + "\n"
