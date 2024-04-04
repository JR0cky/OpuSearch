from model.processing import Processing
import pandas as pd


class BilingualContext:
    """Get context of each match in source_files and target language

    """
    def __init__(self, path, regex, pre_context=None, post_context=None,
                 anno=True, caseinsensitive=False):
        self.__segments_l2_qual = None
        self.__segments_l1_qual = None
        self.__path = path
        self.__regex = regex
        self.__caseinsensitive = caseinsensitive
        self.__src_pattern = r'\(src\)="[0-9]+">'
        self.__text_list, self.__matches, self.__indices, self.__files = Processing.perform_new_search(
                    self.__path,
                    self.__regex,
                    stats=False,
                    unparsed_stats_context=True,
                    mono_pattern=self.__src_pattern,
                    mono=False,
                    caseinsensitive=self.__caseinsensitive)
        self.__segments_l1 = None
        self.__l1 = None
        self.__l2 = None
        self.__segments_l2 = None
        self.__pre_context = pre_context
        self.__post_context = post_context
        self.__pre_context_list_src = []
        self.__post_context_list_src = []
        self.__pre_context_list_trg = []
        self.__post_context_list_trg = []
        self.__indices_src_first = []
        self.__indices_src_last = []
        self.__indices_trg_first = []
        self.__indices_trg_last = []
        self.__segments = []
        self.__anno = anno

        # run function for processing context
        self.__process()

    def get_matches_context(self):
        return self.__matches

    def __process(self):
        # get whole segment for each match
        self.__segments = self.__get_segments()
        # get separated lists for src and trg
        self.__l1 = Processing.filter_alignment(self.__text_list, src=True)
        self.__l2 = Processing.filter_alignment(self.__text_list, src=False)
        # create dictionaries for looking up indices
        self.__l1_dict = self.__lang_list_to_dict(self.__l1)
        self.__l2_dict = self.__lang_list_to_dict(self.__l2)
        # extract all segments containing matches
        self.__extract_lang_segments()
        # extract the start and end indices in src list for each segment
        self.__indices_src_first, self.__indices_src_last \
            = self.__extract_indices(src=True)
        # extract the start and end indices in trg list for each segment
        self.__indices_trg_first, self.__indices_trg_last \
            = self.__extract_indices(src=False)

        # get pre-context for source_files
        self.__pre_context_list_src = self.__set_pre_context(
            self.__l1,
            self.__indices_src_first,
            self.__pre_context
        )
        # get post-context for source_files
        self.__post_context_list_src = self.__set_post_context(
            self.__l1,
            self.__indices_src_last,
            self.__post_context
        )
        # get pre-context for target
        self.__pre_context_list_trg = self.__set_pre_context(
            self.__l2,
            self.__indices_trg_first,
            self.__pre_context
        )
        # get post-context for target
        self.__post_context_list_trg = self.__set_post_context(
            self.__l2,
            self.__indices_trg_last,
            self.__post_context
        )
        # remove annotations
        if not self.__anno:
            self.__segments_l1 = Processing.remove_annotation(self.__segments_l1, nested=True)
            self.__segments_l2 = Processing.remove_annotation(self.__segments_l2, nested=True)
            self.__pre_context_list_src = Processing.remove_annotation(self.__pre_context_list_src, nested=True)
            self.__post_context_list_src = Processing.remove_annotation(self.__post_context_list_src, nested=True)
            self.__pre_context_list_trg = Processing.remove_annotation(self.__pre_context_list_trg, nested=True)
            self.__post_context_list_trg = Processing.remove_annotation(self.__post_context_list_trg, nested=True)

    def __get_segments(self):
        # initialise list of segments
        merged = []
        # get segment for every match (nested list) based on indices of matches
        for index in self.__indices:
            pre = []  # initialise list for lines before match
            post = []  # initialise list for lines after match
            count_left = 0  # counter for going left
            count_right = 0  # counter for going right
            current_left = ""  # current string before match
            current_right = ""  # current string after match
            while True:
                # check if separator left of match has been reached
                if not current_left.startswith("="):
                    count_left += 1  # increase count
                    # get next line before match with index (count)
                    current_left = self.__text_list[index - count_left]
                    # leave out separator if match is at the left margin
                    if not current_left.startswith("="):
                        pre.append(current_left)
                # check if separator right of match has been reached
                if not current_right.startswith("="):
                    count_right += 1  # increase count
                    # get next line after match with index (count)
                    current_right = self.__text_list[index + count_right]
                    # leave out separator if match is at the right margin
                    if not current_right.startswith("="):
                        post.append(current_right)
                # stop if full segment has been captured
                else:
                    break
            # merge segments to one list
            # and append to (nested) list of segments
            merged.append(pre + [self.__text_list[index]] + post)
        return merged

    @staticmethod
    def __lang_list_to_dict(lst):
        lang_dict = {}
        for i, val in enumerate(lst):
            if val not in lang_dict:
                lang_dict[val] = i
        return lang_dict

    def __extract_lang_segments(self):
        self.__segments_l1 = [[line for line in match
                               if line.startswith("(src)")]
                              for match in self.__segments]
        self.__segments_l2 = [[line for line in match
                               if line.startswith("(trg)")]
                              for match in self.__segments]

    # get indices of first and last element of segments
    # for source_files and target each
    @staticmethod
    def __extract_ind(sublst, dictionary):
        first_ind = []
        last_ind = []
        for elem in sublst:
            # extract first and last elem in each segment match
            first, last = elem[0], elem[-1]
            # look up indices in dictionaries for each segment
            # append indices to lists
            first_ind.append(dictionary[first])
            last_ind.append(dictionary[last])
        return first_ind, last_ind

    def __extract_indices(self, src=True):
        if src:
            first, last = self.__extract_ind(self.__segments_l1,
                                             self.__l1_dict)

        else:
            first, last = self.__extract_ind(self.__segments_l2,
                                             self.__l2_dict)
        return first, last

    def __set_pre_context(self, lst, indices, pre_context):
        pre_context_list = [
            lst[index - pre_context:index]
            for index in indices]
        return pre_context_list

    def __set_post_context(self, lst, indices, post_context):
        post_context_list = [
            lst[index + 1: index + 1 + post_context]
            for index in indices]
        return post_context_list

    def write_context_qual_bil(self, l1, l2, path=None, root_path=None):
        """ Write monolingual matches and their context to textfile for
            a qualitative analysis

                @param l1: source_files language
                @param l2: target language
                @param path: file path to be set
                @param root_path: file path for root to be set
                @return:
                """
        # automatically create file path if none is given
        if path is None:
            path = Processing.automate_path_context(
                regex=self.__regex,
                pre_con=self.__pre_context,
                post_con=self.__post_context,
                l1=l1,
                l2=l2,
                mono=False,
                qual=True,
                root_path=root_path
            )
        # add match marker to segments before combining lists
        self.__segments_l1_qual = [
            [str(match) + "\t<<<<<<<< MATCH" for match in segment]
            for segment in self.__segments_l1]
        self.__segments_l2_qual = [
            [str(match) + "\t<<<<<<<< MATCH" for match in segment]
            for segment in self.__segments_l2]
        # write content to text file
        with open(path, "w", encoding="utf-8") as file_out:
            # throw everything together for formatting
            for (pre_con_src, match_src, post_con_src,
                 pre_con_trg, match_trg, post_con_trg, file) in \
                    zip(self.__pre_context_list_src,
                        self.__segments_l1_qual,
                        self.__post_context_list_src,
                        self.__pre_context_list_trg,
                        self.__segments_l2_qual,
                        self.__post_context_list_trg,
                        self.__files):
                # write results in string format
                # chr(10) = "\n"
                file_out.write(
                    f"{chr(10).join(pre_con_src)}\n"
                    f"{chr(10).join(match_src)}\n"
                    f"{chr(10).join(post_con_src)}\n\n"

                    f"{chr(10).join(pre_con_trg)}\n"
                    f"{chr(10).join(match_trg)}\n"
                    f"{chr(10).join(post_con_trg)}\n\n"

                    f"FILES: {file}\n"
                    f"REGEX:{self.__regex}\n"
                    f"FOUND {len(self.__matches)} MATCHES\n\n"
                    f"{'*' * 100}\n\n"
                )
        return path

    def write_context_quant_bil(self, l1, l2, path=None, root_path=None):
        """ Write bilingual matches and their context to csv file
            for further processing

                @param l1: source_files language
                @param l2: target language
                @param path: file path to be set
                @param root_path: file path for root to be set
                @return:
                """

        # automatically create file path if none is given
        if path is None:
            path = Processing.automate_path_context(
                regex=self.__regex,
                l1=l1,
                l2=l2,
                pre_con=self.__pre_context,
                post_con=self.__post_context,
                qual=False,
                mono=False,
                root_path=root_path
            )
        # create list of duplicated regex pattern for last column
        regex_list = [self.__regex for elem in self.__matches]
        # create column of pre-context lines for src separated by linebreak
        pre_con_merged_src = ["\n".join(elem) for elem
                              in self.__pre_context_list_src]
        # create column of post-context lines for src separated by linebreak
        post_con_merged_src = ["\n".join(elem) for elem
                               in self.__post_context_list_src]
        # create column of pre-context lines for trg separated by linebreak
        pre_con_merged_trg = ["\n".join(elem) for elem
                              in self.__pre_context_list_trg]
        # create column of post-context lines for trg separated by linebreak
        post_con_merged_trg = ["\n".join(elem) for elem
                               in self.__post_context_list_trg]
        # create column of joined matches (based on segment) for src
        matches_src = ["\n".join(elem) for elem in self.__segments_l1]
        # create column of joined matches (based on segment) for trg
        matches_trg = ["\n".join(elem) for elem in self.__segments_l2]
        # merge all list in form of columns in dataframe
        df = pd.DataFrame(list(zip(pre_con_merged_src, matches_src,
                                   post_con_merged_src, pre_con_merged_trg,
                                   matches_trg, post_con_merged_trg,
                                   self.__files, regex_list)),
                          columns=[f"Match Pre-Context "
                                   f"(-{self.__pre_context})",
                                   f"Match {l1}",
                                   f"Match Post-Context: "
                                   f"(+{self.__post_context})",
                                   f"Translation Pre-Context "
                                   f"(-{self.__pre_context})",
                                   f"Match {l2}",
                                   f"Translation Post-Context: "
                                   f"(+{self.__post_context})",
                                   "Files",
                                   "Regex"])
        # remove duplicate rows
        df.drop_duplicates(keep='first', inplace=True)
        # write dataframe to csv
        df.to_csv(path, encoding="utf-8")
        return path


if __name__ == "__main__":
    context = BilingualContext(path="../data/generated/alignments_fr_es_500_parsed.txt",
                               regex=r"Comment", pre_context=2, post_context=2, anno=True, caseinsensitive=True)

    context.write_context_quant_bil(l1="French", l2="Spanish",
                                    root_path="../data/search_results/")
    context.write_context_qual_bil(l1="French",
                                   l2="Spanish",
                                   root_path="../data/search_results/")
