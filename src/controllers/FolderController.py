"""
FelipedelosH
2026

Generate a folders
"""
import os

class FolderController:
    def __new__(cls):
        raise TypeError("FolderController cannot be instantiated")

    @staticmethod
    def createInitalFolders(path, logger):
        # MAIN FOLDERS
        _folders = [
            "OUTPUT",
            "INPUT"
        ]

        for folder in _folders:
            _path = os.path.join(path, folder)
            FolderController.createFolder(_path)


    @staticmethod
    def createFolder(path):
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
        except:
            pass
