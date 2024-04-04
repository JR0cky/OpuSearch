import re
import pandas as pd
from collections import defaultdict
from model.processing import Processing


# TODO check counts of results for monolingual context and stats
class MonolingualStats:
    """Get monolingual matches from corresponding regex and
       write them to a csv-file
    """

    def __init__(self, path, regex, src=True, parsed=False, caseinsensitive=False):
        self.__path = path
        self.__regex = regex
        self.__src_pattern = r'\(src\)="[0-9]+">'
        self.__trg_pattern = r'\(trg\)="[0-9]+">'
        self.__src = src
        self.__parsed = parsed
        self.__caseinsensitive = caseinsensitive
        if self.__src:
            # set src pattern to search ID in alignments' values
            self.__current_pattern_ID = self.__src_pattern
        else:
            # set trg pattern to search ID in alignments' values
            self.__current_pattern_ID = self.__trg_pattern
        # other routine for unparsed data
        if not self.__parsed:
            self.__matches, self.__files = \
                Processing.perform_new_search(
                    self.__path,
                    self.__regex,
                    stats=False,
                    unparsed_stats_context=True,
                    mono=True,
                    mono_pattern=self.__current_pattern_ID,
                    caseinsensitive=self.__caseinsensitive
                )
            self.__process_counts_unparsed()
        else:
            self.__POS = []
            self.__lemma = []
            self.__token = []
            self.__counts = {}
            self.__sets_files = []
            # get data
            self.__parsed_dict, self.__matches, self.__files = \
                Processing.perform_new_search(
                    self.__path,
                    self.__regex,
                    stats=True,
                    mono=True,
                    mono_pattern=self.__current_pattern_ID,
                    caseinsensitive=self.__caseinsensitive
                )
            # run processing for monolingual matches
            self.__process_counts()

    def __process_counts_unparsed(self):
        # remove annotation
        self.__matches = Processing.remove_annotation(self.__matches,
                                                      nested=False)
        # get counts for (unique) matches
        self.__counts_unparsed = Processing.get_counts(self.__matches)

    def __process_counts(self):
        self.__counts = defaultdict(dict)
        if self.__matches:
            # remove annotation for aggregation
            self.__matches_clean = Processing.remove_annotation(self.__matches,
                                                                nested=False)
            # Iterate through each match
            for i, match in enumerate(self.__matches):
                token = []
                POS = []
                lemma = []
                # get file key
                match_key = self.__files[i]
                # get values of file key (second level)
                match_data = self.__parsed_dict.get(match_key, {})
                # go through alignments and lines indicated by IDs
                for alignment, lines in match_data.items():
                    # get ID of match to match it with the one in the alignment
                    match_ID = re.search(self.__current_pattern_ID, match)
                    if match_ID is None:
                        continue
                    match_ID = match_ID.group()
                    if match_ID in alignment:
                        # get identifier of match
                        match_pattern = re.search(self.__current_pattern_ID,
                                                  match)
                        # if ID was found among values
                        if match_pattern:
                            # single out ID in match
                            ID = match_pattern.group(0)
                            token.append(lines[ID]["string"])
                            POS.append(lines[ID]["POS"])
                            lemma.append(lines[ID]["lemma"])
                # Get file pairs that belong to the particular alignment
                self.__sets_files.append([match_key])
                # clean the match out of the annotation
                match = re.sub(self.__current_pattern_ID, "", match)

                # Update the dictionary with metadata
                self.__counts[str(i)].update({
                    'match': match,
                    'POS': POS,
                    'lemma': lemma,
                    'token': token,
                })
        else:
            pass

    def get_counts(self):
        if self.__parsed:
            return len(self.__counts)
        else:
            return len(self.__counts_unparsed)

    def write_monolingual_stats(self, lang, path=None, root_path=None):
        """ Write monolingual matches with counts to file

        @param path: path file path to be set
        @param lang: language that is searched
        @param root_path: file path for root to be set
        @return: file path
        """
        if path is None:
            path = Processing.automate_path_statistics(regex=self.__regex,
                                                       l1=lang,
                                                       root_path=root_path)
        # handle case for unparsed data
        if not self.__parsed:
            Processing.write_statistics_to_file(path, self.__regex, self.__counts_unparsed,
                                                self.__files, l1=lang)
        else:
            df = pd.DataFrame.from_dict(self.__counts,
                                        orient='index').reset_index()
            df.columns = ['Number', f'Match {lang.strip()}',
                          'POS', 'Lemma', 'Token']
            # drop artificial index column
            df = df.drop("Number", axis=1)
            # make everything hashable
            df = df.astype(str)
            # get counts
            count = df[[f'Match {lang}']].value_counts().reset_index(
                name='Count_Match')
            count_POS = df[[f'Match {lang}',
                            'POS']].value_counts().reset_index(
                name='Count_POS')
            # handle files
            df['File_Pairs'] = self.__sets_files
            files = df.groupby([f'Match {lang}'])['File_Pairs'].agg(
                list).reset_index()
            # flatten lists if necessary
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: Processing.is_nested(x))
            # make set to get unique file pairs
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: set(x))
            # get count of file pairs
            files['File_Count'] = files['File_Pairs'].apply(lambda x: len(x))
            # merge original dataframe and counts for src and trg combinations
            merged_df = pd.merge(df, count, on=[f'Match {lang}'],
                                 how='left')
            # merge original dataframe and counts for POS_src
            merged_df = pd.merge(merged_df, count_POS,
                                 on=[f'Match {lang}', 'POS'],
                                 how='left')
            # drop left over index column
            merged_df.drop(["File_Pairs"], axis=1, inplace=True)
            # sort merged dataframe by highest count_POS_src
            merged_df = merged_df.sort_values(
                by=['Count_Match', 'Count_POS'],
                ascending=[False, False])
            # reduce duplicates
            merged_df.drop_duplicates(keep='first', inplace=True)
            # merge final dataframe with file data
            all_data = pd.merge(merged_df, files,
                                on=[f'Match {lang}'],
                                how='left')
            # add column with Regex
            all_data['Regex'] = self.__regex
            # flatten lists
            all_data["POS"] = all_data["POS"].apply(lambda x: eval(x))
            all_data["Lemma"] = all_data["Lemma"].apply(lambda x: eval(x))
            all_data["Token"] = all_data["Token"].apply(lambda x: eval(x))
            exploded = all_data.explode(["POS", "Lemma", "Token"])
            # write data to csv
            exploded.to_csv(path)
        return path


if __name__ == "__main__":
    mono_matches = MonolingualStats(
        path="../data/generated/alignments_fr_es_500_parsed.txt",
        regex=r"Comment",
        src=True,
        parsed=True,
        caseinsensitive=True
    )
    counts = mono_matches.get_counts()
    if counts:
        mono_matches.write_monolingual_stats(lang="French", root_path="../data/search_results/")
    else:
        print("no results")
