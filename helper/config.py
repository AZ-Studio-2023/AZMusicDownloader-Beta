# coding:utf-8
from enum import Enum
from sys import platform, getwindowsversion
from helper.getvalue import configpath, autopath
from helper.SettingHelper import get_all_api
from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator,  FolderValidator, ConfigSerializer, FolderListValidator)

class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    # Folders
    downloadFolder = ConfigItem(
        "Folders", "Download", autopath, FolderValidator())

    # Application
    beta = ConfigItem(
        "Application", "beta", False, BoolValidator())
    update_card = ConfigItem(
        "Application", "update_card", False, BoolValidator(), restart=True)
        
    #pluginsFolders
    PluginFolders = ConfigItem(
        "Plugins", "Folders", [], FolderListValidator(), restart=True)
    
    # Search
    twitcard = ConfigItem(
        "Search", "twitcard", False, BoolValidator(), restart=True)
    hotcard = ConfigItem(
        "Search", "hotcard", False, BoolValidator(), restart=True)
    
    # Personalize
    language = OptionsConfigItem(
        "Personalize", "Language", Language.CHINESE_SIMPLIFIED, OptionsValidator(Language), LanguageSerializer(), restart=True)
    micaEnabled = ConfigItem("Personalize", "MicaEnabled", platform == 'win32' and getwindowsversion().build >= 22000, BoolValidator())
    
    #BetaOnly
    toast = ConfigItem(
        "BetaOnly", "toast", False, BoolValidator())
    PluginEnable = ConfigItem(
        "BetaOnly", "EnablePlugins", False, BoolValidator(), restart=True)
    debug_card = ConfigItem(
        "BetaOnly", "debug_card", False, BoolValidator(), restart=True)

cfg = Config()
qconfig.load(configpath, cfg)

class Plufig(Config):
    apicard = OptionsConfigItem(
        "Search", "apicard", "NCMA", OptionsValidator(get_all_api(folders_arg=cfg.PluginFolders.value)))

pfg = Plufig()
qconfig.load(configpath, pfg)