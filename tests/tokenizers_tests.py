import unittest

# from markogen import MarkovStemmer, Tokenizer, SentenceTokenizer,\
#     split_single, split_multi

from markogen.tokenizers import *

import logging

log = logging.getLogger('markov')

class testHappySequenceTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = HappyTokenizer(True)

    def test_sentences(self):
	    text = u"A sentence begins with a non-whitespace and ends with a period,"\
	           "exclamation point or a question mark (or end of string).\n"\
	           "There may be a closing quote following the ending punctuation."
	    tokens = self.tokenizer.tokenize(text)
	    self.assertEqual(len(tokens), 36)

    def test_quoted_sentences(self):
	    text = u'''"He's not a good man", she said. "I know", I   said.'''
	    tokens = self.tokenizer.split(text)
	    self.assertEqual(tokens, [u"He's", u' ', u'not', u' ', u'a',\
				                  u' ', u'good', u' ', u'man', u' ', \
				                  u'she', u' ', u'said', u' ', u'I', \
				                  u' ', u'know', u' ', u'I', u' ', u'said'])

import logging
class testDefaultSequenceTokenizer(unittest.TestCase):
    """
    A sentence begins with a non-whitespace and ends with a period,
    exclamation point or a question mark (or end of string).
    There may be a closing quote following the ending punctuation.
    """
    def setUp(self):
        self.tokenizer = SentenceTokenizer()


    def test_standard_sentences(self):
	    text = u"A sentence begins with a non-whitespace and ends with a period,"\
	           "exclamation point or a question mark (or end of string).\n"\
	           "There may be a closing quote following the ending punctuation."
	    sentences = SentenceTokenizer().split(text)
	    self.assertEqual(len(sentences), 2)

    def test_quoted_sentences(self):
        text = u""""Dorian Gray?  Is that his name?" asked Lord Henry, walking across the studio towards Basil Hallward.\n\n"""\
	           """"Yes, that is his name.  I didn't intend to tell it to you".\n\n"""\
	           """"But why not?"\n\n"""\
	           """"Oh, I can't explain.  When I like people immensely, I never tell theirnames to any one."""
        sentences = SentenceTokenizer().split(text)
        logging.debug(sentences)
        self.assertEqual(len(sentences), 8)

    def test_quoted_sentences(self):
        text = u""""Dorian Gray? Is that his name?", asked Mr.Henry."""
        sentences = SentenceTokenizer().split(text);
        self.assertEqual(len(sentences), 2)


class testNLTKSentenceTokenizer(unittest.TestCase):
    """Doc string"""
    def setUp(self):
        self.tokenizer = NLTKSentenceTokenizer()

    def testQuotedStrings(self):
        text = u""""Dorian Gray? Is that his name?", asked Mrs. Henry."""
        sentences = NLTKSentenceTokenizer().split(text)
        self.assertEqual(len(sentences), 3)

class testCobeTokenTokenizer(unittest.TestCase):
    def setUp(self):
        self.tokenizer = CobeTokenizer()

    def testSplitEmpty(self):
        self.assertEquals(len(self.tokenizer.split(u"")), 0)

    def testSplitSentence(self):
        words = self.tokenizer.split(u"hi.")
        self.assertEquals(words, ["hi", "."])

    def testSplitComma(self):
        words = self.tokenizer.split(u"hi, cobe")
        self.assertEquals(words, ["hi", ",", " ", "cobe"])

    def testSplitDash(self):
        words = self.tokenizer.split(u"hi - cobe")
        self.assertEquals(words, ["hi", " ", "-", " ", "cobe"])

    def testSplitMultipleSpacesWithDash(self):
        words = self.tokenizer.split(u"hi  -  cobe")
        self.assertEquals(words, ["hi", " ", "-", " ", "cobe"])

    def testSplitLeadingDash(self):
        words = self.tokenizer.split(u"-foo")
        self.assertEquals(words, ["-foo"])

    def testSplitLeadingSpace(self):
        words = self.tokenizer.split(u" foo")
        self.assertEquals(words, ["foo"])

        words = self.tokenizer.split(u"  foo")
        self.assertEquals(words, ["foo"])

    def testSplitTrailingSpace(self):
        words = self.tokenizer.split(u"foo ")
        self.assertEquals(words, ["foo"])

        words = self.tokenizer.split(u"foo  ")
        self.assertEquals(words, ["foo"])

    def testSplitSmiles(self):
        words = self.tokenizer.split(u":)")
        self.assertEquals(words, [":)"])

        words = self.tokenizer.split(u";)")
        self.assertEquals(words, [";)"])

        # not smiles
        words = self.tokenizer.split(u":(")
        self.assertEquals(words, [":("])

        words = self.tokenizer.split(u";(")
        self.assertEquals(words, [";("])

    def testSplitUrl(self):
        words = self.tokenizer.split(u"http://www.google.com/")
        self.assertEquals(words, ["http://www.google.com/"])

        words = self.tokenizer.split(u"https://www.google.com/")
        self.assertEquals(words, ["https://www.google.com/"])

        # odd protocols
        words = self.tokenizer.split(u"cobe://www.google.com/")
        self.assertEquals(words, ["cobe://www.google.com/"])

        words = self.tokenizer.split(u"cobe:www.google.com/")
        self.assertEquals(words, ["cobe:www.google.com/"])

        words = self.tokenizer.split(u":foo")
        self.assertEquals(words, [":", "foo"])

    def testSplitMultipleSpaces(self):
        words = self.tokenizer.split(u"this is  a test")
        self.assertEquals(words, ["this", " ", "is", " ", "a", " ", "test"])

    # def testSplitVerySadFrown(self):
    #     words = self.tokenizer.split(u"testing :    (")
    #     self.assertEquals(words, ["testing", " ", ":    ("])

    #     words = self.tokenizer.split(u"testing          :    (")
    #     self.assertEquals(words, ["testing", " ", ":    ("])

    #     words = self.tokenizer.split(u"testing          :    (  foo")
    #     self.assertEquals(words, ["testing", " ", ":    (", " ", "foo"])

    def testSplitHyphenatedWord(self):
        words = self.tokenizer.split(u"test-ing")
        self.assertEquals(words, ["test-ing"])

        words = self.tokenizer.split(u":-)")
        self.assertEquals(words, [":-)"])

        words = self.tokenizer.split(u"test-ing :-) 1-2-3")
        self.assertEquals(words, ["test-ing", " ", ":-)", " ", "1-2-3"])

    def testSplitApostrophes(self):
        words = self.tokenizer.split(u"don't :'(")
        self.assertEquals(words, ["don't", " ", ":'("])

    # def testSplitNonUnicode(self):
    #     self.assertRaises(TypeError, self.tokenizer.split, "foo")

    def testJoin(self):
        self.assertEquals("foo bar baz",
                          self.tokenizer.join(["foo", " ", "bar", " ", "baz"]))


# class testStemmer(unittest.TestCase):
#     def setUp(self):
#         self.stemmer = MarkovStemmer("english")

#     def testStemmer(self):
#         self.assertEquals("foo", self.stemmer.stem("foo"))
#         self.assertEquals("jump", self.stemmer.stem("jumping"))
#         self.assertEquals("run", self.stemmer.stem("running"))

#     def testStemmerCase(self):
#         self.assertEquals("foo", self.stemmer.stem("Foo"))
#         self.assertEquals("foo", self.stemmer.stem("FOO"))

#         self.assertEquals("foo", self.stemmer.stem("FOO'S"))
#         self.assertEquals("foo", self.stemmer.stem("FOOING"))
#         self.assertEquals("foo", self.stemmer.stem("Fooing"))

