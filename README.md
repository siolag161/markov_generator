# markov_generator
Simple n-order text generator based on markov chain. Parameters are not stored
persistently, only in memory.

# Usage:
```python

usage: __main__.py [-h] -f TEXTFILE [-o ORDER] [-n NUM_SENTENCES] [-m MAX_LEN]

optional arguments:
  -h, --help            show this help message and exit
  -f TEXTFILE, --textfile TEXTFILE
                        Input text file
  -o ORDER, --order ORDER
                        Markov order, default = 2
  -n NUM_SENTENCES, --num_sentences NUM_SENTENCES
                        Number of sentences to be generated, default = 10
  -m MAX_LEN, --max_len MAX_LEN
                        Maximum character per sentence, default = 15
```

For example, a command to generate 5 sentences from the Tao corpus would yield something like:

```python
python -m markogen -f inputs/tao.txt -n5

[1]: Is it not because it could not hurt men.

[2]: The softest thing in the Tao, the more implements to add to his own person last, and do not know it.

[3]: The excellence of a reward for the things which I call it The Great.

[4]: There are few in the world delight to exalt him and do not know it.

[5]: Therefore when one knows that the ancients prized this Tao, the more.

```


