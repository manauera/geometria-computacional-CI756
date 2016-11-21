# coding=UTF-8
class Point(object):
    def __init__(self, x, y, segment=None):
        self.x = x
        self.y = y
        self.segment = segment

    def __repr__(self):
        return "(%s,%s) - %s" % (self.x, self.y, self.segment.id)

# funções para executar uma ordenação em um array de Point
def getKeyX(point):
    return point.x
def getKeyY(point):
    return point.y

class Segment(object):
    def __init__(self, id, x1, x2, y1, y2):
        self.id = id
        if y1 > y2:
            self.upper = Point(x1, y1, self)
            self.lower = Point(x2, y2, self)
            if x1 < x2:
                self.left = Point(x1, y1, self)
                self.right = Point(x2, y2, self)
            else:
                self.left = Point(x2, y2, self)  
                self.right = Point(x1, y1, self)
        else:
            self.upper = Point(x2, y2, self)
            self.lower = Point(x1, y1, self)
            if x2 < x1:
                self.left = Point(x2, y2, self)
                self.right = Point(x1, y1, self)
            else:
                self.left = Point(x1, y1, self)
                self.right = Point(x2, y2, self)
        self.reported = False

    def __repr__(self):
        return "%s" % (self.id)

class Window(object):
    def __init__(self, x, x1, y, y1):
        self.x1 = x1
        self.y1 = y1
        self.x = x
        self.y = y

class Node(object):
    def __init__(self, key, point):
        self.key = key
        self.point = point
        self.left = None
        self.right = None
        self.tree_assoc = None
        self.height = 1

    def __repr__(self):
        return "[%s - %s]" % (self.point.segment.id, self.height)

class IntNode(object):
    def __init__(self, interval):
        self.key = interval
        self.segments = None
        self.left = None
        self.right = None
        self.height = 1

    def __repr__(self):
        if self.segments:
            return "%s %s - S:%s" % (self.key, self.height, self.segments)
        else:
            return "%s %s" % (self.key, self.height)

class Interval(object):
    def __init__(self, x, x1, closed, semi=False):
        if x < x1:
            self.left = x 
            self.right = x1
        else:
            self.left = x1
            self.right = x
        self.semiclosed = semi
        self.closed = closed

    def __repr__(self):
        if self.semiclosed == 1:
            return "(%s:%s]" % (self.left, self.right)
        if self.semiclosed == 2:
            return "[%s:%s)" % (self.left, self.right)
        if self.closed:
            return "[%s:%s]" % (self.left, self.right)
        else:
            return "(%s:%s)" % (self.left, self.right)



#---------------------------------------------------#
# Função que recebe segmentos e uma janela, retornando
# os segmentos dentro dela
#
# Entrada: uma lista de segmentos e uma janela [x:x']x[y:y']
# Saída: os segmentos que estão dentro da janela
#---------------------------------------------------#
def windowQuery(segments, window):
    endpoints = []
    for s in segments:
        endpoints.append(s.upper)
        endpoints.append(s.lower)

    sorted_endpoints_x = sorted(endpoints, key=getKeyX)
    sorted_endpoints_y = sorted(endpoints, key=getKeyY)
    

    window_left = Segment(-1, window.x, window.x, window.y, window.y1)
    window_right = Segment(-2, window.x1, window.x1, window.y, window.y1)
    window_top = Segment(-3, window.x, window.x1, window.y1, window.y1)
    window_bottom = Segment(-4, window.x, window.x1, window.y, window.y)

    elem_intervals_v = interval_x(sorted_endpoints_x)
    elem_intervals_h = interval_y(sorted_endpoints_y)


    rtree = RangeTree(sorted_endpoints_x)
    stree_v = segmentTree(elem_intervals_v, segments, True)
    stree_h = segmentTree(elem_intervals_h, segments, False)



    q1 = query2DRangeTree(rtree, window.x, window.x1, window.y, window.y1)

    q2 = []
    querySegmentTreeVertical(stree_v, window_left, q2)
    querySegmentTreeVertical(stree_v, window_right, q2)
    querySegmentTreeHorizontal(stree_h, window_top, q2)
    querySegmentTreeHorizontal(stree_h, window_bottom, q2)

    return q1 + q2

#---------------------------------------------------#
# Função para gerar intervalos elementares para a
# árvore de segmentos
#
# Entrada: uma lista P de pontos
# Saída: intervalos elementares baseados no eixo-x
#---------------------------------------------------#
def interval_x(P):
    response = []
    response.append(Interval(-float("inf"), P[0].x, False))
    i = 0
    while i < len(P)-1:
        if P[i].x != P[i+1].x:
            response.append(Interval(P[i].x, P[i].x, True))
            response.append(Interval(P[i].x, P[i+1].x, False))
        i += 1
    response.append(Interval(P[-1].x, P[-1].x, True))
    response.append(Interval(P[-1].x, float("inf"), False))
    return response

#---------------------------------------------------#
# Função para gerar intervalos elementares para a
# árvore de segmentos
#
# Entrada: uma lista P de pontos
# Saída: intervalos elementares baseados no eixo-y
#---------------------------------------------------#
def interval_y(P):
    response = []
    response.append(Interval(-float("inf"), P[0].y, False))
    i = 0
    while i < len(P)-1:
        if P[i].y != P[i+1].y:
            response.append(Interval(P[i].y, P[i].y, True))
            response.append(Interval(P[i].y, P[i+1].y, False))
        i += 1
    response.append(Interval(P[-1].y, P[-1].y, True))
    response.append(Interval(P[-1].y, float("inf"), False))
    return response

#---------------------------------------------------#
# Função para gerar a árvore de segmentos baseada
# nos intervalos elementares
#
# Entrada: uma lista I de intervalos elementares
# Saída: uma árvore de segmentos
#---------------------------------------------------#
def segmentTree(I, segments, vertical):
    root = intervalTree(I)
    for s in segments:
        if vertical:
            insertSegmentVertical(root, s)
        else:
            insertSegmentHorizontal(root, s)
    return root

def intervalTree(I):
    if len(I) == 1:
        v = IntNode(I[0])
    else:
        left, right = split2(I)

        if left[0].closed and right[-1].closed:
            v = IntNode(Interval(left[0].left, right[-1].right, True))
        # fechado à direita
        if not left[0].closed and right[-1].closed:
            v = IntNode(Interval(left[0].left, right[-1].right, False, 1))
        # fechado à esquerda
        if left[0].closed and not right[-1].closed:
            v = IntNode(Interval(left[0].left, right[-1].right, False, 2))
        if not left[0].closed and not right[-1].closed:
            v = IntNode(Interval(left[0].left, right[-1].right, False))

        l_left = intervalTree(left)
        l_right = intervalTree(right)

        v.left = l_left
        v.right = l_right
        v.height = max(height(v.left), height(v.right)) + 1
    return v

#---------------------------------------------------#
# Insere um segmento na árvore de segmentos baseado
# no eixo x
#
# Entrada: o nó raiz da árvore e o segmento
# Saída: NA
#---------------------------------------------------#
def insertSegmentVertical(node, s):
    if not node:
        return
    if intervalContainedX(node.key, s):
        node.segments = insert_y(node.segments, s.upper)
        return
    else:
        if node.left:
            if s.left.x <= node.left.key.right:
                insertSegmentVertical(node.left, s)
        if node.right:
            if s.right.x >= node.right.key.left:
                insertSegmentVertical(node.right, s)

#---------------------------------------------------#
# Insere um segmento na árvore de segmentos baseado
# no eixo y
#
# Entrada: o nó raiz da árvore e o segmento
# Saída: NA
#---------------------------------------------------#
def insertSegmentHorizontal(node, s):
    if not node:
        return
    if intervalContainedY(node.key, s):
        node.segments = insert_x(node.segments, s.upper)
        return
    else:
        if node.left:
            if s.lower.y <= node.left.key.right:
                insertSegmentHorizontal(node.left, s)
        if node.right:
            if s.upper.y >= node.right.key.left:
                insertSegmentHorizontal(node.right, s)


#---------------------------------------------------#
# Responde se um intervalo está completamente contido
# entre os endpoints do segmento baseado no eixo x
#
# Entrada: um intervalo e um segmento
# Saída: True caso o intervalo esteja completamente contido
#        False caso contrário
#---------------------------------------------------#
def intervalContainedX(intvl, s):
    if s.left.x <= intvl.left and intvl.right <= s.right.x:
        return True
    return False

#---------------------------------------------------#
# Responde se um intervalo está completamente contido
# entre os endpoints do segmento baseado no eixo y
#
# Entrada: um intervalo e um segmento
# Saída: True caso o intervalo esteja completamente contido
#        False caso contrário
#---------------------------------------------------#
def intervalContainedY(intvl, s):
    if s.lower.y <= intvl.left and intvl.right <= s.upper.y:
        return True
    return False

#---------------------------------------------------#
# Faz uma busca na árvore de segmentos baseado em uma
# fronteira vertical da janela de busca e guarda a 
# resposta em response
#
# Entrada: o nó raiz, um segmento de busca vertical e 
#          um array para armazenar a resposta
# Saída: NA
#---------------------------------------------------#
def querySegmentTreeVertical(node, q, response):
    if leaf(node):
        response += reportIntersectionVertical(node.segments, q)
        return

    if node.left.key.closed:
        if q.upper.x <= node.left.key.right:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.left, q, response)
    else:
        if not node.left.key.semiclosed and q.upper.x < node.left.key.right:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.left, q, response)

        if node.left.key.semiclosed == 1 and q.upper.x <= node.left.key.right:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.left, q, response)

        if node.left.key.semiclosed == 2 and q.upper.x < node.left.key.right:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.left, q, response)          

    if node.right.key.closed:
        if q.upper.x >= node.right.key.left:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.right, q, response)
    else:
        if not node.right.key.semiclosed and q.upper.x > node.right.key.left:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.right, q, response)

        if node.right.key.semiclosed == 1 and q.upper.x > node.right.key.left:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.right, q, response)

        if node.right.key.semiclosed == 2 and q.upper.x >= node.right.key.left:
            response += reportIntersectionVertical(node.segments, q)
            querySegmentTreeVertical(node.right, q, response)
    return 

#---------------------------------------------------#
# Faz uma busca na árvore de segmentos baseado em uma
# fronteira horizontal da janela de busca e guarda a 
# resposta em response
#
# Entrada: o nó raiz, um segmento de busca horizontal e 
#          um array para armazenar a resposta
# Saída: NA
#---------------------------------------------------#
def querySegmentTreeHorizontal(node, q, response):
    if leaf(node):
        response += reportIntersectionHorizontal(node.segments, q)
        return

    if node.left.key.closed:
        if q.left.y <= node.left.key.right:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.left, q, response)
    else:
        if not node.left.key.semiclosed and q.left.y < node.left.key.right:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.left, q, response)

        if node.left.key.semiclosed == 1 and q.left.y <= node.left.key.right:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.left, q, response)

        if node.left.key.semiclosed == 2 and q.left.y < node.left.key.right:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.left, q, response)            

    if node.right.key.closed:
        if q.left.y >= node.right.key.left:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.right, q, response)
    else:
        if not node.right.key.semiclosed and q.left.y > node.right.key.left:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.right, q, response)

        if node.right.key.semiclosed == 1 and q.left.y > node.right.key.left:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.right, q, response)

        if node.right.key.semiclosed == 2 and q.left.y >= node.right.key.left:
            response += reportIntersectionHorizontal(node.segments, q)
            querySegmentTreeHorizontal(node.right, q, response)
    return 

#---------------------------------------------------#
# Realiza a busca no subconjunto canônico e reporta 
# os segmentos que intersectam uma fronteira vertical
# da janela
#
# Entrada: o nó raiz e um segmento de busca vertical 
# Saída: os segmentos que intersectam 
#---------------------------------------------------#
def reportIntersectionVertical(node, q):
    response = []
    
    if not node:
        return response
    if not node.point.segment.reported:
        if intersects(node.point.segment, q):
            response.append(node.point.segment.id)
            node.point.segment.reported = True
            if node.left:
                response += reportIntersectionVertical(node.left, q)
            if node.right:
                response += reportIntersectionVertical(node.right, q)
        else:
            if node.key > q.upper.y:
                if node.left:
                    response += reportIntersectionVertical(node.left, q)
            else:
                if node.right:
                    response += reportIntersectionVertical(node.right, q)
    else:
        response += reportIntersectionVertical(node.left, q)
        response += reportIntersectionVertical(node.right, q)
    return response

#---------------------------------------------------#
# Realiza a busca no subconjunto canônico e reporta 
# os segmentos que intersectam uma fronteira horizontal
# da janela
#
# Entrada: o nó raiz e um segmento de busca horizontal 
# Saída: os segmentos que intersectam 
#---------------------------------------------------#
def reportIntersectionHorizontal(node, q):
    response = []
    
    if not node:
        return response
    if not node.point.segment.reported:
        if intersects(node.point.segment, q):
            response.append(node.point.segment.id)
            node.point.segment.reported = True
            if node.left:
                response += reportIntersectionHorizontal(node.left, q)
            if node.right:
                response += reportIntersectionHorizontal(node.right, q)
            #return response
        else:
            if node.key > q.upper.x:
                if node.left:
                    response += reportIntersectionHorizontal(node.left, q)
                    #return response
            else:
                if node.right:
                    response += reportIntersectionHorizontal(node.right, q)
                    #return response
    else:
        response += reportIntersectionHorizontal(node.left, q)
        response += reportIntersectionHorizontal(node.right, q)
    return response

#---------------------------------------------------#
# calculo de intereseção de segmentos
#---------------------------------------------------#
def ccw(A,B,C):
    return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def intersects(s1, s2):
    return intersect(s1.upper, s1.lower, s2.upper, s2.lower)
#---------------------------------------------------#

#---------------------------------------------------#
# Monta uma Range Tree 2D baseado em pontos no plano
#
# Entrada: um conjunto de pontos
# Saída: nó raiz da árvore
#---------------------------------------------------#
def RangeTree(P):
    T = avlTree(P)
    if len(P) == 0:
        return
    if len(P) == 1:
        v = Node(P[0].x, P[0])
        v.tree_assoc = T
    else:
        #--------------------------------------------#
        # Divide o conjunto de pontos com base na
        # mediana da coordenada x em duas listas, esquerda
        # e direita, onde pontos com coordenada menor
        # que x_mid na esquerda, e maiores à direita
        left, right = split(P)
        # guarda o nó do meio, no caso, o maior da lista
        # da esquerda
        x_mid = left.pop(getRootIndex(left))

        v_left = RangeTree(left)
        v_right = RangeTree(right)
        v = Node(x_mid.x, x_mid)
        v.left = v_left
        v.right = v_right

        # guarda a raiz da árvore balanceada associada
        # no nó do meio
        v.tree_assoc = T
        #--------------------------------------------#

        v.height = max(height(v.left), height(v.right)) + 1

    return v

#---------------------------------------------------#
# Busca em uma Range Tree 2D baseado em uma janela
#
# Entrada: a raiz da Range Tree e uma janela
# Saída: pontos que estão dentro da janela
#---------------------------------------------------#
def query2DRangeTree(node, x, x1, y, y1):
    response = []
    v_split = findSplitNode(node, x, x1)
    if leaf(v_split):
        if (x < v_split.point.x and v_split.point.x < x1 and
            y < v_split.point.y and v_split.point.y < y1):
            if not v_split.point.segment.reported:
                response.append(v_split.point.segment.id)
                v_split.point.segment.reported = True
    else:
        if (x < v_split.point.x and v_split.point.x < x1 and
            y < v_split.point.y and v_split.point.y < y1):
            if not v_split.point.segment.reported:
                response.append(v_split.point.segment.id)
                v_split.point.segment.reported = True
        v = v_split.left
        while not leaf(v):
            if x <= v.point.x:
                response.extend(query1DRangeTree(v.tree_assoc, y, y1))
                v = v.left
            else:
                v = v.right
        if v and v.point.segment.reported:
            if (x < v.point.x and v.point.x < x1 and
                y < v.point.y and v.point.y < y1):
                response.append(v.point.segment.id)
                v.point.segment.reported = True

        v = v_split.right
        while not leaf(v):
            if v.point.x < x1:
                response.extend(query1DRangeTree(v.tree_assoc, y, y1))
                v = v.right
            else:
                v = v.left
        if v and not v.point.segment.reported:
            if (x < v.point.x and v.point.x < x1 and
                y < v.point.y and v.point.y < y1):
                response.append(v.point.segment.id)
                v.point.segment.reported = True

    return response

#---------------------------------------------------#
# Busca em uma Range Tree 1D baseado em uma janela
#
# Entrada: a raiz da Range Tree e uma janela
# Saída: pontos que estão dentro da janela
#---------------------------------------------------#
def query1DRangeTree(node, x, x1):
    response = []
    v_split = findSplitNode(node, x, x1)
    if leaf(v_split):
        if x < v_split.key and v_split.key < x1:
            if not v_split.point.segment.reported:
                response.append(v_split.point.segment.id)
                v_split.point.segment.reported = True
    else:
        if x < v_split.key and v_split.key < x1:
            if not v_split.point.segment.reported:
                response.append(v_split.point.segment.id)
                v_split.point.segment.reported = True
        #--------------------------------------------#
        # percorre a subárvore à esquerda do nó split
        # e reporta todos os pontos à direita.
        #

        v = v_split.left
        while not leaf(v):
            if x < v.key:
                reportSubtree(v.right, response)
                v = v.left
            else:
                v = v.right
        if v and x < v.key:
            if not v.point.segment.reported:
                response.append(v.point.segment.id)
                v.point.segment.reported = True
        #
        # semelhante para o limite de x'
        #
        v = v_split.right
        while not leaf(v):
            if v.key < x1:
                reportSubtree(v.left, response)
                v = v.right
            else:
                v = v.left
        if v and v.key < x1:
            if not v.point.segment.reported:
                response.append(v.point.segment.id)
                v.point.segment.reported = True
        #
        #--------------------------------------------#
    return response

#---------------------------------------------------#
# Função que concatena recursivamente os nós na
# resposta que será reportada
#
# Entrada: um nó e uma lista de resposta
# Saída: NA
#---------------------------------------------------#
def reportSubtree(node, response):
    if not node:
        return True
    reportSubtree(node.left, response)
    reportSubtree(node.right, response)
    if not node.point.segment.reported:
        response.append(node.point.segment.id)
        node.point.segment.reported = True
    return True

#---------------------------------------------------#
# Função que encontra e retorna o nó split
#
# Entrada: nó raiz e um intervalo [x:x']
# Saída: nó split
#---------------------------------------------------#
def findSplitNode(node, x, x1):
    v = node
    while not leaf(v) and (x1 <= v.key or x > v.key):
        if x1 <= v.key:
            v = v.left
        else:
            v = v.right
    return v

#---------------------------------------------------#
# Função que divide uma coleção de pontos em
# menores que a mediana das coordenas-x
#
# Entrada: uma coleção de pontos
# Saída: duas listas de pontos, P_left e P_right
#---------------------------------------------------#
def split(points):
    left = []
    right = []
    if len(points) % 2 == 0:
        x_mid = len(points)/2
    else:
        x_mid = (len(points)-1)/ 2

    i = 0

    while i <= x_mid:
        left.append(points[i])
        i += 1
    while i < len(points):
        right.append(points[i])
        i += 1

    return left, right

def split2(points):
    left = []
    right = []
    if len(points) % 2 == 0:
        x_mid = len(points)/2
    else:
        x_mid = (len(points)-1)/ 2

    i = 0

    while i < x_mid:
        left.append(points[i])
        i += 1
    while i < len(points):
        right.append(points[i])
        i += 1

    return left, right

#---------------------------------------------------#
# Função que devolve o maior elemento de uma lista
# de pontos com base na coordenada-x
#
# Entrada: uma coleção de pontos
# Saída: índice do maior elemento
#---------------------------------------------------#
def getRootIndex(t):
    maior = 0
    i = 0
    for e in t:
        if t[maior].x < e.x:
            maior = i
        i += 1
    return maior

#---------------------------------------------------#
# Função identifica se o nó é folha
#
# Entrada: um nó
# Saída: True se for um nó folha,
#        False caso contrário
#---------------------------------------------------#
def leaf(node):
    if not node or (not node.left and not node.right):
        return True
    return False



#---------------------------------------------------#
#------------- Funções para árvore AVL -------------#
#---------------------------------------------------#

#---------------------------------------------------#
# Entrada: uma coleção de pontos, e um booleano
#          indicando por qual coordenada será 
#          usada como chave (true para eixo x)
# Saída: uma arvore binária balanceada
#---------------------------------------------------#
def avlTree(P):
    root = None
    for point in P:
        root = insert_y( root, point )
    return root

#---------------------------------------------------#
# Função recursiva para inserir um ponto na árvore
# com base na coordenada y
#
# Entrada: o nó raiz e o ponto a ser inserido
# Saída: uma arvore binária balanceada
#---------------------------------------------------#
def insert_y(node, point):
    if not node:
        n = Node( point.y, point )
        return n
    else:
        if node.key < point.y:
            node.right = insert_y( node.right, point )
        else:
            node.left = insert_y( node.left, point )

    node.height = max(height(node.left), height(node.right)) + 1

    balance = get_balance(node)
    
    if balance > 1 and point.y < node.left.key:
        return rot_right(node)
    if balance > 1 and point.y > node.left.key:
        return rot_left_right(node)
    
    if balance < -1 and point.y > node.right.key:
        return rot_left(node)
    if balance < -1 and point.y < node.right.key:
        return rot_right_left(node)

    return node

#---------------------------------------------------#
# Função recursiva para inserir um ponto na árvore
# com base na coordenada x
#
# Entrada: o nó raiz e o ponto a ser inserido
# Saída: uma arvore binária balanceada
#---------------------------------------------------#
def insert_x(node, point):
    if not node:
        n = Node( point.x, point )
        return n
    else:
        if node.key < point.x:
            node.right = insert_x( node.right, point )
        else:
            node.left = insert_x( node.left, point )

    node.height = max(height(node.left), height(node.right)) + 1

    balance = get_balance(node)
    
    if balance > 1 and point.x < node.left.key:
        return rot_right(node)
    if balance > 1 and point.x > node.left.key:
        return rot_left_right(node)
    
    if balance < -1 and point.x > node.right.key:
        return rot_left(node)
    if balance < -1 and point.x < node.right.key:
        return rot_right_left(node)

    return node

#---------------------------------------------------#
# Funções helpers para manter balanceamento da AVL
#---------------------------------------------------#
def rot_right(y):
    x = y.left
    y.left = x.right
    x.right = y

    y.height = max(height(y.left), height(y.right)) + 1
    x.height = max(height(x.left), height(x.right)) + 1

    return x

def rot_left(y):
    x = y.right
    y.right = x.left
    x.left = y 

    y.height = max(height(y.left), height(y.right)) + 1
    x.height = max(height(x.left), height(x.right)) + 1

    return x

def rot_left_right(n):
    n.left = rot_left(n.left)
    return rot_right(n)

def rot_right_left(n):
    n.right = rot_right(n.right)
    return rot_left(n)

# imprime a árvore "deitada"
def imprime_arv(node):
    if not node:
        return
    imprime_arv(node.left)
    esp = ''
    for i in xrange(node.height):
        esp = esp + "    "
    print esp, node
    imprime_arv(node.right)

# retorna o balanceamento do nó para a árvore AVL
# 0 caso não exista
def get_balance(node):
    if not node:
        return 0
    return height(node.left) - height(node.right)

# retorna a altura do nó, 0 caso não exista
def height(node):
    if not node:
        return 0
    return node.height

# função para reiniciar os segmentos como se não tivessem
# sido reportados ainda
def clean(s, ids):
    for i in ids:
        s[i-1].reported = False