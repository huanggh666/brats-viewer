#--- Author: huanggh, HAI Studio
#--- contact: huanggh666@163.com
#--- 2018-5-26

import cv2
import subprocess
import send2trash
import numpy as np
import nibabel as nib
import sys, os, glob, time
import SimpleITK as sitk
from a_ui import Ui_MainWindow   # 导入生成.py里生成的类
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class Mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Mywindow,self).__init__()
        self.setupUi(self)
        # self.setCentralWidget(self.label)
        
        self.actionsaveas.triggered.connect(self.saveas)
        self.actionsave.triggered.connect(self.save)
        self.actiondel.triggered.connect(self.delete)
        self.actionfusion.triggered.connect(self.fusion)
        self.actiondel_et.triggered.connect(self.delete_et)
        self.actionnormalize.triggered.connect(self.normalize)
        self.actionlines.triggered.connect(self.focus_lines)
        self.actionnewwindow.triggered.connect(self.new_window)
        self.actionwt2tc.triggered.connect(self.wt2tc)
        self.actiontc2wt.triggered.connect(self.tc2wt)
        self.actionslicesave.triggered.connect(self.slice_save)

        self.current = ''
        self.show_lines = 1
        self.slice_save_flag = -1

    def file_open(self):
        file_dir = "E:\yan\dataset\BraTS\BRATS2017"
        if self.current:
            (file_dir, file_name) = os.path.split(self.current)
            
        img_name = QFileDialog.getOpenFileName(self, "打开", file_dir, '3D图像(*.nii *.nii.gz *.mha)')
        if img_name[0]:
            print(img_name[0])
            self.current = img_name[0]
            self.get_names()
            self.nii_read()
            
    def save(self):
        if self.current:
            img_nib = nib.AnalyzeImage(self.img_data.astype('int16'), None)
            nib.save(img_nib, self.current)
    
    def saveas(self):
        if self.current:
            filename = QFileDialog.getSaveFileName(self, "保存","E:/", 'imge(*.nii.gz *.nii)')
            if filename[0]:
                img_nib = nib.AnalyzeImage(self.img_data.astype('int16'), None)
                nib.save(img_nib, filename[0])


    def delete(self):
        if not self.current:
            return
        reply = QMessageBox.question(self,'删除','是否要删除{0}'.format(self.current),
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No) 
        if reply == QMessageBox.Yes:
            send2trash.send2trash('\\'.join(self.current.split('/')))
            if len(self.names) == 1:
                self.current = ''
                self.label_2.clear()
                self.label_3.clear()
                self.label_1.clear()
            else:
                self.next()
                self.get_names()


    def delete_et(self):
        if not self.current:
            return
        T = np.max(self.img_data)
        if T == 1 or T == 2 or T == 4:
            self.img_data[self.img_data == 4] = 1
            self.nii_show()
    
    def wt2tc(self):
        if not self.current:
            return
        T = np.max(self.img_data)
        if T == 1 or T == 2 or T == 4:
            self.img_data[self.img_data == 2] = 1
            self.nii_show()

    def tc2wt(self):
        if not self.current:
            return
        T = np.max(self.img_data)
        if T == 1 or T == 2 or T == 4:
            self.img_data[self.img_data == 1] = 2
            self.nii_show()

    def next(self):
        if not self.current:
            return
        if len(self.names) <= 1:
            return
        P = self.names.index(self.current) + 1
        if P > len(self.names) - 1:
            P = 0
        self.current = self.names[P]
        self.nii_read()
        
        
    def back(self):
        if not self.current:
            return
        if len(self.names) <= 1:
            return
        P = self.names.index(self.current)
        self.current = self.names[P - 1]
        self.nii_read()

            
    def nii_read(self):
        if os.path.isfile(self.current):
            if '.nii' in self.current:
                img_nib = nib.load(self.current)
                if len(img_nib.get_data().shape) != 3:
                    return
                self.img_data = img_nib.get_data()
                if self.img_data.min()<0:
                    mask = np.asarray(self.img_data==0, 'int')
                    self.img_data += self.img_data.min()
                    self.img_data = self.img_data * (1-mask)
                self.nii_show()
            elif '.mha' in self.current:
                img_mha = sitk.ReadImage(self.current)
                img_mha = sitk.GetArrayFromImage(img_mha)
                self.img_data = np.transpose(img_mha, [2,1,0])
                self.nii_show()

    def nii_show(self):
        if not self.current:
            return
        if len(self.img_data) == 2:
            self.img = (255 * (self.img_data[0] / self.img_data[0].max())).astype('uint8')
            slice_img_1, slice_img_2, slice_img_3 = self.nii_slice()
            self.img = (255 * (self.img_data[1] / 4)).astype('uint8')
            slice_seg_1, slice_seg_2, slice_seg_3 = self.nii_slice()
            self.fusion_show(slice_img_1, slice_seg_1, self.label_1)
            self.fusion_show(slice_img_2, slice_seg_2, self.label_2)
            self.fusion_show(slice_img_3, slice_seg_3, self.label_3)
        else:
            T = np.max(self.img_data)
            if T == 1 or T == 2 or T == 3 or T == 4:
                s1 = (self.img_data == 1).sum()
                s2 = (self.img_data == 2).sum()
                s4 = (self.img_data == 4).sum()
                self.label_7.setText('value 1:{0}, 2:{1}, 4:{2}'.format(s1, s2, s4))
                self.img = (255 * (self.img_data / 4)).astype('uint8')
                slice_1, slice_2, slice_3 = self.nii_slice()
                self.nii_seg_show(slice_1, self.label_1)
                self.nii_seg_show(slice_2, self.label_2)
                self.nii_seg_show(slice_3, self.label_3)
            else:
                self.label_7.setText('value max:{0}'.format(T))
                self.img = (255 * (self.img_data / T)).astype('uint8')
                slice_1, slice_2, slice_3 = self.nii_slice()
                self.nii_modal_show(slice_1, self.label_1)
                self.nii_modal_show(slice_2, self.label_2)
                self.nii_modal_show(slice_3, self.label_3)

    def nii_slice(self):
        x = self.spinBox.value()
        y = self.spinBox_2.value()
        z = self.spinBox_3.value()
        slice_1 = self.img[x,:,:]
        slice_1 = self.slice_tag(slice_1, y, z)
        self.label_4.setText('sagittal slice:{0} '.format(x)+str(slice_1.shape))
        slice_2 = self.img[:,y,:].copy()
        slice_2 = self.slice_tag(slice_2, x, z)
        self.label_5.setText('coronal slice:{0} '.format(y)+str(slice_2.shape))
        slice_3 = self.img[:,:,z].copy()
        slice_3 = self.slice_tag(slice_3, x, y)
        self.label_6.setText('axial slice:{0} :'.format(y)+str(slice_3.shape))
        return slice_1, slice_2, slice_3

    def slice_tag(self, slice_i, i1, i2):
        if self.show_lines == 1:
            slice_i[i1,:] = 80
            slice_i[:,i2] = 80
        return slice_i
    
    def focus_lines(self):
        self.show_lines = self.show_lines * -1
        self.nii_show()
    
    def normalize(self):
        if not self.current:
            return
        if len(self.img_data) == 2:
            return
        T = self.img_data.max()
        if T == 1 or T == 2 or T == 4:
            return
        pixels = self.img_data[self.img_data > 0]
        mean = pixels.mean()
        std = pixels.std()
        img = (self.img_data - mean) / std
        img = img - img.min()
        self.img_data[self.img_data > 0] = img[self.img_data > 0]
        self.nii_show()
        
    
    def fusion(self):
        if not self.current:
            return
        if self.img_data.max() < 10:
            return
        if len(self.img_data) == 2:
            return
        file_dir = "E:\Master\dataset\BraTS\BRATS2017"
        if self.current:
            (file_dir, file_name) = os.path.split(self.current)
        img_name = QFileDialog.getOpenFileName(self, "打开", file_dir, '图像(*.nii *.nii.gz)')
        if img_name[0]:
            seg = nib.load(img_name[0]).get_data()
            if seg.max() < 10:
                self.img_data = np.stack([self.img_data, seg])
                self.nii_show()
    
    def slice_save(self):
        if not self.current:
            return
        self.slice_save_flag = 0
        self.nii_show()
        self.statusBar().showMessage("Slice have been saved in desktop!!!")
        self.slice_save_flag = -1
        
    def slice_save_dependon_flag(self, img):
        if self.slice_save_flag >=0:
            if len(img.shape) == 2:
                desktoppath = os.path.join(os.path.expanduser("~"), 'Desktop')
                cv2.imwrite(f'{desktoppath}/{self.slice_save_flag}.png', img)
                self.slice_save_flag += 1
            elif len(img.shape)==3 and img.shape[-1]==3:
                img_save = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                desktoppath = os.path.join(os.path.expanduser("~"), 'Desktop')
                cv2.imwrite(f'{desktoppath}/{self.slice_save_flag}.png', img_save)
                self.slice_save_flag += 1
                self.statusBar().showMessage("slice have saved !!!")

    def nii_modal_show(self, slice, label):
        img = np.rot90(slice).copy()
        img_h, img_w = img.shape
        if img_w >= 200 and img_h >= 200:
            img = slice.copy()
            img = cv2.arrowedLine(img, (10,10), (10,20), 80)
            img = cv2.arrowedLine(img, (10,10), (20,10), 80)
        else:
            img = cv2.arrowedLine(img, (10,img_h-1-10), (20,img_h-1-10), 80)
            img = cv2.arrowedLine(img, (10,img_h-1-10), (10,img_h-1-20), 80)
        self.slice_save_dependon_flag(img)
        Qimg = QImage(img, img_w, img_h, img_w, QImage.Format_Grayscale8)
        if img_h > label.height() or img_w > label.width():
            if img_h/label.height() > img_w/label.width():
                Qimg = Qimg.scaled(int(label.height()*img_w/img_h), label.height())
            else:
                Qimg = Qimg.scaled(label.width(), int(label.width()*img_h / img_w))
        label.setPixmap(QtGui.QPixmap.fromImage(Qimg))
        (file_dir, file_name) = os.path.split(self.current)
        self.statusBar().showMessage(file_name)                  

    def nii_seg_show(self, slice, label):
        img = np.rot90(slice).copy()
        img_h, img_w = img.shape
        if img_w >= 200 and img_h >= 200:
            img = slice.copy()
            img = cv2.arrowedLine(img, (10,10), (10,20), 80)
            img = cv2.arrowedLine(img, (10,10), (20,10), 80)
        else:
            img = cv2.arrowedLine(img, (10,img_h-1-10), (20,img_h-1-10), 80)
            img = cv2.arrowedLine(img, (10,img_h-1-10), (10,img_h-1-20), 80)
        mask = img == 0
        img = cv2.applyColorMap(img, cv2.COLORMAP_RAINBOW)
        img[mask] = 0
        self.slice_save_dependon_flag(img)
        Qimg = QImage(img, img_w,img_h, img_w*3, QImage.Format_RGB888) 
        if img_h > label.height() or img_w > label.width():
            if img_h/label.height() > img_w / label.width():
                Qimg = Qimg.scaled(int(label.height()*img_w/img_h), label.height())
            else:
                Qimg = Qimg.scaled(label.width(), int(label.width()*img_h / img_w))
        label.setPixmap(QtGui.QPixmap.fromImage(Qimg))
        (file_dir, file_name) = os.path.split(self.current)
        self.statusBar().showMessage(file_name)

    def fusion_show(self, img, seg, label):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        seg_mask = cv2.cvtColor(seg, cv2.COLOR_GRAY2BGR)
        seg = cv2.applyColorMap(seg, cv2.COLORMAP_RAINBOW)
        img[seg_mask > 0] = seg[seg_mask > 0]
        fusion = np.rot90(img).copy()
        img_h, img_w = fusion.shape[:2]
        if img_w >= 200 and img_h >= 200:
            fusion = img.copy()
            fusion = cv2.arrowedLine(fusion, (10,10), (10,20), 200)
            fusion = cv2.arrowedLine(fusion, (10,10), (20,10), 200)
        else:
            fusion = cv2.arrowedLine(fusion, (10,img_h-1-10), (20,img_h-1-10), 200)
            fusion = cv2.arrowedLine(fusion, (10,img_h-1-10), (10,img_h-1-20), 200)
        self.slice_save_dependon_flag(img)
        Qimg = QImage(fusion, img_w,img_h, img_w*3, QImage.Format_RGB888) 
        if img_h > label.height() or img_w > label.width():
            if img_h/label.height() > img_w / label.width():
                Qimg = Qimg.scaled(label.height()*img_w // img_h, label.height())
            else:
                Qimg = Qimg.scaled(label.width(), label.width()*img_h // img_w)
        label.setPixmap(QtGui.QPixmap.fromImage(Qimg))


    def label_contain_mouse(self, label, pos):
        pos_label = label.geometry()
        pos_label.setX(pos_label.x())
        pos_label.setY(pos_label.y() + 56)
        pos_label.setWidth(label.geometry().width())
        pos_label.setHeight(label.geometry().height())
        if pos_label.contains(pos):
            return (pos.x() - pos_label.x(), pos.y() - pos_label.y())
        else:
            return (0,0)

            
    def nii_mouse(self, pos):
        y, z = self.label_contain_mouse(self.label_1, pos)
        if y:
            self.spinBox_2.setValue(y)
            self.spinBox_3.setValue(154 - z)
            return
        x, z = self.label_contain_mouse(self.label_2, pos)
        if x:
            self.spinBox.setValue(x)
            self.spinBox_3.setValue(154 - z)
            return
        x, y = self.label_contain_mouse(self.label_3, pos)
        if x:
            self.spinBox.setValue(y)
            self.spinBox_2.setValue(x)
            return
            
  
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.nii_mouse(event.pos())

    def get_names(self):
        (file_dir, file_name) = os.path.split(self.current)
        (name_part, name_ext) = os.path.splitext(file_name)
        self.names = self.names_change(glob.glob(file_dir + '/*' + name_ext))
                      
            
    def names_change(self,names):
        re_names = []
        for name in names:
            (file_dir, file_name) = os.path.split(name)
            re_names.append(file_dir + '/' + file_name)
        return re_names
        
    @staticmethod
    def new_window():
        subprocess.Popen(['pythonw', 'a.pyw'])
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Mywindow()
    window.show()
    
    if len(sys.argv) >= 2:
        window.img_current = sys.argv[1]
        window.img_read()
        window.get_img_names()
    sys.exit(app.exec_())
