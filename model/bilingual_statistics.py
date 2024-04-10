import ast
import re
import pandas as pd
from collections import defaultdict
from model.processing import Processing


class BilingualStats:
    """Get bilingual matches from corresponding regex and
       write them with their translations to a csv-file

    """
    def __init__(self, path, regex, parsed=False, src_aggregate=False, caseinsensitive=False):
        self.__path = path
        self.__regex = regex
        self.__parsed = parsed
        self.__src_aggregate = src_aggregate
        self.__src_pattern = r'\(src\)="[0-9]+">'
        self.__trg_pattern = r'\(trg\)="[0-9]+">'
        self.__caseinsensitive = caseinsensitive
        self.__matches_src_all = []
        self.__matches_clean = []
        self.__sets_files = []
        # other routine for unparsed data
        if not self.__parsed:
            self.__match_combo = []
            self.__text_list, self.__matches, self.__indices, self.__files = \
                Processing.perform_new_search(
                    self.__path,
                    self.__regex,
                    stats=False,
                    unparsed_stats_context=True,
                    mono=False,
                    mono_pattern=self.__src_pattern,
                    caseinsensitive=self.__caseinsensitive
                )
            self.__process_counts_unparsed()
        else:
            self.__parsed_dict, self.__matches_l1, self.__files = \
                Processing.perform_new_search(
                    self.__path,
                    self.__regex,
                    stats=True,
                    unparsed_stats_context=False,
                    mono=False,
                    mono_pattern=self.__src_pattern,
                    caseinsensitive=self.__caseinsensitive
                )
            # extract matches, translations and metadata
            self.__process_counts()

    def __process_counts_unparsed(self):
        """ Process alignments for match in source_files language

                @return:
                """
        # summarise multiple mappings, e.g. one line for source_files, two for target
        # remove "=" as separator, empty entries and files starting with "#"
        # self.__text_list = [elem for elem in self.__text_list if not elem.startswith("=") and not elem.startswith("#")
        #                     and len(elem) > 0]
        if self.__src_aggregate:
            self.__summarise_mappings()
        else:
            self.__get_mappings()
        # extract source_files and target
        self.__extract_lang(src=True)
        self.__extract_lang(src=False)

        # remove annotation
        self.__matches_L1 = Processing.remove_annotation(self.__matches_L1, nested=False)
        self.__matches_L2 = Processing.remove_annotation(self.__matches_L2, nested=False)

        # create tuples to count combinations of source_files and translation
        self.__match_combo = [elem for elem in zip(self.__matches_L1,
                                                   self.__matches_L2)]
        # create dictionary with counts
        self.__counts_unparsed = Processing.get_counts(self.__match_combo)

    def __get_mappings(self):
        for index in self.__indices:
            all_lines = [self.__text_list[index]]
            # src src trg, 1st src as match
            if self.__text_list[index + 2].startswith("(trg)") \
                    and self.__text_list[index + 1].startswith("(src)"):
                all_lines.append(self.__text_list[index + 2])
            # src trg trg
            elif self.__text_list[index + 2].startswith("(trg)") \
                    and self.__text_list[index + 1].startswith("(trg)"):
                all_lines.extend(self.__text_list[index + 1:index + 3])
            # src src trg, 2nd src as match
            elif self.__text_list[index + 1].startswith("(trg)") \
                    and self.__text_list[index - 1].startswith("(src)"):
                all_lines.append(self.__text_list[index + 1])
            # 1 src 1 trg
            elif self.__text_list[index + 1].startswith("(trg)") \
                    and self.__text_list[index].startswith("(src)"):
                all_lines.append(self.__text_list[index + 1])
            self.__match_combo.append(all_lines)

    def __summarise_mappings(self):
        for index in self.__indices:
            # src src trg, 1st src as match
            if self.__text_list[index + 2].startswith("(trg)") \
                    and self.__text_list[index + 1].startswith("(src)"):
                self.__match_combo.append(self.__text_list[index:index + 3])
            # src trg trg
            elif self.__text_list[index + 2].startswith("(trg)") \
                    and self.__text_list[index + 1].startswith("(trg)"):
                self.__match_combo.append(self.__text_list[index:index + 3])
            # src src trg, 2nd src as match
            elif self.__text_list[index + 1].startswith("(trg)") \
                    and self.__text_list[index - 1].startswith("(src)"):
                self.__match_combo.append(
                    self.__text_list[index - 1:index + 2]
                )
            # 1 src 1 trg
            elif self.__text_list[index + 1].startswith("(trg)") \
                    and self.__text_list[index].startswith("(src)"):
                self.__match_combo.append(self.__text_list[index:index + 2])

    def __extract_lang(self, src=True):
        """Extract source_files and target language and put them into a nested list

        """
        # get source_files
        if src:
            self.__matches_L1 = [" ".join([line for line in match
                                  if line.startswith("(src)")])
                                 for match in self.__match_combo]
        # get target
        else:
            self.__matches_L2 = [" ".join([line for line in match
                                  if line.startswith("(trg)")])
                                 for match in self.__match_combo]

    def get_counts(self):
        # getter for checking counts
        if self.__parsed:
            if self.__src_aggregate:
                return len(self.__final_src_all)
            else:
                return len(self.__final_src_single)
        else:
            return len(self.__counts_unparsed)

    @staticmethod
    def __extract_metadata(lines, pattern_regex, inner_data, metadata_key):
        meta_data = []
        for elem in inner_data:
            tmp = []
            for match_ID in pattern_regex.findall(elem):
                tmp.append(lines[match_ID][metadata_key])
            meta_data.extend(tmp)
        return meta_data

    def __process_counts(self):
        # dictionary for summarised src
        self.__final_src_all = defaultdict(dict)
        # dictionary for single src
        self.__final_src_single = defaultdict(dict)
        # check for search results
        if self.__matches_l1:
            # remove annotation for aggregation
            self.__matches_clean = Processing.remove_annotation(
                self.__matches_l1, nested=False)
            # pre-compile search pattern for match
            trg_pattern_regex = re.compile(f'({self.__trg_pattern})')
            src_pattern_regex = re.compile(f'({self.__src_pattern})')
            # Iterate through each match
            for i, match in enumerate(self.__matches_l1):
                token_src_single = []
                POS_src_single = []
                lemma_src_single = []
                token_trg_all = []
                POS_trg_all = []
                lemma_trg_all = []
                token_src_all = []
                POS_src_all = []
                lemma_src_all = []
                # get file key
                match_key = self.__files[i]
                # get values of file key (second level)
                match_data = self.__parsed_dict.get(match_key, {})
                # Iterate through second level of
                # nested dictionary (alignments)
                for alignment, lines in match_data.items():
                    # get ID of match to match it with the one in the alignment
                    match_ID = src_pattern_regex.search(match)
                    match_ID = match_ID.group()
                    if match_ID in alignment:
                        # append everything with target to inner trg list
                        inner_trg = re.findall(self.__trg_pattern, alignment)
                        # go through target_lines for IDs
                        tmp_token_trg = self.__extract_metadata(
                            lines, trg_pattern_regex, inner_trg, "string")
                        tmp_POS_trg = self.__extract_metadata(
                            lines, trg_pattern_regex, inner_trg, "POS")
                        tmp_lemma_trg = self.__extract_metadata(
                            lines, trg_pattern_regex, inner_trg, "lemma")
                        # append trg metadata to final lists for counter
                        token_trg_all.extend(tmp_token_trg)
                        POS_trg_all.extend(tmp_POS_trg)
                        lemma_trg_all.extend(tmp_lemma_trg)
                        # check if src lines shall be summarised:
                        if self.__src_aggregate:
                            # check if two lines with src are in align
                            inner_src = re.findall(self.__src_pattern,
                                                   alignment)
                            # go through src lines for IDs
                            tmp_token_src = self.__extract_metadata(
                                lines, src_pattern_regex, inner_src, "string")
                            tmp_POS_src = self.__extract_metadata(
                                lines, src_pattern_regex, inner_src, "POS")
                            tmp_lemma_src = self.__extract_metadata(
                                lines, src_pattern_regex, inner_src, "lemma")
                            # append src metadata to final lists for counter
                            token_src_all.append(tmp_token_src)
                            POS_src_all.append(tmp_POS_src)
                            lemma_src_all.append(tmp_lemma_src)
                            # append summarised src lines
                            self.__matches_src_all.append(tmp_token_src)
                        else:
                            # single out ID in match
                            src_ID = src_pattern_regex.search(match)
                            token_src_single.extend(
                                lines[src_ID.group()]["string"])
                            POS_src_single.extend(
                                lines[src_ID.group()]["POS"])
                            lemma_src_single.extend(
                                lines[src_ID.group()]["lemma"])
                # Get file pairs that belong to the particular alignment
                self.__sets_files.append([match_key])
                if not self.__src_aggregate:
                    # clean the match out of the annotation
                    match = re.sub(self.__src_pattern, "", match)
                    # get count for combination of results and translation
                    # update dictionary with metadata
                    self.__final_src_single[str(i)].update({
                        'match': match,
                        'target': ' '.join(
                            ' '.join(
                                map(str, sublist))
                            for sublist in token_trg_all),
                        'POS_src': POS_src_single,
                        'lemma_src': lemma_src_single,
                        'token_src': token_src_single,
                        'POS_trg': POS_trg_all,
                        'lemma_trg': lemma_trg_all,
                        'token_trg': token_trg_all
                    }
                    )
                else:
                    src_lines = " ".join(" ".join(sublist)
                                         for sublist
                                         in self.__matches_src_all[i])
                    # update dict with all src lines and corresponding values
                    self.__final_src_all[str(i)].update({
                        'match': src_lines,
                        'target': ' '.join(' '.join(map(str, sublist))
                                           for sublist in token_trg_all),
                        'POS_src_all': POS_src_all,
                        'lemma_src_all': lemma_src_all,
                        'token_src_all': token_src_all,
                        'POS_trg': POS_trg_all,
                        'lemma_trg': lemma_trg_all,
                        'token_trg': token_trg_all
                    }
                    )
        else:
            pass

    def write_bilingual_stats(self, l1, l2, path=None, root_path=None):
        """ Write monolingual matches with counts to file

        @param l1: source_files language
        @param l2: target language
        @param path: file path to be set
        @param root_path: file path for root to be set
        @return: file path
        """
        l1 = l1.strip()
        l2 = l2.strip()
        if path is None:
            path = Processing.automate_path_statistics(
                regex=self.__regex, l1=l1, l2=l2,
                root_path=root_path)
        # handle case for unparsed data
        if not self.__parsed:
            Processing.write_statistics_to_file(path, self.__regex, self.__counts_unparsed,
                                                self.__files, l1=l1, l2=l2)
        else:
            # create dataframes from dictionary
            if not self.__src_aggregate:
                df = pd.DataFrame.from_dict(
                    self.__final_src_single, orient='index').reset_index()
            else:
                df = pd.DataFrame.from_dict(
                    self.__final_src_all, orient='index').reset_index()
            # set columns
            df.columns = ['Number', f'Match {l1.strip()}', f'Match {l2.strip()}',
                          'POS_src', 'Lemma_src',
                          'Token_src', 'POS_trg', 'Lemma_trg', 'Token_trg']
            # drop artificial index column
            df = df.drop("Number", axis=1)
            # make everything hashable
            df = df.astype(str)
            # get counts
            count = df[[f'Match {l1}',
                        f'Match {l2}']].value_counts().reset_index(
                name='Count_Alignment')
            count_POS_src = df[[f'Match {l1}',
                                'POS_src']].value_counts().reset_index(
                name='Count_POS_src')
            count_POS_trg = df[[f'Match {l2}',
                                'POS_trg']].value_counts().reset_index(
                name='Count_POS_trg')

            # add counts and sets of file pairs for all matches
            df["File_Pairs"] = self.__sets_files
            files = df.groupby([f'Match {l1}',
                                f'Match {l2}'])['File_Pairs'].agg(
                list).reset_index()
            # flatten lists if necessary
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: Processing.is_nested(x))
            # make set to get unique file pairs
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: set(x))
            # get count of file pairs
            files['File_Count'] = files['File_Pairs'].apply(lambda x: len(x))
            # merge original dataframe and counts for src and trg combinations
            merged_df = pd.merge(df, count, on=[f'Match {l1}',
                                                f'Match {l2}'],
                                 how='left')
            # merge original dataframe and counts for POS_src
            merged_df = pd.merge(merged_df, count_POS_src,
                                 on=[f'Match {l1}', 'POS_src'], how='left')
            # merge original dataframe and counts for POS_trg
            merged_df = pd.merge(merged_df, count_POS_trg,
                                 on=[f'Match {l2}', 'POS_trg'], how='left')
            # drop left over index column
            merged_df.drop(["File_Pairs"], axis=1, inplace=True)
            # sort merged dataframe by highest count_POS_src
            merged_df = merged_df.sort_values(
                by=['Count_Alignment', 'Count_POS_src', 'Count_POS_trg'],
                ascending=[False, False, False])
            # reduce duplicates
            merged_df.drop_duplicates(keep='first', inplace=True)
            # merge final dataframe with file data
            all_data = pd.merge(merged_df, files, on=[f'Match {l1}',
                                                      f'Match {l2}'],
                                how='left')
            # add column with Regex
            all_data['Regex'] = self.__regex
            # drop columns for POS count
            all_data = all_data.drop(["Count_POS_src", "Count_POS_trg"], axis=1)
            if self.__src_aggregate:
                # Safely evaluate the string representations of lists back into actual lists
                all_data["POS_src"] = all_data["POS_src"].apply(ast.literal_eval)

                all_data["Lemma_src"] = all_data["Lemma_src"].apply(ast.literal_eval)

                all_data["Token_src"] = all_data["Token_src"].apply(ast.literal_eval)
                # Explode the lists
                exploded = all_data.explode(["POS_src", "Lemma_src", "Token_src"])
                # remove duplicates for count alignments
                exploded = exploded.drop_duplicates(subset=[f'Match {l1}', f'Match {l2}', 'Count_Alignment'])
                # write data to csv
                exploded.to_csv(path)
            else:
                # remove duplicates for count alignments
                all_data = all_data.drop_duplicates(subset=[f'Match {l1}', f'Match {l2}', 'Count_Alignment'])
                # write data to csv
                all_data.to_csv(path)
        return path


# regexframe = \b(?:Comment|Mais comment)\s(?:[^.?!]+[.?!])


if __name__ == "__main__":
    bilingual = BilingualStats(path="../data/generated/alignments_en_fr_1000_parsed.txt",
                               regex=r'the\s', src_aggregate=True, parsed=True, caseinsensitive=False)
    bilingual.write_bilingual_stats(l1="French", l2="English",
                                    root_path="../data/search_results/")
