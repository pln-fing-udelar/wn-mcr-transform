#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from nltk.corpus import WordNetCorpusReader
import shutil
import tarfile
import unittest


class TestTransform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.languages = ["cat", "eng", "eus", "glg", "spa"]
        cls.wn_names = {}
        for lang in cls.languages:
            cls.wn_names[lang] = '.wordnet_' + lang
            with tarfile.open('wordnet_' + lang + '.tar.gz') as f:
                    f.extractall(cls.wn_names[lang])

    def test_all_synsets(self):
        self.wncr = WordNetCorpusReader(self.wn_names['spa'], None)
        for synset in self.wncr.all_synsets():
            a = synset
        # success if there is no error
        # This will also test that all synsets in data files are in index files.

    def test_invalid_literal_for_int_16(self):
        self.wncr = WordNetCorpusReader(self.wn_names['spa'], None)
        for synset in self.wncr.synsets("agudeza"):
            a = synset
#        self.wncr._synset_from_pos_and_line('n',
#                                            "04122387 00 n 0a agudeza 0 broma 0 chiste 0 chufleta 0 comentario_burlón 0 cuchufleta 0 idea 0 ocurrencia 0 pulla 0 salida 0 04 @ 04120601 n 0000 + 00620096 v 0000 + 00499330 v 0000 + 00558467 v 0000 | comentario ingenioso para hacer reír  \n")
#        # success if there is no error

    def test_key_error(self):
        self.wncr = WordNetCorpusReader(self.wn_names['spa'], None)
        self.wncr.lemma("menor.a.09.menor").antonyms()
        # success if there is no error

    def test_load_wordnet(self):
        for lang in self.languages:
            self.wncr = WordNetCorpusReader(self.wn_names[lang], None)
            # success if there is no error

    @classmethod
    def tearDownClass(cls):
        for lang in cls.languages:
            shutil.rmtree(cls.wn_names[lang])


if __name__ == '__main__':
    unittest.main()
