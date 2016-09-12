# coding=UTF-8
import math
from math import sqrt
from math import acos, cos, degrees

class Ponto(object):
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

        self.prox = None
        self.ant = None
        self.edge = None
        self.tipo = None
        self.theta = None

    def __repr__(self):
        return "%s (%s,%s)" % (self.id, self.x, self.y)
        
class Face(object):
    def __init__(self, id, inner):
        self.id = id
        self.inner = inner
    def __repr__(self):
        return "%s - edge: %s" % (self.id, self.inner)

class Edge(object):
    def __init__(self, id, v1, v2, face):
        self.id = id
        self.orig = v1
        self.face = face
        self.twin = None
        self.prox = None
        self.ant = None
        self.v1 = v1
        self.v2 = v2
        self.helper = None

    def __repr__(self):
        return "%s {%s, %s}" % (self.id, self.v1.id, self.v2.id)
    #-----------------------------------------------#
    # Calcula a intersecção de dois segmentos
    # Entrada: um segmento
    # Saida: ponto de interseccao,
    #        false caso nao exista
    #-----------------------------------------------#
    def intersection(self, seg):

        # caso o maior x de uma reta, seja menor que o menor x da outra
        max_x1 = max( self.v1.x, self.v2.x)
        min_x2 = min( seg.v1.x, seg.v2.x)
        if  max_x1 < min_x2:
            # falta tratar para quando o ponto dos segmentos sao os mesmos
            return False

        div1 = (self.v2.x - self.v1.x)
        div2 = (seg.v2.x - seg.v1.x)
        if ((div1 == 0) or (div2 == 0)):
            print "Error! Divisao por 0!"
            return False

        A1 = float((self.v2.y - self.v1.y) / div1)
        A2 = float((seg.v2.y - seg.v1.y) / div2)
        if A1 == A2:
            print "Segmentos paralelos"
            return False

        b1 = self.v2.y - A1 * self.v2.x
        b2 = seg.v2.y - A2 * seg.v2.x

        div = (A1 - A2)
        if div == 0:
            print "Error! Divisao por 0 nao permitida"
            return False

        x_intersec = float((b2 - b1) / div)

        # aqui soh aceita segmento no momento
        # adapatar para aceitar retas e semi-retas
        if (x_intersec < max(min(self.v1.x, self.v2.x),min(seg.v1.x, seg.v2.x)) or\
            x_intersec > min(max(self.v1.x, self.v2.x),max(seg.v1.x, seg.v2.x))):
            print x_intersec, "false"
            return False
        else:
            print "Se encontram em ", x_intersec
            return x_intersec

    # a fazer: retorna o vertice logo acima da aresta
    def origin(self):
        return self.v1

    def next(self):
        return self.orig.edge


    # a fazer: retorna o vertice logo abaixo da aresta
    def helper_merge(self):
        return True



class Triangulo(object):
    # no caso, recebe os indices dos vertices
    def __init__(self, vertices):
        self.vertices = []
        for v in vertices:
            self.vertices.append(v)

    def __str__(self):
        return "%s %s %s"%(self.vertices[0], self.vertices[1], self.vertices[2])




class Poligono(object):
    def __init__(self, vertices):
        self.num_triangulos = None
        self.triangulos = []
        self.monotone = []
        self.edges = []
        self.vertices = vertices
        self.faces = []
        outer_face = Face(0, None)
        inner_face = Face(1, None)
        self.faces.append(outer_face)
        self.faces.append(inner_face)


        # forma o poligono na ordem em que foi dada na entrada
        for i in xrange(0, len(vertices)):
            # incia os vertices
            self.vertices[i-1].prox = self.vertices[i]
            self.vertices[i].ant = vertices[i-1]

            # inicia as arestas
            if i < len(vertices)-1:
                e = Edge(i+1,vertices[i], vertices[i+1], inner_face)
                e_twin = Edge(-(i+1), vertices[i+1], vertices[i], outer_face)

                # inicia as faces
                if self.faces[1].inner == None:
                    self.faces[1].inner = e
                if self.faces[0].inner == None:
                    self.faces[0].inner = e_twin

                # insere a nova aresta na estrutura do poligono
                self.edges.append(e)
                self.vertices[i].edge = e
                self.edges[i].twin = e_twin

        # inicia a última aresta
        e = Edge(len(vertices), vertices[len(vertices)-1], vertices[0], inner_face)
        e_twin = Edge(-len(vertices), vertices[0], vertices[len(vertices)-1], outer_face)
        self.edges.append(e)
        self.vertices[len(vertices)-1].edge = e
        self.edges[len(vertices)-1].twin = e_twin

        for i in xrange(0, len(vertices)):
            self.edges[i-1].prox = self.edges[i]
            self.edges[i-1].twin.prox = self.edges[i].twin
            self.edges[i].ant = self.edges[i-1]
            self.edges[i].twin.ant = self.edges[i-1].twin

            p2 = self.edges[i].twin.orig
            ref = self.edges[i].orig
            p1 = self.edges[i].ant.orig

            x1, y1 = p1.x - ref.x, p1.y - ref.y
            x2, y2 = p2.x - ref.x, p2.y - ref.y
            ref.theta = theta(x1, y1, x2, y2)            
    #-----------------------------------------------#
    # Decompoe o poligono em poligonos monotonicos
    # Entrada: poligono simples P
    # Saida: uma divisao de P em poligono monotonico
    #-----------------------------------------------#
    def monotone_decomposition(self):
        print "monotone_decomposition()"
        print "..."
        Q = self.vertices[:]
        quick_order_y(Q, 0, len(Q)-1)
        print_v(Q)
        classify(Q)
        print_v(Q)
        return True


def angulo(e1, e2):
    p2 = e1.v2
    ref = e1.orig
    p1 = e2.orig

    x1, y1 = p1.x - ref.x, p1.y - ref.y
    x2, y2 = p2.x - ref.x, p2.y - ref.y
    return theta(x1,y1,x2,y2)
#-----------------------------------------------#
# Ordenação de vértices pela coordenada y, baseado
# em quicksort
# Entrada: uma lista de vertices
# Saida: a lista ordenada pela coordenada y
#-----------------------------------------------#
def quick_order_y(v, esq, dir):
    pivo = esq
    for i in xrange(esq+1, dir+1):
        j = i
        if v[j].y < v[pivo].y:
            aux = v[j]
            while j > pivo:
                v[j] = v[j-1]
                j -= 1
            v[j] = aux
            pivo += 1               
    if pivo-1 >= esq:
        quick_order_y(v, esq, pivo-1)
    if pivo+1 <= dir:
        quick_order_y(v, pivo+1, dir)


#-----------------------------------------------#
# Recebe dois vértices e retorna o angulo entre
# angulo entre eles
# Entrada:
# Saida:
#-----------------------------------------------#
def theta(x1, y1, x2, y2): # adaptar para receber um segmento
    dot = (x1 * x2) + (y1 * y2)
    denom = sqrt((x1 ** 2 + y1 ** 2) * (x2 ** 2 + y2 ** 2))
    if x1 * y2 < x2 * y1:
        angulo = math.degrees(acos(dot/denom))
    else:
        angulo = 360.0 - math.degrees(acos(dot/denom))
    return int(angulo)


#-----------------------------------------------#
# Função que implementa sweep line para dividir
# o poligono em pedaços monotônicos
# Entrada: um Poligono
# Saída: uma subdivisão em D
#-----------------------------------------------#
def sweep(p):
    status = []
    D = []
    Q = p.vertices[:]
    quick_order_y(Q, 0, len(Q)-1)
    while Q:
        v = Q.pop()
        p.monotone.append(v)
        handle_vertex(p, v, status)

#-----------------------------------------------#
# Lida com cada tipo de vertice
# Entrada: um vértice
# Saída: a função apropriada para cada tipo de
#        vértice
#-----------------------------------------------#
def handle_vertex(p, v, status):
    # vertice do tipo start
    if abaixo(v, v.ant) and abaixo(v, v.prox) and v.theta < 180:
        v.tipo = 'start'
        p.edges[v.id-1].helper = p.vertices[v.id-1]
        status.append(p.edges[v.id-1])

    # vertice do tipo end
    if acima(v, v.ant) and acima(v, v.prox) and v.theta < 180:
        v.tipo = 'end'
        if p.edges[v.id-2].helper.tipo == 'merge':
            insere_diagonal(p, v, p.edges[v.id-2].helper)
        status.remove(p.edges[v.id-2])

    # vertice do tipo split
    if abaixo(v, v.ant) and abaixo(v, v.prox) and v.theta > 180:
        v.tipo = 'split'
        aresta = esquerda(status, v)
        insere_diagonal(p, v, aresta.helper)
        aresta.helper = v
        p.edges[v.id-1].helper = v
        status.append(p.edges[v.id-1])

    # vertice do tipo merge
    if acima(v, v.ant) and acima(v, v.prox) and v.theta > 180:
        v.tipo = 'merge'
        if p.edges[v.id-2].helper.tipo == 'merge':
            insere_diagonal(p, v, p.edges[v.id-2].helper)
        status.remove(p.edges[v.id-2])
        aresta = esquerda(status, v)
        if aresta.helper.tipo == 'merge':
            insere_diagonal(p, v, aresta.helper)
        aresta.helper = v

    # vertice normal
    if (abaixo(v, v.ant) and acima(v, v.prox)) or (abaixo(v, v.prox) and acima(v, v.ant)):
        v.tipo = 'regular'
        # Caso o interior do poligono esteja para direita
        if interior_dir(v):
            # caso o helper da aresta for do tipo merge, insere uma diagonal em D
            if p.edges[v.id-2].helper.tipo == 'merge':
                insere_diagonal(p, v, p.edges[v.id-2].helper)
            status.remove(p.edges[v.id-2])
            p.edges[v.id-1].helper = v
            status.append(p.edges[v.id-1])
        else:
            aresta = esquerda(status, v)
            # caso o helper da aresta for do tipo merge, insere uma diagonal em D
            if aresta.helper.tipo == 'merge':
                insere_diagonal(p, v, p.edges[v.id-1].helper)
            aresta.helper = v
    return

#-----------------------------------------------#
# Insere uma diagonal do vertice ao helper em D
# Entrada: um vertice e o helper
# Saída: insere a aresta formada pelos dois vertices
#        em D
#-----------------------------------------------#
def interior_dir(v):
    return True

def triangulo(e):
    v1 = e.prox.prox.v2.id
    v2 = e.v1.id
    if v1 == v2:
        return True
    else:
        return False

#-----------------------------------------------#
# Calcula a triangulacao de um poligono
# Entrada: self
# Saida: um poligono triangulado,
#        false caso nao exista
#-----------------------------------------------#
def triangulate(p):
    # uma fila Q 
    Q = p.faces[1:]

    while Q:
        f = Q.pop(0)
        # 'e' é a aresta inicial da face 'f'
        e = f.inner
        v1 = e.prox.prox.v2.id
        v2 = e.v1.id
        # caso não seja um triangulo, insere uma diagonal
        if v1 != v2:

            # se o angulo formado entre os vertices for maior que 
            # 180, significa que a diagonal ficará fora do poligono
            # então troca até pegar uma ponta
            while angulo(e, e.ant) >= 180:
                e = e.ant
                f.inner = e
                
            v = e.prox.orig
            helper = e.ant.orig
            # cria uma nova face
            new_face = Face(len(p.faces), None)
            # cria a diagonal e sua twin
            diagonal = Edge(len(p.edges)+1, v, helper, f)
            twin = Edge(len(p.edges)+2, helper, v, new_face)
            
            # a proxima da diagonal, tem a mesma face que a aresta do helper 
            # a anterior também
            diagonal.prox = e.ant
            diagonal.ant  = e
            # a twin da diagonal recebe a nova face
            twin.prox = e.prox
            twin.ant  = e.ant.ant


            e.ant.ant.prox = twin
            e.ant.ant = diagonal
            e.prox.ant = twin
            e.prox = diagonal
            
            # a nova face é a face associada à 'twin' da nova diagonal
            new_face.inner = twin

            diagonal.twin = twin
            twin.twin = diagonal

            # atualiza as faces que as arestas adicionadas apontam
            diagonal.face = f
            diagonal.prox.face = f
            diagonal.ant.face  = f
            # para as semi-arestas correspondentes também
            twin.face = new_face
            twin.prox.face = new_face
            twin.ant.face  = new_face

            p.edges.append(diagonal)
            p.edges.append(twin)
            p.faces.append(new_face)

            # adiciona a nova face na fila
            Q.append(p.faces[-1])
    return True


#-----------------------------------------------#
# Insere uma diagonal do vertice ao helper em D
# Entrada: um vertice e o helper
# Saída: insere a aresta formada pelos dois vertices
#        em D
#-----------------------------------------------#
def insere_diagonal(p, v, helper):
    
    diag_prox = p.edges[helper.edge.id - 1]
    diag_ant  = p.edges[v.edge.ant.id - 1]
    twin_prox = p.edges[v.edge.id - 1]
    twin_ant  = p.edges[helper.edge.ant.id - 1]

    # cria uma nova face
    new_face = Face(len(p.faces), None)
    # cria a diagonal e sua twin
    diagonal = Edge(len(p.edges)+1, v, helper, diag_prox.face)
    twin = Edge(len(p.edges)+2, helper, v, new_face)
    
    # a proxima da diagonal, tem a mesma face que a aresta do helper 
    diagonal.prox = diag_prox
    diag_prox.ant = diagonal
    # a nova face é a face associada à 'twin' da nova diagonal
    new_face.inner = twin
    twin_prox.face.inner = diagonal

    # a anterior também
    diagonal.ant  = diag_ant
    diag_ant.prox = diagonal

    # a twin da diagonal recebe a nova face
    twin.prox = twin_prox
    twin_prox.ant = twin
    twin.ant  = twin_ant
    twin_ant.prox = twin

    diagonal.twin = twin
    twin.twin = diagonal

    p.edges.append(diagonal)
    p.edges.append(twin)
    p.faces.append(new_face)

    v.edge.ant = diagonal.twin
    #print 'v.edge ', v.edge
    helper.edge = diagonal.twin
    #print 'helper.edge ', helper.edge

    inicio = twin.v1
    e = twin.prox
    while e.v1 != inicio:
        e.face = new_face
        e = e.prox
    #print diagonal, new_face
    #print 'arestas de v',p.edges[v.id-1], p.edges[v.id-2]
    #print 'arestas de helper',  p.edges[helper.id-1], p.edges[helper.id-2]
    return True

def monotone_piece(p, diagonal):

    inicio = diagonal.v1
    v = diagonal.v2
    while v != inicio:
        v = v.prox
        return True

#-----------------------------------------------#
# Função para encontrar a aresta imediatamente
# à esquerda do vertice v
# Entrada: um lista, um vertice
# Saída: a aresta à esquerda de v
#-----------------------------------------------#
def esquerda(status, v):
    menor = 1000000
    ej = None
    for e in status:
        d = distancia(e, v)
        if d < menor:
            menor = d
            ej = e
    return ej

#-----------------------------------------------#
# Funções helper
#-----------------------------------------------#
def distancia(e, v):
    num = (e.v2.y - e.v1.y)*v.x - (e.v2.x - e.v1.x)*v.y + e.v2.x * e.v1.y - e.v2.y * e.v1.x
    denom = sqrt( (e.v2.y - e.v1.y)**2 + (e.v2.x - e.v1.x)**2 )
    if denom == 0:
        return False
    else:
        return  num / denom

def abaixo(p, q):
    if (q.y < p.y or (q.y == p.y and q.x > p.x) ):
        return True
    return False

def acima(p, q):
    if (q.y > p.y) or (q.y == p.y and q.x < p.x):
        return True
    return False

def cross_sign(x1, y1, x2, y2):
    return x1 * y2 < x2 * y1

def print_v(vertices):
    for v in vertices:
        print "     ", v, " 0: ", v.theta
        #print v.ant, " --- ", v.prox
        print ""

def print_s(arestas):
    for s in arestas:
        print s, s.face.id, s.prox

def print_f(faces):
    for f in faces:
        print 'face: ', f
        inicio = f.inner
        e = inicio.prox
        while e != inicio:
            print e
            e = e.prox
        #print f
        #   print f.inner.prox
