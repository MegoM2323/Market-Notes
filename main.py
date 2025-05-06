import subprocess
import sys

try:
    import sqlite3
    import pandas as pd
    from datetime import datetime
    import yfinance as yf
    from PyQt5 import QtGui, QtWidgets, uic, QtCore
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTreeWidgetItemIterator, QMenu, QMenuBar, \
        QFileDialog, QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QMessageBox
    import investpy
    import pandas_datareader as web
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt
except:
    for library in ["datetime", "PyQt5", "time", "yfinance", "sqlite3, 'pandas', 'investpy', 'pandas_datareader, 'matplotlib"]:
        subprocess.run(["pip install", library])
    import sqlite3
    import yfinance as yf
    import pandas as pd
    from datetime import datetime
    from PyQt5 import QtGui, QtWidgets, uic, QtCore
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTreeWidgetItemIterator, QMenu, QMenuBar, \
        QFileDialog, QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QMessageBox
    import investpy
    import pandas_datareader as web
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
    def get_current(self):
        name = self.text_name.text()
        text = self.text_field.toPlainText()
        time = self.get_now_time()
        tag = 'nan'
        return name, text, tag, time

    def set_current(self, data):
        self.text_name.setText(str(data[0]))
        self.text_field.setText(str(data[1]))

    def get_now_time(self):
        res = str(datetime.now())[:-7]
        return res

    def create_note(self):
        self.save_note()
        self.set_current(('', '', 'nan'))

    def save_note(self):
        data = self.get_current()
        if data[0] != '':
            if data[0] != '':
                self.cur.execute('INSERT INTO notes VALUES(?, ?, ?, ?) ', data)
                self.db.commit()
                self.update_list()

    def select_note(self):
        element = self.tree_notes.currentItem().text(0)
        data = self.cur.execute('SELECT * FROM notes WHERE name=?', [element]).fetchall()[0]
        self.set_current(data)

    def delete_note(self):
        try:
            element = self.tree_notes.selectedItems()[0].text(0)
            self.cur.execute('DELETE FROM notes WHERE name=?', [element])
            self.db.commit()
            self.update_list()
            self.set_current(('', ''))
        except:
            pass

    def update_list(self):
        self.tree_notes.clear()
        data = self.cur.execute('SELECT * FROM notes').fetchall()
        data = list(map(lambda x: [str(x[0]), str(x[-1])], data))
        for el in data:
            a = QtWidgets.QTreeWidgetItem(self.tree_notes, el)
            self.tree_notes.addTopLevelItem(a)

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self)[0]
        with open(file_name, 'r', encoding='utf-8') as f:
            data = f.read()
            self.text_field.setText(data)

    def quit(self):
        self.save_note()
        app.closeAllWindows()

    @QtCore.pyqtSlot()
    def menu_bar_action(self):
        action = self.sender()
        if action.text() == 'Сохранить как':
            self.save_note()
        elif action.text() == 'Открыть':
            self.open_file()
        elif action.text() == 'Выйти':
            self.quit()

    def keyPressEvent(self, event):
        if int(event.modifiers()) == 67108864:
            if event.key() == QtCore.Qt.Key_S:
                self.save_note()
            elif event.key() == QtCore.Qt.Key_O:
                self.open_file()
            elif event.key() == QtCore.Qt.Key_Q:
                self.quit()
            elif event.key() == QtCore.Qt.Key_P:
                self.close_all_graphs()
            elif event.key() == QtCore.Qt.Key_E:
                self.crate_graph()

    def crate_graph(self):
        symbol = self.symbol_text.text()
        ma_list = self.ma_text.text()
        tickers = self.tickers_text.text()
        tickers = tickers.split()
        bright = self.bright_counter.value()
        try:
            ma_list = list(map(int, ma_list.split(' ')))
        except:
            ma_list = []
        kwargs = {}
        kwargs['MA'] = ma_list
        kwargs['tickers'] = tickers
        kwargs['bright'] = bright
        if self.sma_check.checkState() == 2:
            kwargs['SMA'] = True
        else:
            kwargs['SMA'] = False
        if self.ema_check.checkState() == 2:
            kwargs['EMA'] = True
        else:
            kwargs['EMA'] = False
        if self.rsi_check.checkState() == 2:
            kwargs['RSI'] = True
        else:
            kwargs['RSI'] = False
        if self.log_check.checkState() == 2:
            kwargs['LOG'] = True
        else:
            kwargs['LOG'] = False
        try:
            graph = WindowGraph(symbol, **kwargs)
            graph.show()
            self.graphs.append(graph)
        except:
            pass

    def close_all_graphs(self):
        self.graphs = []

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.close_all_graphs()
        self.close()

    def __init__(self):
        super().__init__()
        uic.loadUi("Templates/01.ui", self)
        self.graphs = []
        self.db = sqlite3.connect('BASE.db')
        self.cur = self.db.cursor()
        self.setWindowTitle("MyNotes")
        self.new_btn.clicked.connect(self.create_note)
        self.save_btn.clicked.connect(self.save_note)
        self.delete_btn.clicked.connect(self.delete_note)
        self.tree_notes.currentItemChanged.connect(self.select_note)
        self.plot_btn.clicked.connect(self.crate_graph)
        self.close_all_btn.clicked.connect(self.close_all_graphs)
        self.about_pr_wiget = AboutPragramMenu()

        filemenu = QMenu('&Файл', self)
        filemenu1 = QMenu('&Сочетания клавиш', self)
        filemenu2 = QMenu('&О программе', self)
        self.menubar.addMenu(filemenu)
        self.menubar.addMenu(filemenu1)
        self.menubar.addMenu(filemenu2)

        filemenu1.addAction('Построить | Ctrl + E', self.crate_graph)
        filemenu1.addAction('Закрыть все графики | Ctrl + P', self.close_all_graphs)
        filemenu2.addAction('О программе', self.about_pr_wiget.show)
        filemenu.addAction('Сохранить', self.save_note)
        filemenu.addAction('Открыть', self.open_file)
        filemenu.addSeparator()
        filemenu.addAction('Выйти', self.quit)

        self.update_list()


class WindowGraph(QDialog):
    def __init__(self, symbol, **kwargs):
        self.symbol = symbol
        super(WindowGraph, self).__init__()
        self.setWindowTitle(self.symbol)
        self.plt = plt
        self.figure = self.plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.symbol_text = QLineEdit()

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot(**kwargs)

    def get_info(self, symbol):
        start = datetime(2015, 5, 1)
        end = datetime.now()
        exeptions = []
        try:
            data = yf.download(tickers=f'{symbol}-USD')
        except:
            try:
                data = web.DataReader(f"{symbol}-USD", "yahoo", start, end)
            except:
                try:
                    Investpy_Data_start = str(start).split()[0].split('-')[::-1]
                    Investpy_Data_end = str(end).split()[0].split('-')[::-1]
                    data = investpy.get_crypto_historical_data(crypto=symbol,
                                                           from_date='/'.join(Investpy_Data_start),
                                                           to_date='/'.join(Investpy_Data_end))
                except Exception:
                    Error('Ошибка получения информации')
            return None
        return data

    def create_sma(self, data, days):
        SMA = []
        value = sum(data[:days]) / days
        for i in range(days, len(data) - 1):
            SMA.append(value)
            value -= data[i - days] / days
            value += data[i + 1] / days
        return SMA

    def create_ema(self, data, days):
        EMA = []
        EMA.append(data[0])
        coef = 2 / (days + 1)
        for i in range(len(data) - 1):
            value = coef * data[i] + (1 - coef) * EMA[i - 1]
            EMA.append(value)
        return EMA

    def prepare_data(self, data, **kwargs):
        res_sl = {}
        limiter = 10 ** 10

        if kwargs['RSI']:
            delta = data.diff(1)
            delta.dropna(inplace=True)
            positive = delta.copy()
            negative = delta.copy()
            positive[positive < 0] = 0
            negative[negative > 0] = 0
            days = 14
            average_gain = positive.rolling(window=days).mean()
            average_loss = abs(negative.rolling(window=days).mean())
            relative_strenght = average_gain / average_loss
            RSI = 100 - (100 / (1 + relative_strenght))
            res_sl['RSI'] = RSI

        def create(STR):
            for el in kwargs['MA']:
                if STR == 'SMA':
                    res_sl[f'{STR}_{el}'] = self.create_sma(data, el)[-len(data):]
                elif STR == 'EMA':
                    res_sl[f'{STR}_{el}'] = self.create_ema(data, el)[-len(data):]

        if len(kwargs['MA']) > 0:
            if kwargs['EMA']:
                create('EMA')
            if kwargs['SMA']:
                create('SMA')
        for ticker in kwargs['tickers']:
            res_sl[f'{ticker}'] = self.get_info(ticker)['Close']
        for key in res_sl.keys():
            limiter = min(limiter, len(res_sl[key]))
        for key in res_sl.keys():
            res_sl[key] = res_sl[key][-limiter:]
        res_sl['REAL'] = data[-limiter:]
        res = pd.DataFrame(res_sl)
        return res

    def plot(self, **kwargs):
        data = self.get_info(str(self.symbol))
        if data.shape[0] == 0:
            self.close()
        data = data['Close']
        res = self.prepare_data(data, **kwargs)
        res.fillna(0)

        self.figure.clear()
        if kwargs['RSI']:
            ax1 = self.plt.subplot(211)
        else:
            ax1 = self.plt.subplot(111)
        ax1.set_title(self.symbol.upper())
        ax1.grid(True)
        if kwargs['LOG']:
            ax1.set_yscale('log')

        if kwargs['RSI']:
            ax2 = self.plt.subplot(212)
            ax2.plot(res.index, res['RSI'], color='lightgrey')
            ax2.axhline(y=0, linestyle='--', alpha=0.5, color='#ff0000')
            ax2.axhline(y=10, linestyle='--', alpha=0.5, color='#ffaa00')
            ax2.axhline(y=20, linestyle='--', alpha=0.5, color='#00ff00')
            ax2.axhline(y=30, linestyle='--', alpha=0.5, color='y')
            ax2.axhline(y=70, linestyle='--', alpha=0.5, color='y')
            ax2.axhline(y=80, linestyle='--', alpha=0.5, color='#00ff00')
            ax2.axhline(y=90, linestyle='--', alpha=0.5, color='#ffaa00')
            ax2.axhline(y=100, linestyle='--', alpha=0.5, color='#ff0000')

        names = []
        for i in res.keys():
            if i == 'REAL':
                line = ax1.plot(res[i], '-', label=i, color='blue')
            elif i in kwargs['tickers']:
                line = ax1.plot(res[i], '-', label=i, alpha=kwargs['bright'] / 100)
            elif i == 'RSI':
                continue
            else:
                line = ax1.plot(res[i], '-', label=i)
            names.append(line[0])

        ax1.legend(handles=names)
        ax1.legend(loc=2)  # upper left
        self.canvas.draw()


class AboutPragramMenu(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("Templates/about_program.ui", self)
        self.setWindowTitle('О программе')

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.close()


class Error():
    def __init__(self, name, message):
        msg = QMessageBox()
        msg.setWindowTitle(name)
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('Templates/Logo.png'))
    mainWin = MainWindow()
    mainWin.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
