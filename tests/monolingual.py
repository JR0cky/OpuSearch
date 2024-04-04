import unittest
import pandas as pd
from model.monolingual_context import MonolingualContext
from model.monolingual_statistics import MonolingualStats


class BilContextMethods(unittest.TestCase):
    pass


class BilStatsMethods(unittest.TestCase):
    pass


class TestCombo(unittest.TestCase):
    def test_combo_parsed(self):
        stats = MonolingualStats(path="../data/generated/alignments_fr_es_500_parsed.txt",
                                 regex=r'Comment', parsed=True, src=True)

        path_stats = stats.write_monolingual_stats(lang="French", root_path="../data/search_results/")
        context = MonolingualContext(path="../data/generated/alignments_fr_es_500_parsed.txt",
                                     regex=r"Comment", pre_context=4, post_context=5, anno=True)
        path_context = context.write_context_quant_mono(lang="French", root_path="../data/search_results/")
        mono_stats = pd.read_csv(path_stats)
        mono_context = pd.read_csv(path_context)

        self.assertEqual(len(mono_context), mono_stats['Count_Match'].sum())


if __name__ == "__main__":
    unittest.main()
