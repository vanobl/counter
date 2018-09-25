import sys
import os
import PySide2

from counter import Counter

if __name__ == '__main__':
    app = PySide2.QtWidgets.QApplication(sys.argv)
    mainwindow = Counter(os.path.join('faces', 'main.ui'))
    sys.exit(app.exec_())
