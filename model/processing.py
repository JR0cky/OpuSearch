import os.path
import re
import pandas as pd


class Preprocessing:
    """Preprocessing of bilingual alignments as output from Opus
       OpenSubtitles Corpus

    """

    def __init__(self, path):
        self.__path = path
        self.__limit = re.search(r'\d+', self.__path).group()
        self.__text_list = []
        self.__text_list_cleaned = []
        # call method to handle processing of raw text file
        self.__clean_data_anno()

    def __clean_data_anno(self):
        """Use json format if data has already been read from text file

        """
        with open(self.__path, "r", encoding="utf-8") as file_in:
            for line in file_in:
                self.__text_list.append(line.strip("\n"))
            # Define the regex pattern to match the annotations
            pattern = r'_#[^ ]*'
            # Use re.sub to replace matched patterns with a space
            self.__text_list_cleaned = [re.sub(pattern, '', line)
                                        for line in self.__text_list]

    def get_text_list(self):
        return self.__text_list_cleaned


class PreprocessingParsed:
    """Preprocessing of bilingual alignments as output from Opus
       OpenSubtitles Corpus
    """

    def __init__(self, path=None, files=None, indices=None, mono=False):
        self.__path = path
        self.__limit = re.search(r'\d+', self.__path).group()
        self.__files = files
        self.__indices = indices
        self.__mono = mono
        self.__metadata = {}
        # Call functions for processing
        self.__processing()

    def __read_alignments(self):
        with open(self.__path, "r", encoding="utf-8") as file_in:
            self.__lines = [line for line in file_in]

    def __process_mono_matches(self):
        self.__mono_matches = []
        self.__mono_matches_parsed = []
        for index in self.__indices:
            self.__mono_matches_parsed.append(self.__lines[index].strip("\n"))
            freed = " ".join(
                map(str, self.__split_string_meta([self.__lines[index]],
                                                  all_meta=False)))
            self.__mono_matches.append(freed)

    def __process_alignments(self):
        # initialise lists of segments
        self.__alignments_parsed = []
        self.__alignments = []
        # get segment for every match (nested list) based on indices of matches
        for index in self.__indices:
            pre = []  # initialize list for lines before match
            post = []  # initialize list for lines after match
            count_left = 0  # counter for going left
            count_right = 0  # counter for going right
            while True:
                try:
                    # check if separator left of match has been reached
                    current_left = self.__lines[index - count_left - 1]
                    if current_left.startswith("="):
                        break
                    else:
                        pre.insert(0, current_left.strip("\n"))
                        count_left += 1
                except IndexError:
                    break
            while True:
                try:
                    # check if separator right of match has been reached
                    current_right = self.__lines[index + count_right + 1]
                    if current_right.startswith("="):
                        break
                    post.append(current_right.strip("\n"))
                    count_right += 1
                except IndexError:
                    break
            # merge segments to one list
            # and append to (nested) list of segments
            self.__alignments_parsed.append(pre +
                                            [self.__lines[index].strip("\n")]
                                            + post)
            pre_free = [self.__split_string_meta(
                elem, all_meta=False) for elem in pre]
            post_free = [self.__split_string_meta(
                elem, all_meta=False) for elem in post]

            # Join the inner lists (tokens) for pre_free, line_element
            # and post_free without spaces
            joined_pre_free = [" ".join(map(str, inner_list))
                               for inner_list in pre_free]
            line_element = " ".join(
                map(str, self.__split_string_meta([self.__lines[index]],
                                                  all_meta=False)))
            joined_post_free = [" ".join(map(str, inner_list))
                                for inner_list in post_free]

            # Join the outer lists
            self.__alignments.append("".join(joined_pre_free) + " "
                                     + line_element + " "
                                     + "".join(joined_post_free))

    @staticmethod
    def __split_string_meta(text, all_meta=True):
        token = []
        # convert list entry to string
        text = "".join(text)
        # correct minor errors in pattern before accessing data
        # text = re.sub(" ~", "~", text)
        # text = re.sub("- ", "-", text)
        # text = re.sub(r'>-\s*(\S)', r'>-\1', text)
        # correct white spaces between numbers
        # text = re.sub(r'(\d) (\d)', r'\1.\2', text)
        # text = re.sub(r'_#\s+', '_#', text)
        # split at white space
        first_split = text.split()
        # split at delimiter to get metadata
        second_split = [elem.split("_#") for elem in first_split]
        # get original string, POS and lemma of every token
        try:
            token = [elem[0] for elem in second_split]
            POS = [elem[1] for elem in second_split]
            lemma = [elem[2] for elem in second_split]
        except IndexError:
            POS = ["X" for elem in second_split]
            lemma = [elem[0] for elem in second_split]
        if all_meta:
            return token, POS, lemma
        else:
            return token

    def __process_match(self, src_pattern=None, trg_pattern=None, entry=None,
                        current_level=None):
        if self.__mono:
            if entry.startswith("(src)"):
                src_match = re.search(src_pattern, entry)
                src_match = src_match.group()
                text = re.split(src_pattern, entry)
                src_token, src_POS, src_lemma = self.__split_string_meta(
                    text[1:])
                if src_match not in current_level:
                    current_level[src_match] = {"string": src_token,
                                                "POS": src_POS,
                                                "lemma": src_lemma}

            elif entry.startswith("(trg)"):
                trg_match = re.search(trg_pattern, entry)
                trg_match = trg_match.group()
                text = re.split(trg_pattern, entry)
                trg_token, trg_POS, trg_lemma = self.__split_string_meta(
                    text[1:])
                if trg_match not in current_level:
                    current_level[trg_match] = {"string": trg_token,
                                                "POS": trg_POS,
                                                "lemma": trg_lemma}
        else:
            for elem in entry:
                if elem.startswith("(src)"):
                    src_match = re.search(src_pattern, elem)
                    src_match = src_match.group()
                    text = re.split(src_pattern, elem)
                    src_token, src_POS, src_lemma = self.__split_string_meta(
                        text[1:])
                    if src_match not in current_level:
                        current_level[src_match] = {"string": src_token,
                                                    "POS": src_POS,
                                                    "lemma": src_lemma}

                elif elem.startswith("(trg)"):
                    trg_match = re.search(trg_pattern, elem)
                    trg_match = trg_match.group()
                    text = re.split(trg_pattern, elem)
                    trg_token, trg_POS, trg_lemma = self.__split_string_meta(
                        text[1:])
                    if trg_match not in current_level:
                        current_level[trg_match] = {"string": trg_token,
                                                    "POS": trg_POS,
                                                    "lemma": trg_lemma}

    @staticmethod
    def __create_key(key_list):
        # create string representation of list without brackets
        return ', '.join(map(str, key_list))

    def __parse_data_mono(self):
        src_pattern = re.compile(r'\(src\)="[0-9]+">')
        trg_pattern = re.compile(r'\(trg\)="[0-9]+">')
        self.__metadata = {}
        match_counter = 0
        current_alignment_key = None
        for file, match, match_parsed in zip(self.__files, self.__mono_matches,
                                             self.__mono_matches_parsed):
            try:
                current_level = self.__metadata
                current_level.setdefault(file, {})
                current_level = current_level[file]
                match_counter += 1
                if match_counter <= len(self.__mono_matches):
                    current_alignment_key = self.__mono_matches[
                        match_counter - 1]
                    # Use setdefault to initialize alignment level
                    current_level.setdefault(current_alignment_key, {})
                if current_alignment_key:
                    self.__process_match(src_pattern=src_pattern,
                                         trg_pattern=trg_pattern,
                                         entry=match_parsed,
                                         current_level=current_level[
                                             current_alignment_key])
            except IndexError:
                pass

    def __parse_data(self):
        src_pattern = re.compile(r'\(src\)="[0-9]+">')
        trg_pattern = re.compile(r'\(trg\)="[0-9]+">')
        self.__metadata = {}
        alignment_counter = 0
        current_alignment_key = None
        for file, alignment, alignment_parsed in zip(self.__files,
                                                     self.__alignments,
                                                     self.__alignments_parsed):
            try:
                current_level = self.__metadata
                current_level.setdefault(file, {})
                current_level = current_level[file]
                alignment_counter += 1
                if alignment_counter <= len(self.__alignments):
                    current_alignment_key = self.__alignments[
                        alignment_counter - 1]
                    # Use setdefault to initialize alignment level
                    current_level.setdefault(current_alignment_key, {})
                if current_alignment_key:
                    self.__process_match(src_pattern, trg_pattern,
                                         alignment_parsed,
                                         current_level[current_alignment_key])
            except IndexError:
                pass

    def __processing(self):
        # do the processing
        self.__read_alignments()
        if not self.__mono:
            self.__process_alignments()
            self.__parse_data()
        else:
            self.__process_mono_matches()
            self.__parse_data_mono()

    def get_dictionary(self):
        return self.__metadata


class Processing:
    """Processing of preprocessed data from Opus
       OpenSubtitles Corpus

    """

    @staticmethod
    def get_matches_index_files(text_list, regex, src_pattern, caseinsensitive=False):
        """Extract matches, corresponding files, and their indices in text list
        @return:
        """
        matches = []
        files = []
        matches_index = []
        for index, item in enumerate(text_list):
            # only append if match has been found
            if re.search(regex, item, flags=re.IGNORECASE if caseinsensitive else 0) and src_pattern.match(item):
                matches.append(item.strip("\n"))
                matches_index.append(index)
                # Search to the left for entries starting with '#'
                left_entries = []
                for left_index in range(index - 1, -1, -1):
                    if text_list[left_index].startswith("#"):
                        left_entries.append(text_list[left_index])
                        left_entries.append(text_list[left_index - 1])
                        break
                    else:
                        continue
                # remove line breaks from files
                # left_entries = [elem.strip("\n") for elem in left_entries]
                files.append(", ".join(reversed(left_entries)))
        return matches, matches_index, files

    @staticmethod
    def perform_new_search(path, regex, stats=True, mono=False, unparsed_stats_context=False,
                           mono_pattern=None, caseinsensitive=False):
        # get text list
        text_list = Preprocessing(path).get_text_list()
        # compile patterns for src and files
        pattern = re.compile(mono_pattern)
        file_pattern = re.compile(r'^# [a-z]{2}/\d+/\d+/\d+\.xml\.gz$')
        # monolingual mode
        if mono:
            text_list_mono = [s for s in text_list if
                              pattern.match(s) or file_pattern.match(s)]
            matches, indices, files = Processing.get_matches_index_files(
                text_list, regex, pattern, caseinsensitive=caseinsensitive)
            # monolingual statistics unparsed
            if unparsed_stats_context:
                return matches, files
            # monolingual statistics parsed
            if stats:
                # monolingual mode with stats, process and return dictionary
                parsed_dict = PreprocessingParsed(path, files, indices,
                                                  mono=True
                                                  ).get_dictionary()
                return parsed_dict, matches, files
            else:
                # mono mode without stats (context)
                matches, indices, files = Processing.get_matches_index_files(
                    text_list_mono, regex, pattern, caseinsensitive=caseinsensitive)
                return text_list_mono, matches, indices, files
        else:
            # Bilingual mode
            matches_l1, indices, files = Processing.get_matches_index_files(
                text_list, regex, pattern, caseinsensitive=caseinsensitive)
            # unparsed bilingual statistics and context
            if unparsed_stats_context:
                return text_list, matches_l1, indices, files
            # parsed bilingual statistics
            if stats:
                # For bilingual mode with stats process and return dictionary
                parsed_dict = PreprocessingParsed(path,
                                                  files,
                                                  indices).get_dictionary()
                return parsed_dict, matches_l1, files

    @staticmethod
    def remove_annotation(data, nested=True):
        """ Remove annotation from data

        @param data: list of matches
        @param nested: check whether data is a flat list or nested list
        @return: list with elements cleaned annotation
        """
        # remove "src" and "trg" annotation including numbers
        if nested:
            data = [[re.sub(r'\([a-z]{3}\)="[0-9]+">', '', item)
                     for item in elem] for elem in data]
        else:
            data = [re.sub(r'\([a-z]{3}\)="[0-9]+">', '', item)
                    for item in data]
        return data

    @staticmethod
    def remove_punctuation(data, punct_marks, nested=True):
        """ Remove punctuation from data

        @param data: list of matches
        @param punct_marks: characters to be excluded from the results
        @param nested: check whether data is monolingual or bilingual
        @return: list with elements cleaned from punctuation
        """
        # create pattern out of given string
        pattern = f"[{punct_marks}]"
        # replace given chars in list of pairs and remove redundant white space
        if nested:
            data = [[re.sub(pattern, "", item).strip() for item in pair]
                    for pair in data]
        else:
            data = [re.sub(pattern, "", item).strip() for item in data]
        return data

    @staticmethod
    def trim_translation(to_trim, span):
        """ Trim strings according to given span
            including nested data (1st level)

        @param to_trim: strings or lists with strings to be trimmed
        @param span: number of tokens to be kept
        @return: data with trimmed strings
        """
        result = []
        for elem in to_trim:
            # check whether element is a string
            if isinstance(elem, str):
                trimmed = " ".join(elem.split()[0:span])
                result.append(trimmed)
            # check whether element is a list
            if isinstance(elem, list):
                joined = " ".join(elem)
                trimmed = " ".join(joined.split()[0:span])
                result.append(trimmed)
        return result

    @staticmethod
    def get_counts(data_list):
        counts_dict = {}
        for elem in data_list:
            if elem in counts_dict:
                counts_dict[elem] += 1
            else:
                counts_dict[elem] = 1
        return counts_dict

    @staticmethod
    def automate_path_statistics(regex, l1=None, l2=None, root_path=None):
        regex_path = regex
        if not regex_path.isalpha():
            regex_path = re.sub(r'[^\w\s]', '', regex_path)

        # handle writing for bilingual files
        if l1 is not None and l2 is not None:
            path = f"bilingual_statistics_{str(l1)}_{str(l2)}_" \
                   f"{regex_path.replace(' ', '_')}.csv"
            path = os.path.join(root_path, path)
        # handle writing for monolingual files
        else:
            path = f"monolingual_statistics_{str(l1)}_" \
                   f"{regex_path.replace(' ', '_')}.csv"
            path = os.path.join(root_path, path)
        return path

    @staticmethod
    def automate_path_context(regex, l1=None, l2=None,
                              pre_con=None, post_con=None,
                              mono=True, qual=True, root_path=None):
        if qual:
            extension = ".txt"
        else:
            extension = ".csv"
        regex_path = regex
        lang_param = "monolingual_context" if mono \
            else "bilingual_context"
        if not regex_path.isalpha():
            regex_path = re.sub(r'[^\w\s]', '', regex_path)
        if mono:
            path = f"{lang_param}_{l1}_" \
                   f"{regex_path.replace(' ', '_')}_" \
                   f"pre_context{str(pre_con)}_" \
                   f"post_context{str(post_con)}{extension}"
            path = os.path.join(root_path, path)
        else:
            path = f"{lang_param}_" \
                   f"{str(l1)}_{str(l2)}_" \
                   f"{regex_path.replace(' ', '_')}_" \
                   f"pre_context{str(pre_con)}_" \
                   f"post_context{str(post_con)}{extension}"
            path = os.path.join(root_path, path)
        return path

    @staticmethod
    def is_nested(lst):
        """
        Function to check if a list is nested (1 level) and flatten it if it is.
        """

        def flatten_if_nested(lst):
            """
            Inner function to flatten a list if it's nested.
            """
            if any(isinstance(item, list) for item in lst):
                return sum(lst, [])
            else:
                return lst

        return flatten_if_nested(lst)

    @staticmethod
    def filter_alignment(data, src=True):
        """ Get the lines for source_files language only

        @return: data (lines) filtered by source_files
        """
        if src:
            data = [elem for elem in data if elem.startswith("(src)")]
        else:
            data = [elem for elem in data if elem.startswith("(trg)")]
        return data

    @staticmethod
    def write_statistics_to_file(path, regex, counts_dict, files, l1=None, l2=None):
        """ Write dictionary with translation pairs to given path

        @param path: filename or path
        @param regex: regular expression given by user
        @param files: file in which each match occurs
        @param l1: source_files language
        @param l2: target language
        @param counts_dict: dictionary with counts of occurrences for matches
        """

        # get number of occurrences
        num = counts_dict.values()
        # get list of regex expression
        regex_list = [regex for elem in counts_dict]
        # check whether language pair was given
        if l1 is not None and l2 is not None:
            # get samples for source_files language
            source = [elem[0] for elem in counts_dict.keys()]
            # get samples for target language
            target = [elem[1] for elem in counts_dict.keys()]
            # store results in dataframe (bilingual)
            df = pd.DataFrame(list(zip(source, target, num, files, regex_list)),
                              columns=[f'Match {l1}', f'Match {l2}', "Count_Alignment", "File_Pairs", "Regex"])
            # handle aggregation of files
            files = df.groupby([f'Match {l1}',
                                f'Match {l2}'])['File_Pairs'].agg(list).reset_index()
            # flatten lists if necessary
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: Processing.is_nested(x))
            # make set to get unique file pairs
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: set(x))
            # get count of file pairs
            files['File_Count'] = files['File_Pairs'].apply(lambda x: len(x))
            # drop left over index column
            df.drop(["File_Pairs"], axis=1, inplace=True)
            df = pd.merge(df, files, on=[f'Match {l1}', f'Match {l2}'], how='left')
        else:
            # get matches for one language
            matches = [elem for elem in counts_dict.keys()]
            # store results in dataframe (monolingual)
            df = pd.DataFrame(list(zip(matches, num, files, regex_list)),
                              columns=[f'Match {l1}', "Count_Match", "File_Pairs", "Regex"])
            # handle aggregation of files
            files = df.groupby(f'Match {l1}')['File_Pairs'].agg(list).reset_index()
            # flatten lists if necessary
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: Processing.is_nested(x))
            # make set to get unique file pairs
            files['File_Pairs'] = files['File_Pairs'].apply(lambda x: set(x))
            # get count of file pairs
            files['File_Count'] = files['File_Pairs'].apply(lambda x: len(x))
            # drop left over index column
            df.drop(["File_Pairs"], axis=1, inplace=True)
            df = pd.merge(df, files, on=[f'Match {l1}'], how='left')
        # write dataframe to csv
        df.to_csv(path, encoding="utf-8")
