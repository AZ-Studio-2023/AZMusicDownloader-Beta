# coding:utf-8
from helper.config import cfg, pfg
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, CustomColorSettingCard,
                            OptionsSettingCard, PushSettingCard, setTheme, PrimaryPushButton,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea, PushButton, 
                            ComboBoxSettingCard, ExpandLayout, Theme, InfoBar, FlyoutView, Flyout)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog
from sys import platform, getwindowsversion
from helper.getvalue import YEAR, AUTHOR, VERSION, HELP_URL, FEEDBACK_URL, RELEASE_URL, autopath, AZ_URL, verdetail, apilists
from helper.inital import delfin, get_update, showup, setSettingsQss
from helper.localmusicsHelper import ref
from helper.SettingHelper import DeleteAllData
from sys import exit

class SettingInterface(ScrollArea):
    micaEnableChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.setObjectName('settings')
        self.settingLabel = QLabel(self.tr("设置"), self)
        self.upworker = get_update()
        self.upworker.finished.connect(self.showupupgrade)
        
        # Personalize
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
            self.tr('语言'),
            self.tr('选择应用显示语言'),
            texts=['简体中文', self.tr('使用系统设置')],
            parent=self.personalGroup
        )
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.tr('云母效果'),
            self.tr('应用Mica半透明效果（仅支持Windows11）'),
            cfg.micaEnabled,
            self.personalGroup
        )

        # Folders
        self.DownloadSettings = SettingCardGroup(self.tr("下载设置"), self.scrollWidget)
        self.downloadFolderCard = PushSettingCard(
            self.tr('选择目录'),
            FIF.FOLDER,
            self.tr("下载目录"),
            cfg.get(cfg.downloadFolder),
            self.DownloadSettings
        )
        self.FolderAuto = PushSettingCard(
            self.tr('恢复默认'),
            FIF.CLEAR_SELECTION,
            self.tr("恢复下载目录默认值"),
            self.tr('下载目录默认值为：') + autopath + self.tr('（即用户音乐文件夹）'),
            self.DownloadSettings
        )

        # Application
        self.appGroup = SettingCardGroup(self.tr('应用程序设置'), self.scrollWidget)
        self.beta = SwitchSettingCard(
            FIF.DEVELOPER_TOOLS,
            self.tr('Beta实验功能'),
            self.tr('开启后会启用实验功能'),
            configItem=cfg.beta,
            parent=self.appGroup
        )
        self.beta.checkedChanged.connect(self.beta_enable)
        self.Update_Card = SwitchSettingCard(
            FIF.FLAG,
            self.tr('禁用更新检查'),
            self.tr('开启后启动将不会检查版本更新'),
            configItem=cfg.update_card,
            parent=self.appGroup
        )
        self.backtoinit = PushSettingCard(
            self.tr('重置'),
            FIF.CANCEL,
            self.tr("重置应用"),
            self.tr('重置操作重启后生效'),
            self.appGroup
        )

        # Search
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
        self.apiCard = ComboBoxSettingCard(
            pfg.apicard,
            FIF.GLOBE,
            self.tr('第三方音乐API'),
            self.tr('仅会修改搜索下载页使用的API。由于QQMA需要账号COOKIE才能进行调用，请自行部署。'),
            texts=apilists,
            parent=self.searchGroup
        )
        
        #BetaOnly
        if cfg.beta.value:
            self.betaonly()

        # About
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
        
        self.micaCard.setEnabled(platform == 'win32' and getwindowsversion().build >= 22000)
        if cfg.beta.value:
            self.toast_Card.setEnabled(platform == 'win32' and getwindowsversion().build >= 17134)
        self.__initWidget()

    def betaonly(self):
        self.BetaOnlyGroup = SettingCardGroup(self.tr('Beta Only'), self.scrollWidget)
        self.debug_Card = SwitchSettingCard(
                FIF.CODE,
                self.tr('Debug Mode'),
                self.tr('The global exception capture will be disabled, and there will be outputs in the commandline.(Code Running Only)'),
                configItem=cfg.debug_card,
                parent=self.BetaOnlyGroup
        )
        self.plugin_Card = SwitchSettingCard(
                FIF.DICTIONARY_ADD,
                self.tr('Enable Plugins'),
                self.tr('You can use more APIs or other features through using plugins.'),
                configItem=cfg.PluginEnable,
                parent=self.BetaOnlyGroup
        )
        self.toast_Card = SwitchSettingCard(
                FIF.MEGAPHONE,
                self.tr('Enable Windows Toast'),
                self.tr(
                    'Use System Notification to notice you when the process is finished. ( Windows 10.0.17134 or later)'),
                configItem=cfg.toast,
                parent=self.BetaOnlyGroup
        )

    def beta_enable(self):
        if cfg.beta.value:
            self.betaonly()
            self.toast_Card.setEnabled(platform == 'win32' and getwindowsversion().build >= 17134)
            self.expandLayout.addWidget(self.BetaOnlyGroup)
            self.BetaOnlyGroup.addSettingCard(self.debug_Card)
            self.BetaOnlyGroup.addSettingCard(self.plugin_Card)
            self.BetaOnlyGroup.addSettingCard(self.toast_Card)
            self.debug_Card.setVisible(True)
            self.plugin_Card.setVisible(True)
            self.toast_Card.setVisible(True)
            self.BetaOnlyGroup.setVisible(True)
        else:
            self.debug_Card.setValue(False)
            self.plugin_Card.setValue(False)
            self.toast_Card.setValue(False)
            self.debug_Card.setVisible(False)
            self.plugin_Card.setVisible(False)
            self.toast_Card.setVisible(False)
            self.BetaOnlyGroup.setVisible(False)
    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 120, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        setSettingsQss(parent=self)

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
        self.personalGroup.addSettingCard(self.micaCard)

        self.appGroup.addSettingCard(self.beta)
        self.appGroup.addSettingCard(self.Update_Card)
        self.appGroup.addSettingCard(self.backtoinit)
        
        if cfg.beta.value:
            self.BetaOnlyGroup.addSettingCard(self.debug_Card)
            self.BetaOnlyGroup.addSettingCard(self.plugin_Card)
            self.BetaOnlyGroup.addSettingCard(self.toast_Card)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)
        
        self.searchGroup.addSettingCard(self.twitCard)
        self.searchGroup.addSettingCard(self.hotCard)
        self.searchGroup.addSettingCard(self.apiCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(60, 10, 60, 0)
        self.expandLayout.addWidget(self.DownloadSettings)
        self.expandLayout.addWidget(self.searchGroup)
        self.expandLayout.addWidget(self.personalGroup)
        if cfg.beta.value:
            self.expandLayout.addWidget(self.BetaOnlyGroup)
        self.expandLayout.addWidget(self.appGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('设置需要重启程序后生效'),
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
        ref(musicpath=folder)
        
    def __FolederAutoCardClicked(self):
        cfg.set(cfg.downloadFolder, autopath)
        self.downloadFolderCard.setContent(cfg.get(cfg.downloadFolder))
        ref(musicpath=autopath)
        
    def __backtoinitClicked(self):
        w = DeleteAllData(self)
        if not w.exec():
            delfin(IfMusicPath=w.DataCheckBox.isChecked())
            exit(0)

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        setSettingsQss(parent=self)
        
    def opengithub(self):
        QDesktopServices.openUrl(QUrl(RELEASE_URL))
    def openaz(self):
        QDesktopServices.openUrl(QUrl(AZ_URL))
    def showupupgrade(self, updata):
        showup(parent = self, updata = updata, upworker = self.upworker)
    def upupgrade(self):
        self.upworker.start()
        
    def beta_not(self):
        if not cfg.beta.value:
            self.debug_Card.setValue(False)
            self.plugin_Card.setValue(False)
            self.toast_Card.setValue(False)
            self.debug_Card.setVisible(False)
            self.plugin_Card.setVisible(False)
            self.toast_Card.setVisible(False)
            self.BetaOnlyGroup.setVisible(False)
        
    def __changelog(self):
        view = FlyoutView(
            title=f'AZMusicDownloader {VERSION}更新日志 ',
            content=verdetail,
            #image='resource/splash.png',
            isClosable=True
        )
        
        # add button to view
        button1 = PushButton(FIF.GITHUB, 'GitHub')
        button1.setFixedWidth(120)
        button1.clicked.connect(self.opengithub)
        view.addWidget(button1, align=Qt.AlignRight)
        
        button2 = PushButton('AZ Studio')
        button2.setFixedWidth(120)
        button2.clicked.connect(self.openaz)
        view.addWidget(button2, align=Qt.AlignRight)
        
        button3 = PrimaryPushButton('检查更新')
        button3.setFixedWidth(120)
        button3.clicked.connect(self.upupgrade)
        view.addWidget(button3, align=Qt.AlignRight)

        # adjust layout (optional)
        view.widgetLayout.insertSpacing(1, 5)
        view.widgetLayout.addSpacing(5)

        # show view
        w = Flyout.make(view, self.aboutCard, self)
        view.closed.connect(w.close)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)
        self.micaCard.checkedChanged.connect(self.micaEnableChanged)

        self.downloadFolderCard.clicked.connect(self.__onDownloadFolderCardClicked)
        self.FolderAuto.clicked.connect(self.__FolederAutoCardClicked)
        self.backtoinit.clicked.connect(self.__backtoinitClicked)
        self.beta.checkedChanged.connect(self.beta_not)
        self.aboutCard.clicked.connect(self.__changelog)
        self.feedbackCard.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))
