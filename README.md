## brats-viewer update 19.8.7
* To facilitate getting the mean dice scores of the results downloaded online, a feature that draging the directory to the mainwindow to find the zip file automatically is added.

## brats-viewer update 
* ".mha" files of brats2015 are supported to open.
* Dragentering file is supported. We can drag supported file to mainwindow to open it conveniently.
* We can drag supported the zipfile downloaded online from BraTS servers to mainwindow to conveniently get mean line. The mean line is shown in another widget and it is copied  to clipboard.
* Add contex menu.
![Image text](https://github.com/ihuanggh/brats17-viewer/blob/master/source/ui.png)

## brats-viewer  0.1 
A python program for reading the brats 2017 and 2018 dataset based on pyqt5.  
Just run anii.pyw with command "python anii.pyw".  
Or change the filename "anii.pyw" to "anii.py" then run it.  
Besides, you can set "pythonw.exe" as default application to open "anii.pyw". In this case, you can run it by double click on mouse without any console shown in the screen.  
The interface is shown below.  
![Image text](https://github.com/ihuanggh/brats17-viewer/blob/master/source/interface.png)

If you want to change the UI form, you should use "pyuic5" and "pyrcc5" to reconstruct the UI files.