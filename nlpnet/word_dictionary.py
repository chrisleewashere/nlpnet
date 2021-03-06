# -*- coding: utf-8 -*-

import itertools
from collections import Counter

class WordDictionary(dict):
    """
    Class to store words and their corresponding indices in
    the network lookup table. Also deals with padding and
    maps rare words to a special index.
    """
    
    padding_left = '*LEFT*'
    padding_right = '*RIGHT*'
    rare = '*RARE*'
    
    def __init__(self, tokens, size=None, minimum_occurrences=None, wordlist=None):
        """
        Fills a dictionary (to be used for indexing) with the most
        common words in the given text.
        
        :param tokens: Either a list of tokens or a list of lists of tokens 
            (each token represented as a string).
        :param size: Maximum number of token indices 
            (not including paddings, rare, etc.).
        :param minimum_occurrences: The minimum number of occurrences a token must 
            have in order to be included.
        :param wordlist: Use this list of words to build the dictionary. Overrides tokens
            if not None.
        """
        if wordlist is None:
            # work with the supplied tokens. extract frequencies.
            
            # gets frequency count
            c = self._get_frequency_count(tokens)
        
            if minimum_occurrences is None:
                minimum_occurrences = 1
            
            words = [key for key, number in c.most_common() 
                     if number >= minimum_occurrences]
        
        else:
            # using supplied wordlist
            words = list(wordlist) 
            
        # verifies the maximum size
        if size is None:
            size = len(words)
        else:
            size = min(size, len(words))
            words = words[:size]
        
        # set all words in the dictionary
        for word, num in itertools.izip(words, xrange(size)):
            self[word] = num
        
        # if the given words include the rare symbol, don't replace it
        if WordDictionary.rare in words:
            self.num_tokens = size - 1
            
            # using dict.get() instead of [] because we override the latter
            key = WordDictionary.rare.lower()
            self.index_rare = super(WordDictionary, self).get(key)
        else:
            self.num_tokens = size
            self.index_rare = size
            self[WordDictionary.rare] = self.index_rare
        
        self.index_padding_left = self.num_tokens + 1
        self.index_padding_right = self.num_tokens + 2
        self[WordDictionary.padding_left] = self.index_padding_left
        self[WordDictionary.padding_right] = self.index_padding_right
    
    @classmethod
    def init_from_wordlist(cls, wordlist):
        """
        Initializes the WordDictionary instance with a list of words, independently from their 
        frequencies. Every word in the list gets an entry.
        """
        return cls(None, wordlist=wordlist)
    
    @classmethod
    def init_empty(cls):
        """
        Initializes an empty Word Dictionary.
        """
        return cls([[]])
    
    def _get_frequency_count(self, token_list):
        """
        Returns a token counter for tokens in token_list.
        
        :param token_list: Either a list of tokens (as strings) or a list 
            of lists of tokens.
        """
        if type(token_list[0]) == list:
            c = Counter(t.lower() for sent in token_list for t in sent)
        else:
            c = Counter(t.lower() for t in token_list)
        return c
    
    
    def update_tokens(self, tokens, size=None, minimum_occurrences=1, freqs=None):
        """
        Updates the dictionary, adding more types until size is reached.
        
        :param freqs: a dictionary providing a token count.
        """
        if freqs is None:
            freqs = self._get_frequency_count(tokens)
            
        if size is None or size == 0:
            # size None or 0 means no size limit
            size = len(freqs)
        
        if self.num_tokens >= size:
            return
        else:
            size_diff = size - self.num_tokens
        
        # a new version of freqs with only tokens not present in the dictionary
        # and above minimum frequency 
        candidate_tokens = dict((token, freqs[token])
                                for token in freqs 
                                if token not in self and freqs[token] >= minimum_occurrences)
        
        # order the types from the most frequent to the least
        new_tokens = sorted(candidate_tokens, key=lambda x: candidate_tokens[x], reverse=True)
        
        next_value = len(self)
        for token in new_tokens:
            self[token] = next_value
            next_value += 1
            size_diff -= 1
            if size_diff == 0:
                break
        
        self.check()
    
    def __contains__(self, key):
        """
        Overrides the "in" operator. Case insensitive.
        """
        return super(WordDictionary, self).__contains__(key.lower())
    
    def __setitem__(self, key, value):
        """
        Overrides the [] write operator. It converts every key to lower case
        before assignment.
        """
        super(WordDictionary, self).__setitem__(key.lower(), value)
    
    def __getitem__(self, key):
        """
        Overrides the [] read operator. 
        
        Two differences from the original:
        1) when given a word without an entry, it returns the value for the *RARE* key.
        2) all entries are converted to lower case before verification.
        """
        return super(WordDictionary, self).get(key.lower(), self.index_rare)
    
    def get(self, key):
        """
        Overrides the dictionary get method, so when given a word without an entry, it returns 
        the value for the *RARE* key. Note that it is not possible to supply a default value as 
        in the dict class.
        """
        return super(WordDictionary, self).get(key.lower(), self.index_rare)
        
    def check(self):
        """
        Checks the internal structure of the dictionary and makes necessary adjustments, 
        such as updating num_tokens.
        """
        self.index_padding_left = self[WordDictionary.padding_left]
        self.index_padding_right = self[WordDictionary.padding_right]
        self.index_rare = self[WordDictionary.rare]
        self.num_tokens = len(self) - 3
    
    def get_words(self, indices):
        """
        Returns the words represented by a sequence of indices.
        """
        words = [w for w in self if self[w] in indices]
        return words
    
    def get_indices(self, words):
        """
        Returns the indices corresponding to a sequence of tokens.
        """
        indices = [self[w] for w in words]
        return indices
    