from pathlib import Path
import plac
import spacy
from spacy.tokens import DocBin
import srsly
import sys


@plac.annotations(
    model=("Model name. Defaults to 'en'.", "option", "m", str),
    input_file=("Input file (jsonl)", "positional", None, Path),
    output_dir=("Output directory", "positional", None, Path),
    n_texts=("Number of texts to convert", "option", "t", int),
)
def convert(model="en", input_file=None, output_dir=None, n_texts=0):
    # Load model with tokenizer + sentencizer only
    try:
        nlp = spacy.load(model)
    except OSError:
        print(f"Model '{model}' not found. Please download the model using: python -m spacy download {model}")
        sys.exit(1)
        
    nlp.select_pipes(disable=[pipe for pipe in nlp.pipe_names if pipe != "sentencizer"])
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer", first=True)
    
    # AI-driven feature: Efficient batch processing for large datasets
    texts = []
    cats = []
    count = 0

    if not input_file.exists():
        print("Input file not found:", input_file)
        sys.exit(1)
    else:
        with open(input_file) as fileh:
            for line in fileh:
                data = srsly.json_loads(line)
                texts.append(data.get("text", ""))
                cats.append(data.get("cats", {}))

    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(".")

    # AI-driven feature: Optimize memory usage with DocBin
    doc_bin = DocBin(store_user_data=True)

    for i, doc in enumerate(nlp.pipe(texts, batch_size=100)):
        doc.cats = cats[i]
        doc_bin.add(doc)
        if n_texts > 0 and count == n_texts:
            break
        count += 1

    output_path = output_dir / input_file.with_suffix(".spacy")
    doc_bin.to_disk(output_path)

    print(f"Conversion complete. Output saved to {output_path}")

if __name__ == "__main__":
    plac.call(convert)
