import os
import re
import sys
import csv
import datetime
import time
import platform
import sqlite3
import pdb
import webbrowser
import qtawesome as qta
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtTest import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
from modules.src_translations import *
from modules.secrets import *


class SRC_ControlInfo(QMainWindow):
    def __init__(self, parent=None):
        super(SRC_ControlInfo, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        settings = QSettings("berkaygediz", "SpanRC")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LayoutDirection.LeftToRight,
                Qt.AlignmentFlag.AlignCenter,
                QSize(int(screen.width() * 0.2),
                      int(screen.height() * 0.2)),
                screen
            )
        )

        if settings.value("current_language") == None:
            settings.setValue("current_language", "English")
            settings.sync()
        self.language = settings.value("current_language")
        self.setStyleSheet("background-color: transparent;")
        self.setWindowOpacity(0.75)
        self.widget_central = QWidget()
        self.layout_central = QVBoxLayout(self.widget_central)
        self.widget_central.setStyleSheet(
            "background-color: #6F61C0; border-radius: 50px; border: 1px solid #A084E8; border-radius: 10px;")

        self.title = QLabel("SpanRC", self)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont('Roboto', 30))
        self.title.setStyleSheet(
            "background-color: #A084E8; color: #FFFFFF; font-weight: bold; font-size: 30px; border-radius: 25px; border: 1px solid #000000;")
        self.layout_central.addWidget(self.title)

        self.label_status = QLabel("...", self)
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status.setFont(QFont('Roboto', 10))
        self.layout_central.addWidget(self.label_status)

        self.setCentralWidget(self.widget_central)

        if serverconnect():
            sqlite_file = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'src.db')
            sqlitedb = sqlite3.connect(sqlite_file)
            sqlitecursor = sqlitedb.cursor()
            sqlitecursor.execute(
                "CREATE TABLE IF NOT EXISTS profile (nametag TEXT, email TEXT, password TEXT)")
            sqlitecursor.execute(
                "CREATE TABLE IF NOT EXISTS apps (spanrc INTEGER DEFAULT 0, email TEXT)")
            sqlitecursor.execute(
                "CREATE TABLE IF NOT EXISTS log (email TEXT, devicename TEXT, product NVARCHAR(100), activity NVARCHAR(100), log TEXT, logdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

            profile_email = sqlitecursor.execute(
                "SELECT email FROM profile").fetchone()
            profile_pw = sqlitecursor.execute(
                "SELECT password FROM profile").fetchone()

            if profile_email is not None and profile_pw is not None:
                local_email = profile_email[0]
                local_pw = profile_pw[0]
                mysql_connection = serverconnect()
                if mysql_connection:
                    mysqlcursor = mysql_connection.cursor()
                    mysqlcursor.execute(
                        "SELECT * FROM profile WHERE email = %s", (local_email,))
                    user_result = mysqlcursor.fetchone()
                    if user_result is not None:
                        if local_email == user_result[1] and local_pw == user_result[3]:
                            mysqlcursor.execute(
                                "INSERT INTO log (email, devicename, product, activity, log) VALUES (%s, %s, %s, %s, %s)", (user_result[1], platform.node(), "SpanRC", "Login", "Verified"))
                            mysql_connection.commit()
                            mysqlcursor.execute(
                                "SELECT * FROM user_settings WHERE email = %s AND product = %s", (local_email, "SpanRC"))
                            user_settings = mysqlcursor.fetchone()
                            mysql_connection.commit()
                            mysql_connection.close()
                            if user_settings is not None:
                                settings.setValue(
                                    "current_theme", user_settings[3])
                                settings.setValue(
                                    "current_language", user_settings[4])
                                settings.sync()
                            else:
                                settings.setValue(
                                    "current_theme", "light")
                                settings.setValue(
                                    "current_language", "English")
                                settings.sync()
                            self.label_status.setStyleSheet(
                                "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                            self.label_status.setText(
                                "💡" + local_email.split('@')[0])
                            pdb.set_trace()
                            SRC_Workbook().show()
                            QTimer.singleShot(1250, self.hide)
                        else:
                            def logout():
                                sqlite_file = os.path.join(os.path.dirname(
                                    os.path.abspath(__file__)), 'src.db')
                                sqliteConnection = sqlite3.connect(sqlite_file)
                                sqlitecursor = sqliteConnection.cursor()
                                sqlitecursor.execute(
                                    "DROP TABLE IF EXISTS profile")
                                sqlitecursor.connection.commit()
                                sqlitecursor.execute(
                                    "DROP TABLE IF EXISTS apps")
                                sqlitecursor.connection.commit()
                                sqlitecursor.execute(
                                    "DROP TABLE IF EXISTS log")
                                sqlitecursor.connection.commit()
                                sqlitecursor.execute(
                                    "DROP TABLE IF EXISTS user_settings")
                                sqlitecursor.connection.commit()
                                SRC_ControlInfo().show()
                                QTimer.singleShot(0, self.hide)
                            self.label_status.setStyleSheet(
                                "background-color: #252525; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                            self.label_status.setText(
                                translations[settings.value("current_language")]["wrong_password"])
                            mysqlcursor.execute(
                                "INSERT INTO log (email, devicename, product, activity, log) VALUES (%s, %s, %s, %s, %s)", (local_email, platform.node(), "SpanRC", "Login", "Failed"))
                            mysql_connection.commit()
                            logoutbutton = QPushButton(translations[settings.value(
                                "current_language")]["logout"])
                            logoutbutton.setStyleSheet(
                                "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                            logoutbutton.clicked.connect(logout)
                            self.layout_central.addWidget(logoutbutton)
                    else:
                        self.label_status.setStyleSheet(
                            "background-color: #252525; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                        self.label_status.setText(
                            translations[settings.value("current_language")]["no_account"])
                        logoutbutton = QPushButton(translations[settings.value(
                            "current_language")]["register"])
                        logoutbutton.setStyleSheet(
                            "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                        logoutbutton.clicked.connect(SRC_Welcome().show)
                        self.layout_central.addWidget(logoutbutton)
                        self.close_button = QPushButton(translations[settings.value(
                            "current_language")]["exit"])
                        self.close_button.setStyleSheet(
                            "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                        self.close_button.clicked.connect(sys.exit)
                        self.layout_central.addWidget(self.close_button)

                else:
                    self.label_status.setText(
                        translations[settings.value("current_language")]["connection_denied"])
                    logoutbutton = QPushButton(translations[settings.value(
                        "current_language")]["register"])
                    logoutbutton.setStyleSheet(
                        "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
                    logoutbutton.clicked.connect(SRC_Welcome().show)
                    self.layout_central.addWidget(logoutbutton)
            else:
                SRC_Welcome().show()
                QTimer.singleShot(0, self.hide)
        else:
            self.label_status.setText(translations[settings.value(
                "current_language")]["connection_denied"])
            self.label_status.setStyleSheet(
                "background-color: #252525; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")
            QTimer.singleShot(10000, sys.exit)


class SRC_Welcome(QMainWindow):
    def __init__(self, parent=None):
        super(SRC_Welcome, self).__init__(parent)
        starttime = datetime.datetime.now()
        settings = QSettings("berkaygediz", "SpanRC")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LayoutDirection.LeftToRight,
                Qt.AlignmentFlag.AlignCenter,
                QSize(int(screen.width() * 0.4),
                      int(screen.height() * 0.5)),
                screen
            )
        )

        if settings.value("current_language") == None:
            settings.setValue("current_language", "English")
            settings.sync()
        self.language = settings.value("current_language")

        self.setStyleSheet("background-color: #F9E090;")
        self.setWindowTitle(translations[settings.value(
            "current_language")]["welcome-title"])
        introduction = QVBoxLayout()
        self.statusBar().setStyleSheet(
            "background-color: #F9E090; color: #000000; font-weight: bold; font-size: 12px; border-radius: 10px; border: 1px solid #000000;")
        product_label = QLabel("SpanRC 🎉")
        product_label.setStyleSheet(
            "background-color: #DFBB9D; color: #000000; font-size: 28px; font-weight: bold; border-radius: 10px; border: 1px solid #000000;")
        product_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        intro_label = QLabel(translations[settings.value(
            "current_language")]["intro"])
        intro_label.setStyleSheet(
            "background-color: #F7E2D6; color: #000000; font-size: 12px; border-radius: 10px; border: 1px solid #000000;")
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        intro_label.setFixedHeight(50)

        def SRC_changeLanguage():
            language = self.language_combobox.currentText()
            settings = QSettings("berkaygediz", "SpanRC")
            settings.setValue("current_language", language)
            settings.sync()

        self.language_combobox = QComboBox()
        self.language_combobox.setStyleSheet(
            "background-color: #B3E8E5; color: #000000; border-radius: 10px; border: 1px solid #000000; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px; font-size: 16px;")
        self.language_combobox.addItems(
            ["English", "Türkçe", "Azərbaycanca", "Deutsch", "Español"])
        self.language_combobox.currentTextChanged.connect(SRC_changeLanguage)
        self.language_combobox.setCurrentText(
            settings.value("current_language"))

        introduction.addWidget(product_label)
        introduction.addWidget(intro_label)
        introduction.addWidget(self.language_combobox)
        label_email = QLabel(
            translations[settings.value("current_language")]["email"] + ":")
        label_email.setStyleSheet(
            "color: #A72461; font-weight: bold; font-size: 16px; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px;")
        textbox_email = QLineEdit()
        textbox_email.setStyleSheet(
            "background-color: #B3E8E5; color: #000000; border-radius: 10px; border: 1px solid #000000; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px; font-size: 16px;")

        label_password = QLabel(
            translations[settings.value("current_language")]["password"] + ":")
        label_password.setStyleSheet(
            "color: #A72461; font-weight: bold; font-size: 16px; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px;")
        textbox_password = QLineEdit()
        textbox_password.setStyleSheet(
            "background-color: #B3E8E5; color: #000000; border-radius: 10px; border: 1px solid #000000; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px; font-size: 16px;")
        textbox_password.setEchoMode(QLineEdit.EchoMode.Password)

        label_exception = QLabel()
        label_exception.setStyleSheet(
            "color: #A72461; font-weight: bold; font-size: 16px; margin: 10px; margin-left: 0px; margin-right: 0px; padding: 0px;")
        label_exception.setAlignment(Qt.AlignmentFlag.AlignCenter)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(label_email)
        bottom_layout.addWidget(textbox_email)
        bottom_layout.addWidget(label_password)
        bottom_layout.addWidget(textbox_password)
        bottom_layout.addWidget(label_exception)

        button_layout = QHBoxLayout()

        button_login = QPushButton(
            translations[settings.value("current_language")]["login"])
        button_login.setStyleSheet(
            "background-color: #A72461; color: #FFFFFF; font-weight: bold; padding: 10px; border-radius: 10px; border: 1px solid #000000; margin: 10px;")

        def is_valid_email(email):
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            return re.match(email_regex, email)

        def register():
            email = textbox_email.text()
            password = textbox_password.text()

            if email == "" or password == "":
                label_exception.setText(translations[settings.value(
                    "current_language")]["fill_all"])
            elif not is_valid_email(textbox_email.text()):
                label_exception.setText(translations[settings.value(
                    "current_language")]["invalid_email"])
            else:
                mysqlserver = serverconnect()
                mysqlcursor = mysqlserver.cursor()
                sqlite_file = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), 'src.db')
                sqliteConnection = sqlite3.connect(sqlite_file)
                mysqlcursor.execute(
                    "SELECT email FROM profile WHERE email = %s", (email,))
                user_result = mysqlcursor.fetchone()

                if user_result == None:
                    mysqlcursor.execute("INSERT INTO profile (email, password) VALUES (%s, %s)", (
                        email, password))
                    mysqlserver.commit()
                    mysqlcursor.execute(
                        "INSERT INTO log (email, devicename, product, activity, log) VALUES (%s, %s, %s, %s, %s)", (email, platform.node(), "SpanRC", "Register", "Success"))
                    mysqlserver.commit()
                    mysqlcursor.execute(
                        "INSERT INTO apps (spanrc, email) VALUES (%s, %s)", (0, email))
                    mysqlserver.commit()
                    language = settings.value("current_language")
                    mysqlcursor.execute(
                        "INSERT INTO user_settings (email, product, theme, language) VALUES (%s, %s, %s, %s)", (email, "SpanRC", "light", language))
                    mysqlserver.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS profile")
                    sqliteConnection.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS apps")
                    sqliteConnection.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS log")
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS profile (email TEXT, password TEXT)")
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS apps (spanrc INTEGER DEFAULT 0, email TEXT)")
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS log (email TEXT, devicename TEXT, log TEXT, logdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS user_settings (email TEXT, theme TEXT, language TEXT)")
                    sqliteConnection.commit()
                    sqliteConnection.execute("INSERT INTO profile (nametag, email, password) VALUES (?, ?, ?)", (
                        email.split('@')[0], email, password))
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO apps (spanrc, email) VALUES (?, ?)", (0, email))
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO log (email, devicename, product, activity, log) VALUES (?, ?, ?, ?, ?)", (email, platform.node(), "SpanRC", "Register", "Success"))
                    sqliteConnection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO user_settings (email, theme, language) VALUES (?, ?, ?)", (email, "light", language))
                    sqliteConnection.commit()
                    time.sleep(1)
                    label_exception.setText(translations[settings.value(
                        "current_language")]["register_success"])
                    QTimer.singleShot(3500, self.hide)
                    SRC_Workbook().show()
                else:
                    label_exception.setText(
                        translations[settings.value("current_language")]["already_registered"])

        def login():
            email = textbox_email.text()
            password = textbox_password.text()

            if email == "" or password == "":
                label_exception.setText(translations[settings.value(
                    "current_language")]["fill_all"])
            elif not is_valid_email(email):
                label_exception.setText(translations[settings.value(
                    "current_language")]["invalid_email"])
            else:
                mysqlserver = serverconnect()
                mysqlcursor = mysqlserver.cursor()
                sqlite_file = os.path.join(os.path.dirname(
                    os.path.abspath(__file__)), 'src.db')
                sqliteConnection = sqlite3.connect(sqlite_file).cursor()
                mysqlcursor.execute(
                    "SELECT email FROM profile WHERE email = %s", (email,))
                user_result = mysqlcursor.fetchone()
                mysqlcursor.execute(
                    "SELECT password FROM profile WHERE password = %s", (password,))
                pw_result = mysqlcursor.fetchone()

                if user_result and pw_result:
                    mysqlcursor.execute("INSERT INTO log (email, devicename, product, activity, log) VALUES (%s, %s, %s, %s, %s)", (
                        email, platform.node(), "SpanRC", "Login", "Success"))
                    mysqlserver.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS profile")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS apps")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute("DROP TABLE IF EXISTS log")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "DROP TABLE IF EXISTS user_settings")
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS profile (nametag TEXT, email TEXT, password TEXT)")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS apps (spanrc INTEGER DEFAULT 0, email TEXT)")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS log (email TEXT, devicename TEXT, product NVARCHAR(100), activity NVARCHAR(100), log TEXT, logdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "CREATE TABLE IF NOT EXISTS user_settings (email TEXT, theme TEXT, language TEXT)")
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO profile (nametag, email, password) VALUES (?, ?, ?)", (email.split('@')[0], email, password))
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO apps (spanrc, email) VALUES (?, ?)", (0, email))
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO user_settings (email, theme, language) VALUES (?, ?, ?)", (email, "light", "English"))
                    sqliteConnection.connection.commit()
                    sqliteConnection.execute(
                        "INSERT INTO log (email, devicename, product, activity, log) VALUES (?, ?, ?, ?, ?)", (email, platform.node(), "SpanRC", "Login", "Success"))
                    sqliteConnection.connection.commit()
                    time.sleep(1)
                    textbox_email.setText("")
                    textbox_password.setText("")
                    label_exception.setText("")
                    QTimer.singleShot(3500, self.hide)
                    SRC_Workbook().show()
                else:
                    settings.setValue("current_language", "English")
                    label_exception.setText(
                        translations[settings.value("current_language")]["wrong_credentials"])

        button_login.clicked.connect(login)
        button_register = QPushButton(translations[settings.value(
            "current_language")]["register"])
        button_register.setStyleSheet(
            "background-color: #A72461; color: #FFFFFF; font-weight: bold; padding: 10px; border-radius: 10px; border: 1px solid #000000; margin: 10px;")
        button_register.clicked.connect(register)

        button_layout.addWidget(button_login)
        button_layout.addWidget(button_register)

        introduction.addLayout(bottom_layout)
        introduction.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(introduction)

        self.setCentralWidget(central_widget)
        endtime = datetime.datetime.now()
        self.statusBar().showMessage(
            str((endtime - starttime).total_seconds()) + " ms", 2500)

# undocommand codes


class SRC_ActivationStatus(QMainWindow):
    def __init__(self, parent=None):
        super(SRC_ActivationStatus, self).__init__(parent)
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(
        ), QApplication.desktop().availableGeometry()))

        # QVBoxLayout oluşturma
        layout = QVBoxLayout()

        self.activation_label = QLabel()
        self.activation_label.setWordWrap(True)
        self.activation_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.activation_label.setTextFormat(Qt.RichText)
        self.activation_label.setText("<center>"
                                      "<b>SpanRC</b><br>"
                                      "Activate your product or delete your account<br><br>"
                                      "</center>")
        button_layout = QHBoxLayout()

        self.activation_button = QPushButton("Activate")
        self.activation_button.setStyleSheet(
            "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")

        def activateSite():
            webbrowser.open('http://localhost/bg-ecosystem-web/activate.php')
        self.activation_button.clicked.connect(activateSite)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(
            "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")

        def deleteAccount():
            webbrowser.open('http://localhost/bg-ecosystem-web/profile.php')
        self.delete_button.clicked.connect(deleteAccount)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet(
            "background-color: #7900FF; color: #FFFFFF; font-weight: bold; font-size: 16px; border-radius: 30px; border: 1px solid #000000;")

        def logout():
            sqlite_file = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), 'src.db')
            sqliteConnection = sqlite3.connect(sqlite_file)
            sqlitecursor = sqliteConnection.cursor()
            sqlitecursor.execute("DROP TABLE IF EXISTS profile")
            sqlitecursor.connection.commit()
            sqlitecursor.execute("DROP TABLE IF EXISTS apps")
            sqlitecursor.connection.commit()
            sqlitecursor.execute("DROP TABLE IF EXISTS log")
            sqlitecursor.connection.commit()
            sqlitecursor.execute("DROP TABLE IF EXISTS user_settings")
            sqlitecursor.connection.commit()
            SRC_ControlInfo().show()
            QTimer.singleShot(0, self.hide)
        self.logout_button.clicked.connect(logout)

        button_layout.addWidget(self.activation_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.logout_button)

        layout.addWidget(self.activation_label)
        layout.addLayout(button_layout)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


class SRC_Workbook(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # press c to continue (initialization bug)
        pdb.set_trace()
        print("1. SRC_Workbook init")
        starttime = datetime.datetime.now()
        settings = QSettings("berkaygediz", "SpanRC")
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        sqlite_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'src.db')
        sqlitedb = sqlite3.connect(sqlite_file)
        sqlitecursor = sqlitedb.cursor()
        user_email = sqlitecursor.execute(
            "SELECT email FROM profile").fetchone()[0]
        mysqlserver = serverconnect()
        mysqlcursor = mysqlserver.cursor()
        print("2. SRC_Workbook - database process")
        auth = mysqlcursor.execute(
            "SELECT spanrc FROM apps WHERE spanrc = '1' AND email = %s", (user_email,))
        auth = mysqlcursor.fetchone()
        sqlitedb.close()
        mysqlserver.close()
        if auth is not None:
            self.src_thread = SRC_Threading()
            self.src_thread.update_signal.connect(
                self.SRC_updateStatistics)
            self.SRC_themePalette()
            self.undo_stack = QUndoStack(self)
            self.undo_stack.setUndoLimit(100)
            self.selected_file = None
            self.file_name = None
            self.is_saved = None
            self.default_directory = QDir().homePath()
            self.directory = self.default_directory
            self.SRC_setupDock()
            self.dock_widget.hide()
            self.status_bar = self.statusBar()
            self.src_table = QTableWidget(self)
            self.setCentralWidget(self.src_table)
            self.SRC_setupActions()
            self.SRC_setupToolbar()
            self.setPalette(self.light_theme)
            self.src_table.itemSelectionChanged.connect(
                self.src_thread.start)
            self.src_table.setCursor(Qt.CursorShape.SizeAllCursor)
            self.showMaximized()
            self.setFocus()
            QTimer.singleShot(50, self.SRC_restoreTheme)
            QTimer.singleShot(150, self.SRC_restoreState)
            if self.src_table.columnCount() == 0 and self.src_table.rowCount() == 0:
                self.src_table.setColumnCount(100)
                self.src_table.setRowCount(50)
                self.src_table.clearSpans()
                self.src_table.setItem(0, 0, QTableWidgetItem(''))

            self.SRC_updateTitle()
            self.setFocus()
            endtime = datetime.datetime.now()
            self.status_bar.showMessage(
                str((endtime - starttime).total_seconds()) + " ms", 2500)
            print("3. SRC_Workbook loaded")
        else:
            QMessageBox.warning(
                self, "Hata", "Ürünü kullanmak için satın almanız gerekmektedir!")
            sys.exit()

    def syncsettings(self):
        settings = QSettings("berkaygediz", "SpanRC")
        sqlite_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'src.db')
        sqliteConnection = sqlite3.connect(sqlite_file).cursor()
        user_email = sqliteConnection.execute(
            "SELECT email FROM profile").fetchone()[0]
        sqliteConnection.connection.commit()
        sqliteConnection.connection.close()
        try:
            mysqlserver = serverconnect()
            mysqlcursor = mysqlserver.cursor()

            mysqlcursor.execute("UPDATE user_settings SET theme = %s, language = %s WHERE email = %s AND product = %s", (
                settings.value("current_theme"), settings.value("current_language"), user_email, "SpanRC"))
            mysqlserver.commit()
            mysqlserver.close()
            QMessageBox.information(self, "SpanRC",
                                    "Settings synced successfully.")
        except:
            QMessageBox.critical(self, "SpanRC",
                                 "Error while syncing settings. Please try again later.")

    def logout(self):
        sqlite_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'src.db')
        sqliteConnection = sqlite3.connect(sqlite_file).cursor()
        sqliteConnection.execute("DROP TABLE IF EXISTS profile")
        sqliteConnection.connection.commit()
        sqliteConnection.execute("DROP TABLE IF EXISTS apps")
        sqliteConnection.connection.commit()
        sqliteConnection.execute("DROP TABLE IF EXISTS log")
        sqliteConnection.connection.commit()
        try:
            settings = QSettings("berkaygediz", "SpanRC")
            settings.clear()
            settings.sync()
        except:
            pass
        QTimer.singleShot(0, self.hide)
        QTimer.singleShot(750, SRC_ControlInfo().show)

    def SRC_setupToolbar(self):
        sqlite_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'src.db')
        sqliteConnection = sqlite3.connect(sqlite_file).cursor()
        user_email = sqliteConnection.execute(
            "SELECT email FROM profile").fetchone()[0]
        sqliteConnection.connection.commit()
        sqliteConnection.connection.close()
        mysqlserver = serverconnect()
        mysqlcursor = mysqlserver.cursor()
        mysqlcursor.execute(
            "SELECT * FROM user_settings WHERE email = %s AND product = %s", (user_email, "SpanRC"))
        user_settings = mysqlcursor.fetchone()
        mysqlserver.close()
        if user_settings is not None:
            settings.setValue("current_theme", user_settings[3])
            settings.setValue("current_language", user_settings[4])
            self.language_combobox.setCurrentText(user_settings[4])
            settings.sync()
        else:
            settings.setValue("current_theme", "light")
            settings.setValue("current_language", "English")
            settings.sync()
        self.account_toolbar = self.addToolBar("Account")
        self.SRC_toolbarLabel(self.account_toolbar, translations[settings.value(
            "current_language")]["account"] + ": ")
        self.user_name = QLabel(user_email)
        self.user_name.setStyleSheet("color: white; font-weight: bold;")
        self.account_toolbar.addWidget(self.user_name)
        self.account_toolbar.addAction(self.logoutaction)
        self.account_toolbar.addAction(self.syncsettingsaction)

    def SRC_toolbarTranslate(self):
        self.logoutaction.setText(translations[settings.value(
            "current_language")]["logout"])

    def SRC_setupActions(self):
        actionicon = qta.icon('fa5s.sign-out-alt', color=icon_theme)
        self.logoutaction = self.SRC_createAction(
            translations[settings.value("current_language")]["logout"], "", self.logout, None, actionicon)
        actionicon = qta.icon('fa5s.sync', color=icon_theme)
        self.syncsettingsaction = self.SRC_createAction(translations[settings.value(
            "current_language")]["syncsettings"], "", self.syncsettings, None, actionicon)
