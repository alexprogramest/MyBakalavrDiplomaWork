import sys
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.pyplot import Figure
import networkx as nx
import numpy as np
from netgraph import InteractiveGraph


class data_tab(QtWidgets.QWidget):

    def __init__(self, parent, title):

        QtWidgets.QWidget.__init__(self, parent)

        self.data_tab_glayout = QtWidgets.QGridLayout(self)
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(parent)

        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()

        self.canvas_vlayout = QtWidgets.QVBoxLayout(self.canvas)
        self.data_tab_glayout.addWidget(self.canvas, 0, 0, 2, 1)

        #self.figure.canvas.mpl_connect('button_press_event', self.onclick)

        self.axe = self.canvas.figure.add_subplot(111)
        self.canvas.figure.subplots_adjust(left=0.025, top=0.965, bottom=0.040, right=0.975)
        # add the tab to the parent
        parent.addTab(self, "")

        # set text name
        parent.setTabText(parent.indexOf(self), title)

    def createInteractiveGraph(self, DG, pos, node_color, labels):

        self.graph_instance = InteractiveGraph(DG, node_layout=pos, edge_layout='curved', origin=(-1, -1), scale=(2, 2),
                                          node_color=node_color, node_size=8.,
                                          node_labels=True, node_label_fontdict=dict(size=10),
                                          edge_labels=labels, edge_label_fontdict=dict(size=10), ax=self.axe
                                          )

        self.canvas.draw()


class MyApp(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.showMaximized()

        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.core_tab = QtWidgets.QTabWidget(self.centralwidget)
        self.verticalLayout.addWidget(self.core_tab)
        self.add_tab_btn = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.add_tab_btn)
        self.refresh_tab_btn = QtWidgets.QPushButton(self.centralwidget)
        self.verticalLayout.addWidget(self.refresh_tab_btn)
        self.setCentralWidget(self.centralwidget)

        self.add_tab_btn.setText("Add Tab")
        self.refresh_tab_btn.setText("Refresh Tabs")

        self.core_tab.setEnabled(True)
        self.core_tab.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.core_tab.setElideMode(QtCore.Qt.ElideNone)
        self.core_tab.setDocumentMode(False)
        self.core_tab.setTabsClosable(True)
        self.core_tab.setMovable(True)
        self.core_tab.setTabBarAutoHide(False)

        self.tab_counter = 0

        self.random_tabs = [("a", ["b", "c"]),
                            ("d", ["e", "f", "g"]),
                            ("h", ["i", "j", "k", "l"]),
                            ("m", ["n"]),
                            ("o", ["p", "q"]),
                            ("r", ["s", "t", "u", "v", "w", "x", "y", "z"])]

        self.add_tab_btn.clicked.connect(self.openRandomTab)
        self.refresh_tab_btn.clicked.connect(self.refreshAllTabs)

    def openRandomTab(self):

        tab = data_tab(self.core_tab, "test " + str(self.tab_counter))
        self._drawDataGraph(self.tab_counter % len(self.random_tabs), tab)
        self.tab_counter += 1

        self.core_tab.setCurrentIndex(self.core_tab.indexOf(tab))


    def _drawDataGraph(self, tabNb, dataWidget):
        dataWidget.axe.cla()

        # 1. draw graph
        producer = self.random_tabs[tabNb][0]
        consumers = self.random_tabs[tabNb][1]

        color_map = []
        DG = nx.DiGraph()
        for i, cons in enumerate(consumers):
            DG.add_edge(producer, cons, label=f"edge-{i}")

        node_color = dict()
        for node in DG:
            if node in producer:
                node_color[node] = "#DCE46F"
            else:
                node_color[node] = "#6FA2E4"
        pos = nx.shell_layout(DG)
        pos[producer] = pos[producer] + np.array([0.2, 0])
        labels = nx.get_edge_attributes(DG, 'label')

        dataWidget.createInteractiveGraph(DG, pos, node_color, labels)


    def refreshAllTabs(self):

        # loop through all pages and associated to get
        for tab_index in range(self.core_tab.count()):
            data_tab_widget = self.core_tab.widget(tab_index)

            # draw graph
            self._drawDataGraph(tab_index % len(self.random_tabs), data_tab_widget)




sys.argv = ['']
app = QtWidgets.QApplication(sys.argv)
main_app = MyApp()
main_app.show()
app.exec_()