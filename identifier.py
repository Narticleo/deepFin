from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from image_viewer import ImageViewer
from recognizer import Recognizer
import function
import os
import random
import cv2

recognizer = Recognizer("model/model.pth")

class identifier(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeepFin')
        self.setWindowIcon(QIcon('./deepfin_icon.png'))  
        self.resize(1200, 920)

        self.mode = True
        #主圖片
        self.main_image_dir = None
        self.main_image_path = []
        self.main_image_index = 0
        self.main_image = QtWidgets.QGraphicsView(self)
        self.main_image.setGeometry(QtCore.QRect(70, 30, 371, 311))
        self.main_scene = QtWidgets.QGraphicsScene(self)
        self.main_scene.setSceneRect(0, 0, 361, 301)

        #主操作鍵
        self.folder_label = QtWidgets.QLabel('選擇資料夾:',self)
        self.folder_edit = QtWidgets.QLineEdit(self)
        self.folder_button = QtWidgets.QPushButton('瀏覽',self)
        self.folder_button.clicked.connect(self.openFolder)
        self.run_button = QtWidgets.QPushButton('找top10',self)
        self.status_label = QtWidgets.QLabel(self)
        self.status_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.run_button.clicked.connect(lambda: self.runtop10model())
        self.remove_button = QtWidgets.QPushButton('刪除資料夾',self)
        self.remove_button.clicked.connect(lambda: self.remove_dir())
        self.new_id_label = QtWidgets.QLabel('新ID名稱:',self)
        self.new_id_edit = QtWidgets.QLineEdit(self)
        self.folder_label.setGeometry(QtCore.QRect(100, 430, 321, 28))
        self.folder_edit.setGeometry(QtCore.QRect(100, 470, 221, 28))
        self.folder_button.setGeometry(QtCore.QRect(325, 470, 96, 28))
        self.run_button.setGeometry(QtCore.QRect(100, 510, 321, 28))
        self.remove_button.setGeometry(QtCore.QRect(100, 550, 321, 28))
        self.status_label.setGeometry(QtCore.QRect(100, 390, 321, 28))
        self.new_id_label.setGeometry(QtCore.QRect(100, 630, 91, 28))
        self.new_id_edit.setGeometry(QtCore.QRect(171, 630, 250, 28))

        self.button = QtWidgets.QPushButton('重新計算',self)
        self.button.clicked.connect(lambda: self.recal())
        self.button.setGeometry(QtCore.QRect(100, 590, 321, 28))
        self.boolbtn = QtWidgets.QPushButton('原始',self)
        self.boolbtn.clicked.connect(lambda: self.change_mode())
        self.boolbtn.setGeometry(QtCore.QRect(470, 300, 111, 31))

        self.main_index = QtWidgets.QLabel(self)
        self.main_index.setAlignment(QtCore.Qt.AlignCenter)
        self.main_index.setGeometry(QtCore.QRect(470, 60, 111, 31))
        self.main_pre_btn = QtWidgets.QPushButton('上一張',self)
        self.main_pre_btn.setGeometry(QtCore.QRect(470, 120, 111, 31))
        self.main_pre_btn.clicked.connect(lambda: self.preImage())
        self.main_next_btn = QtWidgets.QPushButton('下一張',self)
        self.main_next_btn.setGeometry(QtCore.QRect(470, 180, 111, 31))
        self.main_next_btn.clicked.connect(lambda: self.nextImage())
        self.main_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.main_viewer_btn.setGeometry(QtCore.QRect(470, 240, 111, 31))
        self.main_viewer_btn.clicked.connect(lambda: self.runViewer())
        self.new_button = QtWidgets.QPushButton('新增',self)
        self.new_button.setGeometry(QtCore.QRect(100, 670, 321, 28))
        self.new_button.clicked.connect(lambda: self.new_id())

        #top 10照片
        #top1
        self.top1_image_dir = None
        self.top1_image_path = []
        self.top1_image_index = 0
        self.top1_image =  QtWidgets.QGraphicsView(self)
        self.top1_image.setGeometry(QtCore.QRect(630, 20, 161, 131))
        self.top1_scene = QtWidgets.QGraphicsScene()
        self.top1_scene.setSceneRect(0, 0, 151, 121)
        self.top1_scene.clear()
        self.top1_image.setScene(self.top1_scene)
        self.top1label = QtWidgets.QLabel('top1', self)
        self.top1label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top1label.setAlignment(QtCore.Qt.AlignCenter)
        self.top1label.setGeometry(QtCore.QRect(800, 20, 93, 28))
        self.top1_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top1_random_btn.setGeometry(QtCore.QRect(800, 50, 93, 28))
        self.top1_random_btn.clicked.connect(lambda: self.change_top_image(self.top1_image_path, self.top1_scene, self.top1_image))
        self.top1_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top1_viewer_btn.setGeometry(QtCore.QRect(800, 80, 93, 28))
        self.top1_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top1_image_dir))
        self.top1_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top1_save_btn.setGeometry(QtCore.QRect(800, 110, 93, 28))
        self.top1_save_btn.clicked.connect(lambda: self.save_top_image(self.top1_image_dir,self.main_image_path))
        self.top1th = QtWidgets.QLabel(self)
        self.top1th.setAlignment(QtCore.Qt.AlignCenter)
        self.top1th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top1th.setGeometry(QtCore.QRect(630, 160, 161, 28))

        #top2
        self.top2_image_dir = None
        self.top2_image_path = []
        self.top2_image_index = 0
        self.top2_image =  QtWidgets.QGraphicsView(self)
        self.top2_image.setGeometry(QtCore.QRect(630, 200, 161, 131))
        self.top2_scene = QtWidgets.QGraphicsScene()
        self.top2_scene.setSceneRect(0, 0, 151, 121)
        self.top2_scene.clear()
        self.top2_image.setScene(self.top2_scene)
        self.top2label = QtWidgets.QLabel('top2', self)
        self.top2label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top2label.setAlignment(QtCore.Qt.AlignCenter)
        self.top2label.setGeometry(QtCore.QRect(800, 200, 93, 28))
        self.top2_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top2_random_btn.setGeometry(QtCore.QRect(800, 230, 93, 28))
        self.top2_random_btn.clicked.connect(lambda: self.change_top_image(self.top2_image_path, self.top2_scene, self.top2_image))
        self.top2_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top2_viewer_btn.setGeometry(QtCore.QRect(800, 260, 93, 28))
        self.top2_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top2_image_dir))
        self.top2_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top2_save_btn.setGeometry(QtCore.QRect(800, 290, 93, 28))
        self.top2_save_btn.clicked.connect(lambda: self.save_top_image(self.top2_image_dir,self.main_image_path))
        self.top2th = QtWidgets.QLabel(self)
        self.top2th.setAlignment(QtCore.Qt.AlignCenter)
        self.top2th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top2th.setGeometry(QtCore.QRect(630, 340, 161, 28))

        #top3
        self.top3_image_dir = None
        self.top3_image_path = []
        self.top3_image_index = 0
        self.top3_image =  QtWidgets.QGraphicsView(self)
        self.top3_image.setGeometry(QtCore.QRect(630, 380, 161, 131))
        self.top3_scene = QtWidgets.QGraphicsScene()
        self.top3_scene.setSceneRect(0, 0, 151, 121)
        self.top3_scene.clear()
        self.top3_image.setScene(self.top3_scene)
        self.top3label = QtWidgets.QLabel('top3', self)
        self.top3label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top3label.setAlignment(QtCore.Qt.AlignCenter)
        self.top3label.setGeometry(QtCore.QRect(800, 380, 93, 28))
        self.top3_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top3_random_btn.setGeometry(QtCore.QRect(800, 410, 93, 28))
        self.top3_random_btn.clicked.connect(lambda: self.change_top_image(self.top3_image_path, self.top3_scene, self.top3_image))
        self.top3_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top3_viewer_btn.setGeometry(QtCore.QRect(800, 440, 93, 28))
        self.top3_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top3_image_dir))
        self.top3_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top3_save_btn.setGeometry(QtCore.QRect(800, 470, 93, 28))
        self.top3_save_btn.clicked.connect(lambda: self.save_top_image(self.top3_image_dir,self.main_image_path))
        self.top3th = QtWidgets.QLabel(self)
        self.top3th.setAlignment(QtCore.Qt.AlignCenter)
        self.top3th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top3th.setGeometry(QtCore.QRect(630, 520, 161, 28))

        #top4
        self.top4_image_dir = None
        self.top4_image_path = []
        self.top4_image_index = 0
        self.top4_image =  QtWidgets.QGraphicsView(self)
        self.top4_image.setGeometry(QtCore.QRect(630, 560, 161, 131))
        self.top4_scene = QtWidgets.QGraphicsScene()
        self.top4_scene.setSceneRect(0, 0, 151, 121)
        self.top4_scene.clear()
        self.top4_image.setScene(self.top4_scene)
        self.top4label = QtWidgets.QLabel('top4', self)
        self.top4label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top4label.setAlignment(QtCore.Qt.AlignCenter)
        self.top4label.setGeometry(QtCore.QRect(800, 560, 93, 28))
        self.top4_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top4_random_btn.setGeometry(QtCore.QRect(800, 590, 93, 28))
        self.top4_random_btn.clicked.connect(lambda: self.change_top_image(self.top4_image_path, self.top4_scene, self.top4_image))
        self.top4_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top4_viewer_btn.setGeometry(QtCore.QRect(800, 620, 93, 28))
        self.top4_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top4_image_dir))
        self.top4_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top4_save_btn.setGeometry(QtCore.QRect(800, 650, 93, 28))
        self.top4_save_btn.clicked.connect(lambda: self.save_top_image(self.top4_image_dir,self.main_image_path))
        self.top4th = QtWidgets.QLabel(self)
        self.top4th.setAlignment(QtCore.Qt.AlignCenter)
        self.top4th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top4th.setGeometry(QtCore.QRect(630, 700, 161, 28))

        #top5
        self.top5_image_dir = None
        self.top5_image_path = []
        self.top5_image_index = 0
        self.top5_image =  QtWidgets.QGraphicsView(self)
        self.top5_image.setGeometry(QtCore.QRect(630, 740, 161, 131))
        self.top5_scene = QtWidgets.QGraphicsScene()
        self.top5_scene.setSceneRect(0, 0, 151, 121)
        self.top5_scene.clear()
        self.top5_image.setScene(self.top5_scene)
        self.top5label = QtWidgets.QLabel('top5', self)
        self.top5label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top5label.setAlignment(QtCore.Qt.AlignCenter)
        self.top5label.setGeometry(QtCore.QRect(800, 740, 93, 28))
        self.top5_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top5_random_btn.setGeometry(QtCore.QRect(800, 770, 93, 28))
        self.top5_random_btn.clicked.connect(lambda: self.change_top_image(self.top5_image_path, self.top5_scene, self.top5_image))
        self.top5_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top5_viewer_btn.setGeometry(QtCore.QRect(800, 800, 93, 28))
        self.top5_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top5_image_dir))
        self.top5_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top5_save_btn.setGeometry(QtCore.QRect(800, 830, 93, 28))
        self.top5_save_btn.clicked.connect(lambda: self.save_top_image(self.top5_image_dir,self.main_image_path))
        self.top5th = QtWidgets.QLabel(self)
        self.top5th.setAlignment(QtCore.Qt.AlignCenter)
        self.top5th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top5th.setGeometry(QtCore.QRect(630, 880, 161, 28))

        #top6
        self.top6_image_dir = None
        self.top6_image_path = []
        self.top6_image_index = 0
        self.top6_image =  QtWidgets.QGraphicsView(self)
        self.top6_image.setGeometry(QtCore.QRect(920, 20, 161, 131))
        self.top6_scene = QtWidgets.QGraphicsScene()
        self.top6_scene.setSceneRect(0, 0, 151, 121)
        self.top6_scene.clear()
        self.top6_image.setScene(self.top6_scene)
        self.top6label = QtWidgets.QLabel('top6', self)
        self.top6label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top6label.setAlignment(QtCore.Qt.AlignCenter)
        self.top6label.setGeometry(QtCore.QRect(1090, 20, 93, 28))
        self.top6_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top6_random_btn.setGeometry(QtCore.QRect(1090, 50, 93, 28))
        self.top6_random_btn.clicked.connect(lambda: self.change_top_image(self.top6_image_path, self.top6_scene, self.top6_image))
        self.top6_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top6_viewer_btn.setGeometry(QtCore.QRect(1090, 80, 93, 28))
        self.top6_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top6_image_dir))
        self.top6_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top6_save_btn.setGeometry(QtCore.QRect(1090, 110, 93, 28))
        self.top6_save_btn.clicked.connect(lambda: self.save_top_image(self.top6_image_dir,self.main_image_path))
        self.top6th = QtWidgets.QLabel(self)
        self.top6th.setAlignment(QtCore.Qt.AlignCenter)
        self.top6th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top6th.setGeometry(QtCore.QRect(920, 160, 161, 28))

        #top7
        self.top7_image_dir = None
        self.top7_image_path = []
        self.top7_image_index = 0
        self.top7_image =  QtWidgets.QGraphicsView(self)
        self.top7_image.setGeometry(QtCore.QRect(920, 200, 161, 131))
        self.top7_scene = QtWidgets.QGraphicsScene()
        self.top7_scene.setSceneRect(0, 0, 151, 121)
        self.top7_scene.clear()
        self.top7_image.setScene(self.top7_scene)
        self.top7label = QtWidgets.QLabel('top7', self)
        self.top7label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top7label.setAlignment(QtCore.Qt.AlignCenter)
        self.top7label.setGeometry(QtCore.QRect(1090, 200, 93, 28))
        self.top7_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top7_random_btn.setGeometry(QtCore.QRect(1090, 230, 93, 28))
        self.top7_random_btn.clicked.connect(lambda: self.change_top_image(self.top7_image_path, self.top7_scene, self.top7_image))
        self.top7_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top7_viewer_btn.setGeometry(QtCore.QRect(1090, 260, 93, 28))
        self.top7_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top7_image_dir))
        self.top7_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top7_save_btn.setGeometry(QtCore.QRect(1090, 290, 93, 28))
        self.top7_save_btn.clicked.connect(lambda: self.save_top_image(self.top7_image_dir,self.main_image_path))
        self.top7th = QtWidgets.QLabel(self)
        self.top7th.setAlignment(QtCore.Qt.AlignCenter)
        self.top7th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top7th.setGeometry(QtCore.QRect(920, 340, 161, 28))

        #top8
        self.top8_image_dir = None
        self.top8_image_path = []
        self.top8_image_index = 0
        self.top8_image =  QtWidgets.QGraphicsView(self)
        self.top8_image.setGeometry(QtCore.QRect(920, 380, 161, 131))
        self.top8_scene = QtWidgets.QGraphicsScene()
        self.top8_scene.setSceneRect(0, 0, 151, 121)
        self.top8_scene.clear()
        self.top8_image.setScene(self.top8_scene)
        self.top8label = QtWidgets.QLabel('top8', self)
        self.top8label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top8label.setAlignment(QtCore.Qt.AlignCenter)
        self.top8label.setGeometry(QtCore.QRect(1090, 380, 93, 28))
        self.top8_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top8_random_btn.setGeometry(QtCore.QRect(1090, 410, 93, 28))
        self.top8_random_btn.clicked.connect(lambda: self.change_top_image(self.top8_image_path, self.top8_scene, self.top8_image))
        self.top8_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top8_viewer_btn.setGeometry(QtCore.QRect(1090, 440, 93, 28))
        self.top8_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top8_image_dir))
        self.top8_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top8_save_btn.setGeometry(QtCore.QRect(1090, 470, 93, 28))
        self.top8_save_btn.clicked.connect(lambda: self.save_top_image(self.top8_image_dir,self.main_image_path))
        self.top8th = QtWidgets.QLabel(self)
        self.top8th.setAlignment(QtCore.Qt.AlignCenter)
        self.top8th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top8th.setGeometry(QtCore.QRect(920, 520, 161, 28))

        #top9
        self.top9_image_dir = None
        self.top9_image_path = []
        self.top9_image_index = 0
        self.top9_image =  QtWidgets.QGraphicsView(self)
        self.top9_image.setGeometry(QtCore.QRect(920, 560, 161, 131))
        self.top9_scene = QtWidgets.QGraphicsScene()
        self.top9_scene.setSceneRect(0, 0, 151, 121)
        self.top9_scene.clear()
        self.top9_image.setScene(self.top9_scene)
        self.top9label = QtWidgets.QLabel('top9', self)
        self.top9label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top9label.setAlignment(QtCore.Qt.AlignCenter)
        self.top9label.setGeometry(QtCore.QRect(1090, 560, 93, 28))
        self.top9_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top9_random_btn.setGeometry(QtCore.QRect(1090, 590, 93, 28))
        self.top9_random_btn.clicked.connect(lambda: self.change_top_image(self.top9_image_path, self.top9_scene, self.top9_image))
        self.top9_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top9_viewer_btn.setGeometry(QtCore.QRect(1090, 620, 93, 28))
        self.top9_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top9_image_dir))
        self.top9_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top9_save_btn.setGeometry(QtCore.QRect(1090, 650, 93, 28))
        self.top9_save_btn.clicked.connect(lambda: self.save_top_image(self.top9_image_dir,self.main_image_path))
        self.top9th = QtWidgets.QLabel(self)
        self.top9th.setAlignment(QtCore.Qt.AlignCenter)
        self.top9th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top9th.setGeometry(QtCore.QRect(920, 700, 161, 28))

        #top10
        self.top10_image_dir = None
        self.top10_image_path = []
        self.top10_image_index = 0
        self.top10_image =  QtWidgets.QGraphicsView(self)
        self.top10_image.setGeometry(QtCore.QRect(920, 740, 161, 131))
        self.top10_scene = QtWidgets.QGraphicsScene()
        self.top10_scene.setSceneRect(0, 0, 151, 121)
        self.top10_scene.clear()
        self.top10_image.setScene(self.top10_scene)
        self.top10label = QtWidgets.QLabel('top10', self)
        self.top10label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top10label.setAlignment(QtCore.Qt.AlignCenter)
        self.top10label.setGeometry(QtCore.QRect(1090, 740, 93, 28))
        self.top10_random_btn = QtWidgets.QPushButton('換一張',self)
        self.top10_random_btn.setGeometry(QtCore.QRect(1090, 770, 93, 28))
        self.top10_random_btn.clicked.connect(lambda: self.change_top_image(self.top10_image_path, self.top10_scene, self.top10_image))
        self.top10_viewer_btn = QtWidgets.QPushButton('放大',self)
        self.top10_viewer_btn.setGeometry(QtCore.QRect(1090, 800, 93, 28))
        self.top10_viewer_btn.clicked.connect(lambda: self.runtop10Viewer(self.top10_image_dir))
        self.top10_save_btn = QtWidgets.QPushButton('儲存',self)
        self.top10_save_btn.setGeometry(QtCore.QRect(1090, 830, 93, 28))
        self.top10_save_btn.clicked.connect(lambda: self.save_top_image(self.top10_image_dir,self.main_image_path))
        self.top10th = QtWidgets.QLabel(self)
        self.top10th.setAlignment(QtCore.Qt.AlignCenter)
        self.top10th.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.top10th.setGeometry(QtCore.QRect(920, 880, 161, 28))

    
    def change_mode(self):
        # print(self.top1_image_dir)
        # print(os.path.exists(self.main_image_dir))
        if os.path.exists(self.main_image_dir) and self.top1_image_dir:
            if self.mode == True:
                self.boolbtn.setText('對比')
            else:
                self.boolbtn.setText('原始')
            self.mode = not self.mode
            self.main_scene.clear()
            self.main_image.setScene(self.main_scene)
            self.top1_scene.clear()
            self.top1_image.setScene(self.top1_scene)
            self.top2_scene.clear()
            self.top2_image.setScene(self.top2_scene)
            self.top3_scene.clear()
            self.top3_image.setScene(self.top3_scene)
            self.top4_scene.clear() 
            self.top4_image.setScene(self.top4_scene)
            self.top5_scene.clear()
            self.top5_image.setScene(self.top5_scene)
            self.top6_scene.clear()
            self.top6_image.setScene(self.top6_scene)
            self.top7_scene.clear()
            self.top7_image.setScene(self.top7_scene)
            self.top8_scene.clear()
            self.top8_image.setScene(self.top8_scene)
            self.top9_scene.clear()
            self.top9_image.setScene(self.top9_scene)
            self.top10_scene.clear()
            self.top10_image.setScene(self.top10_scene)

            if self.mode:

                self.img = QtGui.QPixmap(self.main_image_path[self.main_image_index])
                self.img = self.img.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.img)
                self.main_image.setScene(self.main_scene)

                #top1
                self.top1img = QtGui.QPixmap(self.top1_image_path[self.top1_image_index])
                self.top1img = self.top1img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top1_scene.addPixmap(self.top1img)
                self.top1_image.setScene(self.top1_scene)

                #top2
                self.top2img = QtGui.QPixmap(self.top2_image_path[self.top2_image_index])
                self.top2img = self.top2img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top2_scene.addPixmap(self.top2img)                   
                self.top2_image.setScene(self.top2_scene)

                #top3
                self.top3img = QtGui.QPixmap(self.top3_image_path[self.top3_image_index])
                self.top3img = self.top3img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top3_scene.addPixmap(self.top3img)
                self.top3_image.setScene(self.top3_scene)

                #top4
                self.top4img = QtGui.QPixmap(self.top4_image_path[self.top4_image_index])
                self.top4img = self.top4img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top4_scene.addPixmap(self.top4img)                   
                self.top4_image.setScene(self.top4_scene)

                #top5
                self.top5img = QtGui.QPixmap(self.top5_image_path[self.top5_image_index])
                self.top5img = self.top5img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top5_scene.addPixmap(self.top5img)                   
                self.top5_image.setScene(self.top5_scene)

                #top6
                self.top6img = QtGui.QPixmap(self.top6_image_path[self.top6_image_index])
                self.top6img = self.top6img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top6_scene.addPixmap(self.top6img)
                self.top6_image.setScene(self.top6_scene)

                #top7
                self.top7img = QtGui.QPixmap(self.top7_image_path[self.top7_image_index])
                self.top7img = self.top7img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top7_scene.addPixmap(self.top7img)                   
                self.top7_image.setScene(self.top7_scene)

                #top8
                self.top8img = QtGui.QPixmap(self.top8_image_path[self.top8_image_index])
                self.top8img = self.top8img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top8_scene.addPixmap(self.top8img)
                self.top8_image.setScene(self.top8_scene)

                #top9
                self.top9img = QtGui.QPixmap(self.top9_image_path[self.top9_image_index])
                self.top9img = self.top9img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top9_scene.addPixmap(self.top9img)                   
                self.top9_image.setScene(self.top9_scene)

                #top10
                self.top10img = QtGui.QPixmap(self.top10_image_path[self.top10_image_index])
                self.top10img = self.top10img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top10_scene.addPixmap(self.top10img)                   
                self.top10_image.setScene(self.top10_scene)
            else:
                self.clahe = self.apply_clahe(self.main_image_path[self.main_image_index])
                self.clahe = self.clahe.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.clahe)
                self.main_image.setScene(self.main_scene)

                self.top1clahe = self.apply_clahe(self.top1_image_path[self.top1_image_index])
                self.top1clahe = self.top1clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top1_scene.addPixmap(self.top1clahe)
                self.top1_image.setScene(self.top1_scene)

                self.top2clahe = self.apply_clahe(self.top2_image_path[self.top2_image_index])
                self.top2clahe = self.top2clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top2_scene.addPixmap(self.top2clahe)
                self.top2_image.setScene(self.top2_scene)

                self.top3clahe = self.apply_clahe(self.top3_image_path[self.top3_image_index])
                self.top3clahe = self.top3clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top3_scene.addPixmap(self.top3clahe)
                self.top3_image.setScene(self.top3_scene)

                self.top4clahe = self.apply_clahe(self.top4_image_path[self.top4_image_index])
                self.top4clahe = self.top4clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top4_scene.addPixmap(self.top4clahe)
                self.top4_image.setScene(self.top4_scene)

                self.top5clahe = self.apply_clahe(self.top5_image_path[self.top5_image_index])
                self.top5clahe = self.top5clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top5_scene.addPixmap(self.top5clahe)
                self.top5_image.setScene(self.top5_scene)

                self.top6clahe = self.apply_clahe(self.top6_image_path[self.top6_image_index])
                self.top6clahe = self.top6clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top6_scene.addPixmap(self.top6clahe)
                self.top6_image.setScene(self.top6_scene)

                self.top7clahe = self.apply_clahe(self.top7_image_path[self.top7_image_index])
                self.top7clahe = self.top7clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top7_scene.addPixmap(self.top7clahe)
                self.top7_image.setScene(self.top7_scene)

                self.top8clahe = self.apply_clahe(self.top8_image_path[self.top8_image_index])
                self.top8clahe = self.top8clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top8_scene.addPixmap(self.top8clahe)
                self.top8_image.setScene(self.top8_scene)

                self.top9clahe = self.apply_clahe(self.top9_image_path[self.top9_image_index])
                self.top9clahe = self.top9clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top9_scene.addPixmap(self.top9clahe)
                self.top9_image.setScene(self.top9_scene)
            
                self.top10clahe = self.apply_clahe(self.top10_image_path[self.top10_image_index])
                self.top10clahe = self.top10clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top10_scene.addPixmap(self.top10clahe)
                self.top10_image.setScene(self.top10_scene)
        
    def change_top_image(self,image_path,top_scene,topimage):
        if image_path:
            top_scene.clear()
            topimage.setScene(top_scene)
            index = random.randint(0,len(image_path)-1)
            if top_scene == self.top1_scene:
                self.top1_image_index = index
            elif top_scene == self.top2_scene:
                self.top2_image_index = index
            elif top_scene == self.top3_scene:
                self.top3_image_index = index
            elif top_scene == self.top4_scene:
                self.top4_image_index = index
            elif top_scene == self.top5_scene:
                self.top5_image_index = index
            elif top_scene == self.top6_scene:
                self.top6_image_index = index
            elif top_scene == self.top7_scene:
                self.top7_image_index = index
            elif top_scene == self.top8_scene:
                self.top8_image_index = index
            elif top_scene == self.top9_scene:
                self.top9_image_index = index
            else:
                self.top10_image_index = index

            if self.mode:
                change_image = QtGui.QPixmap(image_path[index])
            else:
                change_image = self.apply_clahe(image_path[index])
            change_image = change_image.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
            top_scene.addPixmap(change_image)
            topimage.setScene(top_scene)

    def new_id(self):
        if self.main_image_dir:
            new_id = self.new_id_edit.text()
            print(new_id)
            self.status_label.setText(function.create_new_id(self.main_image_dir,new_id,recognizer))

    def save_top_image(self,image_path,new_path):
        if image_path:
            self.status_label.setText(function.combine_with_new_pics(image_path,new_path,recognizer))

    def remove_dir(self):
        if self.main_image_dir:
            self.status_label.setText(function.remove_id(self.main_image_dir))


    def recal(self):
        if self.main_image_dir:
            self.status_label.setText(function.recalculation_id(self.main_image_dir,recognizer))

    def runtop10model(self):
        if self.main_image_dir:
            #先清理視窗
            self.top1_scene.clear()
            self.top1_image.setScene(self.top1_scene)
            self.top2_scene.clear()
            self.top2_image.setScene(self.top2_scene)
            self.top3_scene.clear()
            self.top3_image.setScene(self.top3_scene)
            self.top4_scene.clear()
            self.top4_image.setScene(self.top4_scene)
            self.top5_scene.clear()
            self.top5_image.setScene(self.top5_scene)
            self.top6_scene.clear()
            self.top6_image.setScene(self.top6_scene)
            self.top7_scene.clear()
            self.top7_image.setScene(self.top7_scene)
            self.top8_scene.clear()
            self.top8_image.setScene(self.top8_scene)
            self.top9_scene.clear()
            self.top9_image.setScene(self.top9_scene)
            self.top10_scene.clear()
            self.top10_image.setScene(self.top10_scene)

            # print(self.main_image_path)
            emb = function.to_embedding(self.main_image_path,recognizer)
            emb = function.find_center(emb)
            top10list,top10threshold = function.get_top10_folder(emb)

            self.top1_image_dir = top10list[0]
            self.top2_image_dir = top10list[1]
            self.top3_image_dir = top10list[2]
            self.top4_image_dir = top10list[3]
            self.top5_image_dir = top10list[4]
            self.top6_image_dir = top10list[5]
            self.top7_image_dir = top10list[6]
            self.top8_image_dir = top10list[7]
            self.top9_image_dir = top10list[8]
            self.top10_image_dir = top10list[9]

            self.top1th.setText(f"{top10threshold[0]:.2f}")
            self.top2th.setText(f"{top10threshold[1]:.2f}")
            self.top3th.setText(f"{top10threshold[2]:.2f}")
            self.top4th.setText(f"{top10threshold[3]:.2f}")
            self.top5th.setText(f"{top10threshold[4]:.2f}")
            self.top6th.setText(f"{top10threshold[5]:.2f}")
            self.top7th.setText(f"{top10threshold[6]:.2f}")
            self.top8th.setText(f"{top10threshold[7]:.2f}")
            self.top9th.setText(f"{top10threshold[8]:.2f}")
            self.top10th.setText(f"{top10threshold[9]:.2f}")
            
            self.top1label.setText(os.path.basename(self.top1_image_dir))
            self.top2label.setText(os.path.basename(self.top2_image_dir))
            self.top3label.setText(os.path.basename(self.top3_image_dir))
            self.top4label.setText(os.path.basename(self.top4_image_dir))
            self.top5label.setText(os.path.basename(self.top5_image_dir))
            self.top6label.setText(os.path.basename(self.top6_image_dir))
            self.top7label.setText(os.path.basename(self.top7_image_dir))
            self.top8label.setText(os.path.basename(self.top8_image_dir))
            self.top9label.setText(os.path.basename(self.top9_image_dir))
            self.top10label.setText(os.path.basename(self.top10_image_dir))
            self.status_label.setText('done!')
            #位置照片
            self.top1_image_path = [os.path.join(self.top1_image_dir, filename) for filename in os.listdir(self.top1_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top2_image_path = [os.path.join(self.top2_image_dir, filename) for filename in os.listdir(self.top2_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top3_image_path = [os.path.join(self.top3_image_dir, filename) for filename in os.listdir(self.top3_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top4_image_path = [os.path.join(self.top4_image_dir, filename) for filename in os.listdir(self.top4_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top5_image_path = [os.path.join(self.top5_image_dir, filename) for filename in os.listdir(self.top5_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top6_image_path = [os.path.join(self.top6_image_dir, filename) for filename in os.listdir(self.top6_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top7_image_path = [os.path.join(self.top7_image_dir, filename) for filename in os.listdir(self.top7_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top8_image_path = [os.path.join(self.top8_image_dir, filename) for filename in os.listdir(self.top8_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top9_image_path = [os.path.join(self.top9_image_dir, filename) for filename in os.listdir(self.top9_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            self.top10_image_path = [os.path.join(self.top10_image_dir, filename) for filename in os.listdir(self.top10_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            
            #隨機照片
            self.top1_image_index = random.randint(0,len(self.top1_image_path)-1)
            self.top2_image_index = random.randint(0,len(self.top2_image_path)-1)
            self.top3_image_index = random.randint(0,len(self.top3_image_path)-1)
            self.top4_image_index = random.randint(0,len(self.top4_image_path)-1)
            self.top5_image_index = random.randint(0,len(self.top5_image_path)-1)
            self.top6_image_index = random.randint(0,len(self.top6_image_path)-1)
            self.top7_image_index = random.randint(0,len(self.top7_image_path)-1)
            self.top8_image_index = random.randint(0,len(self.top8_image_path)-1)
            self.top9_image_index = random.randint(0,len(self.top9_image_path)-1)
            self.top10_image_index = random.randint(0,len(self.top10_image_path)-1)


            if self.mode:
                #top1
                self.top1img = QtGui.QPixmap(self.top1_image_path[self.top1_image_index])
                self.top1img = self.top1img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top1_scene.addPixmap(self.top1img)
                self.top1_image.setScene(self.top1_scene)

                #top2
                self.top2img = QtGui.QPixmap(self.top2_image_path[self.top2_image_index])
                self.top2img = self.top2img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top2_scene.addPixmap(self.top2img)                   
                self.top2_image.setScene(self.top2_scene)

                #top3
                self.top3img = QtGui.QPixmap(self.top3_image_path[self.top3_image_index])
                self.top3img = self.top3img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top3_scene.addPixmap(self.top3img)
                self.top3_image.setScene(self.top3_scene)

                #top4
                self.top4img = QtGui.QPixmap(self.top4_image_path[self.top4_image_index])
                self.top4img = self.top4img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top4_scene.addPixmap(self.top4img)                   
                self.top4_image.setScene(self.top4_scene)

                #top5
                self.top5img = QtGui.QPixmap(self.top5_image_path[self.top5_image_index])
                self.top5img = self.top5img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top5_scene.addPixmap(self.top5img)                   
                self.top5_image.setScene(self.top5_scene)

                #top6
                self.top6img = QtGui.QPixmap(self.top6_image_path[self.top6_image_index])
                self.top6img = self.top6img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top6_scene.addPixmap(self.top6img)
                self.top6_image.setScene(self.top6_scene)

                #top7
                self.top7img = QtGui.QPixmap(self.top7_image_path[self.top7_image_index])
                self.top7img = self.top7img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top7_scene.addPixmap(self.top7img)                   
                self.top7_image.setScene(self.top7_scene)

                #top8
                self.top8img = QtGui.QPixmap(self.top8_image_path[self.top8_image_index])
                self.top8img = self.top8img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top8_scene.addPixmap(self.top8img)
                self.top8_image.setScene(self.top8_scene)

                #top9
                self.top9img = QtGui.QPixmap(self.top9_image_path[self.top9_image_index])
                self.top9img = self.top9img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top9_scene.addPixmap(self.top9img)                   
                self.top9_image.setScene(self.top9_scene)

                #top10
                self.top10img = QtGui.QPixmap(self.top10_image_path[self.top10_image_index])
                self.top10img = self.top10img.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top10_scene.addPixmap(self.top10img)                   
                self.top10_image.setScene(self.top10_scene)
            else:
                self.top1clahe = self.apply_clahe(self.top1_image_path[self.top1_image_index])
                self.top1clahe = self.top1clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top1_scene.addPixmap(self.top1clahe)
                self.top1_image.setScene(self.top1_scene)

                self.top2clahe = self.apply_clahe(self.top2_image_path[self.top2_image_index])
                self.top2clahe = self.top2clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top2_scene.addPixmap(self.top2clahe)
                self.top2_image.setScene(self.top2_scene)

                self.top3clahe = self.apply_clahe(self.top3_image_path[self.top3_image_index])
                self.top3clahe = self.top3clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top3_scene.addPixmap(self.top3clahe)
                self.top3_image.setScene(self.top3_scene)

                self.top4clahe = self.apply_clahe(self.top4_image_path[self.top4_image_index])
                self.top4clahe = self.top4clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top4_scene.addPixmap(self.top4clahe)
                self.top4_image.setScene(self.top4_scene)

                self.top5clahe = self.apply_clahe(self.top5_image_path[self.top5_image_index])
                self.top5clahe = self.top5clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top5_scene.addPixmap(self.top5clahe)
                self.top5_image.setScene(self.top5_scene)

                self.top6clahe = self.apply_clahe(self.top6_image_path[self.top6_image_index])
                self.top6clahe = self.top6clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top6_scene.addPixmap(self.top6clahe)
                self.top6_image.setScene(self.top6_scene)

                self.top7clahe = self.apply_clahe(self.top7_image_path[self.top7_image_index])
                self.top7clahe = self.top7clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top7_scene.addPixmap(self.top7clahe)
                self.top7_image.setScene(self.top7_scene)

                self.top8clahe = self.apply_clahe(self.top8_image_path[self.top8_image_index])
                self.top8clahe = self.top8clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top8_scene.addPixmap(self.top8clahe)
                self.top8_image.setScene(self.top8_scene)

                self.top9clahe = self.apply_clahe(self.top9_image_path[self.top9_image_index])
                self.top9clahe = self.top9clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top9_scene.addPixmap(self.top9clahe)
                self.top9_image.setScene(self.top9_scene)
            
                self.top10clahe = self.apply_clahe(self.top10_image_path[self.top10_image_index])
                self.top10clahe = self.top10clahe.scaled(151, 121, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.top10_scene.addPixmap(self.top10clahe)
                self.top10_image.setScene(self.top10_scene)


    def apply_clahe(self,image_path):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l2 = clahe.apply(l)
        processed_lab = cv2.merge([l2, a, b])
        processed_img = cv2.cvtColor(processed_lab, cv2.COLOR_LAB2BGR)
        height, width, channel = processed_img.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(processed_img.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888).rgbSwapped()
        return QtGui.QPixmap.fromImage(qImg)

    def runtop10Viewer(self,folder_path):
        if folder_path:
            self.viewer = ImageViewer()
            self.viewer.image_dir = folder_path
            self.viewer.loadImagePaths(folder_path)
            self.viewer.show()
    
    def runViewer(self):
        folder_path = self.folder_edit.text()
        if folder_path:
            self.mainviewer = ImageViewer()
            self.viewer.image_dir = folder_path
            self.mainviewer.loadImagePaths(folder_path)
            self.mainviewer.show()

    def openFolder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder_path:
            self.main_image_index = 0
            self.main_scene.clear()
            self.main_image.setScene(self.main_scene)
            self.folder_edit.setText(folder_path)
            self.main_image_dir = folder_path
            self.main_image_path = [os.path.join(self.main_image_dir, filename) for filename in os.listdir(self.main_image_dir) if filename.lower().endswith(('.jpg', '.png', '.jpeg', 'JPG'))]
            if self.mode:
                self.img = QtGui.QPixmap(self.main_image_path[self.main_image_index])
                self.img = self.img.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.img)
                self.main_image.setScene(self.main_scene)
            else:
                self.clahe = self.apply_clahe(self.main_image_path[self.main_image_index])
                self.clahe = self.clahe.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.clahe)
                self.main_image.setScene(self.main_scene)
            self.main_index.setText(f"Image {self.main_image_index + 1}/{len(self.main_image_path)}")
            self.status_label.setText("尚未完成更新")

    def preImage(self):
        if self.main_image_path:
            self.main_scene.clear()
            self.main_image.setScene(self.main_scene)
            self.main_image_index = (self.main_image_index - 1) % len(self.main_image_path)
            if self.mode:
                self.img = QtGui.QPixmap(self.main_image_path[self.main_image_index])
                self.img = self.img.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.img)
                self.main_image.setScene(self.main_scene)
            else:
                self.clahe = self.apply_clahe(self.main_image_path[self.main_image_index])
                self.clahe = self.clahe.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.clahe)
                self.main_image.setScene(self.main_scene)
            self.main_index.setText(f"Image {self.main_image_index + 1}/{len(self.main_image_path)}")

    def nextImage(self):
        if self.main_image_path:
            self.main_scene.clear()
            self.main_image.setScene(self.main_scene)
            self.main_image_index = (self.main_image_index + 1) % len(self.main_image_path)
            if self.mode:
                self.img = QtGui.QPixmap(self.main_image_path[self.main_image_index])
                self.img = self.img.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.img)
                self.main_image.setScene(self.main_scene)
            else:
                self.clahe = self.apply_clahe(self.main_image_path[self.main_image_index])
                self.clahe = self.clahe.scaled(361, 301, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
                self.main_scene.addPixmap(self.clahe)
                self.main_image.setScene(self.main_scene)
            self.main_index.setText(f"Image {self.main_image_index + 1}/{len(self.main_image_path)}")