# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
    QErrorMessage,
)


class UiUserSettings(object):
    def setupUi(self, UserNameLineEdit):
        if not UserNameLineEdit.objectName():
            UserNameLineEdit.setObjectName("UserNameLineEdit")
        UserNameLineEdit.resize(190, 270)
        UserNameLineEdit.setMinimumSize(QSize(190, 270))
        UserNameLineEdit.setMaximumSize(QSize(190, 270))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(124, 230, 196, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        brush2 = QBrush(QColor(227, 255, 246, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Light, brush2)
        brush3 = QBrush(QColor(175, 242, 221, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Midlight, brush3)
        brush4 = QBrush(QColor(62, 115, 98, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Dark, brush4)
        brush5 = QBrush(QColor(83, 153, 131, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        brush6 = QBrush(QColor(255, 255, 255, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush6)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush)
        brush7 = QBrush(QColor(189, 242, 225, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush7)
        brush8 = QBrush(QColor(255, 255, 220, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        brush9 = QBrush(QColor(0, 0, 0, 127))
        brush9.setStyle(Qt.SolidPattern)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush9)
        # endif
        palette.setBrush(QPalette.Active, QPalette.Accent, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Light, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush9)
        # endif
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Light, brush2)
        palette.setBrush(QPalette.Disabled, QPalette.Midlight, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Dark, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Mid, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
        brush10 = QBrush(QColor(62, 115, 98, 127))
        brush10.setStyle(Qt.SolidPattern)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush10)
        # endif
        brush11 = QBrush(QColor(181, 255, 231, 255))
        brush11.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush11)
        UserNameLineEdit.setPalette(palette)
        self.userNameLineEdit = QLineEdit(UserNameLineEdit)
        self.userNameLineEdit.setObjectName("userNameLineEdit")
        self.userNameLineEdit.setGeometry(QRect(40, 50, 113, 22))
        self.userNameLabel = QLabel(UserNameLineEdit)
        self.userNameLabel.setObjectName("userNameLabel")
        self.userNameLabel.setGeometry(QRect(40, 20, 91, 16))
        font = QFont()
        font.setFamilies(["Calibri"])
        font.setPointSize(11)
        font.setItalic(False)
        self.userNameLabel.setFont(font)
        self.subjectIdLineEdit = QLineEdit(UserNameLineEdit)
        self.subjectIdLineEdit.setObjectName("subjectIdLineEdit")
        self.subjectIdLineEdit.setGeometry(QRect(40, 120, 113, 22))
        self.subjectIdLabel = QLabel(UserNameLineEdit)
        self.subjectIdLabel.setObjectName("subjectIdLabel")
        self.subjectIdLabel.setGeometry(QRect(40, 90, 101, 16))
        font1 = QFont()
        font1.setFamilies(["Calibri"])
        font1.setPointSize(11)
        self.subjectIdLabel.setFont(font1)
        self.submitPushButton = QPushButton(UserNameLineEdit)
        self.submitPushButton.setObjectName("submitPushButton")
        self.submitPushButton.setGeometry(QRect(40, 220, 111, 24))
        palette1 = QPalette()
        brush12 = QBrush(QColor(76, 168, 133, 255))
        brush12.setStyle(Qt.SolidPattern)
        palette1.setBrush(QPalette.Active, QPalette.Button, brush12)
        palette1.setBrush(QPalette.Inactive, QPalette.Button, brush12)
        palette1.setBrush(QPalette.Disabled, QPalette.Button, brush12)
        self.submitPushButton.setPalette(palette1)
        self.submitPushButton.setFont(font1)
        self.sesssionIdLabel = QLabel(UserNameLineEdit)
        self.sesssionIdLabel.setObjectName("sesssionIdLabel")
        self.sesssionIdLabel.setGeometry(QRect(40, 160, 101, 16))
        self.sesssionIdLabel.setFont(font1)
        self.sessionIdLineEdit = QLineEdit(UserNameLineEdit)
        self.sessionIdLineEdit.setObjectName("sessionIdLineEdit")
        self.sessionIdLineEdit.setGeometry(QRect(40, 190, 113, 22))
        self.error_message = QErrorMessage(UserNameLineEdit)

        self.retranslateUi(UserNameLineEdit)

        QMetaObject.connectSlotsByName(UserNameLineEdit)

    # setupUi

    def retranslateUi(self, UserNameLineEdit):
        UserNameLineEdit.setWindowTitle(
            QCoreApplication.translate("UserNameLineEdit", "Schema", None)
        )
        self.userNameLabel.setText(
            QCoreApplication.translate("UserNameLineEdit", "User Full Name", None)
        )
        self.subjectIdLabel.setText(
            QCoreApplication.translate("UserNameLineEdit", "Subject ID", None)
        )
        self.submitPushButton.setText(
            QCoreApplication.translate("UserNameLineEdit", "Submit", None)
        )
        self.sesssionIdLabel.setText(
            QCoreApplication.translate("UserNameLineEdit", "Session ID", None)
        )

    # retranslateUi
