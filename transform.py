#!/usr/bin/env python
# This module transforms MCR 3.0 database files into WordNet 3.0 database files.
# The resulting files can be loaded with the nltk WordNet reader using:
#   nltk.corpus.reader.wordnet.WordNetCorpusReader(<FILES_ROOT>)
# 
# Author: Luis Chiruzzo <luischir@fing.edu.uy>

from sets import Set

import io
import re
import sys

POS_NAMES = {
    "n": "noun",
    "a": "adj",
    "v": "verb",
    "r": "adv"
}

RELATION_MAP = {
    1: "=",
    2: ">",
    4: "\\",
    6: "#s",
    7: "#m",
    8: "#p",
    12: "~",
    19: "*",
    33: "!",
    34: "&",
    49: "^",
    52: "$",
    63: "-c",
    64: "+",
    66: "-r",
    68: "-u"
}

SYMMETRIC_RELATION_MAP = {
    6: "%s",
    7: "%m",
    8: "%p",
    12: "@",
    52: "$",
    63: ";c",
    64: "+",
    66: ";r",
    68: ";u"
}

FILE_HEADER_INFO = \
    "  2 This file was created from the Multilingual Central Repository 3.0.\n" + \
    "  3 The latest MCR 3.0 files can be downloaded from\n" + \
    "  4 http://adimen.si.ehu.es/web/MCR/\n" + \
    "  5 The latest version of the transformation process can be found in\n" + \
    "  6 https://github.com/pln-fing-udelar/wn-mcr-transform\n" + \
    "  7 \n" + \
    "  8 For more details on the MCR 3.0 contents, including references to the\n" + \
    "  9 original resources, please consult the following paper:\n" + \
    "  10   Gonzalez-Agirre A., Laparra E. and Rigau G. Multilingual Central\n" + \
    "  11   Repository version 3.0: upgrading a very large lexical knowledge\n" + \
    "  12   base. In Proceedings of the Sixth International Global WordNet\n" + \
    "  13   Conference (GWC'12). Matsue, Japan. January, 2012.\n" + \
    "  14 which can be downloaded at:\n" + \
    "  15 http://adimen.si.ehu.es/~rigau/publications/gwc12-glr.pdf\n" + \
    "  16 \n" + \
    "  17 The contents of the MCR package are distributed under different open licenses.\n" + \
    "  18 If you want to redistribute this software, part of it, or derived works based\n" + \
    "  19 on it or on any of its parts, make sure you are doing so under the terms stated\n" + \
    "  20 in the license applying to each of the involved modules.\n" + \
    "  21 The licenses applying to the modules contained in MCR are the following:\n" + \
    "  22  - English WordNet synset and relation data, contained in folder engWN/ are\n" + \
    "  23      distributed under the original WordNet license. You can find it at\n" + \
    "  24      http://wordnet.princeton.edu/wordnet/license\n" + \
    "  25  - Basque WordNet synset and relation data, contained in folder eusWN/ are\n" + \
    "  26      distributed under CreativeCommons Attribution-NonCommercial-ShareAlike 3.0\n" + \
    "  27      Unported (CC BY-NC-SA 3.0) license. You can find it at\n" + \
    "  28      http://creativecommons.org/licenses/by-nc-sa/3.0\n" + \
    "  29  - All other data in MCR package are distributed under Attribution 3.0 Unported\n" + \
    "  30      (CC BY 3.0) license. You can find it at\n" + \
    "  31      http://creativecommons.org/licenses/by/3.0/\n"

def get_file_header_info(lang, pos):
    return u"  1 MCR WordNet 3.0 (" + lang + u") " + POS_NAMES[pos] + u" data file\n" + FILE_HEADER_INFO

unknown_count = 0

def get_offset_pos(synset):
    split = synset.split("-")
    offset = split[2]
    pos = split[3]
    return offset, pos

def get_synset(lang, offset, pos):
    return lang + u"-30-" + offset + u"-" + pos

def lexical_relations():
    return ["!"]

def utf8len(s):
    return len(s.encode('utf-8'))

def create_data_file(pos, lang, synsets, variations, relations, eng_synsets, spa_glosses, synset_map):
    global unknown_count

    text_chunks = []
    variation_map = {}

    text = get_file_header_info(lang, pos)
    index = utf8len(text)
    text_chunks.append(text)

    synsets_set = dict([pos, set(synsets[pos][0])] for pos in synsets)
    
    for synset, gloss in synsets[pos]:
        synset_name = get_synset(lang, synset, pos)
        eng_offset = synset + pos
        
        text = synset
        synset_map[u"@" + text + pos] = index
        index += utf8len(text)
        text_chunks.append(u"@" + text + pos)
        
        text = u" 00 " + pos + u" "
        index += utf8len(text)
        text_chunks.append(text)
        
        # variations
        if synset_name in variations:
            text = format(len(variations[synset_name]), '02x') + u" "
            index += utf8len(text)
            text_chunks.append(text)
            
            for variation in variations[synset_name]:
                text = variation
                index += utf8len(text)
                text_chunks.append(text)
                
                m = re.match(r'(.*?)(\(.*\))?$', text.lower())
                lemma_name, syn_mark = m.groups()
                if not lemma_name in variation_map:
                    variation_map[lemma_name] = []
                variation_map[lemma_name].append(synset)
                
                text = u" 0 "
                index += utf8len(text)
                text_chunks.append(text)
        else:
            # use the english lemma
            if eng_offset in eng_synsets:
                lemma = u"`" + eng_synsets[eng_offset]
                m = re.match(r'(.*?)(\(.*\))?$', lemma.lower())
                lemma_name, syn_mark = m.groups()
                if not lemma_name in variation_map:
                    variation_map[lemma_name] = []
                variation_map[lemma_name].append(synset)
            else:
                unknown_count += 1
                lemma = u"<unknown" + str(unknown_count).zfill(4) + u">"
                if not lemma in variation_map:
                    variation_map[lemma] = []
                variation_map[lemma].append(synset)
            text = u"01 " + lemma + u" 0 "
            index += utf8len(text)
            text_chunks.append(text)

        # relations
        if synset_name in relations:
            valid_relations = []
            for type, rs in relations[synset_name]:
                rel_offset, rel_pos = get_offset_pos(rs)
                if rel_offset in synsets_set[rel_pos] or rel_offset + rel_pos in eng_synsets:
                    if type in lexical_relations():
                        synset_to = get_synset(lang, rel_offset, rel_pos)

                        if synset_name in variations:
                            len_lemmas_from = len(variations[synset_name])
                        else:
                            len_lemmas_from = 1

                        if synset_to in variations:
                            len_lemmas_to = len(variations[synset_to])
                        else:
                            len_lemmas_to = 1

                        for i_lemma_from in range(1, len_lemmas_from+1):
                            for i_lemma_to in range(1, len_lemmas_to+1):
                                valid_relations.append((type, rel_offset, rel_pos, i_lemma_from, i_lemma_to))
                    else:
                        valid_relations.append((type, rel_offset, rel_pos, 0, 0))

            text = str(len(valid_relations)).zfill(2) + u" "
            index += utf8len(text)
            text_chunks.append(text)
            
            for type, rel_offset, rel_pos, lemma_from, lemma_to in valid_relations:
                text = type + u" "
                index += utf8len(text)
                text_chunks.append(text)
                
                text = rel_offset
                index += utf8len(text)
                text_chunks.append(u"@" + text + rel_pos)

                text = u" " + rel_pos + u" " + format(lemma_from, '02x') + format(lemma_to, '02x') + u" "
                index += utf8len(text)
                text_chunks.append(text)
        else:
            text = u"0 "
            index += utf8len(text)
            text_chunks.append(text)

        # gloss
        if (gloss == u"NULL" or gloss.strip() == "") and eng_offset in spa_glosses:
            try:
                text = u"| " + spa_glosses[eng_offset] + u"  \n"
                index += utf8len(text)
                text_chunks.append(text)
            except UnicodeEncodeError as e:
                text = u"| " + gloss + u"  \n"
                index += utf8len(text)
                text_chunks.append(text)
                print eng_offset
                print e
        else:
            text = u"| " + gloss + u"  \n"
            index += utf8len(text)
            text_chunks.append(text)

    return text_chunks, variation_map

def write_data_file(root_result, pos, text_chunks, synset_map):
    filename = root_result + "/data." + POS_NAMES[pos]
    print filename
    file = io.open(filename, mode="w", encoding="utf-8")
    for text in text_chunks:
        if text in synset_map:
            file.write(u"{0:08d}".format(synset_map[text]))
        else:
            file.write(text)
    file.close()

def write_index_file(root_result, pos, lang, variations_map, synset_map):
    lemmas = sorted(variations_map.keys())
    filename = root_result + "/index." + POS_NAMES[pos]
    print filename
    file = io.open(filename, mode="w", encoding="utf-8")
    file.write(get_file_header_info(lang, pos))
    for lemma in lemmas:
        synset_count = str(len(variations_map[lemma]))
        file.write(lemma + u" " + pos + u" " + synset_count + u" 0 " + synset_count + u" 0")
        for offset in variations_map[lemma]:
            file.write(u" {0:08d}".format(synset_map[u"@" + offset + pos]))
        file.write(u"  \n")
    file.close()

def load_synsets(root_eng, pos, eng_synsets, eng_glosses):
    file = io.open(root_eng + "/data." + POS_NAMES[pos], encoding="utf-8")
    for line in file:
        if not line.startswith("  "):
            split = line.split(" ")
            offset = split[0]
            first_lemma = split[4]
            eng_synsets[offset + pos] = first_lemma
            gloss_split = line.split(" | ")
            eng_glosses[offset + pos] = gloss_split[1].strip()
    file.close()
    
def write_english_glosses(eng_glosses, result_path):
    print "Writing english glosses..."
    file = io.open(result_path, mode="w", encoding="utf-8")
    for offset in sorted(eng_glosses):
        file.write(offset + u" | " + eng_glosses[offset] + u"\n")
    file.close()
    
def load_foreign_glosses(foreign_glosses_path):
    print "Loading foreign glosses..."
    file = io.open(foreign_glosses_path, encoding="utf-8")
    glosses = {}
    for line in file:
        split = line.split(" | ")
        offset = split[0].strip()
        gloss = split[1].strip()
        glosses[offset] = gloss
    file.close()
    return glosses

def load_valid_synsets(root_mcr, lang):
    print "Loading valid synsets..."
    file = io.open(root_mcr + "/" + lang + "WN/wei_" + lang + "-30_synset.tsv", encoding="utf-8")
    synsets = {}
    for pos in POS_NAMES:
        synsets[pos] = []
    for line in file:
        split = line.split("\t")
        if split[0].strip() != "":
            synset_number, synset_pos = get_offset_pos(split[0])
            synset_gloss = split[6]
            synsets[synset_pos].append((synset_number, synset_gloss))
    file.close()
    return synsets

def load_synset_variants(root_mcr, lang):
    print "Loading synset variants..."
    vars_file = io.open(root_mcr + "/" + lang + "WN/wei_" + lang + "-30_variant.tsv", encoding="utf-8")
    variants = {}
    for line in vars_file.readlines():
        split = line.split("\t")
        variant = split[0]
        synset = split[2]
        if synset not in variants:
            variants[synset] = []
        variants[synset].append(variant)
    vars_file.close()
    return variants

def load_synset_relations(root_mcr, lang):
    print "Loading synset relations..."
    rels_file = io.open(root_mcr + "/" + lang + "WN/wei_" + lang + "-30_relation.tsv", encoding="utf-8")
    relations = {}
    for line in rels_file:
        split = line.split("\t")
        type = int(split[0])
        from_synset = split[1]
        to_synset = split[3]
        if type in RELATION_MAP:
            if from_synset not in relations:
                relations[from_synset] = set()
            relations[from_synset].add((RELATION_MAP[type], to_synset))
            if type in SYMMETRIC_RELATION_MAP:
                if to_synset not in relations:
                    relations[to_synset] = set()
                relations[to_synset].add((SYMMETRIC_RELATION_MAP[type], from_synset))
    rels_file.close()
    return relations

def transform(root_mcr, root_eng, lang, root_result, foreign_glosses_path = None):
    """
    Transforms the set of MCR 3.0 files into a text database compatible with the nltk WordNet corpus reader.

    The process reads the files wei_<lang>-30_synset.tsv, wei_<lang>-30_variant.tsv and wei_<lang>-30_relation.tsv and generates a set of files following the WordNet database schema. The generated files will be: data.noun, index.noun, data.verb, index.verb, data.adj, index.adj, data.adv and index.adv.

    If a synset doesn't have any lemma defined in MCR, we use the first lemma of the English version (prepending a character `) for this synset. This means that when traversing the ontology, it's possible to find English placeholders for missing Spanish (or other language) words.

    :param root_mcr: Path to the root folder of MCR 3.0, this folder contains a folder for each language (e.g.: spaWN for Spanish)
    :param root_end: Path to the English WordNet 3.0 files
    :param lang: first three letters of the language to transform (e.g.: spa for Spanish)
    :param root_result: Path where the resulting files will be written
    :param foreign_glosses_path: (optional) Path to the foreign glosses file
    """
    lang = lang.lower()
    synsets = load_valid_synsets(root_mcr, lang)
    variants = load_synset_variants(root_mcr, lang)
    relations = load_synset_relations(root_mcr, lang)

    print "Loading English synsets..."
    eng_synsets = {}
    eng_glosses = {}
    for pos in POS_NAMES:
        load_synsets(root_eng, pos, eng_synsets, eng_glosses)

    if foreign_glosses_path != None:
        foreign_glosses = load_foreign_glosses(foreign_glosses_path)
    else:
        foreign_glosses = {}
    
    print "Creating data files..."
    synset_map = {}

    data = {}
    variations = {}

    for pos in POS_NAMES:
        data[pos], variations[pos] = create_data_file(pos, lang, synsets, variants, relations, eng_synsets, foreign_glosses, synset_map)

    for pos in POS_NAMES:
        write_data_file(root_result, pos, data[pos], synset_map)
        write_index_file(root_result, pos, lang, variations[pos], synset_map)

def export_glosses(root_eng, result_path):
    """
    Exports to a file the English glosses for all the synsets that do not have a corresponding gloss in MCR 3.0. This file can be translated and, if the format is honored, it can be fed back into the transformation process with glosses in the foreign language.

    :param root_end: Path to the English WordNet 3.0 files
    :param result_path: Path where the output will be written
    """
    print "Loading English synsets..."
    eng_synsets = {}
    eng_glosses = {}
    for pos in POS_NAMES:
        load_synsets(root_eng, pos, eng_synsets, eng_glosses)
    
    write_english_glosses(eng_glosses, result_path)

if __name__ == "__main__":
    if 5 <= len(sys.argv) <= 6:
        if len(sys.argv) == 5 or sys.argv[5] == "":
            foreign_glosses_path = None
        else:
            foreign_glosses_path = sys.argv[5]
        transform(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], foreign_glosses_path)
    else:
        print "Invalid number of arguments. Syntax should be:"
        print "    $ python transform.py root_mcr root_eng lang root_result [foreign_glosses_path]"
