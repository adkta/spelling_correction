# -*- coding: utf-8 -*-
import re, collections
from spelling_correction.nepali_devanagari_char_map import char_map

class SpellingCorrecter:

  def __init__(self, corpus_path: str):
      with open(corpus_path, 'r') as f:
          self.WORD_COUNTS = collections.Counter(self.tokens(f.read()))
      self.alphabet = self.init_alphabet()

  def init_alphabet(self):
      alphabet=[]
      for i in char_map:
          alphabet.append(i)
      print(f"Returning {alphabet}")
      return alphabet

  def tokens(self, text): 
      """
      Get all words from the corpus
      """
      return re.findall('[a-z]+', text.lower()) 

  # top 10 words in corpus
  # print(WORD_COUNTS.most_common(10))

  def known(self, words):
      """
      Return the subset of words that are actually 
      in our WORD_COUNTS dictionary.
      """
      return {w for w in words if w in self.WORD_COUNTS}

  def edits0(self, word): 
      """
      Return all strings that are zero edits away 
      from the input word (i.e., the word itself).
      """
      return {word}

  def edits1(self, word):
      """
      Return all strings that are one edit away 
      from the input word.
      """
      def splits(word):
          """
          Return a list of all possible (first, rest) pairs 
          that the input word is made of.
          """
          return [(word[:i], word[i:]) 
                  for i in range(len(word)+1)]
                  
      pairs      = splits(word)
      deletes    = [a+b[1:]           for (a, b) in pairs if b]
      transposes = [a+b[1]+b[0]+b[2:] for (a, b) in pairs if len(b) > 1]
      replaces   = [a+c+b[1:]         for (a, b) in pairs for c in self.alphabet if b]
      inserts    = [a+c+b             for (a, b) in pairs for c in self.alphabet]
      edits = set(deletes + transposes + replaces + inserts)
      # print(f"{edits}")
      return edits

  def edits2(self, word):
      """Return all strings that are two edits away 
      from the input word.
      """
      return {e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)}

  def edits_n(self, words:set[str], n: int) -> set[str]:
      """
      :param words: list[str] list of words to find the edits for
      :param n: int maximum distance (insertion, deletion, reversal, substitution)
      """
      print(f"Distance: {n}")
      if not words:
          print(f"No words to edit!")

      if n == 0:
          return words
      
      edits = {}
      for word in words:
          edits = self.edits1(word)
      
      if n-1 == 0:
          return edits
      else:
          edits.update(self.edits_n(edits, n-1))
          return edits

  def all_known_candidates(self, word, n):
      candidates = {word}
      candidates.update(self.edits_n({word}, n))
      # return self.known(candidates)
      return candidates

  def candidates(self, word):
      return  (self.known(self.edits0(word)) or
                    self.known(self.edits1(word)) or
                    self.known(self.edits2(word)) or
                    {word}) 
  def correct(self, word):
      """
      Get the best correct spelling for the input word
      """
      # Priority is for edit distance 0, then 1, then 2
      # else defaults to the input word itself.
      return max(self.candidates(word), key=self.WORD_COUNTS.get)

  def correct_match(self, match):
      """
      Spell-correct word in match, 
      and preserve proper upper/lower/title case.
      """
      
      word = match.group()
      def case_of(text):
          """
          Return the case-function appropriate 
          for text: upper, lower, title, or just str.:
              """
          return (str.upper if text.isupper() else
                  str.lower if text.islower() else
                  str.title if text.istitle() else
                  str)
      return case_of(word)(self.correct(word.lower()))
      
  def correct_text_generic(self, text):
      """
      Correct all the words within a text, 
      returning the corrected text.
      """
      return re.sub('[a-zA-Z]+', self.correct_match, text)

#original_word = 'fianlly'
#original_word = 'correcat'
#original_word = 'digitl'\
#original_word = 'firea'
#correct_word = correct_text_generic(original_word)
#print('Original word:%s\nCorrect word:%s'%(original_word, correct_word))

    
    