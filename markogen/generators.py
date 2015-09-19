
from itertools import count
from sys import maxsize as MAX_INT

from .models import (MarkovGraph,)
from .tokenizers import (SentenceTokenizer,)

class MarkovGenerator(object):
    """"""
    set_tokenizer_cls = SentenceTokenizer

    def __init__(self, order):
        """"""
        self.graph = MarkovGraph(order=order)
        self.set_tokenizer = self.set_tokenizer_cls()

    def learn(self, text):
        """Update the markov chain from the text. Learning is done\
        sentence by sentence. Returns the number of sentences learnt.
        """
        count = 0
        for sentence in self.set_tokenizer.split(text):
            count += 1
            self.graph.update_by_sentence(sentence)
        return count

    @classmethod
    def _ensure_positive_int_param(cls, param_name, param_value=None):
        if param_value is not None:
            try:
                param_value = int(param_value)
                if param_value < 1:
                    raise Exception("%s has to be a strictly positive integer"%param_name)
            except Exception as _:
                raise Exception("%s has to be an integer"%param_name)
        return param_value

    def generate(self, num_sentences=MAX_INT, max_len=MAX_INT, **args):
        """
        """
        param = self._ensure_positive_int_param("Number of sentences", num_sentences)
        max_len = self._ensure_positive_int_param("Maximum length per sentence", max_len)
        root, end = self.graph.root_node_id(), self.graph.end_node_id()
        for step in count():
            if step >= num_sentences: # False if num_sentences = None
                break
            phrase = " "*max_len
            while len(phrase) >= max_len:
                path = next(self.graph.random_walk(root,end))
                phrase = self.graph._path_to_string(path)
            yield phrase
