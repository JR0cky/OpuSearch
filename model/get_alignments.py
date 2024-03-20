import os
import sys
import opustools


def prepare_alignments(source_path, gen_path, src, trg, limit, parsed=False, time_stamps=False):
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
        download_dir=source_path,
        src_range="1-2",
        tgt_range="1-2",
        preprocess=preprocess,
        write=[os.path.join(gen_path, f'alignments_{src}_{trg}_{limit}_normal.txt') if parsed is False
               else os.path.join(gen_path, f'alignments_{src}_{trg}_{limit}_parsed.txt')],
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
    if len(sys.argv) != 7:
        print("Usage: python your_script.py source_dir generated_dir lang1 lang2 max_length")
        sys.exit(1)
    source_path = sys.argv[1]
    gen_path = sys.argv[2]
    lang1 = sys.argv[3]
    lang2 = sys.argv[4]
    max_length = int(sys.argv[5])
    parsed = sys.argv[6]
    parsed = False if parsed == "normal" else True
    # Call the function with the parsed arguments
    prepare_alignments(source_path=source_path, gen_path=gen_path, src=lang1, trg=lang2, limit=max_length,
                       parsed=parsed)


if __name__ == '__main__':
    # prepare_alignments("D:/", "D:/gen_files", "fr", "es", 50, parsed=True)
    main()
