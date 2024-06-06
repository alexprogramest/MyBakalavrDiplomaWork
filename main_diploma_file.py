"""Previous name of file: draft_1, changed to main_diploma_file, 14.05.2024 9:21"""
import os
import sys
import random
import time

import matplotlib.pyplot
# import matplotlib; matplotlib.use("Qt5Agg")

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
# from PyQt5.uic.properties import QtGui

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

import networkx as nx
import igraph

from netgraph import EditableGraph, InteractiveGraph, Graph
from netgraph._artists import NodeArtist, EdgeArtist

import numpy as np
from itertools import combinations


class MyEditableGraph(EditableGraph):

    def __init__(self, *args, **kwargs):
        self.defined_general_node_label_fontdict = dict(size=14)
        given_graph_data = args[0]
        defined_node_label = {}
        for one_node in given_graph_data.nodes:
            defined_node_label[int(one_node)] = str(int(one_node) + 1)
        super().__init__(*args, **kwargs,
                         node_label_fontdict=self.defined_general_node_label_fontdict,
                         node_labels=defined_node_label)

    def add_node_by_position(self, new_node_position):
        # if event.inaxes != self.ax:
        #     print('Position outside of axis limits! Cannot create node.')
        #     return

        # create node ID; use smallest unused int
        node = 0
        while node in self.node_positions.keys():
            node += 1

        pos = new_node_position
        # pos = self._set_position_of_newly_created_node(0.5, 0.5)

        # copy attributes of last selected artist;
        # if none is selected, use a random artist
        if self._selected_artists:
            node_properties = self._extract_node_properties(self._selected_artists[-1])
        else:
            node_properties = self._last_selected_node_properties

        artist = NodeArtist(xy=pos, **node_properties)

        self._reverse_node_artists[artist] = node

        self._draggable_artist_to_node[artist] = node

        self.artist_to_key[artist] = node

        self._clickable_artists.append(artist)
        self._selectable_artists.append(artist)
        self._draggable_artists.append(artist)
        self._base_linewidth[artist] = artist._lw_data
        self._base_edgecolor[artist] = artist.get_edgecolor()

        self.emphasizeable_artists.append(artist)
        self._base_alpha[artist] = artist.get_alpha()

        self.nodes.append(node)
        self.node_positions[node] = pos
        self.node_artists[node] = artist
        self.ax.add_patch(artist)

        # print(self.nodes)
        # print(self.node_label_fontdict)
        # print(self.node_label_artists)
        # self.draw_node_labels({node: str(node + 1)}, self.defined_general_node_label_fontdict)
        # self.draw_node_labels({4: "00"}, {})

        self._add_label_to_new_node()

        # for node, label in {node: str(node + 1)}.items():
        #     x, y = self.node_positions[node]
        #     # dx, dy = self.node_label_offset[node]
        #     dx, dy = (0., 0.)
        #     artist = self.ax.text(x+dx, y+dy, label, **self.defined_general_node_label_fontdict)
        #     if node in self.node_label_artists:
        #         self.node_label_artists[node].remove()
        #     self.node_label_artists[node] = artist

    def _add_label_to_new_node(self):
        node_label_offset = (0., 0.)
        node_labels = {one_node: str(one_node + 1) for one_node in self.nodes}
        # print(node_labels)

        # print(self.node_label_artists)
        for one_node_label_artist in self.node_label_artists.values():
            one_node_label_artist.remove()

        self.node_label_fontdict = self._initialize_node_label_fontdict(
            self.defined_general_node_label_fontdict,
            {one_node: str(one_node + 1) for one_node in self.nodes},
            node_label_offset)
        self.node_label_offset, self._recompute_node_label_offsets = \
            self._initialize_node_label_offset(node_labels, node_label_offset)
        if self._recompute_node_label_offsets:
            self._update_node_label_offsets()
        self.node_label_artists = dict()
        self.draw_node_labels(node_labels, self.node_label_fontdict)

    def add_edges_to_selected_nodes(self):
        # translate selected artists into nodes
        the_selected_nodes = [self._reverse_node_artists[artist] for artist in self._selected_artists if
                              isinstance(artist, NodeArtist)]
        if len(the_selected_nodes) < 2:
            print("You must choose at least two nodes!")
        else:
            # print(self._selected_artists)
            # print(the_selected_nodes)
            # print(self.nodes)
            # print(self.edges)
            # print(the_selected_nodes)
            # print(tuple(the_selected_nodes))
            all_defined_edges = combinations(the_selected_nodes, 2)
            for one_defined_edge in all_defined_edges:
                if one_defined_edge not in self.edges:
                    self._add_edge(one_defined_edge)

            # self._add_edge((1, 2))

    # def rewrite_graph(self, new_graph_data):
    #
    #     pass

    def rewrite_graph(self, new_graph_data):
        # all_existing_nodes = self.nodes
        # print(self.edges)
        # # delete existing edges
        # print(self.edges[1])
        # print(self.node_positions)

        # copy is necessary! (for both cases)
        all_existing_edges = self.edges.copy()  # self.edges is used inside function *_delete_edge*
        all_existing_nodes = self.nodes.copy()  # self.nodes is used inside function *_delete_node*
        for one_existing_edge in all_existing_edges:
            self._delete_edge(one_existing_edge)

        # delete existing nodes
        for one_existing_node in all_existing_nodes:
            self._delete_node(one_existing_node)

        # delete edges to and from all existing nodes
        # connected_edges = [(source, target) for (source, target) in self.edges if
        #                    ((source in self.nodes) or (target in self.nodes))]
        # for one_connected_edge in connected_edges:
        #     self._delete_edge(one_connected_edge)
        # self.__init__(arg_new_data, ax=arg_ax, node_layout=arg_layout)

        defined_node_layout = nx.spring_layout(new_graph_data)

        # BASE_SCALE = 1e-2
        # temp_base_scale = 1e-2
        # node_size = 3.
        # node_size = self._normalize_numeric_argument(node_size, self.nodes, 'node_size')
        # node_size = self._rescale(node_size, temp_base_scale)
        # origin = (0., 0.)
        # scale = (1., 1.)
        # new_node_positions = self._initialize_node_layout(
        #     defined_node_layout, None, origin, scale, node_size)
        # # self._update_view()
        # # self._make_pretty(self.ax)
        #
        # # new_node_positions = [(((x + 1) / 2), ((y + 1) / 2)) for x, y in defined_node_layout.values()]
        #
        # for one_new_node in new_graph_data.nodes:
        #     self.add_node_by_position(new_node_positions[one_new_node])
        # for one_new_edge in new_graph_data.edges:
        #     self._add_edge(one_new_edge)

        # print(defined_node_layout)
        # print([(((x + 1) / 2), ((y + 1) / 2)) for x, y in defined_node_layout.values()])
        # print(new_node_positions)
        # print(self.node_positions)

    def delete_elements_by_button(self):
        self._delete_nodes()
        self._delete_edges()

    def _on_key_press(self, event):
        if event.key in ('insert', '+'):
            self._add_node(event)
            self._add_label_to_new_node()
        elif event.key in ('delete', '-'):
            self._delete_nodes()
            self._delete_edges()
        elif event.key == '@':
            self._reverse_edges()
        elif event.key == "ctrl+a":
            # print(type(self.node_artists[0]))
            # print(type(self._selectable_artists[0]))
            # self._select_artist(self.node_artists[0])
            # print(self.node_artists)
            # all_artist = self.node_artists.values()
            # I did earlier the same as the author of the library did :) (used slice [:] to copy dict)
            # print(list(self.node_artists.values()))
            # print(list(self.edge_artists.values()))
            for one_node_artist in list(self.node_artists.values()) + list(self.edge_artists.values()):
                self._select_artist(one_node_artist)
            # print("USER")
        else:
            pass

        self.fig.canvas.draw_idle()


class MyTabsWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(MyTabsWidget, self).__init__(parent)
        self.graph_list = []
        self.canvas_list_classes = []

        self.setTabShape(QtWidgets.QTabWidget.Triangular)
        # self.setStyleSheet("QTabBar::tab { height: 100px; width: 100px; background: 'red'}")
        self.setStyleSheet("QTabBar::tab { background: lightyellow }")

        self.first_tab = QtWidgets.QWidget()
        self.last_tab = QtWidgets.QWidget()
        # self.all_tabs_widget.resize(300, 200)

        self.addTab(self.first_tab, "Graph 1")
        self.addTab(self.last_tab, "*add tab*")
        # self.all_tabs_widget.addTab(self.tab2, "Tab 2")

        self._add_graph_to_new_tab(self.widget(0))

        self.tabBarClicked.connect(self.open_the_tab)

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_one_tab)

        # https://qna.habr.com/q/833969
        self.tabBar().setTabButton(len(self) - 1, self.tabBar().RightSide, None)
        # QtWidgets.QTabBar.setTabsClosable(True)

        # self.setMovable(True)

    def _add_graph_to_new_tab(self, arg_chosen_tab):
        main_tab_layout = QtWidgets.QVBoxLayout(arg_chosen_tab)  # self.widget(arg_tab_index)
        the_tab_canvas = GraphCanvas()
        the_tab_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        the_tab_canvas.setFocus()
        main_tab_layout.addWidget(the_tab_canvas)
        self.canvas_list_classes.append(the_tab_canvas)

    def open_the_tab(self, arg_current_index):
        if arg_current_index == len(self) - 1:
            self._create_new_tab(arg_current_index)

        # the_current_canvas = self.canvas_list_classes[self.currentIndex()]
        # the_current_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        # the_current_canvas.setFocus()

        # self.widget(arg_current_index)

        # main_tab_layout = QtWidgets.QVBoxLayout(self.widget(arg_current_index))
        # tab_canvas = GraphCanvas()
        # tab_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        # tab_canvas.setFocus()
        # main_tab_layout.addWidget(tab_canvas)
        # self.canvas = GraphCanvas()

        # print("Opened tab!")

    def _create_new_tab(self, arg_current_index):
        # print("asdfasdf")
        # print(self[1])
        # self.setTabText(len(self) - 1, "Graph " + str(len(self)))
        self.setTabText(len(self) - 1, "Graph " + str(int(self.tabText(arg_current_index - 1).split(" ")[1]) + 1))
        self.last_tab = QtWidgets.QWidget()
        self.addTab(self.last_tab, "*add tab*")

        # yes, it is necessary! *personal comment*
        self.setTabsClosable(False)
        self.setTabsClosable(True)

        # self.tabCloseRequested.connect(self.close_one_tab)
        self.tabBar().setTabButton(len(self) - 1, self.tabBar().RightSide, None)

        # print(len(self) - 1)

        self._add_graph_to_new_tab(
            self.widget(len(self) - 2))  # subtract 2: not including *add tab* and including index
        # print(self.canvas_list_classes)

        # print(arg_index)
        # print(len(self))

    def close_one_tab(self, arg_current_index):
        chosen_tab_widget = self.widget(arg_current_index)
        chosen_tab_widget.deleteLater()
        self.removeTab(arg_current_index)
        del self.canvas_list_classes[arg_current_index]

    def get_current_tab_canvas(self):
        return self.canvas_list_classes[self.currentIndex()]


class GraphCanvas(FigureCanvasQTAgg):
    # def __init__(self, parent=None, width=5, height=4, dpi=100):
    def __init__(self, parent=None):
        # matplotlib.pyplot.figure()
        self.main_figure, self.ax = plt.subplots(dpi=100)  # facecolor='black'
        # self.main_figure.
        # super(GraphCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi))
        super(GraphCanvas, self).__init__(self.main_figure)
        self.setParent(parent)
        self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="none", edgecolor="black", linewidth=6))

        # self.ax = self.figure.add_subplot(111)
        # self.fig_axes = self.figure.add_axes((0., 1., 0., 1.))

        # -----------graph creation-----------
        # graph_data1 = nx.complete_graph(10)
        graph_data = nx.complete_graph(random.randint(3, 7))

        # print(defined_node_label)
        # graph_data2 = [(0, 1)]
        # layouts:
        # - 'random'      : place nodes in random positions;
        # - 'circular'    : place nodes regularly spaced on a circle;
        # - 'spring'      : place nodes using a force-directed layout (Fruchterman-Reingold algorithm);
        # - 'dot'         : place nodes using the Sugiyama algorithm; the graph should be directed and acyclic;
        # - 'radial'      : place nodes radially using the Sugiyama algorithm; the graph should be directed and acyclic;
        # - 'community'   : place nodes such that nodes belonging to the same community are grouped together;
        # - 'bipartite'   : place nodes regularly spaced on two parallel lines;
        # - 'multipartite': place nodes regularly spaced on several parallel lines;
        # - 'shell'       : place nodes regularly spaced on concentric circles;
        # - 'geometric'   : place nodes according to the length of the edges between them.
        # self.graph = MyEditableGraph(graph_data, ax=self.ax, node_layout="spring", node_labels=True,
        #                              node_label_fontdict=dict(size=14), node_label_offset=0.075)

        # edge_proxy_artists = []
        # edge_width = {
        #     (0, 1): 1,
        #     (1, 2): 2,
        #     (2, 0): 3,
        # }
        #
        # edge_color = {
        #     (0, 1): 'tab:red',
        #     (1, 2): 'tab:purple',
        #     (2, 0): 'tab:brown'
        # }
        # for edge in [(0, 1), (1, 2), (2, 0)]:
        #     proxy = plt.Line2D(
        #         [], [],
        #         linestyle='-',
        #         color=edge_color[edge],
        #         linewidth=edge_width[edge],
        #         label=edge
        #     )
        #     edge_proxy_artists.append(proxy)
        #
        # edge_legend = self.ax.legend(handles=edge_proxy_artists, loc='upper right', title='Edges')
        # self.ax.add_artist(edge_legend)

        self.graph = MyEditableGraph(graph_data, ax=self.ax)

        # self.graph = InteractiveGraph(graph_data1, ax=self.ax, node_layout="spring")
        # self.graph = Graph(graph_data1, ax=self.ax, node_layout="spring")


class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)

        self.setGeometry(0, 0, 1300, 700)
        self.setWindowTitle("Functional stability calculator")
        self.setWindowIcon(QtGui.QIcon(f"all_images/main_window_icon.jpg"))

        # dialog data saving *GenerateGraphDialog*
        self.graph_generation_entered_data = {
            "previous_entered_nodes_amount": 2,
            "previous_entered_edges_amount": 0
        }

        self._center_main_window()
        # qr = self.frameGeometry()
        # cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())

        # self.center()

        # self.ce

        # self.canvas = GraphCanvas(self, width=5, height=4, dpi=100)
        # self.canvas = GraphCanvas()

        # # Enable key_press_event events:
        # # https://github.com/matplotlib/matplotlib/issues/707/#issuecomment-4181799
        # self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        # self.canvas.setFocus()

        # self.toolbar = NavigationToolbar2QT(self.canvas, self)

        # -----------main widget of window and main layout-----------
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        # -----------tabs creation-----------
        self.all_tabs_widget = MyTabsWidget()
        # self.all_tabs_widget = QtWidgets.QTabWidget()
        # self.tab1 = QtWidgets.QWidget()
        # # self.tab2 = QtWidgets.QWidget()
        # # self.all_tabs_widget.resize(300, 200)
        #
        # self.all_tabs_widget.addTab(self.tab1, "+ tab")
        # # self.all_tabs_widget.addTab(self.tab2, "Tab 2")
        #
        # self.all_tabs_widget.setTabsClosable(True)

        # -----------all button options (footer)-----------
        self.widget_all_buttons = QtWidgets.QWidget()
        self.widget_all_buttons.setObjectName('all_buttons')
        self.widget_all_buttons.setMaximumHeight(100)
        self.widget_all_buttons.setStyleSheet("""
        background-color: lightblue;
        """)  # #9A6E56
        # self.widget_all_buttons.setFixedHeight(100)

        additional_layout1 = QtWidgets.QHBoxLayout(self.widget_all_buttons)

        # additional_layout1.setObjectName("MainDownLayout")

        all_option_buttons = [
            QtWidgets.QPushButton(text="\tCreate node"),
            QtWidgets.QPushButton(text="\tCreate edge(s)"),
            QtWidgets.QPushButton(text="\tGenerate graph"),
            QtWidgets.QPushButton(text="\tFORMULA"),
            QtWidgets.QPushButton(text="\tDelete selected"),
            QtWidgets.QPushButton(text="\tExport file"),
            QtWidgets.QPushButton(text="\tImport file")
        ]
        all_option_buttons_function = [
            self.create_one_node,
            self.create_edges,
            self.generate_new_graph,
            self.calculate_functional_stability,
            self.delete_selected_elements,
            self.export_graph_to_file,
            self.import_graph_from_file,
        ]
        #

        # for one_button_info in zip(all_option_buttons, all_option_buttons_function):
        for one_button_ind in range(len(all_option_buttons)):
            one_button = all_option_buttons[one_button_ind]
            one_button_function = all_option_buttons_function[one_button_ind]

            additional_layout1.addWidget(one_button)
            one_button.clicked.connect(one_button_function)
            one_button.setIcon(QtGui.QIcon(f"all_images/buttons_options_images/button_icon_{one_button_ind + 1}.png"))
            one_button.setIconSize(QtCore.QSize(25, 25))
            # one_button.setMaximumWidth(100)
            drop_shadow_effect = QtWidgets.QGraphicsDropShadowEffect()
            drop_shadow_effect.setBlurRadius(20)
            one_button.setGraphicsEffect(drop_shadow_effect)
            one_button.setStyleSheet("""
            QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
    
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }""")

        # -----------add all content two main layout-----------
        main_layout.addWidget(self.all_tabs_widget)
        # main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.widget_all_buttons)
        # print(self.canvas.graph.artist_to_key)
        # self.setLayout(main_layout)

    def _center_main_window(self):
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

    def create_one_node(self):
        # for one_thing in self.canvas.graph.nodes:
        #     print(one_thing)

        # print(self.canvas.graph.node_positions.values())

        new_position_found = False
        # new_position: tuple = ()
        new_position = (random.random(), random.random())

        # while not new_position_found:
        #     new_position = (random.random(), random.random())
        #     new_position_found = True
        #     for one_node_position in self.canvas.graph.node_positions.values():
        #         all_conditions = [
        #             abs(one_node_position[0] - new_position[0]) <= 0.01 and abs(
        #                 one_node_position[1] - new_position[1]) <= 0.01,
        #             new_position[0] <= 0.01,
        #             new_position[1] <= 0.01,
        #             1 - new_position[0] <= 0.01,
        #             1 - new_position[1] <= 0.01
        #         ]
        #         # if abs(one_node_position[0] - new_position[0]) <= 0.01 or abs(
        #         #         one_node_position[1] - new_position[1]) <= 0.01 or new_position[1] <= 0.01 or new_position[
        #         #     1] <= 0.01:
        #         if any(all_conditions):
        #             new_position_found = False
        #             # print("Searching nice place for new node...")

        # print(self.canvas.graph.node_positions.values())
        # print(new_position)
        the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()
        # print(the_current_canvas)
        the_current_canvas.graph.add_node_by_position(new_position)
        # self.all_tabs_widget.currentWidget().canvas.graph.add_node_by_position(new_position)
        # self.canvas.draw()

        the_current_canvas.draw_idle()

        # if ()

        # self.canvas.drawRectangle()
        # self.canvas.graph._add_node()
        # print(self.canvas.graph.artist_to_key)
        # self.canvas.graph.draw_edges((1, 2), )
        # pass

    def create_edges(self):
        # print(self.canvas.graph._nascent_edge)
        the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()
        the_current_canvas.graph.add_edges_to_selected_nodes()
        the_current_canvas.draw_idle()

    def generate_new_graph(self):
        the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()
        # open_dialog = QtWidgets.QDialog()
        # open_dialog.exec()
        open_dialog = GenerateGraphDialog(self.graph_generation_entered_data)
        pressed_button = open_dialog.exec()

        # print(open_dialog.main_button_box)
        amount_of_nodes = open_dialog.define_nodes_slider.value()
        amount_of_edges = open_dialog.define_edges_slider.value()
        # print(amount_of_nodes)
        # print(amount_of_edges)
        if pressed_button:
            self.graph_generation_entered_data["previous_entered_nodes_amount"] = amount_of_nodes
            self.graph_generation_entered_data["previous_entered_edges_amount"] = amount_of_edges

            new_graph_data = nx.Graph()

            new_graph_nodes = list(range(amount_of_nodes))
            new_graph_edges = list(combinations(new_graph_nodes, 2))
            random.shuffle(new_graph_edges)
            new_graph_edges = new_graph_edges[:amount_of_edges]
            # print(new_graph_edges)

            new_graph_data.add_nodes_from(new_graph_nodes)
            new_graph_data.add_edges_from(new_graph_edges)

            # if pressed_button == open_dialog.main_button_box[0]:
            # new_graph_data = nx.complete_graph(random.randint(3, 7))
            # new_graph_data = nx.erdos_renyi_graph(len(new_graph_nodes), len(new_graph_edges) / (
            #         len(new_graph_nodes) * (len(new_graph_nodes) - 1) / 2))

            # the_current_canvas.graph.rewrite_graph_by_button(new_graph_data,
            #                                                  the_current_canvas.graph.ax,
            #                                                  "spring")

            the_current_canvas.graph.rewrite_graph(new_graph_data)

            the_current_canvas.graph = MyEditableGraph(new_graph_data,
                                                       the_current_canvas.graph.ax,
                                                       node_layout="spring")  # node_layout=nx.planar_layout(new_graph_data)

            # print(the_current_canvas.graph.edges)
            # print(the_current_canvas.graph.nodes)
            the_current_canvas.draw_idle()

            # print(nx.spring_layout(nx.complete_graph(4)))
            # print(the_current_canvas.graph.edges)
            # the_current_canvas.graph.edges = []
            # print(the_current_canvas.graph.edges)
            # new_canvas = GraphCanvas()
            # self.all_tabs_widget.canvas_list_classes[self.all_tabs_widget.currentIndex()] = new_canvas

            # graph_data2 = [(0, 1)]
            # self.all_tabs_widget.canvas_list_classes[self.all_tabs_widget.currentIndex()]
            # new_graph = MyEditableGraph(new_graph_data, ax=self.ax, node_layout="spring")
            # the_current_canvas.graph.clear()
            # print(the_current_canvas.graph.edges)
            # print(the_current_canvas.graph.nodes)

            # the_current_canvas.graph = MyEditableGraph(new_graph_data, ax=the_current_canvas.graph.ax, node_layout="spring")
            # the_current_canvas.draw()
            # print(the_current_canvas.graph.edges)
            # print(the_current_canvas.graph.nodes)

            # the_current_canvas.graph =

    def calculate_functional_stability(self):
        # doing main function of diploma right now...
        the_current_graph = self.all_tabs_widget.get_current_tab_canvas().graph

        the_current_graph_info = nx.Graph()
        the_current_graph_info.add_nodes_from(the_current_graph.nodes)
        the_current_graph_info.add_edges_from(the_current_graph.edges)
        # print(list(nx.chain_decomposition(the_current_graph_info)))

        self.formula_window = FormulaCalcWindow(the_current_graph_info)
        self.formula_window.show()
        # self.setWindowModality(QtCore.Qt.ApplicationModal)

    def delete_selected_elements(self):
        the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()
        the_current_canvas.graph.delete_elements_by_button()
        the_current_canvas.draw_idle()

    def export_graph_to_file(self):
        the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()

        current_graph_data = nx.Graph()
        current_graph_data.add_edges_from(the_current_canvas.graph.edges)
        current_graph_data.add_nodes_from(the_current_canvas.graph.nodes)
        # current_nodes = the_current_canvas.graph.nodes
        current_node_positions = the_current_canvas.graph.node_positions
        # print(current_node_positions)
        # print(nx.spring_layout(current_graph_data))
        for one_node, (x_coord, y_coord) in current_node_positions.items():
            current_graph_data.nodes[one_node]["x_coord"] = x_coord
            current_graph_data.nodes[one_node]["y_coord"] = y_coord
        # print(current_nodes)
        # print(current_node_positions)
        # for one_node in current_nodes:
        #     # current_graph_data.add_node(one_node, node_pos=(current_node_positions[one_node]))
        #     current_graph_data.add_node(one_node)

        # print(current_graph_data)
        # print(nx.get_node_attributes(current_graph_data, "node_pos"))
        # print("asfasdf")
        file_name_for_save, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export graph to:",
                                                                      "some_example.graphml",
                                                                      "Graph format file (*.graphml)")
        # if file_name_for_save
        # print(file_name_for_save == "")
        if file_name_for_save != "":
            nx.write_graphml(current_graph_data, file_name_for_save)

        #
        # path = "C:/Users"
        # fullpath = os.path.realpath(path)
        #
        # if not QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(fullpath)):
        #     print("failed")

        # print(current_graph_data)

    def import_graph_from_file(self):
        file_name_to_import, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import graph from:",
                                                                       "",
                                                                       "Graph format file (*.graphml)")
        if file_name_to_import != "":
            graph_from_file = nx.read_graphml(file_name_to_import)
            improved_graph = nx.Graph()

            found_nodes_from_file = []
            node_positions = {}
            # improved_graph.add_nodes_from(graph_from_file.nodes(data=True))

            # print(graph_from_file.nodes(data=True))
            # improved_graph.add_edges_from(graph_from_file.edges(data=True))

            for one_node_xml_str, attributes in graph_from_file.nodes(data=True):
                # print(one_node_xml_str)
                one_node = int(one_node_xml_str)
                # improved_graph.add_node(one_node)
                found_nodes_from_file.append(one_node)
                node_positions[one_node] = (attributes["x_coord"], attributes["y_coord"])

            # sorting is necessary!
            improved_graph.add_nodes_from(sorted(found_nodes_from_file))

            # sorting is necessary!
            improved_graph.add_edges_from(sorted(
                [(int(one_edge[0]), int(one_edge[1])) for one_edge in graph_from_file.edges(data=True)],
                key=lambda one_defined_edge: one_defined_edge[0] * 2 + one_defined_edge[1]
            ))
            # found_edges_from_file = [(int(one_edge[0]), int(one_edge[1])) for one_edge in graph_from_file.edges(data=True)]
            # found_edges_from_file.sort(key=lambda one_defined_edge: one_defined_edge[0] + one_defined_edge[1] * 2)
            # [].sort(key=lambda x:True)
            # improved_graph.add_edges_from(found_edges_from_file)

            print("Data (graph) was read from file")
            print(improved_graph.nodes)
            print(improved_graph.edges)
            # print(graph_from_file.edges(data=True))

            # print(graph_from_file.nodes(data=True))
            # print(type(nx.Graph()))

            # print(nx.complete_graph())

            # print(improved_graph.nodes)
            # print(improved_graph.edges)
            # print(node_positions)
            # print(self.all_tabs_widget.currentIndex())

            the_current_canvas = self.all_tabs_widget.get_current_tab_canvas()
            # print(the_current_canvas.graph.nodes)
            # print(the_current_canvas.graph.edges)
            the_current_canvas.graph.rewrite_graph(improved_graph)
            # print("asdlkfjhdaskfljd")
            the_current_canvas.graph = MyEditableGraph(improved_graph,
                                                       the_current_canvas.graph.ax,
                                                       node_layout=node_positions)

            # print(the_current_canvas.graph.nodes)
            # print(the_current_canvas.graph.edges)
            the_current_canvas.draw_idle()
            # graph_from_file.nodes

            # print("asdfasdf")
            # print(some_list[0])
            # print("asdfasdf")


# MAIN_STYLESHEET = """
# #all_buttons{
#     height: 20px;
#     background: #9A6E56;
# }
# QPushButton {
#     background: #255983;
#     font: bold 28px;
#     color: #66B5FF;
#     border-width: 2px;
#     border-style: solid;
#     border-color: #66B5FF;
#     border-radius: 15%;
#     text-align: center;
#     outline: none;
# }
# QPushButton:hover {
#     color: #00E5FF;
#     border-color: #00E5FF;
#     background: #007AFF;
#     outline: none;
# }
# """


class FormulaCalcWindow(QtWidgets.QWidget):
    all_methods_for_functional_stability = [
        "Simple paths",
        # "Ezari-Proshan", # is omitted!
        "Litvak-Ushakov"
        # "Exhaustive search",  # another name: "brute-force search"
    ]

    def __init__(self, chosen_graph_info):
        super().__init__()
        self.chosen_graph_data = chosen_graph_info

        # print(self.chosen_graph_data.nodes)
        # print(self.chosen_graph_data.edges)
        # print()

        # self.setGeometry(200, 200, 1300, 700)
        self.setGeometry(0, 0, 700, 900)
        self._center_formula_window()
        self.setWindowIcon(QtGui.QIcon(f"all_images/formula_window_images/formula_window_icon.png"))
        self.setStyleSheet("background-color: #FFFCF4;")

        # choose method
        self.chosen_method_by_user = ""

        self.choose_method_widget = QtWidgets.QWidget()
        # self.choose_method_widget.setGeometry(500, 500)
        self.label_select_method = QtWidgets.QLabel("Select the method: ")
        self.label_select_method.setAlignment(Qt.AlignCenter)
        self.label_select_method.setFont(QtGui.QFont("Arial", 12))

        self.list_of_methods = QtWidgets.QComboBox()
        self.list_of_methods.addItems(self.all_methods_for_functional_stability)
        self.list_of_methods.setMaximumSize(150, 30)
        self.list_of_methods.setStyleSheet(
            """
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding-left: 10px;
            background-color: white;
        }
        # 
        # /* style for drop down area */
        # QComboBox::drop-down {
        #     border: 0px;
        # }
        # 
        # /* style for drop down arrow */
        # comboBox::down-arrow {
        #     # background: url("C:\\MyProjects\\2024Year\\PythonProjects\\GraphCreating\\DiplomaProject4\\all_images\\formula_window_images/arrow_down.jpg")
        #     width: 12px;
        #     height: 12px;
        #     margin-right: 15px;
        # }
        # 
        # /* style for (ComboBox after open select menu */
        # QComboBox:on {
        #     border: 4px solid #c2dbfe:
        # }
        
        # /* style for list menu */
        # QComboBox QListView {
        #     font-size: 12px;
        #     border: 1px solid rgba(0, 0, 0, 10%);
        #     padding: 5px;
        #     background-color: #E0D191;
        #     outline: 0px;
        # }
        # 
        # /* style for list items */
        # 
        # QComboBox QListView:item {
        #     padding-left: 10px;
        #     background-color: #fff;
        # }
        # 
        # QComboBox QListView::item:hover {
        #     background-color: black;
        # }
        # 
        # QComboBox QListView::item:selected {
        #     background-color: black;
        # }
        """)

        self.button_to_define_method = QtWidgets.QPushButton()
        # self.button_to_define_method.setO
        self.button_to_define_method.setText("Get info by method")
        self.button_to_define_method.clicked.connect(self.define_functional_stability_method)
        # self.button_to_define_method.setIcon(QtGui.QIcon(f"all_images/formula_window_images/select_method_icon.jpg"))
        self.button_to_define_method.setStyleSheet(
            """
        QPushButton {
            display: inline-block;
            outline: 0;
            cursor: pointer;
            border: 2px solid #000;
            border-radius: 10px;
            color: #000;
            background: #fff;
            font-size: 15px;
            font-weight: 600;
            line-height: 28px;
            padding: 12px 20px;
            text-align:center;
            transition-duration: .15s;
            transition-property: all;
            transition-timing-function: cubic-bezier(.4,0,.2,1);
        }
        QPushButton:hover{
            background: rgb(251, 193, 245);
        }
        """)

        # self.combo_box.setEditable(True)
        # line_edit = self.combo_box.lineEdit()
        # line_edit.setAlignment(Qt.AlignCenter)
        # self.list_of_methods.setAlignment(Qt.AlignLeft)
        # self.list_of_methods.move(500, 500)

        self.layout_choose_method = QtWidgets.QHBoxLayout(self.choose_method_widget)
        self.layout_choose_method.addWidget(self.label_select_method)
        self.layout_choose_method.addWidget(self.list_of_methods)
        self.layout_choose_method.addWidget(self.button_to_define_method)

        # show name of selected method
        self.label1_defined_chosen_method = QtWidgets.QLabel("Selected method is: ")
        self.label1_defined_chosen_method.setAlignment(Qt.AlignRight)
        label1_defined_chosen_method_font = QtGui.QFont("Arial", 12)
        label1_defined_chosen_method_font.setItalic(True)
        self.label1_defined_chosen_method.setFont(label1_defined_chosen_method_font)

        self.label2_defined_chosen_method = QtWidgets.QLabel()
        self.label2_defined_chosen_method.setAlignment(Qt.AlignLeft)
        label2_defined_chosen_method_font = QtGui.QFont("Arial", 12)
        label2_defined_chosen_method_font.setUnderline(True)
        self.label2_defined_chosen_method.setFont(label2_defined_chosen_method_font)

        self.defined_chosen_method_layout = QtWidgets.QHBoxLayout()
        self.defined_chosen_method_layout.addWidget(self.label1_defined_chosen_method)
        self.defined_chosen_method_layout.addWidget(self.label2_defined_chosen_method)

        # formulas of graph path
        self.formulas_area = QtWidgets.QScrollArea()
        # self.formulas_area.setMaximumHeight(500)
        self.formulas_area.setMinimumHeight(110)
        self.formulas_area.setWidgetResizable(True)  # is necessary if we want to change data of scroll area!
        self.formulas_area.setStyleSheet("""
                QScrollArea {
                    border: 2px dashed #654321;
                }
                QScrollBar:vertical {
                    border: 0px solid #999999;
                    background-color: rgb(34, 35, 52);
                    width:14px;    
                    margin: 0px 0px 0px 3px;
                }
                QScrollBar::handle:vertical {         
                    min-height: 0px;
                    border: 0px solid red;
                    border-radius: 5px;
                    background-color: rgb(92, 95, 141);
                }
                QScrollBar::add-line:vertical {       
                    height: 0px;
                    subcontrol-position: bottom;
                    subcontrol-origin: margin;
                }
                QScrollBar::sub-line:vertical {
                    height: 0 px;
                    subcontrol-position: top;
                    subcontrol-origin: margin;
                }""")

        self.formulas_area_widget = QtWidgets.QWidget()
        self.formulas_area.setWidget(self.formulas_area_widget)

        # self.formulas_area_widget must be added!
        self.layout_selection = QtWidgets.QVBoxLayout(self.formulas_area_widget)
        # self.formulas_area.setLayout(self.layout_selection)

        self.formulas_main_label = QtWidgets.QLabel()
        self.formulas_main_label.setWordWrap(True)
        self.formulas_main_label.setFont(QtGui.QFont("", 12))

        self.layout_selection.addWidget(self.formulas_main_label)

        # self.formulas_area.setWidget(self.formulas_main_label)

        # self.formulas_main_label.setText("29dlshf dkjash fl" * 1000)

        self.formulas_area.setWidget(self.formulas_area_widget)
        # chart
        self.the_chart_canvas = AdditionalChartCanvas()
        # self.the_chart_canvas.ax.plot([0.1, 0.2], [0.1, 0.2])
        # self.the_chart_canvas.ax.set_title("Equal probability of functional stability (p₁ = p₂ = ... = p)")
        # self.the_chart_canvas.ax.grid()

        # node selection
        self.node_selection_area = QtWidgets.QScrollArea()
        # self.node_selection_area.setMinimumHeight(300)
        self.node_selection_area.setMaximumHeight(150)
        # self.node_selection_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.node_selection_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.node_selection_area.setWidgetResizable(True)
        self.node_selection_area.setStyleSheet("""
        QScrollArea {
            border: 2px dashed #654321;
        }
        QScrollBar:vertical {
            border: 0px solid #999999;
            background-color: rgb(34, 35, 52);
            width:14px;    
            margin: 0px 0px 0px 3px;
        }
        QScrollBar::handle:vertical {         
            min-height: 0px;
            border: 0px solid red;
            border-radius: 5px;
            background-color: rgb(92, 95, 141);
        }
        QScrollBar::add-line:vertical {       
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            height: 0 px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }""")

        # self.scroll_widget = QtWidgets.QWidget(self.node_selection_area)
        # self.layout_selection = QtWidgets.QVBoxLayout(self.scroll_widget)

        self.scroll_widget = QtWidgets.QWidget()
        self.layout_selection = QtWidgets.QVBoxLayout()

        self.scroll_widget.setLayout(self.layout_selection)

        # for i in range(1, 50):
        #     some_object = QtWidgets.QLabel("TextLabel")
        #     self.layout_selection.addWidget(some_object)

        # self.all_info_edges_widgets = []
        #
        # for one_edge in self.chosen_graph_data.edges:
        #     one_info_widgets = {
        #         "graph_edge_label": QtWidgets.QLabel(f"({one_edge[0] + 1}->{one_edge[1] + 1})"),
        #         "edge_probability_val_label": QtWidgets.QLabel("\t\t\t0.5"),
        #         "edge_probability_slider": QtWidgets.QSlider(Qt.Horizontal),
        #         "edge_probability_slider_func": lambda arg_value: one_info_widgets[
        #             "edge_probability_val_label"].setText("\t\t\t" + str(arg_value / 100)),
        #         "one_layout_edge_probability": QtWidgets.QHBoxLayout()
        #     }
        #
        #     self.all_info_edges_widgets.append(one_info_widgets)
        #
        # # all_edge_probability_val_labels = []
        # self.all_info_edges_widgets[1]["graph_edge_label"].setText("pelmeni")

        # for one_edge in self.chosen_graph_data.edges:
        for one_edge_ind in range(len(self.chosen_graph_data.edges)):
            one_edge = list(self.chosen_graph_data.edges)[one_edge_ind]
            one_graph_edge_label = QtWidgets.QLabel(f"({one_edge[0] + 1}-{one_edge[1] + 1})")
            # one_graph_edge_label = all_info_edges_widgets[one_edge_ind]["graph_edge_label"]
            one_graph_edge_label.setFont(QtGui.QFont("Arial", 12))

            # one_edge_probability_val_label = QtWidgets.QLabel("\t\t\t0.5")
            one_edge_probability_val_label = QtWidgets.QLabel()
            # one_edge_probability_val_label = all_info_edges_widgets[one_edge_ind]["edge_probability_val_label"]
            # all_edge_probability_val_labels.append(one_edge_probability_val_label)
            one_edge_probability_val_label.setFont(QtGui.QFont("Times New Roman", 13))

            one_edge_probability_val_label.setAlignment(Qt.AlignCenter)

            one_edge_probability_slider = QtWidgets.QSlider(Qt.Horizontal)
            # one_edge_probability_slider = all_info_edges_widgets[one_edge_ind]["edge_probability_slider"]
            one_edge_probability_slider.setMinimum(0)
            one_edge_probability_slider.setMaximum(100)
            one_edge_probability_slider.setValue(50)
            one_edge_probability_slider.setMinimumWidth(400)
            one_edge_probability_slider.setStyleSheet(
                """
                QSlider::groove:horizontal {
                    border: 1px solid #999999;
                    height: 8px; 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                    margin: 2px 0;
                }
                
                QSlider::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                    border: 1px solid #5c5c5c;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 3px;
                }
                """)
            # self.get_subscript_number(one_edge[0]) + "₋" + self.get_subscript_number(one_edge[1])
            one_edge_probability_val_label.setText("\tP" + self.get_subscript_number(one_edge[0] + 1) + "₋"
                                                   + self.get_subscript_number(one_edge[1] + 1) + " = " +
                                                   str(one_edge_probability_slider.value() / 100))

            # one_edge_probability_slider.setGeometry(QtCore.QRect(100, 100, 100, 100))
            # one_edge_probability_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            # one_edge_probability_slider.setTickInterval(5)
            # def one_edge_probability_slider_func(arg_value):
            #     print()
            #     one_edge_probability_val_label.setText("\t\t\t" + str(arg_value / 100))

            # def one_edge_probability_slider_func(arg_value):
            #     return
            #     one_edge_probability_val_label.setText("\t\t\t" + str(arg_value / 100))
            #
            # one_edge_probability_slider.valueChanged.connect(one_edge_probability_slider_func)
            # one_edge_probability_slider.valueChanged.connect(
            #     all_info_edges_widgets[one_edge_ind]["edge_probability_slider_func"])

            the_one_layout_edge_probability = QtWidgets.QHBoxLayout()
            # the_one_layout_edge_probability = all_info_edges_widgets[one_edge_ind]["one_layout_edge_probability"]
            the_one_layout_edge_probability.addWidget(one_graph_edge_label)
            the_one_layout_edge_probability.addWidget(one_edge_probability_slider)
            the_one_layout_edge_probability.addWidget(one_edge_probability_val_label)
            the_one_layout_edge_probability.setAlignment(Qt.AlignRight)

            def one_edge_probability_slider_func(arg_edge_ind):
                # print(one_edge_ind)
                # print(arg_num)

                def func_to_connect(arg_value):
                    # print(arg_num)
                    # return one_edge_probability_val_label.setText("\t\t\t" + str(arg_value / 100))
                    return self.layout_selection.itemAt(arg_edge_ind).layout().itemAt(2).widget().setText(
                        "\tP" + self.get_subscript_number(one_edge[0] + 1) + "₋"
                        + self.get_subscript_number(one_edge[1] + 1) + " = " +
                        str(arg_value / 100))

                return func_to_connect
                # return lambda arg_value: one_edge_probability_val_label.setText("\t\t\t" + str(arg_value / 100))

            # one_edge_probability_slider.valueChanged.connect(
            #     lambda arg_value: self.layout_selection.itemAt(one_edge_ind).layout().itemAt(2).widget().setText(
            #         "\t\t\t" + str(arg_value / 100)))
            one_edge_probability_slider.valueChanged.connect(one_edge_probability_slider_func(one_edge_ind))

            self.layout_selection.addLayout(the_one_layout_edge_probability)

        self.node_selection_area.setWidget(self.scroll_widget)

        # self.scroll_widget.setLayout(self.layout_selection)
        # self.node_selection_area.setWidget(self.scroll_widget)

        # calculate after received node info
        self.button_to_calculate = QtWidgets.QPushButton()
        self.button_to_calculate.setText("Calculate functional stability")
        self.button_to_calculate.setMaximumWidth(260)
        self.button_to_calculate.setStyleSheet(
            """
        QPushButton {
            display: inline-block;
            outline: 0;
            cursor: pointer;
            border: 2px solid #000;
            border-radius: 10px;
            color: #000;
            background: #fff;
            font-size: 15px;
            font-weight: 600;
            line-height: 28px;
            padding: 12px 20px;
            text-align:center;
            transition-duration: .15s;
            transition-property: all;
            transition-timing-function: cubic-bezier(.4,0,.2,1);
        }
        QPushButton:hover{
            background: rgb(251, 193, 245);
        }
        """)

        self.calculate_nodes_label = QtWidgets.QLabel("The answer is: ")
        self.calculate_nodes_label.setAlignment(Qt.AlignCenter)
        self.calculate_nodes_label.setFont(QtGui.QFont("", 12))
        # self.calculate_nodes_label.resize(300, 300)

        self.layout_calculate_info = QtWidgets.QHBoxLayout(self.choose_method_widget)
        self.layout_calculate_info.addWidget(self.button_to_calculate)
        self.layout_calculate_info.addWidget(self.calculate_nodes_label)
        # self.layout_calculate_info.addWidget(self.button_to_define_method)

        # add whole content to main layout
        self.main_vertical_layout = QtWidgets.QVBoxLayout(self)
        # self.main_vertical_layout.setAlignment(Qt.AlignTop)
        self.main_vertical_layout.addWidget(self.choose_method_widget)
        self.main_vertical_layout.addLayout(self.defined_chosen_method_layout)
        self.main_vertical_layout.addWidget(self.formulas_area)
        self.main_vertical_layout.addWidget(self.the_chart_canvas)
        self.main_vertical_layout.addWidget(self.node_selection_area)
        self.main_vertical_layout.addLayout(self.layout_calculate_info)

        # hide almost whole content before first selected method
        self.label1_defined_chosen_method.hide()
        self.label2_defined_chosen_method.hide()
        self.formulas_area.hide()
        self.the_chart_canvas.hide()
        self.node_selection_area.hide()
        self.button_to_calculate.hide()
        self.calculate_nodes_label.hide()

    def _center_formula_window(self):
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
        self.move(frame_geometry.topLeft())

    @staticmethod
    def get_superscript_number(arg_integer):
        subscript_numbers = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        return "".join([subscript_numbers[int(one_digit_str)] for one_digit_str in str(arg_integer)])

    @staticmethod
    def get_subscript_number(arg_integer):
        subscript_numbers = "₀₁₂₃₄₅₆₇₈₉"
        return "".join([subscript_numbers[int(one_digit_str)] for one_digit_str in str(arg_integer)])

    # def check_if

    def _get_minimum_cuts(self, arg_main_graph, arg_source, arg_target, selected_variant_of_search):
        # all_minimum_cuts2 = []
        # all_existing_nodes2 = list(self.chosen_graph_data.nodes)
        # len_all_existing_nodes2 = len(all_existing_nodes2)

        all_minimum_cuts = []
        # all_existing_nodes = list(self.chosen_graph_data.nodes)
        all_existing_nodes = list(arg_main_graph.nodes)

        if selected_variant_of_search == 1:
            # using NetworkX function 'minimum_edge_cut' and check for all nodes

            for one_defined_node in all_existing_nodes:
                for another_defined_node in all_existing_nodes:
                    if one_defined_node == another_defined_node:
                        continue
                    defined_minimum_cut = nx.minimum_edge_cut(arg_main_graph, one_defined_node, another_defined_node)
                    # defined_minimum_cut = nx.algorithms.connectivity.minimum_st_edge_cut(arg_defined_graph,
                    #                                                                      one_defined_node,
                    #                                                                      another_defined_node)
                    improved_minimum_cut = [tuple(sorted(one_temp_edge)) for one_temp_edge in defined_minimum_cut]
                    if improved_minimum_cut not in all_minimum_cuts and improved_minimum_cut:
                        # 'if improved_minimum_cut' check if (...) is not empty because of disconnected graph
                        all_minimum_cuts.append(improved_minimum_cut)
                        # dict_for_first_formula2 = {}

        elif selected_variant_of_search == 2:
            # using NetworkX function 'minimum_st_edge_cut' and check for all nodes
            # link: https://stackoverflow.com/questions/73018718

            # all_existing_nodes2 = list(self.chosen_graph_data.nodes)
            all_cuts = []
            for n in all_existing_nodes:
                for k in all_existing_nodes:
                    if n == k:
                        continue
                    all_cuts.append(nx.algorithms.connectivity.minimum_st_edge_cut(arg_main_graph, n, k))

            all_minimum_cuts = [frozenset([tuple(sorted(i)) for i in j]) for j in
                                [frozenset(cut) for cut in all_cuts if len(cut) == len(min(all_cuts, key=len))]]
            all_minimum_cuts = [set(s) for s in set(all_minimum_cuts)]
            all_minimum_cuts = [list(one_min_cut) for one_min_cut in all_minimum_cuts]

        elif selected_variant_of_search in [3, 4]:
            # using Igraph function
            # 'all_st_cuts' / 'all_st_mincuts'
            # to find
            # all possible / only minimum
            # cuts

            all_existing_edges = list(arg_main_graph.edges)
            all_directed_graph_edges = []
            for one_edge in all_existing_edges:
                all_directed_graph_edges.extend([one_edge, tuple(reversed(one_edge))])

            all_found_cuts = []
            igraph_created_graph = igraph.Graph(edges=all_directed_graph_edges, directed=True)

            all_cuts_objects = []
            if selected_variant_of_search == 3:
                all_cuts_objects = igraph_created_graph.all_st_cuts(source=arg_source, target=arg_target)
            elif selected_variant_of_search == 4:
                all_cuts_objects = igraph_created_graph.all_st_mincuts(source=arg_source, target=arg_target)

            for one_edge_group in [found_cut.cut for found_cut in all_cuts_objects]:
                all_found_cuts.append([all_directed_graph_edges[one_edge_id] for one_edge_id in one_edge_group])

            all_minimum_cuts = all_found_cuts.copy()

        # all_minimum_cuts = all_min_cuts2.copy()
        # print(all_found_cuts)
        # all_minimum_cuts = all_found_cuts.copy()

        return all_minimum_cuts

    def _get_all_info_by_method(self, arg_chosen_method_ind, arg_defined_graph):
        """All info -> formulas and functions to calculate, not values"""
        start_time = time.time()

        # graph_to_operate = arg_defined_graph
        # print(arg_chosen_method_ind)
        # print(arg_chosen_method_ind)
        all_result_data = {}

        first_node = list(arg_defined_graph.nodes)[0]
        last_node = list(arg_defined_graph.nodes)[-1]

        if arg_chosen_method_ind == 0:  # Simple paths
            all_paths = list(nx.all_simple_paths(arg_defined_graph, first_node, last_node))

            dict_for_first_formula = {}
            dict_for_second_formula = {}

            all_paths_probabilities = "All simple paths:\n"
            for one_path_ind in range(len(all_paths)):
                one_path = all_paths[one_path_ind]
                # all_edges_in_path = zip(sorted(one_path), sorted(one_path)[1:])

                # list must be! zip - is object, and values will be removed after generator [.. for ... in zip]
                all_edges_in_path = list(zip(one_path, one_path[1:]))

                # print(list(all_edges_in_path))
                # [one_edge for one_edge in all_edges_in_path]
                multiply_of_probabilities = "×".join([
                    "p" + self.get_subscript_number(one_edge[0] + 1) + "₋" + self.get_subscript_number(one_edge[1] + 1)
                    for one_edge in all_edges_in_path
                ])
                all_paths_probabilities += f" {one_path_ind}. {tuple(one_path)} -> {multiply_of_probabilities}\n"
                # dict_for_second_formula[str(len(one_path) - 1)]
                # print(dict_for_second_formula[str(len(one_path) - 1)])

                # print(list(all_edges_in_path))
                dict_for_first_formula[one_path_ind] = (
                    [tuple(sorted(one_temp_edge)) for one_temp_edge in all_edges_in_path],
                    multiply_of_probabilities
                )
                # arr_for_first_formula.append()

                amount_probabilities = len(one_path) - 1
                if amount_probabilities not in dict_for_second_formula:
                    dict_for_second_formula[amount_probabilities] = 1
                else:
                    dict_for_second_formula[amount_probabilities] += 1

            print(all_paths_probabilities)
            print(dict_for_first_formula)
            print(dict_for_second_formula)

            first_formula = (f"P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)}"
                             f" = 1 - ")
            first_formula += " ".join([
                f"(1 - {the_one_path_info[1]})"
                for the_one_path_info in dict_for_first_formula.values()
            ])

            second_formula = (f"P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)}"
                              f" = 1 - ")
            second_formula += " ".join([
                f"(1 - p{self.get_superscript_number(the_key)})"
                f"{self.get_superscript_number(dict_for_second_formula[the_key])}"
                for the_key in sorted(dict_for_second_formula.keys())
            ])

            print(first_formula)
            print(second_formula)

            def first_formula_func(arg_all_edges_values):  # arg_all_edges_values -> {(0, 1): 2}...
                multiply_values = 1  # (1 - p₀₋₁×p₁₋₂) (1 - p₀₋₂)...
                improved_edges_values = {}  # replace (1, 0) with (0, 1), just sort keys-edges
                for one_edge_to_sort, one_edge_value in arg_all_edges_values.items():
                    improved_edges_values[tuple(sorted(one_edge_to_sort))] = one_edge_value

                for one_path_info in dict_for_first_formula.values():
                    one_path_all_edges = one_path_info[0]
                    # print(one_path_all_edges)
                    # tuple(sorted(one_edge))
                    one_path_all_edges_values = [improved_edges_values[tuple(sorted(one_edge))]
                                                 for one_edge in one_path_all_edges]
                    # print(one_path_all_edges_values)
                    multiply_values *= (1 - np.prod(one_path_all_edges_values))

                return 1 - multiply_values

            # if p₀₋₁ = p₁₋₂ = ... = pₘ₋ ₙ = p
            def second_formula_func(arg_general_edge_val):  # arg_general_edge_val -> 0.5, 0.234, 1 ... -> 'p' value
                multiply_values = 1
                # probability_amount -> p₀₋₂×p₂₋₃×....
                # similar_path_amount -> e.g (1 - p₀₋₂×p₂₋₄) and (1 - p₀₋₃×p₃₋₄) are similar because their
                # probability amounts are equal
                for probability_amount, similar_path_amount in dict_for_second_formula.items():
                    multiply_values *= pow(1 - pow(arg_general_edge_val, probability_amount), similar_path_amount)
                return 1 - multiply_values

            # random_generated_edge_values = {}
            # for one_defined_edge in self.chosen_graph_data.edges:
            #     random_generated_edge_values[one_defined_edge] = random.random()
            # print(random_generated_edge_values)
            # first_formula_func({(0, 1): 0.5, (0, 2): 0.4})

            # print("\n")
            # # print(self.chosen_graph_data.edges)
            # print(random_generated_edge_values)
            # print(first_formula_func(random_generated_edge_values))
            # print(second_formula_func(0.5))

            # print(all_paths)
            # print("arg_chosen_method_ind 1")
            # first_node = list(arg_defined_graph.nodes)[0]
            # last_node = list(arg_defined_graph.nodes)[-1]

            all_result_data["first_formula"] = first_formula
            all_result_data["second_formula"] = second_formula
            all_result_data["first_formula_functions"] = [
                (first_formula_func,
                 f"P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} ")
            ]
            all_result_data["second_formula_functions"] = [second_formula_func]
        elif arg_chosen_method_ind == 1:  # "Litvak-Ushakov"
            use_disjoint = (True, True)  # True, False

            all_paths = list(nx.all_simple_paths(arg_defined_graph, first_node, last_node))

            # --------------
            all_minimum_cuts = self._get_minimum_cuts(arg_defined_graph, first_node, last_node, 3)
            print(all_minimum_cuts)
            print("\n".join(map(str, all_minimum_cuts)))
            # --------------

            dict_for_first_formula = {}  # simple paths info and formulas (including disjoint paths)
            dict_for_first_formula2 = {}  # minimum cuts info and formulas (including disjoint cuts)

            # dict_for_second_formula = {}
            # value_for_second_formula = -1  # simple paths, minimum power: max(p², p³) = p², 0 ≤ p ≤ 1
            # value_for_second_formula2 = -1  # minimum cuts, maximum power: min(p², p³) = p³, 0 ≤ p ≤ 1

            print("\nAll edge disjoint paths:")
            disjoint_paths = list(nx.edge_disjoint_paths(arg_defined_graph, first_node, last_node))
            # disjoint_paths_tuples = [tuple(one_temp_edge) for one_temp_edge in
            #                          list(nx.edge_disjoint_paths(arg_defined_graph, first_node, last_node))]

            print(disjoint_paths)

            if not use_disjoint[0]:
                disjoint_paths = []

            all_paths_probabilities = "\nAll simple paths (including disjoint paths):\n"
            for one_path_ind in range(len(all_paths)):
                one_path = all_paths[one_path_ind]

                # print(one_path)
                # print(disjoint_paths)
                if one_path in disjoint_paths:
                    if one_path == disjoint_paths[0]:
                        multiply_of_probabilities = "1 - "
                        one_disjoint_path_group = []
                        for one_disjoint_path in disjoint_paths:
                            # print(tuple(one_disjoint_path))

                            all_edges_in_disjoint_path = list(zip(one_disjoint_path, one_disjoint_path[1:]))
                            one_disjoint_path_edges = [tuple(sorted(one_temp_edge)) for one_temp_edge in
                                                       all_edges_in_disjoint_path]

                            multiply_of_probabilities += "(1 - "
                            multiply_of_probabilities += "×".join(
                                "p" + self.get_subscript_number(one_edge[0] + 1) + "₋" + self.get_subscript_number(
                                    one_edge[1] + 1)
                                for one_edge in all_edges_in_disjoint_path
                            )
                            multiply_of_probabilities += ")"

                            one_disjoint_path_group.append(one_disjoint_path_edges)

                        dict_for_first_formula[one_path_ind] = (
                            one_disjoint_path_group,
                            multiply_of_probabilities
                        )
                        # print(dict_for_first_formula[one_path_ind])

                        all_paths_probabilities += (f" {one_path_ind}. {tuple(one_disjoint_path_group)} "
                                                    f"-> {multiply_of_probabilities}\n")
                        print("first path")
                    else:
                        # print("other path")
                        continue
                else:
                    all_edges_in_path = list(zip(one_path, one_path[1:]))
                    one_path_edges = [tuple(sorted(one_temp_edge)) for one_temp_edge in all_edges_in_path]

                    multiply_of_probabilities = "×".join([
                        "p" + self.get_subscript_number(one_edge[0] + 1) + "₋" + self.get_subscript_number(
                            one_edge[1] + 1)
                        for one_edge in all_edges_in_path
                    ])

                    dict_for_first_formula[one_path_ind] = (
                        [list(one_path_edges)],
                        multiply_of_probabilities
                    )

                    all_paths_probabilities += f" {one_path_ind}. {tuple(one_path)} -> {multiply_of_probabilities}\n"

                # dict_for_first_formula2[one_path_edges] = []
                # for one_already_created in dict_for_first_formula2:
                #     if not bool(set(one_already_created) & set(one_path_edges)):
                #         dict_for_first_formula2[one_already_created].append(one_path_edges)
                #         dict_for_first_formula2[one_path_edges].append(one_already_created)

                # amount_probabilities = len(one_path) - 1
                # if amount_probabilities not in dict_for_second_formula:
                #     dict_for_second_formula[amount_probabilities] = 1
                # else:
                #     dict_for_second_formula[amount_probabilities] += 1

                # if value_for_second_formula == -1 or value_for_second_formula > len(one_path_edges):
                #     value_for_second_formula = len(one_path_edges)

            print("\nAll edge disjoint minimum cuts:")
            # disjoint_minimum_cuts_info = {}
            # disjoint_minimum_cuts_connections = []
            #
            # for one_minimum_cut_ind in range(len(all_minimum_cuts)):
            #     disjoint_minimum_cuts_info[tuple(all_minimum_cuts[one_minimum_cut_ind])] = []
            #     for another_minimum_cut_ind in range(len(all_minimum_cuts)):
            #         if one_minimum_cut_ind == another_minimum_cut_ind:
            #             continue
            #         if set(all_minimum_cuts[one_minimum_cut_ind]).isdisjoint(all_minimum_cuts[another_minimum_cut_ind]):
            #             disjoint_minimum_cuts_info[tuple(all_minimum_cuts[one_minimum_cut_ind])].append(
            #                 tuple(all_minimum_cuts[one_minimum_cut_ind]))
            #             if sorted((one_minimum_cut_ind,
            #                        another_minimum_cut_ind)) not in disjoint_minimum_cuts_connections:
            #                 disjoint_minimum_cuts_connections.append(
            #                     sorted((one_minimum_cut_ind, another_minimum_cut_ind)))
            #
            # print("\n".join(map(str, disjoint_minimum_cuts_info.items())))
            # print("\n".join(map(str, disjoint_minimum_cuts_connections)))

            # all_minimum_cuts.reverse()
            # already_one_group = False

            disjoint_minimum_cuts = []
            for one_minimum_cut_ind in range(len(all_minimum_cuts)):
                if one_minimum_cut_ind == 0:
                    disjoint_minimum_cuts.append([all_minimum_cuts[one_minimum_cut_ind]])
                else:
                    minimum_cut_is_added = False
                    # if not already_one_group:
                    for one_already_added_group in disjoint_minimum_cuts:
                        # if len(one_already_added_group) > 1:
                        #     continue
                        cut_is_disjoint = True
                        for one_already_added_cut in one_already_added_group:
                            if not set(all_minimum_cuts[one_minimum_cut_ind]).isdisjoint(one_already_added_cut):
                                cut_is_disjoint = False
                                break
                        if cut_is_disjoint:
                            minimum_cut_is_added = True
                            one_already_added_group.append(all_minimum_cuts[one_minimum_cut_ind])
                            # already_one_group = True
                    if not minimum_cut_is_added:
                        disjoint_minimum_cuts.append([all_minimum_cuts[one_minimum_cut_ind]])

            print("\n".join(map(str, disjoint_minimum_cuts)))

            # print(disjoint_minimum_cuts_info)

            # print(arg_defined_graph.edges)

            if not use_disjoint[1]:
                disjoint_minimum_cuts = [[one_temp_cut] for one_temp_cut in all_minimum_cuts]

            # disjoint_minimum_cuts = [one_path_info[0] for one_path_info in dict_for_first_formula.values()]

            all_minimum_cuts_probabilities = "All minimum cuts (including disjoint minimum cuts):\n"
            # for one_minimum_cut_group_ind in range(len(all_minimum_cuts)):
            for one_minimum_cut_group_ind in range(len(disjoint_minimum_cuts)):
                one_minimum_cut_group = disjoint_minimum_cuts[one_minimum_cut_group_ind]
                if len(one_minimum_cut_group) > 1:
                    multiply_of_improbabilities = ""
                    for the_disjoint_minimum_cut in one_minimum_cut_group:
                        multiply_of_improbabilities += "(1 - " + "×".join([
                            "q" + self.get_subscript_number(one_edge[0] + 1) + "₋" + self.get_subscript_number(
                                one_edge[1] + 1)
                            for one_edge in the_disjoint_minimum_cut
                        ]) + ")"

                    all_minimum_cuts_probabilities += (
                        f" {one_minimum_cut_group_ind}. {one_minimum_cut_group}"
                        f" -> {multiply_of_improbabilities}\n")

                    dict_for_first_formula2[one_minimum_cut_group_ind] = (
                        one_minimum_cut_group,
                        multiply_of_improbabilities
                    )

                else:
                    one_minimum_cut = one_minimum_cut_group[0]
                    # print("asdfa")

                    # all_edges_in_path = list(zip(one_path, one_path[1:]))

                    multiply_of_improbabilities = "1 - " + "×".join([
                        "q" + self.get_subscript_number(one_edge[0] + 1) + "₋" + self.get_subscript_number(
                            one_edge[1] + 1)
                        for one_edge in one_minimum_cut
                    ])
                    all_minimum_cuts_probabilities += (f" {one_minimum_cut_group_ind}. {tuple(one_minimum_cut)}"
                                                       f" -> {multiply_of_improbabilities}\n")

                    # one_path_edges = tuple(tuple(sorted(one_temp_edge)) for one_temp_edge in all_edges_in_path)
                    dict_for_first_formula2[one_minimum_cut_group_ind] = (
                        [one_minimum_cut],
                        multiply_of_improbabilities
                    )

                # dict_for_first_formula2[one_path_edges] = []
                # for one_already_created in dict_for_first_formula2:
                #     if not bool(set(one_already_created) & set(one_path_edges)):
                #         dict_for_first_formula2[one_already_created].append(one_path_edges)
                #         dict_for_first_formula2[one_path_edges].append(one_already_created)

                # if value_for_second_formula2 < len(one_minimum_cut):  # -1 < any possible power
                #     value_for_second_formula2 = len(one_minimum_cut)

            # for one_minimum_cut in

            print(all_paths_probabilities)
            # print(f"Simple paths, minimum power {value_for_second_formula}\n")
            print(all_minimum_cuts_probabilities)
            # print(f"Minimum cuts, maximum power {value_for_second_formula2}\n")
            print(dict_for_first_formula)
            print(dict_for_first_formula2)
            # print(dict_for_second_formula)

            # for info_index, (one_found_path, formula_path) in dict_for_first_formula.items():
            #     print(info_index)
            #     pass

            first_formula = f"P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} ≥ max( "
            first_formula += ", ".join([
                the_one_path_info[1] for the_one_path_info in dict_for_first_formula.values()
            ])
            first_formula += (
                f" )\nP{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} "
                f" ≤ min( ")
            first_formula += ", ".join([  # .replace("p", "q")
                the_one_min_cut_info[1] for the_one_min_cut_info in dict_for_first_formula2.values()
            ])
            first_formula += " )"

            second_formula = f"P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} ≥ max( "
            second_formula += ", ".join(
                ["1 - " + "".join([f"(1 - p{self.get_superscript_number(len(temp_disjoint_path))})"
                                   for temp_disjoint_path in the_one_path_info[0]])
                 if len(the_one_path_info[0]) > 1 else
                 "p" + self.get_superscript_number(len(the_one_path_info[0][0]))
                 for the_one_path_info in dict_for_first_formula.values()]
            )
            second_formula += (
                f" )\nP{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} "
                f" ≤ min( ")
            second_formula += ", ".join([  # .replace("p", "q")
                # "q" + self.get_superscript_number(len(the_one_min_cut_info[1])) for the_one_min_cut_info in
                # dict_for_first_formula2.values()
                "".join([f"(1 - q{self.get_superscript_number(len(temp_disjoint_cut))})"
                         for temp_disjoint_cut in the_one_min_cut_info[0]])
                if len(the_one_min_cut_info[0]) > 1 else
                "1 - q" + self.get_superscript_number(len(the_one_min_cut_info[0][0]))
                for the_one_min_cut_info in dict_for_first_formula2.values()
            ])
            second_formula += " )"

            # first_formula += ", ".join([
            #     the_one_path_info[1] for the_one_path_info in dict_for_first_formula.values()
            # ])

            # second_formula = f"P{self.get_subscript_number(first_node)}₋{self.get_subscript_number(last_node)} = 1 - "
            # second_formula += " ".join([
            #     f"(1 - p{self.get_superscript_number(the_key)})"
            #     f"{self.get_superscript_number(dict_for_second_formula[the_key])}"
            #     for the_key in sorted(dict_for_second_formula.keys())
            # ])
            #
            print(first_formula)
            print(second_formula)

            def first_formula_func1(arg_all_edges_values):  # arg_all_edges_values -> {(0, 1): 2}...
                # multiply_values = 1  # (1 - p₀₋₁×p₁₋₂) (1 - p₀₋₂)...
                all_path_edges_values = []

                improved_edges_values = {}  # replace (1, 0) with (0, 1), just sort keys-edges
                for one_edge_to_sort, one_edge_value in arg_all_edges_values.items():
                    improved_edges_values[tuple(sorted(one_edge_to_sort))] = one_edge_value

                for one_path_group_info in dict_for_first_formula.values():
                    one_path_group = one_path_group_info[0]
                    if len(one_path_group) > 1:
                        multiply_result = 1
                        for the_disjoint_path in one_path_group:
                            one_path_group_all_edges_values = [improved_edges_values[tuple(sorted(one_edge))]
                                                               for one_edge in the_disjoint_path]

                            multiply_result *= 1 - np.prod(one_path_group_all_edges_values)

                        all_path_edges_values.append(1 - multiply_result)
                    else:
                        one_path_group_all_edges = one_path_group[0]
                        # print(one_path_group_all_edges)
                        # tuple(sorted(one_edge))
                        one_path_group_all_edges_values = [improved_edges_values[tuple(sorted(one_edge))]
                                                           for one_edge in one_path_group_all_edges]
                        # print(one_path_group_all_edges_values)
                        all_path_edges_values.append(np.prod(one_path_group_all_edges_values))

                return max(all_path_edges_values)

            def first_formula_func2(arg_all_edges_values):  # arg_all_edges_values -> {(0, 1): 0.5}...
                all_min_cuts_edges_values = []
                improved_edges_values = {}  # replace (1, 0) with (0, 1), just sort keys-edges
                for one_edge_to_sort, one_edge_value in arg_all_edges_values.items():
                    improved_edges_values[tuple(sorted(one_edge_to_sort))] = one_edge_value

                for one_minimum_cut_group_info in dict_for_first_formula2.values():
                    one_cut_group = one_minimum_cut_group_info[0]
                    if len(one_cut_group) > 1:
                        multiply_result = 1
                        for the_disjoint_min_cut in one_cut_group:
                            one_min_cut_all_edges_values = [1 - improved_edges_values[tuple(sorted(one_edge))]
                                                            # q = 1 - p!
                                                            for one_edge in the_disjoint_min_cut]

                            multiply_result *= 1 - np.prod(one_min_cut_all_edges_values)
                        all_min_cuts_edges_values.append(multiply_result)
                    else:
                        # print(one_minimum_cut_info[0])
                        one_min_cut_all_edges = one_cut_group[0]
                        one_min_cut_all_edges_values = [1 - improved_edges_values[tuple(sorted(one_edge))]  # q = 1 - p!
                                                        for one_edge in one_min_cut_all_edges]
                        # multiply_values *= (1 - np.prod(one_min_cut_all_edges_values))
                        all_min_cuts_edges_values.append(1 - np.prod(one_min_cut_all_edges_values))

                return min(all_min_cuts_edges_values)

            def second_formula_func1(arg_general_edge_val):  # arg_general_edge_val -> 1, 0, 0.23, 0.6...
                generated_edge_values = {}
                for the_one_generated_edge in self.chosen_graph_data.edges:
                    generated_edge_values[the_one_generated_edge] = arg_general_edge_val
                return first_formula_func1(generated_edge_values)

            def second_formula_func2(arg_general_edge_val):  # arg_general_edge_val -> 1, 0, 0.23, 0.6...
                generated_edge_values = {}
                for the_one_generated_edge in self.chosen_graph_data.edges:
                    generated_edge_values[the_one_generated_edge] = arg_general_edge_val
                return first_formula_func2(generated_edge_values)
                # all_min_cuts_edges_values = []
                # # multiply_values = 1  # (1 - p₀₋₁×p₁₋₂) (1 - p₀₋₂)...
                # improved_edges_values = {}  # replace (1, 0) with (0, 1), just sort keys-edges
                # for one_edge_to_sort, one_edge_value in arg_all_edges_values.items():
                #     improved_edges_values[tuple(sorted(one_edge_to_sort))] = one_edge_value
                #
                # for one_minimum_cut_info in dict_for_first_formula2.values():
                #     # print(one_minimum_cut_info[0])
                #     one_min_cut_all_edges = one_minimum_cut_info[0]
                #     one_min_cut_all_edges_values = [improved_edges_values[tuple(sorted(one_edge))]
                #                                     for one_edge in one_min_cut_all_edges]
                #     # multiply_values *= (1 - np.prod(one_min_cut_all_edges_values))
                #     all_min_cuts_edges_values.append(np.prod(one_min_cut_all_edges_values))
                #
                # return min(all_min_cuts_edges_values)

            random_generated_edge_values = {}
            for one_defined_edge in self.chosen_graph_data.edges:
                random_generated_edge_values[one_defined_edge] = random.random()
            print(random_generated_edge_values)
            print(first_formula_func2(random_generated_edge_values))

            for one_defined_edge in self.chosen_graph_data.edges:
                random_generated_edge_values[one_defined_edge] = 0.5
            print(random_generated_edge_values)
            print(first_formula_func2(random_generated_edge_values))

            for one_defined_edge in self.chosen_graph_data.edges:
                random_generated_edge_values[one_defined_edge] = 1
            print(random_generated_edge_values)
            print(first_formula_func2(random_generated_edge_values))
            # first_formula_func({(0, 1): 0.5, (0, 2): 0.4})

            all_result_data["first_formula"] = first_formula
            all_result_data["second_formula"] = second_formula
            all_result_data["first_formula_functions"] = [
                (first_formula_func1, "Range of values:"),
                (first_formula_func2,
                 f" ≤ P{self.get_subscript_number(first_node + 1)}₋{self.get_subscript_number(last_node + 1)} ≤ ")
            ]
            all_result_data["second_formula_functions"] = [
                second_formula_func1,
                second_formula_func2
            ]

            # # if p₀₋₁ = p₁₋₂ = ... = pₘ₋ ₙ = p
            # def second_formula_func(arg_general_edge_val):  # arg_general_edge_val -> 0.5, 0.234, 1 ... -> 'p' value
            #     multiply_values = 1
            #     # probability_amount -> p₀₋₂×p₂₋₃×....
            #     # similar_path_amount -> e.g (1 - p₀₋₂×p₂₋₄) and (1 - p₀₋₃×p₃₋₄) are similar because their
            #     # probability amounts are equal
            #     for probability_amount, similar_path_amount in dict_for_second_formula.items():
            #         multiply_values *= pow(1 - pow(arg_general_edge_val, probability_amount), similar_path_amount)
            #     return 1 - multiply_values

            # all_existing_edges = list(self.chosen_graph_data.edges)
            # all_existing_nodes = list(self.chosen_graph_data.nodes)
            # all_minimum_cuts = []
            # # print("Litvak-Ushakov")
            # for one_existing_node in all_existing_nodes[:-1]:
            #     # print(one_existing_node)
            #     all_minimum_cuts.append(nx.minimum_edge_cut(arg_defined_graph, one_existing_node, last_node))
            # # print(all_minimum_cuts)
            # print(nx.minimum_edge_cut(arg_defined_graph, first_node, last_node))
            # all_existing_edges = list(self.chosen_graph_data.edges)
            # all_shortest_paths = list(nx.all_shortest_paths(arg_defined_graph, first_node, last_node))
            # # all_minimum_cuts = nx.minimum_edge_cut(arg_defined_graph, first_node, last_node)
            # # all_minimum_cuts2 = nx.minimum_edge_cut(arg_defined_graph)
            # # all_minimum_cuts3 = nx.algorithms.connectivity.minimum_st_edge_cut(arg_defined_graph, first_node, last_node)
            #
            # # for one_val in range()
            # print(all_shortest_paths)
            # print(all_minimum_cuts)
            # print(all_minimum_cuts2)
            # print(all_minimum_cuts3)
            # if nx.is_connected(arg_defined_graph):
            #     print("Is connected")
            # else:
            #     print("Is NOT connected")

            # print("arg_chosen_method_ind 2")

        finish_time = time.time()
        print(f"\nTIME: Processing took {finish_time - start_time} seconds\n")
        return all_result_data
        # elif arg_chosen_method_ind == 2:
        #     print("arg_chosen_method_ind 3")
        # print(list(nx.all_simple_paths(graph_to_operate,
        #                                list(graph_to_operate.nodes)[0],
        #                                list(graph_to_operate.nodes)[-1])))

        # "Ezari-Proshan" will be omitted!
        # "Exhaustive search" will be omitted too!

    def define_functional_stability_method(self):
        start_time_value = time.time()

        # some_graph = nx.Graph()
        # some_graph.add_nodes_from([0, 1, 2])
        # print(some_graph.nodes(data=True)[0])
        # print(graph_to_operate)
        # print(list(graph_to_operate)[1])
        # print(graph_to_operate.edges)

        # print(graph_to_operate.nodes)
        if self.chosen_method_by_user == "":
            self.label1_defined_chosen_method.show()
            self.label2_defined_chosen_method.show()
            self.formulas_area.show()
            self.the_chart_canvas.show()
            self.node_selection_area.show()
            self.button_to_calculate.show()
            self.calculate_nodes_label.show()
            # print("*No method was chosen before!*")
        # else:

        self.chosen_method_by_user = self.list_of_methods.currentText()
        self.label2_defined_chosen_method.setText(self.chosen_method_by_user)

        method_result_data = self._get_all_info_by_method(self.list_of_methods.currentIndex(), self.chosen_graph_data)

        # if self.chosen_method_by_user not in ["Exhaustive search"]:
        #     print("Not exhaustive search!!!")
        #     return

        # self.formulas_main_label.setText("345")

        self.formulas_main_label.setText("General formula:\n" + method_result_data["first_formula"]
                                         + "\nFormula, if p₁ = p₂ = ... = p:\n" + method_result_data["second_formula"])
        # self.formulas_main_label
        # self.formulas_area
        # self.formulas_area_widget
        # self.layout_selection
        # self.layout_selection.addWidget(QtWidgets.QLabel("asdfjhasdhfdjs"))

        first_functions_info = method_result_data["first_formula_functions"]

        def demonstrate_calculated_info():
            all_given_edges = list(self.chosen_graph_data.edges)
            all_edges_probabilities = {}
            for one_node_ind in range(len(all_given_edges)):
                one_widget_edge_info = self.layout_selection.itemAt(one_node_ind).layout().itemAt(1).widget()
                if isinstance(one_widget_edge_info, QtWidgets.QSlider):
                    all_edges_probabilities[
                        tuple(sorted(all_given_edges[one_node_ind]))] = one_widget_edge_info.value() / 100

            # print(all_edges_probabilities)

            calculated_result = ""
            for one_defined_first_function, str_before_answer in first_functions_info:
                calculated_result += str_before_answer + " " + str(one_defined_first_function(all_edges_probabilities))
                # one_first_formula
            self.calculate_nodes_label.setText(calculated_result)

        self.button_to_calculate.clicked.connect(demonstrate_calculated_info)

        self.the_chart_canvas.ax.cla()
        x_values = np.arange(0, 1, 0.01)
        # print(x_values)
        # second_functions =
        for one_defined_second_function in method_result_data["second_formula_functions"]:
            print([one_defined_second_function(one_x_value) for one_x_value in x_values])
            self.the_chart_canvas.ax.plot(
                x_values, [one_defined_second_function(one_x_value) for one_x_value in x_values]
            )
        self.the_chart_canvas.ax.set_title("Equal probability of functional stability (p₁ = p₂ = ... = p)")
        self.the_chart_canvas.ax.grid()
        self.the_chart_canvas.draw()

        finish_time_value = time.time()

        print(f"\nTIME: Chart building took {finish_time_value - start_time_value} seconds\n")

        # method_result_data

        # self.label_select_method.setText("345345")


class GenerateGraphDialog(QtWidgets.QDialog):
    def __init__(self, previous_entered_data=None):
        super().__init__()
        self.setWindowTitle("Generate random")
        self.setWindowIcon(QtGui.QIcon(f"all_images/generate_graph_dialog.png"))

        all_dialog_buttons = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.main_button_box = QtWidgets.QDialogButtonBox(all_dialog_buttons)
        self.main_button_box.accepted.connect(self.accept)
        self.main_button_box.rejected.connect(self.reject)

        self.main_dialog_label = QtWidgets.QLabel("Choose amounts of nodes and edges")

        # all widgets about nodes
        self.define_nodes_slider = QtWidgets.QSlider(Qt.Horizontal)
        nodes_amount_min = 2
        nodes_amount_max = 20
        self.define_nodes_slider.setMinimum(nodes_amount_min)
        self.define_nodes_slider.setMaximum(nodes_amount_max)

        if previous_entered_data:
            self.define_nodes_slider.setValue(previous_entered_data["previous_entered_nodes_amount"])
        # self.define_nodes_slider.setValue(random.randint(2, 20))

        self.define_nodes_label = QtWidgets.QLabel()
        self.define_nodes_label.setText("Nodes amount:\t" + str(self.define_nodes_slider.value()))

        # all widgets about edges
        self.define_edges_slider = QtWidgets.QSlider(Qt.Horizontal)
        first_nodes_slider_value = self.define_nodes_slider.value()
        self.define_edges_slider.setMaximum(first_nodes_slider_value * (first_nodes_slider_value - 1) // 2)

        # print(previous_entered_data["previous_entered_edges_amount"])
        if previous_entered_data:
            self.define_edges_slider.setValue(previous_entered_data["previous_entered_edges_amount"])

        self.define_edges_label = QtWidgets.QLabel()
        self.define_edges_label.setText("Edges amount:\t" + str(self.define_edges_slider.value()))

        # all slider functions
        def define_nodes_func(arg_node_amount):
            self.define_nodes_label.setText("Nodes amount:\t" + str(arg_node_amount))
            self.define_edges_slider.setMaximum(arg_node_amount * (arg_node_amount - 1) // 2)

        self.define_nodes_slider.valueChanged.connect(define_nodes_func)

        def define_edges_func(arg_node_amount):
            self.define_edges_label.setText("Edges amount:\t" + str(arg_node_amount))

        self.define_edges_slider.valueChanged.connect(define_edges_func)

        # add whole content
        self.main_dialog_layout = QtWidgets.QVBoxLayout(self)
        self.main_dialog_layout.addWidget(self.main_dialog_label)
        self.main_dialog_layout.addWidget(self.define_nodes_slider)
        self.main_dialog_layout.addWidget(self.define_nodes_label)
        self.main_dialog_layout.addWidget(self.define_edges_slider)
        self.main_dialog_layout.addWidget(self.define_edges_label)

        self.main_dialog_layout.addWidget(self.main_button_box)

        # one_edge_probability_slider = QtWidgets.QSlider(Qt.Horizontal)
        # # one_edge_probability_slider = all_info_edges_widgets[one_edge_ind]["edge_probability_slider"]
        # one_edge_probability_slider.setValue(50)
        # one_edge_probability_slider.setMinimumWidth(400)
        #
        # one_edge_probability_val_label.setText("\t\t\t" + str(one_edge_probability_slider.value() / 100))


class AdditionalChartCanvas(FigureCanvasQTAgg):
    # def __init__(self, parent=None, width=5, height=4, dpi=100):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # matplotlib.pyplot.figure()
        self.main_figure, self.ax = plt.subplots(dpi=100)  # facecolor='black'
        # self.main_figure.
        # super(GraphCanvas, self).__init__(Figure(figsize=(width, height), dpi=dpi))
        super(AdditionalChartCanvas, self).__init__(self.main_figure)
        # self.setParent(parent)
        # self.ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="none", edgecolor="black", linewidth=6))

        # self.ax = self.figure.add_subplot(111)
        # self.fig_axes = self.figure.add_axes((0., 1., 0., 1.))


def main():
    # plt.ion()
    app = QtWidgets.QApplication(sys.argv)

    # stylesheet_file_name = "styles.css"
    # with open(stylesheet_file_name, "r") as stylesheet_file:
    #     app.setStyleSheet(stylesheet_file.read())
    # app.setStyleSheet(MAIN_STYLESHEET)
    w = MyMainWindow()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
