import unittest
import pandas as pd
from model.bilingual_context import BilingualContext
from model.bilingual_statistics import BilingualStats


class BilContextMethods(unittest.TestCase):
    pass


class BilStatsMethods(unittest.TestCase):
    pass


class TestCombo(unittest.TestCase):
    def test_combo_parsed(self):
        stats = BilingualStats(path="../data/generated/alignments_fr_es_500_parsed.txt",
                               regex=r'Comment', src_aggregate=False, parsed=True)
        stats_aggr = BilingualStats(path="../data/generated/alignments_fr_es_500_parsed.txt",
                                    regex=r'Comment', src_aggregate=True, parsed=True)
        path_stats = stats.write_bilingual_stats(l1="French", l2="Spanish",
                                                 root_path="../data/search_results/")
        path_stats_aggr = stats_aggr.write_bilingual_stats(l1="French", l2="Spanish",
                                                           root_path="../data/search_results/")
        context = BilingualContext(path="../data/generated/alignments_fr_es_500_parsed.txt",
                                   regex=r"Comment", pre_context=4, post_context=5, anno=True)
        path_context = context.write_context_quant_bil(l1="French", l2="Spanish",
                                                       root_path="../data/search_results/")
        bil_stats = pd.read_csv(path_stats)
        bil_stats_aggr = pd.read_csv(path_stats_aggr)
        bil_context = pd.read_csv(path_context)

        self.assertEqual(len(bil_context), bil_stats['Count_Alignment'].sum())


if __name__ == "__main__":
    unittest.main()
