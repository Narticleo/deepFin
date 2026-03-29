# 圖片顯示
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import shutil
bounded_pics = './temp/predict/crops/fin'
predict_folder = './temp/predict'
path_show_on_screen = './temp/predict'

class ImageViewer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.zoom_factor = 1.0
        self.setup_shortcuts()

    def initUI(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.index_label = QtWidgets.QLabel(self)
        self.index_label.setAlignment(QtCore.Qt.AlignCenter)

        self.saved_label = QtWidgets.QLabel(self)
        self.saved_label.setAlignment(QtCore.Qt.AlignCenter)

        self.pre_button = QtWidgets.QPushButton('上一張', self)
        self.pre_button.clicked.connect(self.preImage)

        self.next_button = QtWidgets.QPushButton('下一張', self)
        self.next_button.clicked.connect(self.nextImage)

        self.OK_button = QtWidgets.QPushButton('保留', self)
        self.OK_button.clicked.connect(self.OKImage)
        self.NO_button = QtWidgets.QPushButton('放棄', self)
        self.NO_button.clicked.connect(self.NOImage)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.index_label)
        layout.addWidget(self.saved_label)
        layout.addWidget(self.pre_button)
        layout.addWidget(self.next_button)
        OKNO_layout = QtWidgets.QHBoxLayout()
        OKNO_layout.addWidget(self.OK_button)
        OKNO_layout.addWidget(self.NO_button)
        layout.addLayout(OKNO_layout)
        self.setLayout(layout)

        self.image_dir = None
        self.image_paths = []
        self.current_index = 0
        self.image_is_OK = []

    def loadImagePaths(self, folder_path):
        # output_dir = os.path.join(folder_path, "temp", "predict")
        output_dir = folder_path

        print(self.image_dir)
        self.image_paths = [os.path.join(output_dir, filename) for filename in os.listdir(output_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg'))]
        self.OKimage_paths = [os.path.join(self.image_dir, filename) for filename in os.listdir(self.image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg'))]
        self.image_saved = [0]*len(self.image_paths)
        self.image_is_OK = [0]*len(self.image_paths)
        if self.image_paths:
            self.current_index = 0
            self.showImage()

    def preImage(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            #print(f"image_path: {self.image_paths[self.current_index]}")
            self.showImage()

    def nextImage(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            #print(f"image_path: {self.image_paths[self.current_index]}")
            self.showImage()

    def showImage(self):
        image_path = self.image_paths[self.current_index]
        pixmap = QtGui.QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(pixmap.size() * self.zoom_factor, QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(scaled_pixmap)
        self.index_label.setText(f"Image {self.current_index + 1}/{len(self.image_paths)}")
        if self.image_is_OK[self.current_index] == 1:
            self.saved_label.setText("已確認")
        else:
            self.saved_label.setText("未確認")

    # Ctrl++ 跟 Ctrl+-圖片放大縮小
    def setup_shortcuts(self):
        zoom_in_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.ZoomIn), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)

        zoom_out_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.ZoomOut), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)

    def zoom_in(self):
        self.zoom_factor *= 1.25
        self.showImage()

    def zoom_out(self):
        self.zoom_factor /= 1.25
        self.showImage()

    #可以使用滑鼠滾輪
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    
    def bounded_success_or_fail(self,pic_path, success):
        if not success:
            return
        pic_name = os.path.basename(pic_path)
        bd_path = os.path.join(bounded_pics, pic_name)
        shutil.copyfile(bd_path, pic_path)

    def OKImage(self):
        if self.image_dir:
            self.bounded_success_or_fail(self.OKimage_paths[self.current_index],True)
            self.image_is_OK[self.current_index] = 1
            self.showImage()

            
    def NOImage(self):
        if self.image_dir:
            self.bounded_success_or_fail(self.OKimage_paths[self.current_index],False)
            self.image_is_OK[self.current_index] = 1
            self.showImage()