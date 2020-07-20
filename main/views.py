from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import json
import networkx as nx
from math import radians, cos, sin, asin, sqrt
from itertools import islice
import time

locations = [(1, {"lat": 40.685080276663726, "long": -73.947172164917}), (2, {"lat": 40.68434805779277, "long": -73.94700050354005}), (3, {"lat": 40.68905039003287, "long": -73.94509077072145}), (4, {"lat": 40.68833448542927, "long": -73.94494056701662}), (5, {"lat": 40.68761857313474, "long": -73.94476890563966}), (6, {"lat": 40.68690265314925, "long": -73.94464015960695}), (7, {"lat": 40.68618672547289, "long": -73.94451141357423}), (8, {"lat": 40.68542197605053, "long": -73.9443612098694}), (9, {"lat": 40.68464094630648, "long": -73.94421100616456}), (10, {"lat": 40.68942460983294, "long": -73.9422369003296}), (11, {"lat": 40.68865989756615, "long": -73.94208669662477}), (12, {"lat": 40.6879439887675, "long": -73.94195795059206}), (13, {"lat": 40.6872280722779, "long": -73.94180774688722}), (14, {"lat": 40.68649587700388, "long": -73.9416790008545}), (15, {"lat": 40.68576367368543, "long": -73.94152879714967}), (16, {"lat": 40.68499891940862, "long": -73.94140005111696}), (17, {"lat": 40.68900157859967, "long": -73.93925428390504}), (18, {"lat": 40.688253132146784, "long": -73.93912553787233}), (19, {"lat": 40.68752094813503, "long": -73.93899679183961}), (20, {"lat": 40.686805027100796, "long": -73.93880367279054}), (21, {"lat": 40.686024013564754, "long":  -73.93871784210206}), (22, {"lat": 40.68532434783307, "long": -73.93852472305299}), (23, {"lat": 40.684608403201835, "long": -73.93837451934816}), (24, {"lat": 40.68929444666259, "long": -73.93635749816896}), (25, {"lat": 40.68859481526591, "long": -73.936185836792}), (26, {"lat": 40.68786263500829, "long": -73.93605709075929}), (27, {"lat": 40.68716298857928, "long": -73.93592834472658}), (28, {"lat": 40.686398250359545, "long": -73.93575668334962}), (29, {"lat": 40.68569858855671, "long": -73.93562793731691}), (30, {"lat": 40.684950105007914, "long": -73.93545627593996}) ]
edges = [[1,2], [1,8], [2,9], [3,4], [3,10], [4,5], [4,11], [5,6], [5,12], [6,7], [6,13], [7,8], [7,14], [8,9], [8,15], [9,16], [10,11], [11,12], [11,17], [12,13], [12,18], [13,14], [13,19], [14,15], [14,20], [15,16], [15,21], [16,22], [17,18], [17, 24], [18, 19], [18,25], [19, 20], [19, 26], [20,21], [20,27], [21,22], [21,28], [22,23], [22,29], [23,30], [24,25], [25,26], [26,27], [27,28], [28,29], [29,30] ]


def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))


def haversine(point1, point2):
    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2

    return 2 * 6371.0088 * asin(sqrt(d)) * 1000

Map = nx.Graph()

# Add Nodes
Map.add_nodes_from(locations)

# Compute Distances and add the edges
for _ in range(len(edges)):
    a, b = edges[_]
    dist = haversine((Map.nodes[a]["lat"], Map.nodes[a]["long"]), (Map.nodes[b]["lat"], Map.nodes[b]["long"]))
    Map.add_edges_from([(a, b, {"dist": dist})])


def index(request):
    return render(request, 'index.html')


def func(i, num_of_cars, temp, all_solutions, p_paths_edge):
    # #print("i - " + str(i))
    if i == num_of_cars:
        all_solutions.append(list(temp))
        # #print(all_solutions)
        return

    for j in range(len(p_paths_edge[i])):
        temp.append(p_paths_edge[i][j])
        func(i+1, num_of_cars, temp, all_solutions, p_paths_edge)
        temp.pop()
    return


def proc(src, dest, spec_sol,ind_spec):
    num_of_cars = len(src)
    p_paths_node = []
    p_paths_edge = []

    for s, d in zip(src, dest):
        # Add Yembarwar disimilarity
        p_paths_node.append(k_shortest_paths(Map, s, d, 10, "dist"))

    # #print("3")
    # #print(p_paths_node)
    for cars in p_paths_node:
        t2 = []
        for paths in cars:
            t1 = []
            for p in range(len(paths) - 1):
                if paths[p] < paths[p + 1]:
                    t1.append(
                        {'edge': edges.index([min(paths[p], paths[p + 1]), max(paths[p], paths[p + 1])]), 'dir': 0})
                else:
                    t1.append(
                        {'edge': edges.index([min(paths[p], paths[p + 1]), max(paths[p], paths[p + 1])]), 'dir': 1})
                    # t1.append(edges.index([min(paths[p], paths[p+1]), max(paths[p], paths[p+1])]))
            t2.append(t1)
        p_paths_edge.append(t2)

    # #print("4")
    # #print(p_paths_edge)

    all_solutions = []
    temp = []
    func(0, num_of_cars, temp, all_solutions, p_paths_edge)
    # #print(all_solutions)
    # #print("------------------------------------------------------------")

    if spec_sol:
        for sol in all_solutions:
            for r in range(len(ind_spec)):
                sol.insert(int(ind_spec[r]), spec_sol[r])

    # #print("5")
    # #print(all_solutions)
    ans = all_solutions[0]
    ans_len = 0
    min_cong = 9999999
    # #print(len(all_solutions))
    for sol in all_solutions:
        # #print(".")
        # #print(sol)
        max_timestep = 0
        for car in sol:
            max_timestep = max(max_timestep, len(car))

        cong_tmp = 0
        for t in range(max_timestep):
            map = [0 for val in range(94)]
            for c in range(len(sol)):
                try:
                    if sol[c][t]['dir'] == 0:
                        map[sol[c][t]['edge']] += 1
                    else:
                        map[sol[c][t]['edge'] + 47] += 1
                except:
                    pass

            cong_tmp += sum(val * val for val in map)
        tmp_len = sum(len(pa) for pa in sol)
        # #print('####################')
        # #print(sol)
        # #print('---------------------')
        # #print(cong_tmp)
        # #print('####################')

        if cong_tmp < min_cong or cong_tmp == min_cong and tmp_len < ans_len:
            ans = sol
            min_cong = cong_tmp
            ans_len = tmp_len

    return ans


def dat_inp(request):
    if request.method == 'POST':
        # #print(request.POST)
        src = [5]
        dest = [25]
        ind_spec = request.POST.getlist('spec[]')
        #print("ind_spec");
        #print(ind_spec);
        #print("----------------------------------------------------------")
        src_spec = []
        dest_spec = []

        for i in range(20):
            try:
                srctmp = request.POST.get('src' + str(i+1))
                desttmp = request.POST.get('dest' + str(i+1))
                if srctmp and desttmp and int(srctmp) < 31 and int(desttmp) < 31 and int(srctmp) > 0 and int(desttmp) > 0:
                    if str(i+1) in ind_spec:
                        src_spec.append(int(srctmp))
                        dest_spec.append(int(desttmp))
                    else:
                        src.append(int(srctmp))
                        dest.append(int(desttmp))
            except:
                pass

        #print("src");
        #print(src);
        #print("----------------------------------------------------------")
        #print("src_spec");
        #print(src_spec);
        #print("----------------------------------------------------------")
        # #print("2")
        # #print(src)
        # #print(dest)
        spec_sol = proc(src_spec, dest_spec, [], [])
        #print("spec_sol");
        #print(spec_sol);
        #print("----------------------------------------------------------")
        
        ans = proc(src, dest, spec_sol, ind_spec)
        #print("ans");
        #print(ans);
        #print("----------------------------------------------------------")
        

        # #print("6")
        # #print(ans[0])
        fin_sol = []
        for car in ans:
            tmp = []
            for t in car:
                tmp.append(edges[t['edge']])
            fin_sol.append(tmp)

        # #print(fin_sol)

        lat_long = []
        for car in fin_sol:
            t2 = []
            for path in car:
                t1 = []
                for pos in path:
                    t1.append([locations[pos-1][1]['lat'], locations[pos-1][1]['long']])
                t2.append(t1)
            lat_long.append(t2)

        for r in range(len(ind_spec)):
            src.insert(int(ind_spec[r]), src_spec[r])
            dest.insert(int(ind_spec[r]), dest_spec[r])

        #print("src");
        #print(src);
        #print("----------------------------------------------------------")
        #print("dest");
        #print(dest);
        #print("----------------------------------------------------------")
        
        time.sleep(2) 
        return JsonResponse({'success': 1, 'paths': lat_long, 'src': src, 'dest': dest})
        # return HttpResponse(json.dumps({'success': 1}))
    return JsonResponse({'success': 0})
