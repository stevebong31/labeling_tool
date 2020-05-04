# -*-encoding:utf-8-*-
import sys, os, cv2, json, glob, copy
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.left, self.top = 100, 100
        self.width, self.height = 1080, 720
        # image shape = 1280 - 200 * 2, 720 - 50
        self.margin = 1
        self.stbar = self.statusBar()
        self.stbar.resize(self.width, 20)
        self.mnbar = self.menuBar()
        self.setWindowIcon(QIcon("img/gachon.jpg"))
        self.setWindowTitle("Endoscopy Labeling Tool Software")
        self.file_view = list_widget(self)
        self.class_view = list_widget(self)
        self.display = QLabel("Canvas", self)
        self.check_showdialog = False
        self.check_cropmode = False
        self.check_click = False
        self.toolbar_h = 50
        self.list_view_w = 200
        self.load_classes()
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMouseTracking(True)
        self.color_green = (0, 255, 0)
        self.color_blue = (0, 0, 255)
        self.color_white = (255, 255, 255)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.init_App()

    def init_App(self):
        # =================== Open Button of Menubar ===================
        openAction = QAction(QIcon('img/open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open File')
        openAction.triggered.connect(self.showDialog)

        # =================== Save Button of Menubar ===================
        saveAction = QAction(QIcon('img/save.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        saveAction.triggered.connect(self.save_crop_images)
        saveAction.triggered.connect(self.save_classes)
        saveAction.triggered.connect(self.save_labels)
        saveAction.triggered.connect(self.save_crops)

        # =================== Exit Button of Menubar ===================
        exitAction = QAction(QIcon('img/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.showExitBox)

        # =================== About Button of Menubar ===================
        aboutAction = QAction('About', self)
        aboutAction.setStatusTip('about')
        aboutAction.triggered.connect(self.showMessageBox)

        # =================== shortcut Button of Menubar ===================
        shortAction = QAction('shortcut', self)
        shortAction.setShortcut('Ctrl+H')
        shortAction.setStatusTip('shortcut')
        shortAction.triggered.connect(self.shortcutMessageBox)

        # =================== Crop Button of Toolbar ===================
        cropAction = QAction(QIcon('img/crop.png'), 'Crop', self)
        cropAction.setShortcut('Ctrl+C')
        cropAction.setStatusTip('Crop image')
        cropAction.triggered.connect(self.crop_mode)

        # =================== Auto Crop Button of Toolbar ===================
        autocropAction = QAction(QIcon('img/cropauto.png'), 'Auto crop', self)
        autocropAction.setShortcut('Ctrl+A')
        autocropAction.setStatusTip('Auto crop image')
        autocropAction.triggered.connect(self.auto_crop)

        # =================== Bright reset Button of Toolbar ===================
        brresetAction = QAction(QIcon('img/reset.png'), 'Bright reset', self)
        brresetAction.setShortcut('Ctrl+R')
        brresetAction.setStatusTip('Bright reset image')
        brresetAction.triggered.connect(self.img_bright_reset)

        # =================== Bright up Button of Toolbar ===================
        brupAction = QAction(QIcon('img/plus.png'), 'Bright up', self)
        brupAction.setShortcut('Ctrl+J')
        brupAction.setStatusTip('Bright up image')
        brupAction.triggered.connect(self.img_bright_up)

        # =================== Bright down Button of Toolbar ===================
        brdwAction = QAction(QIcon('img/minus.png'), 'Bright down', self)
        brdwAction.setShortcut('Ctrl+K')
        brdwAction.setStatusTip('Bright down image')
        brdwAction.triggered.connect(self.img_bright_down)

        # =================== Delete Crop Button of Toolbar ===================
        delcropAction = QAction(QIcon('img/cropx.png'), 'Delete Crop', self)
        delcropAction.setShortcut('Ctrl+Z')
        delcropAction.setStatusTip('Delete Crop image')
        delcropAction.triggered.connect(self.delete_crop_data)

        # =================== Delete box Button of Toolbar ===================
        delboxAction = QAction(QIcon('img/boxx.png'), 'Delete box', self)
        delboxAction.setShortcut('Ctrl+X')
        delboxAction.setStatusTip('Delete Box image')
        delboxAction.triggered.connect(self.delete_box_data)

        # ====================== Edit Toolbar Setting =======================
        self.filetoolbar = self.addToolBar('file')
        self.filetoolbar.resize(self.width, self.toolbar_h)
        self.filetoolbar.addAction(openAction)
        self.filetoolbar.addAction(saveAction)

        # ====================== Edit Toolbar Setting =======================
        self.toolbar = self.addToolBar('Edit')
        self.toolbar.resize(self.width, self.toolbar_h)
        self.toolbar.addAction(autocropAction)
        self.toolbar.addAction(cropAction)
        self.toolbar.addAction(delcropAction)
        self.toolbar.addAction(delboxAction)
        self.toolbar.addAction(brupAction)
        self.toolbar.addAction(brdwAction)
        self.toolbar.addAction(brresetAction)
        self.tb_width = self.toolbar.width()
        self.tb_height = self.toolbar.height()

        # ====================== Menubar setting Setting =======================
        self.menu = self.menuBar()
        menu_file = self.menu.addMenu('file')
        menu_edit = self.menu.addMenu('edit')
        menu_help = self.menu.addMenu('help')
        menu_file.addAction(openAction)
        menu_file.addAction(saveAction)
        menu_file.addAction(exitAction)
        menu_edit.addAction(autocropAction)
        menu_edit.addAction(cropAction)
        menu_edit.addAction(delcropAction)
        menu_edit.addAction(delboxAction)
        menu_edit.addAction(brupAction)
        menu_edit.addAction(brdwAction)
        menu_edit.addAction(brresetAction)
        menu_help.addAction(shortAction)
        menu_help.addAction(aboutAction)

        # ====================== File List Widget ======================
        self.file_view.move(0, self.tb_height + 3 * self.margin)
        self.file_view.resize(self.list_view_w, self.height - self.tb_height - self.stbar.height() - 4 * self.margin)
        self.file_view.list_box.resize(self.list_view_w,
                                       self.height - self.tb_height - self.stbar.height() - 4 * self.margin)

        # ===================== Class List Widget =====================
        self.class_view.move(self.width - self.list_view_w, self.tb_height + 3 * self.margin)
        self.class_view.resize(self.list_view_w, self.height - self.tb_height - self.stbar.height() - 4 * self.margin)
        self.class_view.list_box.resize(self.list_view_w,
                                         self.height - self.tb_height - self.stbar.height() - 4 * self.margin)

        # ======================= Display Widget =======================
        self.img_width = self.width - 2 * self.list_view_w
        self.img_height = self.height - self.tb_height - self.stbar.height() - 4 * self.margin
        self.display.setMaximumWidth(self.img_width)
        # self.display.setMinimumHeight(self.img_height)
        self.display.setMaximumWidth(self.img_width)
        # self.display.setMinimumHeight(self.img_height)
        self.display.setMouseTracking(True)
        self.display.move(self.list_view_w, self.tb_height + 3 * self.margin)
        self.display.resize(self.img_width, self.img_height)
        self.display.setAlignment(Qt.AlignCenter)

        # ======================= Read & Display =======================
        self.file_view.list_box.clicked.connect(self.read_img)
        self.show()
        self.canvas_init()

    def showMessageBox(self):
        msgbox = QMessageBox(self)
        msgbox.question(self, 'About', 'Copyright 2019~2020. Gachon university. All rights reserved.', QMessageBox.Yes)

    def shortcutMessageBox(self):
        msgbox = QMessageBox(self)
        msgbox.question(self, 'Shortcut commend', 'Ctrl+O : File open \n '
                                                  'Ctrl+Q : App exit \n '
                                                  'Ctrl+S : Save labels, crops, images \n '
                                                  'Ctrl+X : Delete Box image \n '
                                                  'Ctrl+C : Crop image \n '
                                                  'Ctrl+Z : Delete Crop image \n '
                                                  'Ctrl+J : image Brightness up \n '
                                                  'Ctrl+K : image Brightness down \n '
                                                  'Ctrl+R : Original image load \n '
                                                  'Ctrl+H : Shortcut commend \n ',
                        QMessageBox.Yes)

    def showExitBox(self):
        msgbox = QMessageBox(self)
        event_click = msgbox.question(self, 'Exit', 'Are you sure you want to quit the program?', QMessageBox.Yes | QMessageBox.No)
        if event_click == QMessageBox.Yes:
            qApp.quit()

    def canvas_init(self):  # canvas make initial zero image
        self.img = np.zeros((self.img_width, self.img_height))
        self.pixmap = self.np2qi_img(self.img)
        self.display.setPixmap(self.pixmap)

    def crop_img_dir_create(self):
        self.crop_fname = self.fname + '_crop'
        try:
            if not (os.path.isdir(self.crop_fname)):
                os.makedirs(os.path.join(self.crop_fname))
                print("create directory")
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Failed to create directory")
                raise

    def load_classes(self):
        self.classes = []
        with open('classes.txt') as f:
            for line in f:
                self.classes.append(line.split('\n')[0])

    def load_labels(self):
        self.label_path = os.path.join(self.fname, 'labels.json')
        self.label_path_crop = os.path.join(self.fname + '_crop', 'labels.json')
        self.label_json_true = glob.glob(self.fname + '/labels.json')
        if not self.label_json_true:
            self.box_labels = dict([(tmp, []) for tmp in self.file_list])
            print('initialize box labels')
        else:
            with open(self.label_path) as json_file:
                self.box_labels = json.load(json_file)
            print('load box labels file')

    def load_crops(self):
        self.crop_path = os.path.join(self.fname, 'crops.json')
        self.crop_json_true = glob.glob(self.fname + '/crops.json')
        if not self.crop_json_true:
            self.img_crops = dict([(tmp, []) for tmp in self.file_list])
            print('initialize images crop')
        else:
            with open(self.crop_path) as json_file:
                self.img_crops = json.load(json_file)
            print('load images crop file')

    def save_labels(self):
        if self.check_showdialog == True:
            with open(self.label_path, 'w') as json_file:
                json.dump(self.box_labels, json_file, sort_keys=True, indent=4)
            label_rename_copy = copy.deepcopy(self.box_labels)

            for idx in range(len(self.file_list)):
                print(self.file_list[idx])
                label_rename_copy[self.file_name_only_list[idx] + '_crop.png'] = label_rename_copy.pop(self.file_list[idx])

            with open(self.label_path_crop, 'w') as json_file:
                json.dump(label_rename_copy, json_file, sort_keys=True, indent=4)
            print('save box labels file')

    def save_crops(self):
        if self.check_showdialog == True:
            with open(self.crop_path, 'w') as json_file:
                json.dump(self.img_crops, json_file, sort_keys=True, indent=4)
                print('save images crop file')

    def save_classes(self):
        if self.check_showdialog == True:
            for idx in range(len(self.classes)):
                self.classes[idx] = self.model_classes.item(idx).text()
            file = open('classes.txt', 'w')
            for class_one in self.classes:
                file.write(class_one + '\n')
            file.close()
            print('Save classes')

    def save_crop_images(self):
        if self.check_showdialog == True:
            self.get_list_changed_name_file()
            for idx in range(len(self.file_list)):
                if not self.img_crops[self.file_list[idx]] == []:
                    self.start_point = (self.img_crops[self.file_list[idx]][0]['xmin'],
                                        self.img_crops[self.file_list[idx]][0]['ymin'])
                    self.end_point = (self.img_crops[self.file_list[idx]][0]['xmax'],
                                      self.img_crops[self.file_list[idx]][0]['ymax'])
                    self.img_path = os.path.join(self.fname, self.file_list[idx])
                    self.img_saved = cv2.cvtColor(self.cv_imread(self.img_path), cv2.COLOR_RGB2BGR)
                    self.img_saved = cv2.resize(self.img_saved, (self.img_width, self.img_height))
                    self.img_saved = self.img_saved[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
                    self.img_saved = cv2.resize(self.img_saved, (self.img_width, self.img_height))
                    cv2.imwrite(os.path.join(self.crop_fname, self.file_name_only_list[idx] + '_crop.png'), self.img_saved)

    def get_list_changed_name_file(self):
        if self.check_showdialog == True:
            for idx in range(len(self.file_name_only_list)):
                self.file_name_only_list[idx] = self.model.item(idx).text()
            print(self.file_name_only_list)

    def img_bright_up(self):
        if self.check_showdialog == True:
            self.img = self.img + 3
            self.img = np.clip(self.img, 0, 255)
            self.pixmap = self.np2qi_img(self.img)
            self.display.setPixmap(self.pixmap)

    def img_bright_down(self):
        if self.check_showdialog == True:
            self.img = self.img - 3
            self.img = np.clip(self.img, 0, 255)
            self.pixmap = self.np2qi_img(self.img)
            self.display.setPixmap(self.pixmap)

    def auto_crop(self):
        if self.check_showdialog == True:
            img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            tol = 0
            img_gray[img_gray > 170] = 0
            img_gray[img_gray < 50] = 0
            kernel = np.ones((7, 7), dtype=np.int8)
            img_gray = cv2.erode(img_gray, kernel)
            mask = img_gray > tol
            m, n = img_gray.shape
            mask0, mask1 = mask.any(0), mask.any(1)
            x_min, x_max = int(mask0.argmax()), int(n - mask0[::-1].argmax())
            y_min, y_max = int(mask1.argmax()), int(m - mask1[::-1].argmax())
            self.img = self.img[y_min:y_max, x_min:x_max]
            if not self.img_crops[self.file_list[self.path_row]] == []:
                self.img_crops[self.file_list[self.path_row]] = [{'xmin': x_min, 'xmax': x_max, 'ymin': y_min,'ymax': y_max}]
            else:
                self.img_crops[self.file_list[self.path_row]].append({'xmin': x_min, 'xmax': x_max, 'ymin': y_min, 'ymax': y_max})
            print(self.img_crops)
            self.img = cv2.resize(self.img, (self.img_width, self.img_height))
            self.pixmap = self.np2qi_img(self.img)
            self.display.setPixmap(self.pixmap)

    def crop_mode(self):
        print('Crop mode on')
        self.check_cropmode = True

    def delete_crop_data(self):
        if self.check_showdialog == True:
            print('Crop delete')
            self.img_crops[self.file_list[self.path_row]] = []
            self.read_img()

    def img_bright_reset(self):
        if self.check_showdialog == True:
            self.read_img()

    def delete_box_data(self):
        if self.check_showdialog == True:
            print('Box labels delete')
            if not self.box_labels[self.file_list[self.path_row]] == []:
                self.box_labels[self.file_list[self.path_row]].pop()
                self.read_img()

    def sort_point(self):
        x_all = [self.start_point[0], self.end_point[0]]
        y_all = [self.start_point[1], self.end_point[1]]
        start_point_x = min(x_all)
        start_point_y = min(y_all)
        end_point_x = max(x_all)
        end_point_y = max(y_all)
        return (start_point_x, start_point_y), (end_point_x, end_point_y)

    def mouseMoveEvent(self, event):
        txt = "Mouse 위치 : x={0},y={1}, global={2},{3}".format(event.x() - self.list_view_w,
                                                              event.y() - self.toolbar_h,
                                                              event.globalX() - self.list_view_w,
                                                              event.globalY() - self.stbar.height())
        self.stbar.showMessage(txt)

        if self.check_cropmode == True:
            line_color = self.color_blue
        else:
            line_color = self.color_green

        if self.check_showdialog == True:
            self.tmp_img = self.img.copy()
            self.tmp_img = cv2.line(self.tmp_img, (event.x() - self.list_view_w, 0), (event.x() - self.list_view_w, self.img_width), line_color, 1)
            self.tmp_img = cv2.line(self.tmp_img, (0, event.y() - self.toolbar_h),
                                    (self.img_height + self.list_view_w + 50, event.y() - self.toolbar_h), line_color, 1)
            self.pixmap = self.np2qi_img(self.tmp_img)
            self.display.setPixmap(self.pixmap)

        if event.buttons():
            self.tmp_img = self.img.copy()
            self.tmp_img = cv2.rectangle(self.tmp_img, self.start_point,
                                         (event.x() - self.list_view_w, event.y() - self.toolbar_h), line_color, 1)
            self.pixmap = self.np2qi_img(self.tmp_img)
            self.display.setPixmap(self.pixmap)

    def mousePressEvent(self, event):  # e ; QMouseEvent
        # print('BUTTON PRESS')
        if Qt.LeftButton:
                self.start_point = event.x() - self.list_view_w, event.y() - self.toolbar_h

    def mouseReleaseEvent(self, event):  # e ; QMouseEvent
        # print('BUTTON RELEASE')
        if self.check_showdialog == True:
            if Qt.LeftButton:
                if self.check_cropmode == True: # crop images
                    print('crop')
                    self.end_point = event.x() - self.list_view_w, event.y() - self.toolbar_h
                    self.start_point, self.end_point = self.sort_point()
                    print('start_point', self.start_point, 'end_point', self.end_point)
                    self.img = self.img[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
                    self.img_crops[self.file_list[self.path_row]].append({'xmin': self.start_point[0], 'xmax': self.end_point[0], 'ymin': self.start_point[1], 'ymax': self.end_point[1]})
                    # print(self.img_crops[self.file_list[self.path_row]][0]['xmax'])
                    self.img = cv2.resize(self.img, (self.img_width, self.img_height))
                    self.pixmap = self.np2qi_img(self.img)
                    self.display.setPixmap(self.pixmap)
                    self.check_cropmode = False
                else:
                    print('box')  # label images
                    self.end_point = event.x() - self.list_view_w, event.y() - self.toolbar_h
                    self.start_point, self.end_point = self.sort_point()
                    itms = self.class_view.list_box.selectedIndexes()
                    if not itms:
                        classes = 'None'
                    else:
                        classes = itms[0].data()
                    print('start_point', self.start_point, 'end_point', self.end_point, 'class', classes)
                    self.box_labels[self.file_list[self.path_row]].append({'xmin': self.start_point[0], 'xmax': self.end_point[0], 'ymin': self.start_point[1], 'ymax': self.end_point[1], 'class': classes})
                self.draw_box()

    def draw_box(self):
        for one_label in self.box_labels[self.file_list[self.path_row]]:
            self.start_point = (one_label['xmin'], one_label['ymin'])
            self.end_point = (one_label['xmax'], one_label['ymax'])
            self.img = cv2.rectangle(self.img, self.start_point, self.end_point, self.color_green, 1)
            # print(one_label['class'].dtype)
            cv2.putText(self.img, one_label['class'], (self.start_point[0], self.start_point[1] - 5), self.font, 0.5, self.color_green, 1)
            # print(self.box_labels)
            self.pixmap = self.np2qi_img(self.img)
            self.display.setPixmap(self.pixmap)


    def showDialog(self):
        self.fname = QFileDialog.getExistingDirectory(self, 'Open file')
        self.file_name_only_list = []
        print('f name', self.fname)
        if not self.fname == '':
            self.file_list = [i for i in sorted(os.listdir(self.fname)) if
                         i.split('.')[1] in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']]
            self.model = QStandardItemModel()  #file list view
            for f in self.file_list:
                file_name_only = f.split('.')[0]
                self.model.appendRow(QStandardItem(file_name_only))
                self.file_name_only_list.append(file_name_only)
            self.file_view.list_box.setModel(self.model)

            self.model_classes = QStandardItemModel()  #class list view
            for c in self.classes:
                self.model_classes.appendRow(QStandardItem(c))
            self.class_view.list_box.setModel(self.model_classes)

            self.load_labels()
            self.load_crops()
            self.crop_img_dir_create()
            print(self.box_labels)
            self.check_showdialog = True

    def np2qi_img(self, img):
        bytesPerLine = 3 * self.img_width
        qImg = QImage(img, self.img_width, self.img_height, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage(qImg)

    def read_img(self):
        self.path_row = self.file_view.list_box.currentIndex().row()
        self.img_path = os.path.join(self.fname, self.file_list[self.path_row])
        print(self.path_row, self.img_path)
        self.img = self.cv_imread(self.img_path)
        self.img = cv2.resize(self.img, (self.img_width, self.img_height))

        if not self.img_crops[self.file_list[self.path_row]] == []:
            self.start_point = (self.img_crops[self.file_list[self.path_row]][0]['xmin'], self.img_crops[self.file_list[self.path_row]][0]['ymin'])
            self.end_point = (self.img_crops[self.file_list[self.path_row]][0]['xmax'], self.img_crops[self.file_list[self.path_row]][0]['ymax'])
            self.img = self.img[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
            self.img = cv2.resize(self.img, (self.img_width, self.img_height))

        self.pixmap = self.np2qi_img(self.img)
        self.draw_box()
        self.display.setPixmap(self.pixmap)

    def cv_imread(self, file_path, flags=cv2.IMREAD_COLOR, dtype=np.uint8):  # use for korean path
        try:
            n = np.fromfile(file_path, dtype)
            img = cv2.imdecode(n, flags)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(e)
            return None


class list_widget(QWidget):
    def __init__(self, parent):
        super(list_widget, self).__init__(parent)
        self.list_box = QListView(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())