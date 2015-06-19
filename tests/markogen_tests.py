
from nose.tools import *
from collections import deque

import unittest

from markogen.models import *
from markogen.tools import *

# def setup():
#     print "SETUP!"

# def teardown():
#     print "TEAR DOWN!"

# def test_basic():
#     print "I RAN!"


class testGraphModel(unittest.TestCase):

    def test_construction(self):
        graph = MarkovGraph(order = 3)
        self.assertEqual(graph.order, 3)

    def test_add_nodes(self):
        g = MarkovGraph(order = 3)
        tokens = "a dogs love me not".split()
        self.assertRaises(Exception, g.add_token_node, tokens)
        self.assertEqual(g.num_nodes(), 0)
        for token_group in sliding_window(tokens, 3):
            g.add_token_node(token_group)
        self.assertEqual(g.num_nodes(), 3)

    def test_add_edges(self):
        g = MarkovGraph(order = 3)
        tokens = "a dog loves me not".split()
        for token_group in sliding_window(tokens, 3):
            g.add_token_node(token_group)
        self.assertEqual(g.num_nodes(), 3)
        g.add_edge(0,1)
        g.add_edge(0,1)
        g.add_edge(0,1)
        self.assertEqual(g.edge_count(0,1), 3)
        self.assertEqual(g.edge_count(1,2), 0)
        self.assertEqual(g.node_by_id(0), g.node_by_tokens("adogloves"))
        self.assertEqual(g.node_by_id(0),
                         {'token_1':'dog','token_0':'a','token_2':'loves'})

    def test_random_step(self):
        g = MarkovGraph(order = 3)
        tokens = "a dogs love me not".split()
        for token_group in sliding_window(tokens, 3):
            g.add_token_node(token_group)
        self.assertEqual(g.num_nodes(), 3)
        g.add_edge(0,1)
        g.add_edge(0,1)
        g.add_edge(0,1)
        g.add_edge(0,2)
        g.add_edge(0,2)
        self.assertEqual(g.num_edges(), 2)
        self.assertEqual(g.num_edges(unique=False), 5)
        counters = {1:0, 2:0}
        SAMPLES = 100000
        for i in xrange(SAMPLES):
            step = g.random_step(0)
            counters[step[0]] += 1
        self.assertAlmostEqual(0.6, counters[1]*1.0/SAMPLES, 2)
        self.assertAlmostEqual(0.4, counters[2]*1.0/SAMPLES, 2)

    def test_tokenize(self):
        sentence = "a dog loves me not"
        g = MarkovGraph(order=2)
        tokens = g._tokenize(sentence)

    def test_update_sentence(self):
        sentence = "i love your bunny cun"
        g = MarkovGraph(order=3)
        g.update_by_sentence(sentence)
        self.assertEqual(g.num_nodes(), 9)
        self.assertEqual(g.num_edges(), 8)

    def test_random_walk(self):
        sentence = "i love your bunny cun."
        g = MarkovGraph(order=3)
        g.update_by_sentence(sentence)
        root,end = g.root_node_id(), g.end_node_id()
        path = next(g.random_walk(root,end))
        phrase = g._path_to_string(path)
        self.assertEqual(phrase, sentence)
        order = 3
        sentence = """i love your puppy i love your cat i love your cat"""
        g = MarkovGraph(order=order)
        g.update_by_sentence(sentence)
        root,end = g.root_node_id(), g.end_node_id()
        path = next(g.random_walk(root,end))
        phrase = g._path_to_string(path)
