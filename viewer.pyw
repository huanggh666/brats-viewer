#--- Author: huanggh, HAI Studio
#--- contact: huanggh666@163.com
#--- date: 2018-5-26 
#--- envirnment: python3.6 or later
import glob
import os
import subprocess
import sys
import time
import zipfile

import cv2
import nibabel as nib
import numpy as np
import send2trash
import SimpleITK as sitk
import win32clipboard
import win32con
from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from scipy import ndimage as ndimg

from viewer_ui import Ui_MainWindow  # 导入生成.py里生成的类
from textviewer import WText, set_text_to_clipboard

class Mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Mywindow,self).__init__()
        self.setupUi(self)
        # self.setCentralWidget(self.label)

        self.actionsaveas.triggered.connect(self.saveas)
        self.actionsave.triggered.connect(self.save)
        self.actiondel.triggered.connect(self.delete)
        self.actionfusion.triggered.connect(self.fusion)
        self.actionnormalize.triggered.connect(self.normalize)
        self.actionlines.triggered.connect(self.focus_lines)
        self.actionnewwindow.triggered.connect(self.new_window)
        self.actionet2tc.triggered.connect(self.et2tc)
        self.actiontc2wt.triggered.connect(self.tc2wt)
        self.actionwt2et.triggered.connect(self.wt2et)
        self.actionslicesave.triggered.connect(self.slice_save)
        self.actionarrows.triggered.connect(self.show_arrow_func)
        # self.actiondirectory.triggered.connect(self.open_directory)

        self.horizontalSlider.hide()
        self.spinBox_4.hide()
        self.setAcceptDrops(True)
        self.current = ''
        self.show_lines = 1
        self.show_arrow = 1
        self.slice_save_flag = -1
        self.w_dict = {'w1':None, 'w2':None, 'w3':None, 'w4':None,}

    def file_open(self):
        file_dir = "E:\yan\dataset\BraTS"
        if self.current:
            (file_dir, file_name) = os.path.split(self.current)
            
        get_filename = QFileDialog.getOpenFileName(self, "打开", file_dir, 
                        '3D图像(*.nii *.nii.gz *.mha);;文件(*.zip *.txt)')
        if get_filename[0] != '':
            if get_filename[1] == '3D图像(*.nii *.nii.gz *.mha)':
                print(get_filename[0])
                self.current = get_filename[0].replace('\\', '/')
                self.get_names()
                self.nii_read()
            elif get_filename[1] == '文件(*.zip *.txt)':
                self.open_in_textviewer(get_filename[0])
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
             event.acceptProposedAction()
             
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            filename = event.mimeData().urls()[0].toLocalFile()
            if '.nii' in filename or '.mha' in filename:
                self.current = filename
                self.get_names()
                self.nii_read()
            elif (filename.endswith('.zip') or filename.endswith('.txt')
                  or os.path.isdir(filename)):
                self.open_in_textviewer(filename)

    def open_in_textviewer(self, filename):
        isfull = True
        for widx in range(1, 5):
            if self.w_dict['w'+str(widx)] is None:
                self.w_dict['w'+str(widx)] = WText(filename)
                self.w_dict['w'+str(widx)].open_file()
                self.w_dict['w'+str(widx)].show()
                isfull = False
                break
        if isfull:
            for widx in range(1, 5):
                if self.w_dict['w'+str(widx)].isHidden():
                    self.w_dict['w'+str(widx)].open_file(filename)
                    self.w_dict['w'+str(widx)].show()
                    isfull = False
                    break
            if isfull:
                QMessageBox.information(self, '提示', 
                        '4 text viewers are shown, please close some!!!')
        
    def save(self):
        if self.current:
            reply = QMessageBox.question(self,'保存','保存会覆盖当前文件，是否保存？',
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.No) 
            if reply == QMessageBox.Yes:
                img_nib = nib.AnalyzeImage(self.img_data.astype('int16'), None)
                nib.save(img_nib, self.current)
    
    def saveas(self):
        if self.current:
            desktoppath = os.path.join(os.path.expanduser("~"), 'Desktop')
            file_name = os.path.basename(self.current)
            full_path = f'{desktoppath}/{file_name}'
            filename = QFileDialog.getSaveFileName(self, "保存", full_path, 'imge(*.nii.gz *.nii)')
            if filename[0]:
                img_nib = nib.AnalyzeImage(self.img_data.astype('int16'), None)
                nib.save(img_nib, filename[0])


    def delete(self):
        if self.check_status() == None:
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


    def et2tc(self):
        if self.check_status() == 'label':
            self.img_data[self.img_data == 4] = 1
            self.nii_show()

    def tc2wt(self):
        if self.check_status() == 'label':
            self.img_data[self.img_data == 1] = 2
            self.nii_show()
    
    def wt2et(self):
        if self.check_status() == 'label':
            self.img_data[self.img_data == 2] = 4
            self.nii_show()

    def next(self):     
        '下一个图像'
        if self.check_status() == None:
            return
        if len(self.names) <= 1:
            return
        P = self.names.index(self.current) + 1
        if P > len(self.names) - 1:
            P = 0
        self.current = self.names[P]
        self.nii_read()
        
        
    def back(self): 
        '上一个图像'
        if self.check_status() == None:
            return
        if len(self.names) <= 1:
            return
        P = self.names.index(self.current)
        self.current = self.names[P - 1]
        self.nii_read()

            
    def nii_read(self):     
        '读取.nii或者.mha图像'
        # print(self.current)#--------------
        if os.path.isfile(self.current):
            if self.current.endswith('.nii.gz') or self.current.endswith('.nii.gz'):
                img_nib = nib.load(self.current)
                dim = len(img_nib.get_data().shape)
                if dim != 3 and dim != 4:
                    return
                self.img_data = img_nib.get_data()
                if self.img_data.min()<0:
                    mask = np.array(self.img_data==0, np.uint8)
                    self.img_data = self.img_data - self.img_data.min()
                    self.img_data = self.img_data * (1-mask)
                self.nii_show()
            elif self.current.endswith('.mha'):
                img_mha = sitk.ReadImage(self.current)
                img_mha = sitk.GetArrayFromImage(img_mha)
                self.img_data = np.transpose(img_mha, [2,1,0])
                self.nii_show()
                
    def check_status(self):
        if not self.current:
            return None
        elif len(self.img_data) == 2:
            return 'fusion'
        elif np.max(self.img_data) in [1, 2, 3, 4, 5] and np.min(self.img_data) == 0:
            return 'label'
        else:
            return 'modal'
    
    def nii_show(self):
        status = self.check_status()
        if status == 'fusion':
            self.horizontalSlider.show()
            self.spinBox_4.show()
            self.img = (255 * (self.img_data[0] / self.img_data[0].max())).astype('uint8')
            slice_img_1, slice_img_2, slice_img_3 = self.nii_slice()
            self.img = (255 * (self.img_data[1] / 4)).astype('uint8')
            slice_seg_1, slice_seg_2, slice_seg_3 = self.nii_slice()
            self.fusion_show(slice_img_1, slice_seg_1, self.label_1)
            self.fusion_show(slice_img_2, slice_seg_2, self.label_2)
            self.fusion_show(slice_img_3, slice_seg_3, self.label_3)
        elif status == 'label':
            self.horizontalSlider.hide()
            self.spinBox_4.hide()
            s1 = (self.img_data == 1).sum()
            s2 = (self.img_data == 2).sum()
            s4 = (self.img_data == 4).sum()
            self.label_7.setText('value 1:{0}, 2:{1}, 4:{2}'.format(s1, s2, s4))
            self.img = (255 * (self.img_data / 4)).astype('uint8')
            slice_1, slice_2, slice_3 = self.nii_slice()
            self.nii_seg_show(slice_1, self.label_1)
            self.nii_seg_show(slice_2, self.label_2)
            self.nii_seg_show(slice_3, self.label_3)
        elif status == 'modal':
            self.horizontalSlider.hide()
            self.spinBox_4.hide()
            T = np.max(self.img_data)
            self.label_7.setText('value max:{0}'.format(T))
            if self.img_data.min()<0:
                mask = np.array(self.img_data==0, np.uint8)
                self.img_data = self.img_data - self.img_data.min()
                self.img_data = self.img_data * (1-mask)
                T = T - self.img_data.min()
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
        self.show_lines = 1- self.show_lines
        self.nii_show()
    
    def show_arrow_func(self):
        self.show_arrow = 1 - self.show_arrow
        self.nii_show()
        
    def normalize(self):
        if self.check_status() == 'modal':
            pixels = self.img_data[self.img_data > 0]
            mean = pixels.mean()
            std = pixels.std()
            img = (self.img_data - mean) / std
            img = img - img.min()
            self.img_data[self.img_data > 0] = img[self.img_data > 0]
            self.nii_show()
        
    
    def fusion(self):
        def read_data(filename):
            if filename.endswith('.nii') or filename.endswith('.nii.gz'):
                img_nib = nib.load(filename)
                if len(img_nib.get_data().shape) != 3:
                    return
                return img_nib.get_data()
            elif filename.endswith('.mha'):
                img_mha = sitk.ReadImage(filename)
                img_mha = sitk.GetArrayFromImage(img_mha)
                img_mha = np.transpose(img_mha, [2,1,0])
                return img_mha
        chk_state = self.check_status()
        if chk_state == 'label' or chk_state == 'modal':
            file_dir = "E:\yan\dataset\BraTS"
            if self.current:
                (file_dir, file_name) = os.path.split(self.current)
            img_name = QFileDialog.getOpenFileName(self, "打开", file_dir, '图像(*.nii *.nii.gz *.mha)')
            if img_name[0]:
                data = read_data(img_name[0])
                if chk_state == 'modal':
                    self.img_data = np.stack([self.img_data, data])
                elif chk_state == 'label':
                    self.img_data = np.stack([data, self.img_data])
                self.nii_show()
    
    def slice_save(self):
        if self.check_status() == None:
            return
        self.slice_save_flag = 0
        self.nii_show()
        self.statusBar().showMessage("Slice have been saved in desktop!!!")
        self.slice_save_flag = -1
        
    def slice_save_depend_on_flag(self, img):
        if self.slice_save_flag >= 0:
            desktoppath = os.path.join(os.path.expanduser("~"), 'Desktop')
            slice_ls = [self.spinBox.value(),self.spinBox_2.value(),self.spinBox_3.value()]
            dire_ls = ['sagittal','coronal','axial']
            file_dir, file_name = os.path.split(self.current)
            namepart = file_name.split('.')[0]
            save_path = f'{desktoppath}/{namepart}_{dire_ls[self.slice_save_flag]}_{slice_ls[self.slice_save_flag]}.png'
            if len(img.shape) == 2:
                cv2.imwrite(save_path, img)
                self.slice_save_flag += 1   #;print(save_path)
            elif len(img.shape)==3 and img.shape[-1]==3:
                img_save = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                cv2.imwrite(save_path, img_save)
                self.slice_save_flag += 1

    def nii_modal_show(self, slice, label):
        img = np.rot90(slice).copy()
        img_h, img_w = img.shape
        if img_w >= 200 and img_h >= 200:
            img = slice.copy()
            if self.show_arrow:
                img = cv2.arrowedLine(img, (10,10), (10,20), 80)
                img = cv2.arrowedLine(img, (10,10), (20,10), 80)
        elif self.show_arrow:
            img = cv2.arrowedLine(img, (10,img_h-1-10), (20,img_h-1-10), 80)
            img = cv2.arrowedLine(img, (10,img_h-1-10), (10,img_h-1-20), 80)
        self.slice_save_depend_on_flag(img)
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
            if self.show_arrow:
                img = cv2.arrowedLine(img, (10,10), (10,20), 80)
                img = cv2.arrowedLine(img, (10,10), (20,10), 80)
        elif self.show_arrow:
            img = cv2.arrowedLine(img, (10,img_h-1-10), (20,img_h-1-10), 80)
            img = cv2.arrowedLine(img, (10,img_h-1-10), (10,img_h-1-20), 80)
        mask = img == 0
        img = cv2.applyColorMap(img, cv2.COLORMAP_RAINBOW)
        img[mask] = 0
        self.slice_save_depend_on_flag(img)
        Qimg = QImage(img, img_w,img_h, img_w*3, QImage.Format_RGB888) 
        if img_h > label.height() or img_w > label.width():
            if img_h/label.height() > img_w / label.width():
                Qimg = Qimg.scaled(int(label.height()*img_w/img_h), label.height())
            else:
                Qimg = Qimg.scaled(label.width(), int(label.width()*img_h / img_w))
        label.setPixmap(QtGui.QPixmap.fromImage(Qimg))
        file_dir, file_name = os.path.split(self.current)
        self.statusBar().showMessage(file_name)

    def fusion_show(self, img, seg, label):
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        seg_mask = cv2.cvtColor(seg, cv2.COLOR_GRAY2BGR)
        seg = cv2.applyColorMap(seg, cv2.COLORMAP_RAINBOW)
        alpha = self.spinBox_4.value()/100
        img[seg_mask > 0] = ((1-alpha)*img[seg_mask > 0] + alpha*seg[seg_mask > 0]).astype('uint8')
        fusion = np.rot90(img).copy()
        img_h, img_w = fusion.shape[:2]
        if img_w >= 200 and img_h >= 200:
            fusion = img.copy()
            if self.show_arrow:
                fusion = cv2.arrowedLine(fusion, (10,10), (10,20), 200)
                fusion = cv2.arrowedLine(fusion, (10,10), (20,10), 200)
        elif self.show_arrow:
            fusion = cv2.arrowedLine(fusion, (10,img_h-1-10), (20,img_h-1-10), 200)
            fusion = cv2.arrowedLine(fusion, (10,img_h-1-10), (10,img_h-1-20), 200)
        self.slice_save_depend_on_flag(img)
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
        file_dir, file_name = os.path.split(self.current)
        name_part, name_ext = os.path.splitext(file_name)
        self.names = glob.glob(f'{file_dir}/*{name_ext}')
        self.names = [x.replace('\\', '/') for x in self.names]
            
    @staticmethod
    def new_window():
        path_sys = sys.argv[0]
        if path_sys.endswith('.pyw') or path_sys.endswith('.py'):
            subprocess.Popen(['pythonw', path_sys])
        elif path_sys.endswith('.exe'):
            subprocess.Popen(path_sys)
    
    def closeEvent(self, event):
        event.accept()
        os._exit(0)


class ExtendWindow(Mywindow):
    def __init__(self):
        super().__init__()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.context_menu = QtWidgets.QMenu(self)
        self.menu_copy_path = self.context_menu.addAction('复制路径')
        self.menu_samesp = self.context_menu.addAction('同步样本')
        self.menu_nextsp = self.context_menu.addAction('下一样本')
        self.menu_copy_path.triggered.connect(self.copy_path)
        self.menu_samesp.triggered.connect(self.same_sample)
        self.menu_nextsp.triggered.connect(self.next_sample)
        
        self.actiondirectory.triggered.connect(self.open_directory)
        self.actionopeninnew.triggered.connect(self.open_in_new)
        self.actionsaveslinum.triggered.connect(self.save_view)
        self.actionrestoreslinum.triggered.connect(self.restore_slice_num)
        self.actionrmregion.triggered.connect(self.remove_region)
        self.actionrmlabel.triggered.connect(self.remove_label)
        self.actionrmfocus.triggered.connect(self.remove_focus_region)
        self.actionnextsp.triggered.connect(self.next_sample)
        self.actionlastsp.triggered.connect(self.last_sample)
        self.actionsamesp.triggered.connect(self.same_sample)
        self.actionhist.triggered.connect(self.histotram)
        self.actioncopy_path.triggered.connect(self.copy_path)
        self.actionclearview.triggered.connect(self.clearview)
        
        self.remove_region_flag = False
        self.remove_label_flag = False
        
    def show_menu(self, pos):
        self.context_menu.exec_(QtGui.QCursor.pos())
        
    def next_sample(self):
        self.next_last(num_add=1)
        
    def last_sample(self):
        self.next_last(num_add = -1)
        
    def next_last(self, num_add=1):
        # E:/yan/dataset/BraTS/BRATS2017/Brats17ValidationData Brats17_CBICA_AAM_1
        if self.check_status() == None:
            return
        dir, fname = os.path.split(self.current)
        pdir, dir = os.path.split(dir)
        file_names = glob.glob(f'{pdir}/{dir[:7]}*/*{fname[-11:]}')
        file_names = [x.replace('\\', '/') for x in file_names]
        n = len(file_names)
        if n <= 1:
            return
        idx_current = file_names.index(self.current)
        idx = idx_current + num_add
        if idx >= n:
            idx = 0
        self.current = file_names[idx]
        self.get_names()
        self.nii_read()
        
    def clearview(self):
        self.current = ''
        for i in range(1,4):
            getattr(self, f'label_{i}').clear()
        self.label_4.setText('sagittal')
        self.label_5.setText('coronal')
        self.label_6.setText('axial')
        
    def open_directory(self):
        full_path = self.current
        dir, filename = os.path.split(full_path)
        os.startfile(dir)
        # subprocess.Popen(['start explorer', dir])
    
    def open_in_new(self):
        if self.check_status() == None:
            self.new_window()
        x = self.spinBox.value()
        y = self.spinBox_2.value()
        z = self.spinBox_3.value()
        subprocess.Popen(['pythonw', sys.argv[0], self.current, str(x), str(y), str(z)])
        
    def save_view(self):
        x = self.spinBox.value()
        y = self.spinBox_2.value()
        z = self.spinBox_3.value()
        vd = dict(x=x, y=y, z=z, current=self.current)
        with open('viewinfo', 'w') as file:
            file.write(str(vd))
        self.statusBar().showMessage('viewinfo have saved !')
            
    def restore_slice_num(self):
        if os.path.isfile('viewinfo'):
            with open('viewinfo', 'r') as file:
                vd = eval(file.read())
            self.spinBox.setValue(vd['x'])
            self.spinBox_2.setValue(vd['y'])
            self.spinBox_3.setValue(vd['z'])
            
    def same_sample(self):
        if self.check_status() == None:
            return
        with open('viewinfo','r') as file:
            vd = eval(file.read())
        dir, fname = os.path.split(vd['current'])
        cdir, cfname = os.path.split(self.current)
        if os.path.isfile(f'{cdir}/{fname}'):
            self.current = f'{cdir}/{fname}'
            self.nii_read()
            self.restore_slice_num()
    
    def remove_focus_region(self):
        if self.show_lines != 1:
            return
        if self.check_status() == 'label':
            x = self.spinBox.value()
            y = self.spinBox_2.value()
            z = self.spinBox_3.value()
            mask = np.asarray(self.img_data>0, np.uint8)
            label, num = ndimg.label(mask)
            value = label[x,y,z]
            if value == 0:
                return
            mask = np.asarray(label==value, np.uint8)
            self.img_data = self.img_data * (1-mask)
            self.nii_show()
    
    def remove_label(self):     
        '移除标签触发函数'
        if self.check_status() == 'label':
            self.remove_label_flag = True
            self.remove_region()
        
    def remove_region(self):        
        '移除连通域触发函数'
        if self.check_status() == 'label':
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.remove_region_flag = True
        
    def remove_region_op(self, pos):        
        '移除标签或连通域执行函数'
        def op(x,y,z):
            if self.remove_label_flag:      #---移除标签，否则移除连通域
                self.remove_label_flag = False
                self.img_data[self.img_data == self.img_data[x,y,z]] = 0
                self.nii_show()
                return
            mask = np.asarray(self.img_data>0, np.uint8)
            label, num = ndimg.label(mask)
            value = label[x,y,z]
            if value == 0:
                return
            mask = np.asarray(label==value, np.uint8)
            self.img_data = self.img_data * (1-mask)
            self.nii_show()
        y, z = self.label_contain_mouse(self.label_1, pos)
        if y:
            x = self.spinBox.value()
            op(x,y,154-z)
            return
        x, z = self.label_contain_mouse(self.label_2, pos)
        if x:
            y = self.spinBox_2.value()
            op(x,y,154-z)
            return
        x, y = self.label_contain_mouse(self.label_3, pos)
        if x:
            z = self.spinBox_3.value()
            op(y,x,z)
            return
        
    def mouseReleaseEvent(self, event):     
        '重写鼠标事件函数'
        if event.button() == QtCore.Qt.LeftButton:
            if self.remove_region_flag:
                self.remove_region_flag = False
                self.remove_region_op(event.pos())
                self.setCursor(QtCore.Qt.ArrowCursor)
            else:
                self.nii_mouse(event.pos())
            
    def histotram(self):
        if self.check_status() == 'modal':
            M = self.img_data.max()
            hist = ndimg.histogram(self.img_data, 1, M, M-1)
            plt.bar(range(1,M), hist, color='r')
            plt.title('Histogram')
            plt.show()
            
    def copy_path(self):
        if self.current:
            path = self.current
            set_text_to_clipboard(path)
            QMessageBox.information(self, '提示', f'已复制文件路径:{path}')
            

def setting(window):
    window.current = sys.argv[1]
    window.get_names()
    window.nii_read()
    if len(sys.argv) >= 5:
        x = int(sys.argv[2])
        y = int(sys.argv[3])
        z = int(sys.argv[4])
        window.spinBox.setValue(x)
        window.spinBox_2.setValue(y)
        window.spinBox_3.setValue(z)

def run():
    app = QtWidgets.QApplication(sys.argv)
    window = ExtendWindow()
    window.show()

    if len(sys.argv) >= 2:
        if os.path.isfile(sys.argv[1]):
            setting(window)
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
