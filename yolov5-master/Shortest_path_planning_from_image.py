# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 02:26:07 2020

@author: Riad
"""

import math
import cv2
import numpy as np
from sklearn.cluster import KMeans
from collections import deque, namedtuple
import colour

# we'll use infinity as a default distance to nodes.
inf = float('inf')
Edge = namedtuple('Edge', 'start, end, cost')

img = cv2.imread('squareTrack.jpg')
#image = cv2.imread('track-iot-bot-2x2-red-blue.jpg')
# print(height,"x",width,channels)
img = cv2.resize(img, (804, 797))  # this size fitted perfactly with parametar's values 804x797
img = cv2.resize(img, (480,640)) #this size fitted perfactly with parametar's values
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.medianBlur(gray, 5)
edges = cv2.Canny(blur, 50, 150, apertureSize=3)
adapt_type = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
thresh_type = cv2.THRESH_BINARY_INV
bin_img = cv2.adaptiveThreshold(edges, 255, adapt_type, thresh_type, 11, 2)  # image processed

graph = []
# list of tuple will have the distance between object and the nodes
cal = []
data = []
for i in range(1, 17):
    data.append((1000, i))  # (distance,node no)
    cal.append((1000, i))

Node = []
for j in range(0, 3):
    Node.append([1000, j, j])
# print(cal)
# pair=[(0,1),(0,3)]

lines = []

rho, theta, thresh = 1, np.pi / 180, 400
lines = cv2.HoughLines(bin_img, rho, theta, thresh)  # all the lines with slope and rho
from collections import defaultdict

if lines is not None:

    def segment_by_angle_kmeans(lines, k=2, **kwargs):  # k=2 for two colour
        """Groups lines based on angle with k-means.

        Uses k-means on the coordinates of the angle on the unit circle
        to segment `k` angles inside `lines`.
        """

        # Define criteria = (type, max_iter, epsilon)
        default_criteria_type = cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER
        criteria = kwargs.get('criteria', (default_criteria_type, 10, 0.1))
        flags = kwargs.get('flags', cv2.KMEANS_PP_CENTERS)
        attempts = kwargs.get('attempts', 10)

        # returns angles in [0, pi] in radians
        angles = np.array([line[0][1] for line in lines])
        # multiply the angles by two and find coordinates of that angle
        pts = np.array([[np.cos(2 * angle), np.sin(2 * angle)]
                        for angle in angles], dtype=np.float32)

        # run kmeans on the coords
        labels, centers = cv2.kmeans(pts, k, None, criteria, attempts, flags)[1:]
        labels = labels.reshape(-1)  # transpose to row vec

        # segment lines based on their kmeans label
        segmented = defaultdict(list)
        for i, line in zip(range(len(lines)), lines):
            segmented[labels[i]].append(line)
        segmented = list(segmented.values())
        return segmented


    segmented = segment_by_angle_kmeans(lines)


    def intersection(line1, line2):
        """Finds the intersection of two lines given in Hesse normal form.

        Returns closest integer pixel locations.
        See https://stackoverflow.com/a/383527/5087436
        """
        rho1, theta1 = line1[0]
        rho2, theta2 = line2[0]
        A = np.array([
            [np.cos(theta1), np.sin(theta1)],
            [np.cos(theta2), np.sin(theta2)]
        ])
        b = np.array([[rho1], [rho2]])
        x0, y0 = np.linalg.solve(A, b)
        x0, y0 = int(np.round(x0)), int(np.round(y0))
        return [[x0, y0]]


    def segmented_intersections(lines):
        """Finds the intersections between groups of lines."""

        intersections = []
        for i, group in enumerate(lines[:-1]):
            for next_group in lines[i + 1:]:
                for line1 in group:
                    for line2 in next_group:
                        intersections.append(intersection(line1, line2))

        return intersections


    def object_position(point1, point2, point):
        y_y1 = (point[1] - cent[point1 - 1][1])
        x_x1 = (point[0] - cent[point1 - 1][0])
        y2_y1 = (cent[point2 - 1][1] - cent[point1 - 1][1])
        x2_x1 = (cent[point2 - 1][0] - cent[point1 - 1][0])
        # print(y_y1,x_x1,y2_y1,x2_x1)
        return ((y_y1 * x2_x1) - (y2_y1 * x_x1))


    def distance(single_node, point):
        return (math.sqrt((single_node[0] - point[0]) ** 2 + (single_node[1] - point[1]) ** 2))


    def circle(point, center, r):
        return (((point[0] - center[0]) ** 2) + ((point[1] - center[1]) ** 2) - r ** 2)


    pair = []


    def connection(node1):
        #cross_node = [4, 5, 9, 10]
        #copied_cal = cal[:]
        # print(cent[0][0])
        '''if node1 in cross_node:
            copied_cal = cal[:]
            k = 0
            pair = []
            for j in cent:
                n = list(copied_cal[k])
                n[1] = k + 1
                if node1 in cross_node:
                    n[0] = circle(cent[k], cent[node1 - 1], 150)
                    copied_cal[k] = tuple(n)
                    k += 1
            for i in range(0, 5):
                minimum = min(copied_cal)
                mini = list(minimum)
                # print(minimum)
                copied_cal.remove((mini[0], mini[1]))
                pair.append(mini[1])
            pair.remove(node1)
            return (pair)'''


        copied_cal = cal[:]
        middle_node=[7,6,11,10]
        corner_node=[1,4,13,16]
        k = 0
        con = 0
        pair = []
        for j in cent:
            n = list(copied_cal[k])
            n[1] = k + 1
            n[0] = circle(cent[k], cent[node1 - 1], 200)
            copied_cal[k] = tuple(n)
            k += 1
        if node1 in middle_node:
            con = 5
        elif node1 in corner_node:
            con = 3
        else:
            con = 4
        for i in range(0, con):
            minimum = min(copied_cal)
            mini = list(minimum)
            # print(minimum)
            copied_cal.remove((mini[0], mini[1]))
            pair.append(mini[1])
        pair.remove(node1)
        # print(pair)
        return pair


    def node_assign(position, node):
        copied_data = data[:]
        k = 0
        nearest_node = []
        for j in node:
            n = list(copied_data[k])
            n[1] = k + 1
            n[0] = distance(j, position)
            copied_data[k] = tuple(n)
            k += 1
        for i in range(0, 5):
            minimum = min(copied_data)
            mini = list(minimum)
            # print(minimum)
            copied_data.remove((mini[0], mini[1]))
            nearest_node.append(mini[1])
            # print(mini[0])
            # print(nearest_node)
        node_no = Node[:]
        dist = abs(object_position(nearest_node[0], nearest_node[1], position))
        node_no[0][0] = dist
        node_no[0][1] = nearest_node[0]
        node_no[0][2] = nearest_node[1]

        dist = abs(object_position(nearest_node[0], nearest_node[2], position))
        node_no[1][0] = dist
        node_no[1][1] = nearest_node[0]
        node_no[1][2] = nearest_node[2]

        dist = abs(object_position(nearest_node[0], nearest_node[3], position))
        node_no[2][0] = dist
        node_no[2][1] = nearest_node[0]
        node_no[2][2] = nearest_node[3]
        # print(node_no)
        min_node = min(node_no)
        # print(min_node)
        return (min_node[1], min_node[2])


    def make_edge(start, end, cost=1):
        return Edge(start, end, cost)


    class Graph:
        def __init__(self, edges):
            # let's check that the data is right
            wrong_edges = [i for i in edges if len(i) not in [2, 3]]
            if wrong_edges:
                raise ValueError('Wrong edges data: {}'.format(wrong_edges))

            self.edges = [make_edge(*edge) for edge in edges]

        @property
        def vertices(self):
            return set(
                sum(
                    ([edge.start, edge.end] for edge in self.edges), []
                )
            )

        def get_node_pairs(self, n1, n2, both_ends=True):
            if both_ends:
                node_pairs = [[n1, n2], [n2, n1]]
            else:
                node_pairs = [[n1, n2]]
            return node_pairs

        def remove_edge(self, n1, n2, both_ends=True):
            node_pairs = self.get_node_pairs(n1, n2, both_ends)
            edges = self.edges[:]
            for edge in edges:
                if [edge.start, edge.end] in node_pairs:
                    self.edges.remove(edge)

        def add_edge(self, n1, n2, cost=1, both_ends=True):
            node_pairs = self.get_node_pairs(n1, n2, both_ends)
            for edge in self.edges:
                if [edge.start, edge.end] in node_pairs:
                    return ValueError('Edge {} {} already exists'.format(n1, n2))

            self.edges.append(Edge(start=n1, end=n2, cost=cost))
            if both_ends:
                self.edges.append(Edge(start=n2, end=n1, cost=cost))

        @property
        def neighbours(self):
            neighbours = {vertex: set() for vertex in self.vertices}
            for edge in self.edges:
                neighbours[edge.start].add((edge.end, edge.cost))
                neighbours[edge.end].add((edge.start, edge.cost))
            return neighbours

        def dijkstra(self, source, dest):
            assert source in self.vertices, 'Such source node doesn\'t exist'
            distances = {vertex: inf for vertex in self.vertices}
            previous_vertices = {
                vertex: None for vertex in self.vertices
            }
            distances[source] = 0
            vertices = self.vertices.copy()

            while vertices:
                current_vertex = min(
                    vertices, key=lambda vertex: distances[vertex])
                vertices.remove(current_vertex)
                if distances[current_vertex] == inf:
                    break
                for neighbour, cost in self.neighbours[current_vertex]:
                    alternative_route = distances[current_vertex] + cost
                    if alternative_route < distances[neighbour]:
                        distances[neighbour] = alternative_route
                        previous_vertices[neighbour] = current_vertex

            path, current_vertex = deque(), dest
            while previous_vertices[current_vertex] is not None:
                path.appendleft(current_vertex)
                current_vertex = previous_vertices[current_vertex]
            if path:
                path.appendleft(current_vertex)
            return path

        # for l in range(0,)
        # cost.append(object_position(nearest_node[0],nearest_node[1],position))


    point = []

    intersections = segmented_intersections(segmented)  # get the intersection points

    count = 0
    for intr in intersections:
        if 600 >= intr[0][0] >= 120 and 520 >= intr[0][1] >= 110:
            point.append(intr[0])
            # cv2.circle(img, (int(intr[0][0]), int(intr[0][1])), 1, (255, 0, 0),3)
    font = cv2.FONT_HERSHEY_SIMPLEX
    poi = np.asarray(point)
    # plt.scatter(poi[:, 0], poi[:, 1])
    # startpts=np.array([[186.713, 198.375], [329.329, 198.353], [471.408, 198.351], [613.56, 198.361], [187.645, 329.154], [330.333, 329.707], [471.749, 330.283], [614.222, 330.863], [188.481, 458.102], [331.25, 458.079], [472.083, 458.096], [614.764, 458.097], [189.353, 588.27], [332.221, 588.252], [472.425, 588.267], [615.476,588.258]])
    startpts = np.array(
        [[125, 160], [200, 160], [280, 160], [360, 160], [125, 260], [200, 260], [280, 260], [360, 260], [125, 368],
         [200, 368], [280, 368], [360, 368], [125, 474], [203, 474], [280, 474], [360, 474]])

    kmeans = KMeans(n_clusters=16, init=startpts, n_init=1, random_state=0)
    # kmeans = KMeans(n_clusters=16,n_init=1)
    kmeans.fit(point)
    cent = kmeans.cluster_centers_
    # plt.scatter(cent[:, 0], cent[:, 1], c='black', s=200, alpha=0.5)

    i = 0
    for c in cent:
        i += 1
        cv2.circle(img, (int(c[0]), int(c[1])), 30, (0, 0, 255), 3)
        img = cv2.putText(img, str(i), (int(c[0]-10), int(c[1])), font,
                          1.2, (255, 0, 0), 2, cv2.LINE_AA)

    # po = colour.obstacle(image)
    po = [330,140]
    # print("Connection: ",node_assign(po,cent))
    # print(connection(9))
    print("Total Node: ", i)

    for index in range(1, 17):
        arr = connection(index)
        #print("connection",index,arr)
        for d in arr:
            graph.append((str(index), str(d), distance(cent[index - 1], cent[d - 1])))

    # print(graph)
    N = node_assign(po, cent)
    Nl = list(N)
    print(Nl)
    graph.remove((str(Nl[1]), str(Nl[0]), distance(cent[Nl[0] - 1], cent[Nl[1] - 1])))
    graph.remove((str(Nl[0]), str(Nl[1]), distance(cent[Nl[0] - 1], cent[Nl[1] - 1])))
    #print(graph)

    final_graph = Graph(graph)
    #print(final_graph)

    # print(final_graph.dijkstra("1", "11"))

    for i in final_graph.dijkstra("5", "6"):
        print(i)
    cv2.circle(img, (int(po[0]), int(po[1])), 20, (0, 255, 0), 3)
    print(img.shape)
    im = cv2.resize(img, (540, 540))
    #im = cv2.resize(img, (540, 540))
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()