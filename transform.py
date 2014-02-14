# This module transforms MCR 3.0 database files into WordNet 3.0 database files.
# The resulting files can be loaded with the nltk WordNet reader using:
#   nltk.corpus.reader.wordnet.WordNetCorpusReader(<FILES_ROOT>)
# 
# Author: Luis Chiruzzo <luischir@fing.edu.uy>

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
    1: "=",
    6: "%s",
    7: "%m",
    8: "%p",
    12: "@",
    33: "!",
    34: "&",
    52: "$",
    63: ";c",
    64: "+",
    66: ";r",
    68: ";u"
}

def get_offset_pos(synset):
    split = synset.split("-")
    offset = split[2]
    pos = split[3]
    return [offset, pos]

def create_data_file(pos, synsets, variations, relations, eng_synsets, spa_glosses, synset_map):
    text_chunks = []
    variation_map = {}

    text = "  1 MCR Spanish WordNet 3.0 " + POS_NAMES[pos] + " data file\n"
    index = len(text)
    text_chunks.append(text)

    synsets_set = dict([pos, set(synsets[pos][0])] for pos in synsets)
    
    for [synset, gloss] in synsets[pos]:
        synset_name = "spa-30-" + synset + "-" + pos
        eng_offset = synset + pos
        
        text = synset
        synset_map["@" + text + pos] = index
        index += len(text)
        text_chunks.append("@" + text + pos)
        
        text = " 00 " + pos + " "
        index += len(text)
        text_chunks.append(text)
        
        # variations
        if synset_name in variations:
            text = str(len(variations[synset_name])) + " "
            index += len(text)
            text_chunks.append(text)
            
            for variation in variations[synset_name]:
                text = variation.encode("latin-1")
                index += len(text)
                text_chunks.append(text)
                
                lower = text.lower()
                if not lower in variation_map:
                    variation_map[lower] = []
                variation_map[lower].append(synset)
                
                text = " 0 "
                index += len(text)
                text_chunks.append(text)
        else:
            # use the english lemma
            if eng_offset in eng_synsets:
                lemma = "`" + eng_synsets[eng_offset]
                lower = lemma.lower()
                if not lower in variation_map:
                    variation_map[lower] = []
                variation_map[lower].append(synset)
            else:
                lemma = "<unknown>"
            text = "1 " + lemma + " 0 "
            index += len(text)
            text_chunks.append(text)

        # relations
        if synset_name in relations:
            valid_relations = []
            for [type,rs] in relations[synset_name]:
                [rel_offset, rel_pos] = get_offset_pos(rs)
                if rel_offset in synsets_set[rel_pos]:
                    valid_relations.append([type, rel_offset, rel_pos])
                elif rel_offset + rel_pos in eng_synsets:
                    valid_relations.append([type, rel_offset, rel_pos])
                
            text = str(len(valid_relations)) + " "
            index += len(text)
            text_chunks.append(text)
            
            for [type, rel_offset, rel_pos] in valid_relations:
                text = type + " "
                index += len(text)
                text_chunks.append(text)
                
                text = rel_offset
                index += len(text)
                text_chunks.append("@" + text + rel_pos)

                text = " " + rel_pos + " 0000 "
                index += len(text)
                text_chunks.append(text)
        else:
            text = "0 "
            index += len(text)
            text_chunks.append(text)

        # gloss
        if (gloss == "NULL" or gloss.strip() == "") and eng_offset in spa_glosses:
            try:
                text = "| " + spa_glosses[eng_offset].encode("latin-1") + "  \n"
                index += len(text)
                text_chunks.append(text)
            except UnicodeEncodeError as e:
                text = "| " + gloss.encode("latin-1") + "  \n"
                index += len(text)
                text_chunks.append(text)
                print eng_offset
                print e
        else:
            text = "| " + gloss.encode("latin-1") + "  \n"
            index += len(text)
            text_chunks.append(text)

    return [text_chunks, variation_map]

def write_data_file(root_result, pos, text_chunks, synset_map):
    filename = root_result + "/data." + POS_NAMES[pos]
    print filename
    file = open(filename, "wb")
    for text in text_chunks:
        if text in synset_map:
            file.write("{0:08d}".format(synset_map[text]))
        else:
            file.write(text)
    file.close()

def write_index_file(root_result, pos, variations_map, synset_map):
    lemmas = sorted(variations_map.keys())
    filename = root_result + "/index." + POS_NAMES[pos]
    print filename
    file = open(filename, "wb")
    file.write("  1 MCR Spanish WordNet 3.0 " + POS_NAMES[pos] + " index file\n")
    for lemma in lemmas:
        synset_count = str(len(variations_map[lemma]))
        file.write(lemma + " " + pos + " " + synset_count + " 0 " + synset_count + " 0")
        for offset in variations_map[lemma]:
            file.write(" {0:08d}".format(synset_map["@" + offset + pos]))
        file.write("  \n")
    file.close()

def load_synsets(root_eng, pos, eng_synsets, eng_glosses):
    file = open(root_eng + "/data." + POS_NAMES[pos], "r")
    for line in file.readlines():
        if not line.startswith("  "):
            split = line.split(" ")
            offset = split[0]
            first_lemma = split[4]
            eng_synsets[offset + pos] = first_lemma
            gloss_split = line.split(" | ")
            eng_glosses[offset + pos] = gloss_split[1].strip()
    file.close()
    
def write_english_glosses(root_result, eng_glosses):
    print "Writing english glosses..."
    file = open(root_result + "/eng_glosses.txt", "wb")
    for offset in sorted(eng_glosses):
        file.write(offset + " | " + eng_glosses[offset] + "\n")
    file.close()
    
def load_spanish_glosses(root_result):
    print "Writing english glosses..."
    file = open(root_result + "/spa_glosses.txt", "r")
    glosses = {}
    for line in file.readlines():
        split = line.decode('utf-8').split(" | ")
        offset = split[0].strip()
        gloss = split[1].strip()
        glosses[offset] = gloss
    file.close()
    return glosses

def transform(root_spa, root_eng, root_result):
    """
    Transforms the set of Spanish MCR 3.0 files into a text database compatible with the nltk WordNet corpus reader.

    The process reads the files wei_spa-30_synset.tsv, wei_spa-30_variant.tsv and wei_spa-30_relation.tsv and generates a set of files following the WordNet database schema. The generated files will be: data.noun, index.noun, data.verb, index.verb, data.adj, index.adj, data.adv and index.adv.

    If a synset doesn't have any lemma defined in the Spanish version, we use the first lemma of the English version (prepending a character `) for this synset. This means that when traversing the ontology, it's possible to find English placeholders for missing Spanish words.

    :param root_spa: Path to the MCR 3.0 Spanish files
    :param root_end: Path to the English WordNet 3.0 files
    :param root_result: Path where the resulting files will be written
    """
    print "Loading valid synsets..."
    file = open(root_spa + "/wei_spa-30_synset.tsv")
    synsets = {}
    synsets["n"] = []
    synsets["a"] = []
    synsets["r"] = []
    synsets["v"] = []
    glossless = 0
    for line in file.readlines():
        split = line.split("\t")
        [synset_number, synset_pos] = get_offset_pos(split[0])
        synset_gloss = split[6].decode("utf-8")
        if synset_gloss.strip() == "" or synset_gloss == "NULL":
            glossless += 1
        synsets[synset_pos].append([synset_number, synset_gloss])
    print str(glossless) + " glosses missing"
    file.close()

    print "Loading synset variants..."
    vars_file = open(root_spa + "/wei_spa-30_variant.tsv")
    variants = {}
    for line in vars_file.readlines():
        split = line.decode("utf-8").split("\t")
        variant = split[0]
        synset = split[2]
        if synset not in variants:
            variants[synset] = []
        variants[synset].append(variant)
    vars_file.close()

    print "Loading synset relations..."
    rels_file = open(root_spa + "/wei_spa-30_relation.tsv")
    relations = {}
    for line in rels_file.readlines():
        split = line.decode("utf-8").split("\t")
        type = int(split[0])
        from_synset = split[1]
        to_synset = split[3]
        if type in RELATION_MAP:
            if from_synset not in relations:
                relations[from_synset] = []
            relations[from_synset].append([RELATION_MAP[type], to_synset])
            if type in SYMMETRIC_RELATION_MAP:
                if to_synset not in relations:
                    relations[to_synset] = []
                relations[to_synset].append([SYMMETRIC_RELATION_MAP[type], from_synset])
    rels_file.close()
    print len(relations)

    print "Loading English synsets..."
    eng_synsets = {}
    eng_glosses = {}
    load_synsets(root_eng, "n", eng_synsets, eng_glosses)
    load_synsets(root_eng, "v", eng_synsets, eng_glosses)
    load_synsets(root_eng, "a", eng_synsets, eng_glosses)
    load_synsets(root_eng, "r", eng_synsets, eng_glosses)
    
    #print "Loading Spanish glosses..."
    #spa_glosses = load_spanish_glosses(root_result)
    spa_glosses = {}
    
    print "Creating data files..."
    
    #write_english_glosses(root_result, eng_glosses)
    
    synset_map = {}
    [noun_data, noun_variations] = create_data_file("n", synsets, variants, relations, eng_synsets, spa_glosses, synset_map)
    [verb_data, verb_variations] = create_data_file("v", synsets, variants, relations, eng_synsets, spa_glosses, synset_map)
    [adj_data, adj_variations] = create_data_file("a", synsets, variants, relations, eng_synsets, spa_glosses, synset_map)
    [adv_data, adv_variations] = create_data_file("r", synsets, variants, relations, eng_synsets, spa_glosses, synset_map)

    # write data files
    write_data_file(root_result, "n", noun_data, synset_map)
    write_data_file(root_result, "v", verb_data, synset_map)
    write_data_file(root_result, "a", adj_data, synset_map)
    write_data_file(root_result, "r", adv_data, synset_map)

    # write index files
    write_index_file(root_result, "n", noun_variations, synset_map)
    write_index_file(root_result, "v", verb_variations, synset_map)
    write_index_file(root_result, "a", adj_variations, synset_map)
    write_index_file(root_result, "r", adv_variations, synset_map)
