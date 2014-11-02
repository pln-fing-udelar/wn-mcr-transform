#!/usr/bin/env python
# coding=utf-8
import contextlib
import lzma
from nltk.corpus import WordNetCorpusReader
import shutil
import tarfile
import unittest


class TestTransform(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.languages = ["cat", "eng", "eus", "glg", "spa"]
        for lang in self.languages:
            wn_name = 'wordnet_' + lang
            with contextlib.closing(lzma.LZMAFile(wn_name + '.tar.lzma')) as xz:
                with tarfile.open(fileobj=xz) as f:
                    f.extractall(wn_name)

    def test_load_wordnet(self):
        for lang in self.languages:
            wn_name = 'wordnet_' + lang
            self.wncr = WordNetCorpusReader(wn_name, None)
        # success if there is no error

    def test_invalid_literal_for_int_16(self):
        self.wncr = WordNetCorpusReader('wordnet_spa', None)
        self.wncr._synset_from_pos_and_line('n',
                                            u"04122387 00 n 0a agudeza 0 broma 0 chiste 0 chufleta 0 comentario_burlón 0 cuchufleta 0 idea 0 ocurrencia 0 pulla 0 salida 0 04 @ 04120601 n 0000 + 00620096 v 0000 + 00499330 v 0000 + 00558467 v 0000 | comentario ingenioso para hacer reír  \n")
        # success if there is no error

    def test_key_error(self):
        self.wncr = WordNetCorpusReader('wordnet_spa', None)
        self.wncr.lemma("menor.a.09.menor").antonyms()
        # success if there is no error

    def test_all_synsets(self):
        self.wncr = WordNetCorpusReader('wordnet_spa', None)
        self.wncr.all_synsets()
        # success if there is no error

    @classmethod
    def tearDownClass(self):
        for lang in self.languages:
            wn_name = 'wordnet_' + lang
            shutil.rmtree(wn_name)


if __name__ == '__main__':
    unittest.main()
