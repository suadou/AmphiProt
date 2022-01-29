

# Programe developed: Sergio Suarez-Dou
# From: University of Oviedo
#
# WARNING: Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from numpy import convolve, fft, mean, matrix, square
from matplotlib import pyplot, transforms

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        mainWindow.setMinimumSize(QtCore.QSize(800, 600))
        mainWindow.setMaximumSize(QtCore.QSize(800, 600))
        mainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        mainWindow.setAcceptDrops(False)
        mainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Submit = QtWidgets.QPushButton(self.centralwidget)
        self.Submit.setGeometry(QtCore.QRect(710, 560, 85, 32))
        self.Submit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Submit.setObjectName("Submit")
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(120, 440, 42, 20))
        self.spinBox.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.spinBox.setProperty("value", 25)
        self.spinBox.setObjectName("spinBox")
        self.TextEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.TextEdit.setGeometry(QtCore.QRect(10, 90, 771, 321))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.TextEdit.sizePolicy().hasHeightForWidth())
        self.TextEdit.setSizePolicy(sizePolicy)
        self.TextEdit.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.TextEdit.setTabletTracking(False)
        self.TextEdit.setLocale(QtCore.QLocale(QtCore.QLocale.C, QtCore.QLocale.AnyCountry))
        self.TextEdit.setLineWrapColumnOrWidth(81)
        self.TextEdit.setObjectName("TextEdit")
        self.Cancel = QtWidgets.QPushButton(self.centralwidget)
        self.Cancel.setGeometry(QtCore.QRect(630, 560, 81, 32))
        self.Cancel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Cancel.setObjectName("Cancel")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 19, 58, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 251, 31))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(180, 50, 131, 31))
        self.pushButton.setObjectName("pushButton")
       	self.pushButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Check = QtWidgets.QCheckBox(self.centralwidget)
        self.Check.setGeometry(QtCore.QRect(200, 510, 40, 20))
        self.Check.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Check.setText("")
        self.Check.setObjectName("Check")
        self.Name = QtWidgets.QLineEdit(self.centralwidget)
        self.Name.setGeometry(QtCore.QRect(42, 20, 741, 21))
        self.Name.setObjectName("Name")
        self.Tableselect = QtWidgets.QComboBox(self.centralwidget)
        self.Tableselect.setGeometry(QtCore.QRect(170, 470, 111, 31))
        self.Tableselect.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Tableselect.setObjectName("Tableselect")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Tableselect.addItem("")
        self.Clear = QtWidgets.QPushButton(self.centralwidget)
        self.Clear.setGeometry(QtCore.QRect(720, 410, 61, 32))
        self.Clear.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.Clear.setObjectName("Clear")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 440, 95, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(20, 470, 151, 31))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(20, 510, 180, 20))
        self.label_5.setObjectName("label_5")
        mainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(mainWindow)
        self.Cancel.clicked.connect(mainWindow.close)
        self.Clear.clicked.connect(self.TextEdit.clear)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)
        self.pushButton.clicked.connect(self.openfile)
        self.Submit.clicked.connect(self.running)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Fourier power spectrum of hydrophobicities"))
        self.Submit.setText(_translate("mainWindow", "Submit"))
        self.Cancel.setText(_translate("mainWindow", "Cancel"))
        self.label.setText(_translate("mainWindow", "Name:"))
        self.label_2.setText(_translate("mainWindow", "Amino acid sequence or"))
        self.pushButton.setText(_translate("mainWindow", "open file (FASTA)"))
        self.Tableselect.setCurrentText(_translate("mainWindow", "Eisenberg"))
        self.Tableselect.setItemText(0, _translate("mainWindow", "Eisenberg"))
        self.Tableselect.setItemText(1, _translate("mainWindow", "Kyte&Doolittle"))
        self.Tableselect.setItemText(2, _translate("mainWindow", "Wolfenden"))
        self.Tableselect.setItemText(3, _translate("mainWindow", "Chothia"))
        self.Tableselect.setItemText(4, _translate("mainWindow", "vonHeijne-Blomberg"))
        self.Tableselect.setItemText(5, _translate("mainWindow", "Janin"))
        self.Tableselect.setItemText(6, _translate("mainWindow", "Tanford"))
        self.Tableselect.setItemText(7, _translate("mainWindow", "Wimley"))
        self.Clear.setText(_translate("mainWindow", "Clear"))
        self.label_3.setText(_translate("mainWindow", "Windows size:"))
        self.label_4.setText(_translate("mainWindow", "Hydrophobicity table:"))
        self.label_5.setText(_translate("mainWindow", "Show hydrophobicity plot:"))

    def openfile(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName()
        from Bio import SeqIO
        try:
           record = SeqIO.read(file,"fasta")
           self.TextEdit.setText(str(record.seq))
        except:
           war_read = QtWidgets.QMessageBox()
           war_read.setIcon(war_read.Warning)
           war_read.setText("Error reading selected file")
           war_read.setInformativeText("File must contain FASTA type sequence")
           war_read.setWindowTitle("Warning")
           war_read.setStandardButtons(war_read.Close)
           war_read.buttonClicked.connect(war_read.close)
           war_read.exec();

    def running(self):
        hydro_plot = "false"
        NAME = self.Name.text()
        table_selection = self.Tableselect.currentText()
        table_selection = open("./tables/"+table_selection, "r")
        table_selection = table_selection.read()
        table_selection = table_selection.split()
        i = 0
        code = "IFVLWMAGCYPTSHENQDKR"
        table = [0] * 90
        while i < len(table_selection):
            x = table_selection[i]
            x = ord(x.upper())
            table[x] = table_selection[i+1]
            i += 2 
        sequence = self.TextEdit.toPlainText()
        sequence = sequence.upper()
        seq = []
        seq[:0] = sequence
        warning = "false"
        hydro = []
        for x in range(len(seq)):
            if seq[x] not in code:
               warning = "true"
            hydro.append(float(table[ord(seq[x])]))
        if warning == "true":
           war_seq = QtWidgets.QMessageBox()
           war_seq.setIcon(war_seq.Warning)
           war_seq.setText("Error reading sequence")
           war_seq.setInformativeText("File must contain only letters corresponding to amino acid. Spaces between characters are not allowed.")
           war_seq.setWindowTitle("Warning")
           war_seq.setStandardButtons(war_seq.Close)
           war_seq.buttonClicked.connect(war_seq.close)
           war_seq.exec()
        if warning == "false":
           window = self.spinBox.value()
           km = [1/window] * window
           Mean=convolve(hydro,km,'same')
           y = (round(window/2))
           b = -(round(window/2))
           S = []
           D = []
           ZERO = [0] * window
           D = [ZERO] * (round(window/2))
           while y <= (len(hydro)-(round(window/2))-1): 
                  while b <= ((round(window/2))):
                      S.append((hydro[y+b]-Mean[y]))
                      b+=1
                  T=fft.fft(S)
                  D.append(T)
                  S = []
                  b = -(round(window/2))
                  y+=1
           Dn=D/mean(D)
           I=matrix(abs(Dn))
           I=square(I)
        if self.Check.isChecked():
           pyplot.figure()
           pyplot.subplot(121)
           pyplot.title(NAME+"\n Fourier power spectra")
           pyplot.contourf(I[0:len(hydro)+round(window/2),0:round(window/2)+1])  
           pyplot.ylabel('Amino acid position')
           pyplot.xlabel('Turns per amino acid')
           pyplot.xticks([(window+1)/3.6, round(window/2)], ["1/3.6","1/2"])
           pyplot.xlabel('Turns per amino acid')
           pyplot.grid(color='w', linestyle='-', linewidth=0.75)
           plot = pyplot.subplot(122)
           pyplot.title(NAME+"\n hydrophobicities plot")
           km = [1/15] * 15
           base = pyplot.gca().transData
           rot = transforms.Affine2D().rotate_deg(90)
           pyplot.plot(convolve(hydro,km,'same'), 'r', transform= rot + base)
           pyplot.grid(color='b', linestyle='-', linewidth=0.75)
           pyplot.ylim([1, len(I)])
           pyplot.xlabel("Hydrophobicity")
           pyplot.show()
        else:
           pyplot.figure(figsize=(4.7,7))
           pyplot.contourf(I[0:len(hydro)+round(window/2),0:round(window/2)+1]) 
           pyplot.ylabel('Amino acid position')
           pyplot.title(NAME)
           pyplot.xticks([(window+1)/3.6, round(window/2)], ["1/3.6","1/2"])
           pyplot.xlabel('Turns per amino acid')
           pyplot.grid(color='w', linestyle='-', linewidth=0.75)
           pyplot.show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())