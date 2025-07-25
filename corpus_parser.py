# corpus_parser.py

"""
A reusable Python module for converting and parsing a Pahlavi language corpus.
This script contains all the necessary functions to go from source CSV/TSV files
to a list of processed Sentence objects in memory, with full support for all
10 standard CoNLL-U fields.

Author: [Your Name/Organization Name]
Version: 1.1
Last Updated: [Date]
"""

import os
import pandas as pd
from tqdm.notebook import tqdm
from conllu import parse
from conllu.parser import DEFAULT_FIELD_PARSERS

# --- Class Definitions ---

class Token:
    """
    Represents a single token (word) in a sentence, corresponding to one line
    in a CoNLL-U file. This class now holds all 10 standard CoNLL-U fields.
    """
    def __init__(self, token_data):
        # 1. ID: Word index, integer (starting at 1 for each new sentence).
        try:
            original_id = token_data.get('id')
            self.id = int(float(original_id)) if original_id is not None else None
        except (ValueError, TypeError):
            self.id = token_data.get('id') # Fallback for non-integer IDs (e.g., ranges)

        # 2. FORM: Word form or punctuation.
        self.form = token_data.get('form')

        # 3. LEMMA: Lemma or stem of the word.
        self.lemma = token_data.get('lemma')

        # 4. UPOS: Universal Part-of-Speech tag.
        self.upos = token_data.get('upos')

        # 5. XPOS: Language-specific Part-of-Speech tag. (Can be None)
        self.xpos = token_data.get('xpos')

        # 6. FEATS: List of morphological features from the universal feature inventory.
        self.feats = token_data.get('feats')

        # 7. HEAD: Head of the current word, which is either a value of ID or zero (0).
        try:
            original_head = token_data.get('head')
            self.head = int(float(original_head)) if original_head is not None else None
        except (ValueError, TypeError):
            self.head = token_data.get('head') # Fallback

        # 8. DEPREL: Universal dependency relation to the HEAD.
        self.deprel = token_data.get('deprel')

        # 9. DEPS: Enhanced dependency graph in the form of a list of head-deprel pairs.
        self.deps = token_data.get('deps')

        # 10. MISC: Any other annotation.
        self.misc = token_data.get('misc')

class Sentence:
    """A class to hold a sentence, which is a list of Token objects."""
    def __init__(self, sentence_token_list, source_filename):
        self.metadata = sentence_token_list.metadata
        self.sentence_id = self.metadata.get('sent_id')
        self.file_name = source_filename
        self._tokens = [Token(t) for t in sentence_token_list]

    def get_tokens(self):
        return self._tokens

# --- Internal Helper Functions ---

def _convert_csv_to_conllu(csv_file_path, output_dir):
    """
    (Internal function) Reads a single CSV/TSV file and converts it to CoNLL-U.
    Strictly requires the source file to be UTF-8.
    """
    def _sanitize_field(text):
        if text is None: return "_"
        s = str(text).replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')
        return s.strip() if s.strip() else "_"

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            sample = f.read(2048)
            sep = '\t' if sample.count('\t') >= sample.count(',') else ','
        df = pd.read_csv(csv_file_path, sep=sep, keep_default_na=False, engine='python', dtype=str, encoding='utf-8')
        base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        output_file_path = os.path.join(output_dir, f"{base_name}.conllu")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            current_sentence_tokens = []
            sentence_id_counter = 1
            for index, row in df.iterrows():
                id_val = str(row.get('id', '')).strip()
                lemma_val = str(row.get('lemma', '')).strip()
                is_sentence_boundary = (id_val in ['', '_']) and (lemma_val in ['', '_'])
                if is_sentence_boundary:
                    if current_sentence_tokens:
                        f.write(f"# sent_id = {sentence_id_counter}\n")
                        f.write("# text = " + " ".join(token[1] for token in current_sentence_tokens) + "\n")
                        for token_line in current_sentence_tokens: f.write("\t".join(token_line) + "\n")
                        f.write("\n")
                        sentence_id_counter += 1
                        current_sentence_tokens = []
                else:
                    # Maps your source CSV columns to the 10 standard CoNLL-U columns
                    conllu_token = [
                        _sanitize_field(row.get('id', '_')),           # 1. ID
                        _sanitize_field(row.get('transcription', '_')),# 2. FORM
                        _sanitize_field(row.get('lemma', '_')),        # 3. LEMMA
                        _sanitize_field(row.get('postag', '_')),       # 4. UPOS
                        "_",                                           # 5. XPOS (Placeholder)
                        _sanitize_field(row.get('postfeatures', '_')), # 6. FEATS
                        _sanitize_field(row.get('head', '_')),         # 7. HEAD
                        _sanitize_field(row.get('deprel', '_')),       # 8. DEPREL
                        _sanitize_field(row.get('deps', '_')),         # 9. DEPS
                        _sanitize_field(row.get('meaning', '_'))       # 10. MISC
                    ]
                    current_sentence_tokens.append(conllu_token)
            if current_sentence_tokens:
                f.write(f"# sent_id = {sentence_id_counter}\n")
                f.write("# text = " + " ".join(token[1] for token in current_sentence_tokens) + "\n")
                for token_line in current_sentence_tokens: f.write("\t".join(token_line) + "\n")
                f.write("\n")
    except Exception as e:
        print(f"    - ERROR processing {os.path.basename(csv_file_path)}. Reason: {e}")

def _process_directory(input_dir, output_dir):
    """(Internal function) Scans and converts all files in a directory."""
    os.makedirs(output_dir, exist_ok=True)
    files_to_process = [f for f in os.listdir(input_dir) if f.lower().endswith(('.csv', '.tsv')) and not f.startswith('~$')]
    for filename in tqdm(files_to_process, desc="Converting source files"):
        file_path = os.path.join(input_dir, filename)
        _convert_csv_to_conllu(file_path, output_dir)
    print("\nSource file conversion complete!")

def _load_corpus_from_conllu(conllu_dir):
    """(Internal function) Loads all .conllu files from a directory into memory."""
    custom_field_parsers = DEFAULT_FIELD_PARSERS.copy()
    custom_field_parsers['id'] = lambda line, i: line[i]
    custom_field_parsers['head'] = lambda line, i: line[i]
    all_corpus_sentences_list = []
    conllu_files = [f for f in os.listdir(conllu_dir) if f.lower().endswith('.conllu')]
    for filename in tqdm(conllu_files, desc="Loading and Parsing CoNLL-U files"):
        file_path = os.path.join(conllu_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        lines = data.splitlines()
        clean_lines = [line for line in lines if line.startswith('#') or line.strip() == "" or line.count('\t') == 9]
        clean_data = "\n".join(clean_lines) + "\n"
        sentences_from_lib = parse(clean_data, field_parsers=custom_field_parsers)
        for lib_sentence in sentences_from_lib:
            new_sentence = Sentence(lib_sentence, source_filename=filename)
            all_corpus_sentences_list.append(new_sentence)
    print(f"\nSuccessfully loaded {len(all_corpus_sentences_list)} sentences.")
    return all_corpus_sentences_list

# --- Main Public Function ---

def parse_corpus(input_folder, output_folder):
    """
    The main function to run the entire corpus parsing pipeline.

    Args:
        input_folder (str): Path to the folder with source .csv/.tsv files.
        output_folder (str): Path to a folder where intermediate .conllu files will be saved.

    Returns:
        list: A list of Sentence objects representing the fully parsed corpus.
    """
    print("--- Starting Corpus Parsing Pipeline ---")
    print(f"Step 1: Converting files from '{input_folder}'")
    _process_directory(input_folder, output_folder)
    
    print(f"\nStep 2: Loading processed files from '{output_folder}'")
    corpus = _load_corpus_from_conllu(output_folder)
    
    print("\n--- Pipeline Complete ---")
    return corpus
