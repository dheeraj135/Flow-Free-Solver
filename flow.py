from z3 import *
import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin

app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def solve(phi):
    s = Solver()
    s.add(phi)
    r = s.check()
    if r==sat:
        print("sat")
        m = s.model()
        return m
    else:
        print("unsat")
        return None

def sum_to_one(ls):
    return PbEq([(x,1) for x in ls], 1)

def sum_to_x(ls, sumx):
    return PbEq([(x,1) for x in ls], sumx)

def sum_atleast(ls, sumx):
    return PbGe([(x,1) for x in ls], sumx)

class Flow:
    def __init__(self, matrix,num_colors:int):
        self.n = len(matrix)
        self.m = len(matrix[0])
        self.num_colors = num_colors
        self.inp_matrix = matrix
        self.types = 2
        self.base_matrix = [[[[Bool ("e_{}_{}_{}_{}".format(i,j,k,l)) for l in range(self.types)] for k in range(num_colors)] for j in range(self.m)] for i in range(self.n)] 

    def single_color(self):
        final_conds = []
        for i in range(self.n):
            for j in range(self.m):
                lst = []
                for k in range(self.num_colors):
                    for l in range(self.types) :
                        lst.append(self.base_matrix[i][j][k][l])
                final_conds.append(sum_to_one(lst))
        return And(final_conds)
    
    def set_default_vals(self):
        final_conds = []
        for i in range(self.n):
            for j in range(self.m):
                if (self.inp_matrix[i][j] != 0):
                    final_conds.append(self.base_matrix[i][j][self.inp_matrix[i][j]-1][1])
                else:
                    for k in range(self.num_colors):
                        final_conds.append(Not(self.base_matrix[i][j][k][1]))
        return And(final_conds)

    def special_conds(self):
        movx = [0,0,-1,1]
        movy = [-1,1,0,0]
        final_conds = []
        for i in range(self.n):
            for j in range(self.m):
                box_conds = []
                for k in range(self.num_colors):
                    for l in range(4):
                        ii = i+movx[l]
                        jj = j+movy[l]
                        if ii<0 or ii>=self.n or jj<0 or jj>=self.m:
                            continue
                        box_conds.append(And(self.base_matrix[i][j][k][1],Or(self.base_matrix[ii][jj][k][0],self.base_matrix[ii][jj][k][1])))

                    for l in range(4):
                        ii = i+movx[l]
                        jj = j+movy[l]
                        if ii<0 or ii>=self.n or jj<0 or jj>=self.m:
                            continue
                        for m in range(l+1,4):
                            iii = i+movx[m]
                            jjj = j+movy[m]
                            if iii<0 or iii>=self.n or jjj<0 or jjj>=self.m:
                                continue
                            box_conds.append(And(self.base_matrix[i][j][k][0], Or(self.base_matrix[ii][jj][k][0],self.base_matrix[ii][jj][k][1]),
                                                                               Or(self.base_matrix[iii][jjj][k][0],self.base_matrix[iii][jjj][k][1]) ))
                final_conds.append(sum_to_one(box_conds))
        
        return And(final_conds)
                    

    def work(self):
        x = []
        x.append( self.set_default_vals() )
        x.append( self.single_color() )
        x.append( self.special_conds() )
        # print(x)
        return x

    def print_grid(self,model):
        if model == None:
            print("F")
            return None
        ans = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                for k in range(self.num_colors):
                    val = model[self.base_matrix[i][j][k][0]]
                    val1 = model[self.base_matrix[i][j][k][1]]
                    if is_true(val):
                        print(k+1,end=' ')
                        row.append(k+1)
                    if is_true(val1):
                        row.append(k+1)
                        print(str(k+1), end = ' ')
            ans.append(row)
            print('')
        return ans

input_mat = [
                [1,0,4,0,4,5,0],
                [2,0,7,0,0,6,0],
                [0,0,0,0,7,0,0],
                [0,0,0,0,6,0,5],
                [1,3,2,0,0,0,0],
                [0,0,0,0,0,3,0],
                [0,0,0,0,0,0,0]
            ]

input_mat8 = [
                [0,0,0,0,5,6,5,0],
                [0,0,0,0,4,0,7,0],
                [0,0,2,0,0,0,0,0],
                [0,0,0,0,0,6,7,0],
                [0,0,2,1,0,0,0,0],
                [0,0,0,0,0,3,0,0],
                [0,1,3,4,0,0,0,0],
                [0,0,0,0,0,0,0,0],
]
input_mat9 = [
                [0,0,0,0,0,0,0,0,0],
                [0,1,7,8,0,0,0,0,0],
                [0,0,0,7,9,0,9,8,0],
                [0,0,0,0,0,0,0,4,0],
                [0,2,0,2,1,0,0,0,0],
                [3,4,0,0,0,0,0,6,5],
                [0,5,3,0,0,0,0,0,0],
                [0,6,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0],

]

def to_2D_matrix(l,n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def to_1D_matrix(l):
    flatten_list = [j for sub in l for j in sub]
    return flatten_list

def filter(matrix):
    n = len(matrix)
    m = len(matrix[0])

    count = {}

    for i in range(n):
        for j in range(m):
            if(matrix[i][j]):
                if matrix[i][j] in count:
                    count[matrix[i][j]]+= 1
                else:
                    count[matrix[i][j]] = 1
    
    mapping = {}
    inverse_mapping = {}
    num_colors = 1

    mapping[0] = 0
    inverse_mapping[0] = 0
    for i in count:
        if count[i] != 2:
            return -1,-1,-1
        mapping[i] = num_colors
        inverse_mapping[num_colors] = i
        num_colors += 1

    for i in range(n):
        for j in range(m):
            matrix[i][j] = mapping[matrix[i][j]]

    return matrix,inverse_mapping,num_colors-1

def reverse(matrix, mapping):
    n = len(matrix)
    m = len(matrix[0])

    for i in range(n):
        for j in range(m):
            matrix[i][j] = mapping[matrix[i][j]]
    return matrix

@app.route('/get-solution/', methods=['POST'])
@cross_origin()
def process():
    data = request.json
    n = data["N"]
    m = data["M"]
    matrix = data["input"]
    matrix = to_2D_matrix(matrix,m)
    print(matrix)
    print(len(matrix))
    input_matrix,mapping,num_colors = filter(matrix)
    print(input_matrix)
    print(mapping)
    print(num_colors)
    flow = Flow(input_matrix, num_colors)
    m = solve(flow.work())
    output_matrix = flow.print_grid(m)
    if not output_matrix:
        return jsonify ({"output": -1})
    output_matrix = reverse(output_matrix,mapping)
    output_matrix = to_1D_matrix(output_matrix)
    return jsonify({"output":output_matrix})

app.run()
# for i in range(3):
#     for j in range(i+1,3):
#         print(i,j)