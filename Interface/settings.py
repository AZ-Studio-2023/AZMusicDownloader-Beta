# coding:utf-8
import json
import random
import requests

from helper.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard, InfoBarPosition,
                            OptionsSettingCard, RangeSettingCard, PushSettingCard, InfoBarIcon, PushButton,
                            ColorSettingCard, HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, CustomColorSettingCard,
                            setTheme, setThemeColor, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths, QThread, pyqtSlot
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFontDialog, QFileDialog
import webbrowser
import datetime, winreg
from helper.config import YEAR, AUTHOR, VERSION, HELP_URL, FEEDBACK_URL, RELEASE_URL
from os import remove

reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
documents_path_value = winreg.QueryValueEx(reg_key, "My Music")
personalmusicpath = documents_path_value[0]
autopath = "{}\\AZMusicDownload".format(personalmusicpath)


class SettingInterface(ScrollArea):
    checkUpdateSig = pyqtSignal()
    musicFoldersChanged = pyqtSignal(list)
    acrylicEnableChanged = pyqtSignal(bool)
    downloadFolderChanged = pyqtSignal(str)
    minimizeToTrayChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.setObjectName('settings')
        # setting label

        self.settingLabel = QLabel(self.tr("设置"), self)
        # music folders

        self.personalGroup = SettingCardGroup(self.tr('个性化'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.tr('深浅模式'),
            self.tr("更改应用程序的外观"),
            texts=[
                self.tr('浅色'), self.tr('深色'),
                self.tr('使用系统设置')
            ],
            parent=self.personalGroup
        )
        self.themeColorCard=CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            self.tr('主题颜色'),
            self.tr('更改应用程序的主题颜色'),
            self.personalGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.tr('Language'),
            self.tr('Set your preferred language for UI'),
            texts=['简体中文', '繁體中文', 'English', self.tr('Use system setting')],
            parent=self.personalGroup
        )

        self.DownloadSettings = SettingCardGroup(self.tr("下载设置"), self.scrollWidget)
        self.downloadFolderCard = PushSettingCard(
            self.tr('选择目录'),
            FIF.DOWNLOAD,
            self.tr("下载目录"),
            cfg.get(cfg.downloadFolder),
            self.DownloadSettings
        )
        self.FolderAuto = PushSettingCard(
            self.tr('恢复默认'),
            FIF.DOWNLOAD,
            self.tr("恢复下载目录默认值"),
            self.tr('下载目录默认值为：') + autopath + self.tr('（即用户音乐文件夹）'),
            self.DownloadSettings
        )

        self.appGroup = SettingCardGroup(self.tr('应用程序设置'), self.scrollWidget)
        self.beta = SwitchSettingCard(
            FIF.DEVELOPER_TOOLS,
            self.tr('Beta实验功能'),
            self.tr('开启后会启用实验功能'),
            configItem=cfg.beta,
            parent=self.appGroup
        )
        self.adCard = SwitchSettingCard(
            FIF.CALORIES,
            self.tr('关闭广告'),
            self.tr('这是我们目前唯一的收入来源，求求别关闭qwq，如果真的要关闭的话，得重启后才能生效'),
            configItem=cfg.adcard,
            parent=self.appGroup
        )
        self.backtoinit = PushSettingCard(
            self.tr('重置'),
            FIF.CANCEL,
            self.tr("重置应用"),
            self.tr('重置操作重启后生效'),
            self.appGroup
        )

        self.searchGroup = SettingCardGroup(self.tr('搜索设置'), self.scrollWidget)
        self.twitCard = SwitchSettingCard(
            FIF.TAG,
            self.tr('搜索时展示相关的预选项'),
            self.tr('关闭后会更加节省资源'),
            configItem=cfg.twitcard,
            parent=self.searchGroup
        )
        self.twitCard.setEnabled(False)
        self.hotCard = SwitchSettingCard(
            FIF.TAG,
            self.tr('搜索时展示热门歌曲预选项'),
            self.tr('关闭后启动会更快'),
            configItem=cfg.hotcard,
            parent=self.searchGroup
        )

        # application
        self.aboutGroup = SettingCardGroup(self.tr('关于'), self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            self.tr('打开帮助页面'),
            FIF.HELP,
            self.tr('帮助'),
            self.tr('从帮助页面上获取帮助与支持'),
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('提供反馈'),
            self.tr('通过提供反馈来帮助我们打造更好的应用'),
            self.aboutGroup
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr('Changelog'),
            FIF.INFO,
            self.tr('更新日志'),
            '© ' + self.tr(' ') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION}",
            self.aboutGroup
        )
        self.__initWidget()


    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(60, 63)
        
        # add cards to group
        self.DownloadSettings.addSettingCard(self.downloadFolderCard)
        self.DownloadSettings.addSettingCard(self.FolderAuto)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.languageCard)

        self.appGroup.addSettingCard(self.beta)
        self.appGroup.addSettingCard(self.adCard)
        self.appGroup.addSettingCard(self.backtoinit)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        
        self.searchGroup.addSettingCard(self.twitCard)
        self.searchGroup.addSettingCard(self.hotCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.DownloadSettings)
        self.expandLayout.addWidget(self.appGroup)
        self.expandLayout.addWidget(self.searchGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onDownloadFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("Choose folder"), "./")
        if not folder or cfg.get(cfg.downloadFolder) == folder:
            return
        cfg.set(cfg.downloadFolder, folder)
        self.downloadFolderCard.setContent(folder)
        
    def __FolederAutoCardClicked(self):
        cfg.set(cfg.downloadFolder, autopath)
        self.downloadFolderCard.setContent(cfg.get(cfg.downloadFolder))
        
    def __backtoinitClicked(self):
        try:
            remove("config/config.json")
            self.__showRestartTooltip()
            self.backtoinit.setEnabled(False)
        except:
            InfoBar.error(
            '',
            self.tr('Nothing should be changed.'),
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss()
        
    def __changelog(self):
        QDesktopServices.openUrl(QUrl("https://github.com/AZ-Studio-2023/AZMusicDownloader/releases/tag/v2.2.0"))

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        self.downloadFolderCard.clicked.connect(self.__onDownloadFolderCardClicked)
        self.FolderAuto.clicked.connect(self.__FolederAutoCardClicked)
        self.backtoinit.clicked.connect(self.__backtoinitClicked)
        self.beta.checkedChanged.connect(self.minimizeToTrayChanged)
        self.aboutCard.clicked.connect(self.__changelog)
        self.feedbackCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
