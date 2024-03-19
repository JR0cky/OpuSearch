import os
import sys
import opustools

# TODO edit path logic to handle external paths for generated and source files


def prepare_alignments(src, trg, limit, parsed=False, time_stamps=False):
    # Get the absolute path of the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up one directory to access the 'data' directory
    data_dir = os.path.abspath(os.path.join(script_dir, os.pardir, "data"))
    # Path for the download directory
    download_dir = os.path.join(data_dir, "source_files")
    # Path for writing alignment files
    write_dir = os.path.join(data_dir, "generated")
    # Set parameter for time stamps to be included
    stamp = True if time_stamps else False
    # Set parameters according to option "parsed"
    anno = False if parsed is False else True
    def_anno = ['upos', 'lemma'] if parsed else [""]
    delimiter = " " if parsed is False else "_#"
    preprocess = "parsed" if parsed else "xml"
    opus_reader = opustools.OpusRead(
        directory='OpenSubtitles',
        source=src,
        target=trg,
        maximum=limit,
        download_dir=download_dir,
        src_range="1-2",
        tgt_range="1-2",
        preprocess=preprocess,
        write=[os.path.join(write_dir, f'alignments_{src}_{trg}_{limit}_normal.txt') if parsed is False
               else os.path.join(write_dir, f'alignments_{src}_{trg}_{limit}_parsed.txt')],
        write_mode='normal',  # moses , tmx
        leave_non_alignments_out=True,
        print_annotations=anno,
        source_annotations=def_anno,
        target_annotations=def_anno,
        verbose=True,
        change_annotation_delimiter=delimiter,
        suppress_prompts=False,
        preserve_inline_tags=stamp
    )
    opus_reader.printPairs()


def main():
    # Parse command-line arguments
    if len(sys.argv) != 5:
        print("Usage: python your_script.py source_dir generated_dir lang1 lang2 max_length")
        sys.exit(1)
    lang1 = sys.argv[1]
    lang2 = sys.argv[2]
    max_length = int(sys.argv[3])
    parsed = sys.argv[4]
    parsed = False if parsed == "normal" else True
    # check parameters for source_files and target to see if they exist in parsed format
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    # parent = os.path.dirname(current_directory)
    # lang_parse = pd.read_csv(os.path.join(parent, "data", "source_files", "languages_parsed.csv"))
    # if (lang_parse["code"] == lang1).any() and (lang_parse["code"] == lang2).any():
    #     parsed = True
    # else:
    #     parsed = False
    # Call the function with the parsed arguments
    prepare_alignments(src=lang1, trg=lang2, limit=max_length,
                       parsed=parsed)


if __name__ == '__main__':
    #prepare_alignments("fr", "es", 50, parsed=True)
    main()
