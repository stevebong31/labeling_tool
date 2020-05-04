import sys, os, cv2, glob
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.left, self.top = 100, 100
        self.width, self.height = 1100, 720
        self.margin = 1
        self.setWindowIcon(QIcon("img/gachon.jpg"))
        self.stbar = self.statusBar()
        self.stbar.resize(self.width, 20)
        self.mnbar = self.menuBar()
        self.setWindowTitle("Endoscopy Labeling Tool Software")
        self.file_view = list_widget(self)
        self.result_view = list_widget(self)
        self.display = QLabel("Canvas", self)
        self.toolbar_h = 40
        self.list_view_w = 200
        self.count = 0
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMouseTracking(True)
        self.init_App()
        self.check = 0
        self.load_classes()
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.crop_check = 0

    def init_App(self):
        # ==============================================================
        # ====================== Crop Button Widget ====================
        # ==============================================================
        self.crop_button = radio_button(self)
        self.crop_button.move(200, self.margin + 10)
        self.crop_button_label = QLabel("Crop Mode", self)
        self.crop_button_label.move(220, self.margin + 2)

        # ==============================================================
        # =================== Open Button of Toolbar ===================
        # ==============================================================
        openAction = QAction(QIcon('./img/open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open File')
        openAction.triggered.connect(self.showDialog)

        # =======================a=======================================
        # =================== Save Button of Toolbar ===================
        # ==============================================================
        saveAction = QAction(QIcon('./img/save.png'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save File')
        saveAction.triggered.connect(self.save_file)

        # ==============================================================
        # =================== Exit Button of Toolbar ===================
        # ==============================================================
        exitAction = QAction(QIcon('./img/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # ==============================================================
        # ====================== Toolbar Setting =======================
        # ==============================================================
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.resize(self.width, self.toolbar_h)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(saveAction)
        self.toolbar.addAction(exitAction)
        # self.toolbar.setHeight(toolbar_h)
        self.tb_width = self.toolbar.width()
        self.tb_height = self.toolbar.height()

        # ==============================================================
        # ====================== File List Widget ======================
        # ==============================================================
        self.file_view.move(0, self.tb_height + 3 * self.margin)
        self.file_view.resize(self.list_view_w, self.height - self.tb_height - self.stbar.height() - 4 * self.margin)
        self.file_view.list_box.resize(self.list_view_w,
                                       self.height - self.tb_height - self.stbar.height() - 4 * self.margin)

        # ==============================================================
        # ===================== Result List Widget =====================
        # ==============================================================
        self.result_view.move(self.width - self.list_view_w, self.tb_height + 3 * self.margin)
        self.result_view.resize(self.list_view_w, self.height - self.tb_height - self.stbar.height() - 4 * self.margin)
        self.result_view.list_box.resize(self.list_view_w,
                                         self.height - self.tb_height - self.stbar.height() - 4 * self.margin)

        # ==============================================================
        # ======================= Display Widget =======================
        # ==============================================================
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

        # ==============================================================
        # ======================= Read & Display =======================
        # ==============================================================
        self.file_view.list_box.clicked.connect(self.read_img)
        self.show()
        self.canvas_init()

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

    def keyPressEvent(self, e):
        def isPrintable(key):
            printable = [Qt.Key_Space, Qt.Key_Exclam, Qt.Key_QuoteDbl, Qt.Key_NumberSign, Qt.Key_Dollar,
                                       Qt.Key_Percent, Qt.Key_Ampersand, Qt.Key_Apostrophe, Qt.Key_ParenLeft,
                                       Qt.Key_ParenRight, Qt.Key_Asterisk, Qt.Key_Plus, Qt.Key_Comma, Qt.Key_Minus,
                                       Qt.Key_Period, Qt.Key_Slash, Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4,
                                       Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_Colon, Qt.Key_Semicolon,
                                       Qt.Key_Less, Qt.Key_Equal, Qt.Key_Greater, Qt.Key_Question, Qt.Key_At, Qt.Key_A,
                                       Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I,
                                       Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q,
                                       Qt.Key_R, Qt.Key_S, Qt.Key_T, Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y,
                                       Qt.Key_Z, Qt.Key_BracketLeft, Qt.Key_Backslash, Qt.Key_BracketRight,
                                       Qt.Key_AsciiCircum, Qt.Key_Underscore, Qt.Key_QuoteLeft, Qt.Key_BraceLeft,
                                       Qt.Key_Bar, Qt.Key_BraceRight, Qt.Key_AsciiTilde]
            if key in printable:
                return True
            else:
                return False
        control = False

        if e.modifiers() & Qt.ControlModifier:
            print('Control')
            control = True
            if self.crop_check == 0:
                self.crop_button.radio_button.setChecked(True)
                self.crop_check = 1
                print('Crop mode on')
                self.read_img()
                if not self.dict_crop[self.count][1:]:
                    print('empty')
                else:
                    print('delete all')
                    print(self.dict_crop[self.count])
                    del self.dict_crop[self.count][1:]
                    del self.dict_label[self.count][1:]
                self.read_img()

            else:
                self.crop_check = 0
                self.crop_button.radio_button.setChecked(False)
                print('Crop mode off')

        if e.modifiers() & Qt.ShiftModifier:
            print('Shift')
            self._del_item()
        if e.modifiers() & Qt.AltModifier:
            print('Alt')
        if e.key() == Qt.Key_Delete:
            print('Delete')
            self._del_all_item()
        elif e.key() == Qt.Key_Backspace:
            print('Backspace')
        elif e.key() == Qt.Key_Return:
            self.save2crop_img()
            print('Enter')
        elif e.key() == Qt.Key_Escape:
            print('Escape')
        elif e.key() == Qt.Key_Right:
            print('Right')
        elif e.key() == Qt.Key_Left:
            print('Left')
        elif e.key() == Qt.Key_Up:
            print('Up')
        elif e.key() == Qt.Key_Down:
            print('Down')
        if not control and isPrintable(e.key()):
            print(e.text())

    def save2crop_img(self):
        itms = self.file_view.list_box.selectedIndexes()
        self.file_change_name = itms[0].data()
        self.count = self.file_view.list_box.currentIndex().row()
        print(self.file_change_name, self.count)
        self.img_path = os.path.join(self.fname, self.file_list[self.count])
        img = self.imread_(self.img_path)
        if not len(self.dict_crop[self.count][:]) == 1:
            self.start_point = self.dict_crop[self.count][1:][0][0]
            self.end_point = self.dict_crop[self.count][1:][0][1]
            img = cv2.resize(img, (self.img_width, self.img_height))
            img = img[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
            img = cv2.resize(img, (self.img_width, self.img_height))
            cv2.imwrite(os.path.join(self.crop_fname, self.file_change_name + '.png'), img)
        print('saved cropping images')
        self.dict_label_copy = self.dict_label
        self.dict_label_copy[self.count][0] = self.file_change_name + '.png'
        self.save_file()

    def _del_all_item(self):
        if not self.dict_label[self.count][1:]:
            print('empty')
        else:
            print('delete all')
            print(self.dict_label[self.count])
            del self.dict_label[self.count][1:]
            self.draw_box()
        self.read_img()

    def _del_item(self):
        if not self.dict_label[self.count][1:]:
            print('empty')
        else:
            print('delete')
            self.dict_label[self.count].pop()
        self.read_img()

    def mouseMoveEvent(self, e):
        txt = "Mouse 위치 : x={0},y={1}, global={2},{3}".format(e.x() - self.list_view_w,
                                                              e.y() - self.toolbar.height() - 10,
                                                              e.globalX(), e.globalY())
        self.tmp_img = np.copy(self.img)
        self.tmp_img = cv2.line(self.tmp_img, (e.x() - self.list_view_w, 0), (e.x() - self.list_view_w, self.img_width), (0, 255, 0), 1)
        self.tmp_img = cv2.line(self.tmp_img, (0, e.y() - self.toolbar.height() - 10),
                                (self.img_height + self.list_view_w + 50, e.y() - self.toolbar.height() - 10), (0, 255, 0), 1)
        self.pixmap = self.np2qi_tmp()
        self.display.setPixmap(self.pixmap)

        if e.buttons():
            if self.check == 0:
                self.start_point = e.x() - self.list_view_w, e.y() - self.toolbar.height() - 10
                self.check = 1
            else:
                self.tmp_img = np.copy(self.img)
                self.tmp_img = cv2.rectangle(self.tmp_img, self.start_point,
                                             (e.x() - self.list_view_w, e.y() - self.toolbar.height() - 10),
                                             (0, 255, 0), 1)
                self.pixmap = self.np2qi_tmp()
                self.display.setPixmap(self.pixmap)
        self.stbar.showMessage(txt)

    def showDialog(self):
        self.fname = QFileDialog.getExistingDirectory(self, 'Open file')
        # self.fname = './img'
        self.file_list = [i for i in sorted(os.listdir(self.fname)) if
                          i.split('.')[-1] in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']]
        model = QStandardItemModel()
        for f in self.file_list:
            f_name = os.path.splitext(f)[0]
            model.appendRow(QStandardItem(f_name))
        self.load_file()
        self.file_view.list_box.setModel(model)

        model_result = QStandardItemModel()
        for c in self.classes:
            model_result.appendRow(QStandardItem(c))
        self.result_view.list_box.setModel(model_result)

        print('This is filelist', self.file_list)

    def canvas_init(self):
        self.img = np.zeros((self.img_width, self.img_height))
        self.pixmap = self.np2qi()
        self.display.setPixmap(self.pixmap)

    def read_img(self):
        path = self.fname
        self.count = self.file_view.list_box.currentIndex().row()
        print('This is row', self.count)
        self.img_path = os.path.join(path, self.file_list[self.count])
        print(self.img_path)
        self.img = cv2.cvtColor(self.imread_(self.img_path), cv2.COLOR_BGR2RGB)
        self.img = cv2.resize(self.img, (self.img_width, self.img_height))
        self.pixmap = self.np2qi()
        self.draw_box()
        self.display.setPixmap(self.pixmap)

    def np2qi(self):
        bytesPerLine = 3 * self.img_width
        self.qImg = QImage(self.img, self.img_width, self.img_height, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage(self.qImg)

    def np2qi_tmp(self):
        bytesPerLine = 3 * self.img_width
        self.qImg = QImage(self.tmp_img, self.img_width, self.img_height, bytesPerLine, QImage.Format_RGB888)
        return QPixmap.fromImage(self.qImg)

    def imread_(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
        try:
            n = np.fromfile(filename, dtype)
            img = cv2.imdecode(n, flags)
            return img
        except Exception as e:
            print(e)
            return None

    def draw_box(self):
        self.img_crop()
        for i in range(len(self.dict_label[self.count][1:])):
            self.img = cv2.rectangle(self.img, self.dict_label[self.count][1:][i][0],
                                     self.dict_label[self.count][1:][i][1], (0, 255, 0), 1)
            x_all = [self.dict_label[self.count][1:][i][0][0], self.dict_label[self.count][1:][i][1][0]]
            y_all = [self.dict_label[self.count][1:][i][0][1], self.dict_label[self.count][1:][i][1][1]]
            x = min(x_all)
            y = min(y_all)
            cv2.putText(self.img, self.dict_label[self.count][1:][i][2], (x, y - 5), self.font, 0.5, (0, 255, 0), 1)
        print(self.dict_label)
        self.pixmap = self.np2qi()
        self.display.setPixmap(self.pixmap)

    def re_draw_box(self):
        self.img = cv2.rectangle(self.img, self.start_point, self.end_point, (0, 255, 0), 1)
        x_all = [self.start_point[0], self.end_point[0]]
        y_all = [self.start_point[1], self.end_point[1]]
        x = min(x_all)
        y = min(y_all)
        itms = self.result_view.list_box.selectedIndexes()
        if not itms:
            classes = 'None'
        else:
            classes = itms[0].data()
        cv2.putText(self.img, classes, (x, y - 5), self.font, 0.5, (0, 255, 0), 1)
        print(self.dict_label)
        self.pixmap = self.np2qi()
        self.display.setPixmap(self.pixmap)

    def img_crop(self):
        if not len(self.dict_crop[self.count][:]) == 1:
            self.start_point = self.dict_crop[self.count][1:][0][0]
            self.end_point = self.dict_crop[self.count][1:][0][1]
            self.img = self.img[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
            print('crop init', self.dict_crop)
            self.img = cv2.resize(self.img, (self.img_width, self.img_height))
            self.pixmap = self.np2qi()
            self.display.setPixmap(self.pixmap)

    def sort_point(self):
        x_all = [self.start_point[0], self.end_point[0]]
        y_all = [self.start_point[1], self.end_point[1]]
        start_point_x = min(x_all)
        start_point_y = min(y_all)
        end_point_x = max(x_all)
        end_point_y = max(y_all)
        return (start_point_x, start_point_y), (end_point_x, end_point_y)

    def mousePressEvent(self, e):  # e ; QMouseEvent
        if Qt.LeftButton:
            print('BUTTON PRESS : LEFT')
            self.start_point = e.x() - self.list_view_w, e.y() - self.toolbar.height() - 10
            print(e.buttons())

    def mouseReleaseEvent(self, e):  # e ; QMouseEvent
        if Qt.LeftButton:
            if self.crop_check == 0:
                print('BUTTON RELEASE: LEFT')
                self.end_point = e.x() - self.list_view_w, e.y() - self.toolbar.height() - 10
                self.check = 0
                self.start_point, self.end_point = self.sort_point()
                print('This is labels', self.dict_label[self.count])
                itms = self.result_view.list_box.selectedIndexes()
                print(itms)
                if not itms:
                    classes = 'None'
                else:
                    classes = itms[0].data()
                self.dict_label[self.count].append((self.start_point, self.end_point, classes))
                self.re_draw_box()
            else:
                print('crop')
                self.crop_check = 0
                self.end_point = e.x() - self.list_view_w, e.y() - self.toolbar.height() - 10
                self.crop_button.radio_button.setChecked(False)
                self.start_point, self.end_point = self.sort_point()
                self.img = self.img[self.start_point[1]:self.end_point[1], self.start_point[0]:self.end_point[0]]
                self.dict_crop[self.count].append((self.start_point, self.end_point))
                print('This is crop', self.dict_crop)
                self.img = cv2.resize(self.img, (self.img_width, self.img_height))
                self.pixmap = self.np2qi()
                self.display.setPixmap(self.pixmap)

    def load_file(self):
        # labels txt
        self.txt_labels = glob.glob(self.fname + '/' + 'labels.txt')
        if not self.txt_labels:
            self.dict_label = dict([(tmp, [self.file_list[tmp]]) for tmp in range(len(self.file_list))])
            print('I am crop', self.dict_label)
            print('init')
        else:
            f = open(self.txt_labels[0], 'r')
            data = f.read()
            f.close()
            print('load labels file')
            self.dict_label = eval(data)
            print(self.dict_label)
        # crop txt
        self.txt_crop = glob.glob(self.fname + '/' + 'crops.txt')
        if not self.txt_crop:
            self.dict_crop = dict([(tmp, [self.file_list[tmp]]) for tmp in range(len(self.file_list))])
            print('I am crop', self.dict_crop)
            print('init')
        else:
            f = open(self.txt_crop[0], 'r')
            data = f.read()
            f.close()
            print('load crop file')
            self.dict_crop = eval(data)
            print(self.dict_crop)
        # create directory for saving cropping img
        self.crop_img_dir_create()

    def save_file(self):
        f = open(self.fname + '/' + 'labels.txt', 'w')
        f.write(str(self.dict_label))
        f.close()
        print('labels save complete')

        f = open(self.crop_fname + '/' + 'labels.txt', 'w')
        f.write(str(self.dict_label_copy))
        f.close()
        print('labels copy save complete')

        f = open(self.fname + '/' + 'crops.txt', 'w')
        f.write(str(self.dict_crop))
        f.close()
        print('crop save complete')

    def load_classes(self):
        self.classes = []
        with open('classes.txt') as f:
            for line in f:
                self.classes.append(line.split('\n')[0])

    def test_check(self):
        if self.file_view.list_box.currentChanged():
            print('list item changed')

class list_widget(QWidget):
    def __init__(self, parent):
        super(list_widget, self).__init__(parent)
        self.list_box = QListView(self)

class radio_button(QWidget):
    def __init__(self, parent):
        super(radio_button, self).__init__(parent)
        self.radio_button = QRadioButton(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())