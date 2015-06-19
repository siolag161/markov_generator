
from collections import deque
from itertools import izip

from .tools import weighted_choice
from .tokenizers import (HappyTokenizer, CobeTokenizer)

class Graph(object):
    """ Inspired from the networkx graph.
    from https://github.com/networkx/networkx/blob/master/LICENSE.txt
    """
    def __init__(self, **attrs):
        self.node = dict()
        self.pred = dict()
        self.succ = dict()
        self.adj = self.succ
        self.edge = {}
        self.graph = {}
        self.graph.update(attrs)

    def add_node(self, node, attr_dict=None, **attrs):
        if attr_dict is None:
            attr_dict = attrs
        else:
            try:
                attr_dict.update(**attrs)
            except AttributeError:
                raise Exception('the attr_dict arg must be a dict')

        if node not in self.succ:
            self.succ[node] = {}
            self.pred[node] = {}
            self.node[node] = attr_dict
        else:
            self.node[node].update(attr_dict)

    def __iter__(self):
        return iter(self.node)

    def node_iter(self, data=False):
        if data:
            return iter(self.node.items())
        else:
            return iter(self.node)

    def nodes(self, data=False):
        return list(self.node_iter(data=data))

    def num_nodes(self):
        return len(self.node)

    def graph_order(self):
        return len(self.node)

    def add_edge(self, pred, succ, attr_dict=None, **attrs):
        if attr_dict is None:
            attr_dict = attrs
        else:
            try:
                attr_dict.update(**attrs)
            except AttributeError:
                raise Exception('the attr_dict arg must be a dict')

        if pred not in self.succ:
            self.succ[pred] = {}
            self.pred[pred] = {}
            self.node[pred] = {}

        if succ not in self.succ:
            self.succ[succ] = {}
            self.pred[succ] = {}
            self.node[succ] = {}

        datadict = self.adj[pred].get(succ, dict())
        datadict.update(attr_dict)
        self.succ[pred][succ] = datadict
        self.pred[succ][pred] = datadict

    def num_edges(self, unique=True):
        """number of edges in the graph"""
        edges = list((q for _, v in self.adj.iteritems() if v\
                       for _, q in v.iteritems()))
        if unique:
            return sum(1 for _ in edges)
        else:
            return sum(u.get('count', 0) for u in edges)

    def update_edge_attrs(self, pred, succ, **attrs):
        datadict = self.adj[pred].get(succ, dict())
        datadict.update(**attrs)
        self.succ[pred][succ] = datadict
        self.pred[succ][pred] = datadict

    def edge_iter(self, data=False):
        node_nbrs = self.adj.iteritems()
        if data:
            for node, nbrs in node_nbrs:
                for nbr, ddict in nbrs.iteritems():
                    yield (node, nbr, ddict)
        else:
            for node, nbrs in node_nbrs:
                for nbr in nbrs:
                    yield (node, nbr)

    def get_edge(self, pred, succ):
        return self.succ[pred][succ]

    def successors_iter(self, node):
        """
        """
        try:
            return iter(self.succ[node])
        except KeyError:
            raise Exception("The node %s is not in the digraph."%(node,))

    def successors(self, node):
        return list(self.successors_iter(node))

    def out_edges_iter(self, node, data=True):
        if data:
            nbrs = self.succ[node]
            for nbr, ddict in nbrs.iteritems():
                yield (node, nbr, ddict)
        else:
            for nbr in nbrs:
                yield (node, nbr)

class MarkovGraph(Graph):
    """"""
    START_TOKEN = "[START]"
    END_TOKEN = "[END]"
    tokenizer_cls = CobeTokenizer

    def __init__(self, order, **attr):
        super(MarkovGraph, self).__init__(**attr)
        self.order = order
        self.toks = {}
        self.tokenizer = self.tokenizer_cls()
        self.START_CONTEXT = [self.START_TOKEN]*self.order
        self.END_CONTEXT = [self.END_TOKEN]*self.order

        self.last_token_key = "token_%d"%(self.order-1)

    def add_token_node(self, tokens):
        if len(tokens) != self.order:
            raise Exception("token length must be"\
               "equal to order (%d)" %self.order)

        key = self._node_key_from_tokens(tokens)
        if key in self.toks:
            return self.toks[key]

        node_id = self.num_nodes()
        attr_dict = {"token_%d"%(idx): token \
                     for idx, token in enumerate(tokens)}
        super(MarkovGraph, self).add_node(node_id, attr_dict)
        self.toks[key] = node_id
        return node_id

    def _tokenize(self, sentence):
        tokens = self.tokenizer.split(sentence)
        return self.START_CONTEXT + tokens + self.END_CONTEXT

    def _contexts_by_sentence(self, sentence):
        tokens = self._tokenize(sentence)
        context = deque(maxlen=self.order)
        has_space = False
        for i in xrange(len(tokens)):
            context.append(tokens[i])
            if len(context) == self.order:
                if tokens[i] == ' ':
                    context.pop()
                    has_space = True
                    continue
                yield tuple(context), has_space
                context.popleft()
                has_space = False
    @classmethod
    def _node_key_from_tokens(cls, tokens):
        return "".join(token for token in tokens)

    @classmethod
    def _edges_by_contexts(cls, contexts):
        prev = None
        for curr in contexts:
            if prev is None:
                prev = curr
                continue
            yield prev[0], curr[0], curr[1]
            prev = curr

    def update_by_sentence(self, sentence):
        contexts = self._contexts_by_sentence(sentence)
        for prev, curr, has_space in self._edges_by_contexts(contexts):
            prev_node = self.add_token_node(prev)
            curr_node = self.add_token_node(curr)
            self.add_edge(prev_node, curr_node, has_space=has_space)

    def node_by_tokens(self, tokens):
        key = self._node_key_from_tokens(tokens)
        return self.node[self.toks[key]]

    def node_by_id(self, node_id):
        return self.node[node_id]

    def random_step(self, node):
        nbrs = [(succ, dat["count"]) for (_, succ, dat) \
                 in self.out_edges_iter(node)]
        succ = weighted_choice(nbrs)
        return succ

    def edge_count(self, pred, succ):
        """get the count property"""
        datadict = self.adj[pred].get(succ, dict())
        return datadict.get("count", 0)

    def add_edge(self, pred, succ, attr_dict=None, **attrs):
        super(MarkovGraph, self).add_edge(pred, succ, attr_dict, **attrs)
        count = self.edge_count(pred, succ) + 1
        self.update_edge_attrs(pred, succ, count=count)

    def random_walk(self, start_node, end_node):
        nodes = deque([(start_node, tuple())])
        while nodes:
            curr, path = nodes.popleft()
            succ, _ = self.random_step(curr)
            newpath = path + (succ,)
            if succ == end_node:
                yield newpath
            else:
                nodes.append((succ, newpath))

    def node_id_by_tokens(self, tokens):
        key = self._node_key_from_tokens(tokens)
        if key not in self.toks:
            raise Exception("No node with such tokens footprint")
        return self.toks[key]

    def root_node(self, ):
        """"""
        return self.node_by_tokens(self.START_CONTEXT)

    def root_node_id(self,):
        return self.node_id_by_tokens(self.START_CONTEXT)

    def end_node(self, ):
        """"""
        return self.node_by_tokens(self.END_CONTEXT)

    def end_node_id(self,):
        return self.node_id_by_tokens(self.END_CONTEXT)

    def _path_to_edges(self, path):
        for pred, succ in izip(path[:-1], path[1:]):
            ptoken = self.node[pred][self.last_token_key]
            stoken = self.node[succ][self.last_token_key]
            if ptoken != self.END_TOKEN or stoken != self.END_TOKEN:
                yield self.node[pred][self.last_token_key],\
                    self.node[succ][self.last_token_key],\
                    self.get_edge(pred, succ)["has_space"]

    def _path_to_string(self, path):
        edges = self._path_to_edges(path)
        return "".join(token+" " if has_space else token for \
                     token, _, has_space in edges)
