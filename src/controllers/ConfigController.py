"""
FelipedelosH
2026

Read all config from: .env
"""
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        self.config = {}
        self.loadConfig()

    def loadConfig(self):
        try:
            load_dotenv()
            # CONFIG ENV VARS
            # self.config[""] = os.getenv("")
            self.config["RAR_FILE_TO_CRACK"] = os.getenv("RAR_FILE_TO_CRACK")

            self.config["GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK"] = os.getenv("GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK")
            self.config["GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK"] = int(self.config["GEN_CONFIG_LEN_MIN_SIZE_CHAR_SELECT_TO_CRACK"])

            self.config["GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK"] = os.getenv("GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK")
            self.config["GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK"] = int(self.config["GEN_CONFIG_LEN_MAX_SIZE_CHAR_SELECT_TO_CRACK"])

            self.config["GEN_CONFIG_CHARACTERS_ARR_INPUT_FILE"] = os.getenv("GEN_CONFIG_CHARACTERS_ARR_INPUT_FILE")

            self.config["GEN_CONFIG_DISPLAY_LOGS"] = os.getenv("GEN_CONFIG_DISPLAY_LOGS")
            self.config["GEN_CONFIG_DISPLAY_LOGS"] = True if str(self.config["GEN_CONFIG_DISPLAY_LOGS"]).strip().lower() == "true" else False
            # END CONFIG ENV VARS
        except:
            pass

    def getConfig(self, key):
        try:
            return self.config.get(key)
        except:
            return None
