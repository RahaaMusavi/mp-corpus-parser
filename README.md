# mp-corpus-parser
A Python toolkit for converting and parsing Middle Persian corpus from Export files of the mpcorpus.org to CoNLL-U format
# Pahlavi Corpus Parser

A Python toolkit for converting and parsing a specific Pahlavi language corpus from source CSV/TSV files into a memory-loaded, object-oriented format suitable for linguistic analysis.

This project was developed to standardize a varied corpus format into a clean, searchable CoNLL-U structure.

## Features

* Converts source CSV and TSV files into the standard CoNLL-U format.
* Handles common encoding issues and sanitizes data fields during conversion.
* Parses the clean CoNLL-U files into a list of Python `Sentence` and `Token` objects.
* Provides a simple, high-level function to run the entire pipeline.

## Requirements

* Python 3.x
* The required Python libraries are listed in `requirements.txt`. You can install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

The primary tool is the `parse_corpus` function within the `corpus_parser.py` module. Place the module in your project directory and import it into a script or Jupyter Notebook.

```python
import corpus_parser as mpc

# 1. Configure your folder paths
input_folder = r"PATH_TO_YOUR_SOURCE_CSV_FILES"
output_folder = r"PATH_TO_WHERE_CONLLU_FILES_WILL_BE_SAVED"

# 2. Run the entire pipeline with one command
# This will convert the files and load them into memory.
my_corpus = mpc.parse_corpus(input_folder, output_folder)

# 'my_corpus' is now a list of Sentence objects ready for analysis.
print(f"Successfully parsed the corpus. Found {len(my_corpus)} sentences.")

# Example: Accessing the first sentence and its tokens
if my_corpus:
    first_sentence = my_corpus[0]
    print(f"\nExample Sentence ID: {first_sentence.sentence_id}")
    tokens = [token.form for token in first_sentence.get_tokens()]
    print(f"Tokens: {' '.join(tokens)}")
```

An example of how to use this toolkit for analysis can be found in the `notebooks/example_usage.ipynb` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
