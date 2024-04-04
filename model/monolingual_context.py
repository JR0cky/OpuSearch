import pandas as pd
from model.processing import Processing


class MonolingualContext:
    """Get context of each match in source_files language

    """
    def __init__(self, path, regex, pre_context=None, post_context=None,
                 anno=True, src=True, caseinsensitive=False
                 ):
        self.__path = path
        self.__regex = regex
        self.__src = src
        self.__caseinsensitive = caseinsensitive
        self.__src_pattern = r'\(src\)="[0-9]+">'
        self.__trg_pattern = r'\(trg\)="[0-9]+">'
        # option to either filter for src or trg only
        if self.__src:
            # set src pattern to search ID in alignments' values
            self.__current_pattern_ID = self.__src_pattern
        else:
            # set trg pattern to search ID in alignments' values
            self.__current_pattern_ID = self.__trg_pattern
        # get data
        self.__text_list, self.__matches, self.__indices, self.__files = \
            Processing.perform_new_search(
                self.__path,
                self.__regex,
                stats=False,
                mono=True,
                mono_pattern=self.__current_pattern_ID,
                caseinsensitive=self.__caseinsensitive
            )
        self.__text_list_only = [elem for elem in self.__text_list
                                 if not elem.startswith("=")]
        self.__pre_context = pre_context
        self.__post_context = post_context
        self.__pre_context_list = []
        self.__post_context_list = []
        self.__anno = anno
        # run function for processing context
        self.__process()

    def get_matches_context(self):
        return self.__matches

    def __process(self):
        # get pre- and post-context lines for each match
        if self.__pre_context is not None:
            self.set_pre_context()
        if self.__post_context is not None:
            self.set_post_context()

        # option to remove annotation
        if not self.__anno:
            self.__pre_context_list = Processing.remove_annotation(
                self.__pre_context_list
            )
            self.__matches = Processing.remove_annotation(
                self.__matches, nested=False
            )
            self.__post_context_list = Processing.remove_annotation(
                self.__post_context_list
            )

    def set_pre_context(self):
        """ Retrieve pre-context for a given number of lines

        @return:
        """
        self.__pre_context_list = [
            self.__text_list_only[index - self.__pre_context:index]
            for index in self.__indices]
        self.__pre_context_list = [
            [item for item in sublist if not item.startswith("#")]
            for sublist in self.__pre_context_list
        ]

    def set_post_context(self):
        """ Retrieve post-context for a given number of lines

        @return:
        """
        self.__post_context_list = [
            self.__text_list_only[index + 1: index + 1 + self.__post_context]
            for
            index in self.__indices]
        self.__post_context_list = [
            [item for item in sublist if not item.startswith("#")]
            for sublist in self.__post_context_list
        ]

    def write_context_qual_mono(self, lang, path=None, root_path=None):
        """ Write monolingual matches and their context to textfile for
            a qualitative analysis

        @param path: file path to be set
        @param root_path: file path for root to be set
        @return: file path
        """
        # automatically create file path if none is given
        if path is None:
            path = Processing.automate_path_context(
                regex=self.__regex,
                pre_con=self.__pre_context,
                post_con=self.__post_context,
                mono=True,
                l1=lang,
                root_path=root_path
            )
        # write content to text file
        with open(path, "w", encoding="utf-8") as file_out:
            for (pre_con, match, post_con, file) in zip(
                    self.__pre_context_list,
                    self.__matches,
                    self.__post_context_list,
                    self.__files
            ):
                # write results in string format
                # chr(10) = "\n"
                file_out.write(
                    f"{chr(10).join(pre_con)}\n"
                    f"{match}\t<<<<<<<< MATCH\n"
                    f"{chr(10).join(post_con)}\n\n"
                    f"FILES: {file}\n"
                    f"REGEX: {self.__regex}\n"
                    f"FOUND {len(self.__matches)} MATCHES\n\n"
                    f"{'*' * 100}\n\n")
        return path

    def write_context_quant_mono(self, lang, path=None, root_path=None):
        """ Write monolingual matches and their context to csv file
            for further processing

        @param path: file path to be set
        @param root_path: file path for root to be set
        @return: file path
        """

        # automatically create file path if none is given
        if path is None:
            path = Processing.automate_path_context(
                regex=self.__regex,
                pre_con=self.__pre_context,
                post_con=self.__post_context,
                qual=False,
                mono=True,
                l1=lang,
                root_path=root_path
            )
        # create list of duplicated regex pattern for last column
        regex_list = [self.__regex for elem in self.__matches]
        # create list (column) of pre-context lines separated by linebreak
        pre_con_merged = ["\n".join(elem) for elem in self.__pre_context_list]
        # create list (column) of post-context lines separated by linebreak
        post_con_merged = ["\n".join(elem) for elem
                           in self.__post_context_list]
        # merge all list in form of columns in dataframe
        df = pd.DataFrame(list(
            zip(pre_con_merged, self.__matches, post_con_merged, self.__files,
                regex_list)),
            columns=[f"Pre-Context: (-{self.__pre_context})",
                     f"Match {lang}",
                     f"Post-Context: (+{self.__post_context})",
                     "Files",
                     "Regex"])
        # write dataframe to csv
        df.to_csv(path, encoding="utf-8")
        return path


if __name__ == "__main__":
    context = MonolingualContext(
        path="../data/generated/alignments_fr_es_500_parsed.txt",
        regex=r"Que.*", pre_context=4, post_context=5,
        anno=True, src=True)
    context.write_context_quant_mono(lang="French",
                                     root_path="../data/search_results/")
    context.write_context_qual_mono(lang="French",
                                    root_path="../data/search_results/")
