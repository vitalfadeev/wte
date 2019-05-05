import unittest
import os
import logging

import wte


TEST_FOLDER = "test"
wte.log.setLevel(logging.ERROR)
wte.log_no_words.setLevel(logging.ERROR)
wte.log_non_english.setLevel(logging.ERROR)
wte.log_unsupported.setLevel(logging.ERROR)

def get_words(label):
    src_file = os.path.join(TEST_FOLDER, label + ".txt")
    text = wte.get_contents(src_file)
    return wte.parse_text(label, text)


class TestWTE(unittest.TestCase):
    """
    Main test class for unit tests.
    """

    def __init__(self, *args, **kwargs):
        wte.create_storage(TEST_FOLDER)
        wte.create_storage(wte.TXT_FOLDER)
        wte.create_storage(wte.LOGS_FOLDER)
        super().__init__(*args, **kwargs)

    @unittest.skip("skip")
    def test_1_treemap_word_store(self):
        treemap = wte.TreeMap()

        label = "thesaurus"
        treemap.add_words(label, get_words(label))
        self.assertIsInstance(treemap[label], wte.Word) # one item

        label = "cat"
        treemap.add_words(label, get_words(label))
        self.assertIsInstance(treemap[label], list) # 11 items

        label = "_empty_"
        treemap.add_words(label, get_words(label))
        self.assertNotIn(label, treemap)

    @unittest.skip("skip")
    def test_2_multiple_words_extracting(self):
        label = "cat"
        words = get_words(label)
        self.assertEqual(len(words), 13)

    def test_3_word_label_type(self):
        label = "cat"
        words = get_words(label)

        word1 = words[0]
        self.assertEqual(word1.LabelType, ['Felidae', 'animal'])

        #word2 = words[1]
        #print(word2.LabelType)
        #self.assertEqual(word1.LabelType, ['LB_EN_NAUTICAL_TRANSITIVE', 'Hoist'])
