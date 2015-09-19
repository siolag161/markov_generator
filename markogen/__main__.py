#!/usr/bin/env python

import argparse
import os.path

from .models import MarkovGraph
from .tokenizers import SentenceTokenizer
from .generators import MarkovGenerator

def check_if_file_exists(filepath):
    pass

class ExistingFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        filepath = values
        if not os.path.isfile(filepath):
            raise argparse.ArgumentTypeError("cannot find the input file at %s"%filepath)
        setattr(namespace, self.dest, os.path.realpath(filepath))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "-f","--textfile", required=True,
                         help='Input text file', action=ExistingFileAction)
    parser.add_argument( "-o", "--order", type=int, default=2,
                         help='Markov order, default = 2',)
    parser.add_argument( "-n", "--num_sentences", type=int, default=10,
                         help='Number of sentences to be generated, default = 10',)
    parser.add_argument( "-m", "--max_len", type=int, default=150,
                         help='Maximum character per sentence, default = 150',)
    args = parser.parse_args()
    with open(args.textfile) as f:
        data = f.read()
        generator = MarkovGenerator(args.order)
        generator.learn(data)
        count = 0
        for rep in generator.generate(args.num_sentences, args.max_len):
            count += 1
            print("[%d]: %s\n" %(count, rep))

if __name__ == "__main__":
    main()
