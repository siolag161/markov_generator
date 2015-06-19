
import re
import types

class Tokenizer(object):
    """Doc string"""
    regex = re.compile(".*")

    @classmethod
    def _process_text(cls, text):
        # Try to ensure unicode:
        if type(text) != types.UnicodeType:
            try:
                text = unicode(text)
            except UnicodeDecodeError:
                text = str(text).encode('string_escape')
                text = unicode(text)
        text = text.strip()
        return text

    def tokenize(self, text):
        text = self._process_text(text)
        if len(text) == 0:
            return []
        tokens = [token.strip() if token.strip() != '' \
                  else u' ' for token in self.regex.findall(text)]
        return tokens

    def split(self, text):
        """alias of ``tokenize``"""
        return self.tokenize(text)

    @staticmethod
    def join(words):
        return u"".join(words)

class SentenceTokenizer(Tokenizer):
    """Doc string"""
    def __init__(self,):
        """docstring"""
        self.regex = re.compile(
            "[^.!?\\s]" # First char is non-punct, non-ws\n" +
			"[^.!?]*"   # Greedily consume up to punctuation.\n" +
			"(?:"       # Group for unrolling the loop.\n" +
			"[.!?]"     # (special) inner punctuation ok if\n" +
			"(?!['\"]?\\s|$)"  # not followed by ws or EOS.\n" +
			"[^.!?]*"   # Greedily consume up to punctuation.\n" +
			")*"        # Zero or more (special normal*)\n" +
			"[.!?]?"    # Optional ending punctuation.\n" +
			"['\"]?"    # Optional closing quote.\n" +
			"(?=\\s|$)",
			re.UNICODE)

    def tokenize(self, text):
        text = self._process_text(text)
        return self._split_sentences(text)

    def _split_sentences(self, text):
        return super(SentenceTokenizer, self).tokenize(text)

class NLTKSentenceTokenizer(SentenceTokenizer):
    """"""
    def _split_sentences(self, text):
        from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'prof', 'inc'])
        sentence_splitter = PunktSentenceTokenizer(punkt_param)
        sentences = sentence_splitter.tokenize(text)
        return sentences

######################################################################
# The following strings are components in the regular expression
# that is used for tokenizing. It's important that phone_number
# appears first in the final regex (since it can contain whitespace).
# It also could matter that tags comes after emoticons, due to the
# possibility of having text like
#
#     <:| and some text >:)
#
# Most imporatantly, the final element should always be last, since it
# does a last ditch whitespace-based tokenization of whatever is left.

# This particular element is used in a couple ways, so we define it
# with a name:
EMOTICON_STRING = r"""
    (?:
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

# The components of the tokenizer:
REGEX_STRINGS = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?
      \d{3}          # exchange
      [\-\s.]*
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    EMOTICON_STRING
    ,
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\S)                         # Everything else that isn't whitespace.
    """
)

REGEX_TOKENS = (
    # Phone numbers:
    r"""
    (?:
      (?:            # (international)
        \+?[01]
        [\-\s.]*
      )?
      (?:            # (area code)
        [\(]?
        \d{3}
        [\-\s.\)]*
      )?
      \d{3}          # exchange
      [\-\s.]*
      \d{4}          # base
    )"""
    ,
    # Emoticons:
    EMOTICON_STRING
    ,
    # HTML tags:
     r"""<[^>]+>"""
    ,
    # Twitter username:
    r"""(?:@[\w_]+)"""
    ,
    # Twitter hashtags:
    r"""(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"""
    ,
    # Remaining word types:
    r"""
    (?:[a-z][a-z'\-_]+[a-z])       # Words with apostrophes or dashes.
    |
    (?:[+\-]?\d+[,/.:-]\d+[+\-]?)  # Numbers, including fractions, decimals.
    |
    (?:[\w_]+)                     # Words without apostrophes or dashes.
    |
    (?:\.(?:\s*\.){1,})            # Ellipsis dots.
    |
    (?:\s+)                         # Whitespace

    """
)

######################################################################
# This is the core tokenizing regex:

TOKEN_RE = re.compile(r"""(%s)""" % "|".join(REGEX_TOKENS),
                      re.VERBOSE | re.I | re.UNICODE)
WORD_RE = re.compile(r"""(%s)""" % "|".join(REGEX_STRINGS),
                     re.VERBOSE | re.I | re.UNICODE)

# The emoticon string gets its own regex so that we can
# preserve case for them as needed:
EMOTICON_RE = re.compile(REGEX_STRINGS[1], re.VERBOSE | re.I | re.UNICODE)

# These are for regularizing HTML entities to Unicode:
HTML_ENTITY_DIGIT_RE = re.compile(r"&#\d+;")
HTML_ENTITY_ALPHA_RE = re.compile(r"&\w+;")
AMP = "&amp;"

class HappyTokenizer(Tokenizer):
    """
    """
    def __init__(self, preserve_case=False):
        self.preserve_case = preserve_case

    def _split_tokens(self, text, regex):
        """
        Argument: s -- any string or unicode object
        Value: a tokenize list of strings; conatenating this list
        returns the original string if preserve_case=False
        """
        # Try to ensure unicode:
        try:
            text = unicode(text)
        except UnicodeDecodeError:
            text = str(text).encode('string_escape')
            text = unicode(text)
            # Fix HTML character entitites:
        text = self.__html2unicode(text)
        # Tokenize:
        words = regex.findall(text)
        # Possible alter the case, but avoid changing emoticons like :D into :d:
        if not self.preserve_case:
            #words = map((lambda x: x if EMOTICON_RE.search(x) \
                         #else x.lower()), words)
            words = (word if EMOTICON_RE.search(word) else word.lower() \
                     for word in words)
        return words

    def tokenize(self, s):
        return self._split_tokens(s, WORD_RE)

    def split(self, text):
        tokens = self._split_tokens(text, TOKEN_RE)
        tokens = [token.strip() if token.strip() != ''
                  else u' ' for token in tokens]
        return tokens

    @classmethod
    def __html2unicode(cls, text):
        """
        Internal metod that seeks to replace all the HTML entities in
        s with their corresponding unicode characters.
        """
        import htmlentitydefs
        # First the digits:
        ents = set(HTML_ENTITY_DIGIT_RE.findall(text))
        if len(ents) > 0:
            for ent in ents:
                entnum = ent[2:-1]
                try:
                    entnum = int(entnum)
                    text = text.replace(ent, unichr(entnum))
                except:
                    pass
                # Now the alpha versions:
        ents = set(HTML_ENTITY_ALPHA_RE.findall(text))
        #ents = filter((lambda x: x != AMP), ents)
        ents = [elem for elem in ents if elem != AMP]
        for ent in ents:
            entname = ent[1:-1]
            try:
                text = text.replace(ent,\
                              unichr(htmlentitydefs.name2codepoint[entname]))
            except:
                pass
            text = text.replace(AMP, " and ")
        return text

class CobeTokenizer(Tokenizer):
    """
    """
    regex = re.compile(r"(\w+:\S+"  # urls
                       r"|[\w'-]+"  # words
                       r"|[^\w\s][^\w]*[^\w\s]"  # multiple punctuation
                       r"|[^\w\s]"  # a single punctuation character
                       r"|\s+)",    # whitespace
                       re.UNICODE)
    def split(self, phrase):
        tokens = super(CobeTokenizer, self).split(phrase)
        space = u" "
        for i, token in enumerate(tokens):
            if token[0] == " " and len(token) > 1:
                tokens[i] = space

        return tokens
