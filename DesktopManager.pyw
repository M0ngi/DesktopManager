from PyQt4 import QtCore, QtGui
import sqlite3
import os, time
import sys

class Main(QtGui.QWidget):
    _title = 'Desktop Manager - Tools' # Change me
    _conn = sqlite3.connect('db/Tools.db') # Change me
    _cursor = _conn.cursor()
    _winsize = (500, 500)

    _font = QtGui.QFont()
    _font.setFamily("MS Shell Dlg 2")
    _font.setPointSize(11)
    _font.setBold(True)
    _font.setWeight(75)
    
    # Type: 1 ==> Steam Game || 0 ==> Normal Game
    _cursor.execute("""
    CREATE TABLE IF NOT EXISTS Files (
        id INTEGER PRIMARY KEY,
        name VARCHAR(260),
        path VARCHAR(350),
        type INTEGER(1)
    )
    """)
    _conn.commit()

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.resize(self._winsize[0], self._winsize[1])
        self.setWindowTitle(self._title)
        self.setMaximumSize(self._winsize[0], self._winsize[1])
        self.setMinimumSize(self._winsize[0], self._winsize[1])
        
        # Menu bar

        self.menuBar = QtGui.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, self._winsize[0], 21))

        self.Settings = self.menuBar.addMenu('Settings')

        self.Add = QtGui.QAction('Add', self)
        self.Settings.addAction(self.Add)
        self.Add.triggered.connect(self.SetupAddGui)

        self.AddUrl = QtGui.QAction('Add Url', self)
        self.Settings.addAction(self.AddUrl)
        self.AddUrl.triggered.connect(self.SetupAddUrlGui)

        # ===============================

        self.LoadButtons()

    def LoadButtons(self):
        self.ScrollArea = QtGui.QScrollArea(self)
        self.ScrollArea.setGeometry(QtCore.QRect(0, 21, self._winsize[0], self._winsize[1]-21))
        self.ScrollArea.setWidgetResizable(True)

        self.ScrollContents = QtGui.QWidget(self.ScrollArea)
        self.ScrollContents.setGeometry(QtCore.QRect(0, 0, 380, 247))

        self.Label1 = QtGui.QLabel('\n'+(' '*70)+'Desktop Manager', self.ScrollContents)

        self.ScrollArea.setWidget(self.ScrollContents)
        
        vlay = QtGui.QVBoxLayout()

        self._cursor.execute("SELECT * FROM Files")
        rows = self._cursor.fetchall()
        if len(rows) % 3 != 0:
            end = len(rows)+(3 - (len(rows) % 3))
        else: # Less useless steps
            end = len(rows)-1+(3 - ((len(rows)-1) % 3))

        for r in range(0, end, 3):
            hlay = QtGui.QHBoxLayout()

            if r < len(rows):
                pushButton1 = QtGui.QPushButton()
                pushButton1.setText(rows[r][1])
                pushButton1.clicked.connect(lambda state, a=rows[r][0]: self.SetupManageGui(a))
                hlay.addWidget(pushButton1)

            if r+1 < len(rows):
                pushButton2 = QtGui.QPushButton()
                pushButton2.setText(rows[r+1][1])
                pushButton2.clicked.connect(lambda state, a=rows[r+1][0]: self.SetupManageGui(a))
                hlay.addWidget(pushButton2)

            if r+2 < len(rows):
                pushButton3 = QtGui.QPushButton()
                pushButton3.setText(rows[r+2][1])
                pushButton3.clicked.connect(lambda state, a=rows[r+2][0]: self.SetupManageGui(a))
                hlay.addWidget(pushButton3)

            vlay.addLayout(hlay)

        self.ScrollContents.setLayout(vlay)
        return True

    def SetupManageGui(self, i):
        self.root = self.Window(self._title, (50, 50, 252, 372), (252, 372), (252, 372))

        self._cursor.execute("SELECT type FROM Files WHERE id=?", (i, ) )
        d = int(self._cursor.fetchone()[0])

        Run = QtGui.QPushButton('Run', self.root)
        Run.setGeometry(QtCore.QRect(90, 52, 75, 31))
        Run.clicked.connect(lambda: self.RunApp(i))

        Remove = QtGui.QPushButton('Open Folder', self.root)
        Remove.setGeometry(QtCore.QRect(90, 132, 75, 31))
        Remove.clicked.connect(lambda: self.OpenContainFolder(i))
        if d == 1:
            Remove.setDisabled(True)

        Remove = QtGui.QPushButton('Remove', self.root)
        Remove.setGeometry(QtCore.QRect(90, 212, 75, 31))
        Remove.clicked.connect(lambda: self.RemoveDb(i))
        
        Edit = QtGui.QPushButton('Edit', self.root)
        Edit.setGeometry(QtCore.QRect(90, 292, 75, 31))
        Edit.clicked.connect(lambda: self.SetupEditGui(i, d))
        
        self.root.show()
        return True

    def SetupEditGui(self, i, d):
        self._cursor.execute("SELECT path FROM Files WHERE id=?", (i, ) )
        old_path = str(self._cursor.fetchone()[0])

        if d == 0:
            os.chdir('/'.join(old_path.split('/')[:-1]))

        self._cursor.execute("SELECT name FROM Files WHERE id=?", (i, ) )
        old_name = str(self._cursor.fetchone()[0])

        if d == 1:
            self.root = self.Window(self._title, (50, 50, 543, 219), (543, 219), (543, 219))
        else:
            self.root = self.Window(self._title, (50, 50, 543, 319), (543, 319), (543, 319))
            
        #
        name_txt = QtGui.QLabel('Name', self.root)
        name_txt.setGeometry(QtCore.QRect(20, 50, 51, 21))
        name_txt.setFont(self._font)

        sep_name = QtGui.QLabel(':', self.root)
        sep_name.setGeometry(QtCore.QRect(80, 50, 21, 21))
        sep_name.setFont(self._font)

        self.name = QtGui.QLineEdit(self.root)
        self.name.setGeometry(QtCore.QRect(100, 40, 291, 31))
        self.name.setText(old_name)

        # ===

        path_txt = QtGui.QLabel('Path', self.root)
        path_txt.setGeometry(QtCore.QRect(20, 110, 51, 21))
        path_txt.setFont(self._font)

        sep_path = QtGui.QLabel(':', self.root)
        sep_path.setGeometry(QtCore.QRect(80, 110, 21, 21))
        sep_path.setFont(self._font)

        self.path = QtGui.QLineEdit(self.root)
        self.path.setGeometry(QtCore.QRect(100, 100, 421, 31))
        self.path.setText(old_path)
        if d == 0:
            self.path.setReadOnly(True)

        # ===
        if d == 0:
            sfileb = QtGui.QPushButton('Select File', self.root)
            sfileb.setGeometry(QtCore.QRect(180, 160, 81, 31))
            sfileb.clicked.connect(self.SelectFile)
            
            sfolderb = QtGui.QPushButton('Select Folder', self.root)
            sfolderb.setGeometry(QtCore.QRect(280, 160, 81, 31))
            sfolderb.clicked.connect(self.SelectFolder)

        # ===

        editb = QtGui.QPushButton('Edit', self.root)
        if d == 1:
            editb.setGeometry(QtCore.QRect(230, 150, 81, 31))
        else:
            editb.setGeometry(QtCore.QRect(230, 250, 81, 31))
        editb.clicked.connect(lambda: self.EditDb(i))
        #
        self.root.show()
        return True

    def SetupAddGui(self):
        self.root = self.Window(self._title, (50, 50, 543, 319), (543, 319), (543, 319))
        #
        name_txt = QtGui.QLabel('Name', self.root)
        name_txt.setGeometry(QtCore.QRect(20, 50, 51, 21))
        name_txt.setFont(self._font)

        sep_name = QtGui.QLabel(':', self.root)
        sep_name.setGeometry(QtCore.QRect(80, 50, 21, 21))
        sep_name.setFont(self._font)

        self.name = QtGui.QLineEdit(self.root)
        self.name.setGeometry(QtCore.QRect(100, 40, 291, 40))

        # ===

        path_txt = QtGui.QLabel('Path', self.root)
        path_txt.setGeometry(QtCore.QRect(20, 110, 51, 21))
        path_txt.setFont(self._font)

        sep_path = QtGui.QLabel(':', self.root)
        sep_path.setGeometry(QtCore.QRect(80, 110, 21, 21))
        sep_path.setFont(self._font)

        self.path = QtGui.QLineEdit(self.root)
        self.path.setGeometry(QtCore.QRect(100, 100, 421, 40))
        self.path.setReadOnly(True)

        # ===

        sfileb = QtGui.QPushButton('Select File', self.root)
        sfileb.setGeometry(QtCore.QRect(180, 160, 81, 31))
        sfileb.clicked.connect(self.SelectFile)
        
        sfolderb = QtGui.QPushButton('Select Folder', self.root)
        sfolderb.setGeometry(QtCore.QRect(280, 160, 81, 31))
        sfolderb.clicked.connect(self.SelectFolder)

        # ===

        addb = QtGui.QPushButton('Add', self.root)
        addb.setGeometry(QtCore.QRect(230, 250, 81, 31))
        addb.clicked.connect(lambda: self.InsertIntoDb(0))
        #
        self.root.show()
        return True

    def SetupAddUrlGui(self):
        self.root = self.Window(self._title, (50, 50, 543, 219), (543, 219), (543, 219))

        #
        name_txt = QtGui.QLabel('Name', self.root)
        name_txt.setGeometry(QtCore.QRect(20, 50, 51, 21))
        name_txt.setFont(self._font)

        sep_name = QtGui.QLabel(':', self.root)
        sep_name.setGeometry(QtCore.QRect(80, 50, 21, 21))
        sep_name.setFont(self._font)

        self.name = QtGui.QLineEdit(self.root)
        self.name.setGeometry(QtCore.QRect(100, 40, 291, 40))

        # ===

        path_txt = QtGui.QLabel('Url', self.root)
        path_txt.setGeometry(QtCore.QRect(20, 110, 51, 21))
        path_txt.setFont(self._font)

        sep_path = QtGui.QLabel(':', self.root)
        sep_path.setGeometry(QtCore.QRect(80, 110, 21, 21))
        sep_path.setFont(self._font)

        self.path = QtGui.QLineEdit(self.root)
        self.path.setGeometry(QtCore.QRect(100, 100, 421, 40))
        self.path.setReadOnly(False)

        # ===

        addb = QtGui.QPushButton('Add', self.root)
        addb.setGeometry(QtCore.QRect(230, 160, 81, 31))
        addb.clicked.connect(lambda: self.InsertIntoDb(1))
        #

        self.root.show()
        return True

    def EditDb(self, i):
        path = str(self.path.text())
        name = str(self.name.text())

        if len(path.replace(' ', '')) == 0:
            return False
        if len(name.replace(' ', '')) == 0:
            return False
        
        self._cursor.execute("UPDATE Files SET name=?, path=? WHERE id=?",
                             (name, path, i))
        self._conn.commit()
        self.root.hide()
        return True

    def RemoveDb(self, i):
        self._cursor.execute("DELETE FROM Files WHERE id=?",
                             (i, ))

        self._conn.commit()
        self.root.hide()
        return True

    def RunApp(self, i):
        self._cursor.execute("SELECT path, type FROM Files WHERE id=?", (i, ) )
        d = self._cursor.fetchone()
        path = str(d[0])
        t = int(d[1])

        if t == 0:
            os.chdir('/'.join(path.split('/')[:-1]))

        os.popen('start "" "'+path+'"')

        self.root.hide()
        return True

    def OpenContainFolder(self, i):
        self._cursor.execute("SELECT path FROM Files WHERE id=?", (i, ) )
        path = str(self._cursor.fetchone()[0])
        path = '/'.join(path.split('/')[:-1])+"/"

        os.popen('start "" "'+path+'"')
        
        self.root.hide()
        return True

    def InsertIntoDb(self, t):
        path = str(self.path.text())
        name = str(self.name.text())
        
        if len(path.replace(' ', '')) == 0:
            return False
        if len(name.replace(' ', '')) == 0:
            return False

        self._cursor.execute("""INSERT INTO Files VALUES(
            null,
            ?,
            ?,
            ?)
        """, (name, path, t))
        self._conn.commit() # Apply changes
        self.root.hide()
        return True

    def Window(self, title, geo, maxsize, minsize):
        win = QtGui.QWidget()
        win.setGeometry(geo[0], geo[1], geo[2], geo[3])
        win.setWindowTitle(title)
        win.setMaximumSize(maxsize[0], maxsize[1])
        win.setMinimumSize(minsize[0], minsize[1])
        return win

    def SelectFile(self):
        self.path.setReadOnly(False)
        self.path.setText(QtGui.QFileDialog.getOpenFileName())
        self.path.setReadOnly(True)
        return True

    def SelectFolder(self, QLineObj):
        self.path.setReadOnly(False)
        self.path.setText(QtGui.QFileDialog.getExistingDirectory())
        self.path.setReadOnly(True)
        return True

# ================================== End Class Main ==============================================

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Desktop Manager - Tools') # Change me
    app.setWindowIcon(QtGui.QIcon('db/Tools.png')) # Change me
    
    main = Main()
    main.show()

    sys.exit(app.exec_())
