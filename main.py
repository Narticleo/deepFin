from ultralytics import YOLO
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from image_viewer import ImageViewer
from identifier import identifier
import sys
import os
import shutil

predict_folder = './temp/predict'

#YOLO 背景執行
class YOLOThread(QtCore.QThread):
    finished = QtCore.pyqtSignal()

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        model = YOLO("model/best.pt")
        model.predict(source=self.folder_path, mode="predict", project="temp", name='predict', save=True, imgsz=(512, 512), conf=0.51, device="cpu", save_crop=True)
        self.finished.emit()

# 主視窗
class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeepFin')
        self.setGeometry(100, 100, 300, 150)
        self.setWindowIcon(QIcon('./deepfin_icon.png'))  # 添加這行設置圖示

        self.folder_label = QtWidgets.QLabel('選擇資料夾:')
        self.folder_edit = QtWidgets.QLineEdit()
        self.folder_button = QtWidgets.QPushButton('瀏覽')
        self.folder_button.clicked.connect(self.openFolder)

        self.run_button = QtWidgets.QPushButton('執行YOLO')
        self.run_button.clicked.connect(self.runYOLO)

        self.recognizer_button = QtWidgets.QPushButton('分類器')
        self.recognizer_button.clicked.connect(self.runrecognizer)

        style = '''
            QProgressBar {
                border-radius: 5px;
                text-align:center;
                height: 10px;
                width:200px;
            }
            QProgressBar::chunk {
                background: #09c;
                width:1px;
            }
        '''
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(style)
        
        self.image_button = QtWidgets.QPushButton('查看照片')
        self.image_button.clicked.connect(self.runViewer)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.folder_label)
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)
        layout.addWidget(self.image_button)
        layout.addWidget(self.run_button)
        layout.addWidget(self.recognizer_button)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def openFolder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder_path:
            self.folder_edit.setText(folder_path)
           

    # YOLO
    def runYOLO(self):
        folder_path = self.folder_edit.text()
        if folder_path:
            if os.path.exists(predict_folder):
                shutil.rmtree(predict_folder)
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setValue(50)
            self.yolo_thread = YOLOThread(folder_path)
            self.yolo_thread.finished.connect(self.YOLOFinished)
            self.yolo_thread.start()

    def YOLOFinished(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.viewer = ImageViewer()
        self.viewer.image_dir = self.folder_edit.text()
        self.viewer.loadImagePaths(predict_folder)
        self.viewer.show()


    def runViewer(self):
        folder_path = self.folder_edit.text()
        print(folder_path)
        if folder_path:
            self.viewer = ImageViewer()
            self.viewer.image_dir = self.folder_edit.text()
            self.viewer.loadImagePaths(folder_path)
            self.viewer.show()

    def runrecognizer(self):
        self.reco = identifier()
        self.reco.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec_())