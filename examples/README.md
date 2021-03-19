<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy examples

For spaCy v3 we've converted many of the [v2 example
scripts](https://github.com/explosion/spaCy/tree/v2.3.x/examples/) into
end-to-end [spacy projects](https://spacy.io/usage/projects) workflows. The
workflows include all the steps to go from data to packaged spaCy models.

## 🪐 Pipeline component demos

The simplest demos for training a single pipeline component are in the
[`pipelines`](https://github.com/explosion/projects/blob/v3/pipelines) category
including:

- [`pipelines/ner_demo`](https://github.com/explosion/projects/blob/v3/pipelines/ner_demo):
  Train a named entity recognizer
- [`pipelines/textcat_demo`](https://github.com/explosion/projects/blob/v3/pipelines/textcat_demo):
  Train a text classifier
- [`pipelines/parser_intent_demo`](https://github.com/explosion/projects/blob/v3/pipelines/parser_intent_demo):
  Train a dependency parser for custom semantics

## 🪐 Tutorials

The [`tutorials`](https://github.com/explosion/projects/blob/v3/tutorials)
category includes examples that work through specific NLP use cases end-to-end:

- [`tutorials/textcat_goemotions`](https://github.com/explosion/projects/blob/v3/tutorials/textcat_goemotions):
  Train a text classifier to categorize emotions in Reddit posts
- [`tutorials/nel_emerson`](https://github.com/explosion/projects/blob/v3/tutorials/nel_emerson):
  Use an entity linker to disambiguate mentions of the same name

Check out the [projects documentation](https://spacy.io/usage/projects) and
browse through the [available
projects](https://github.com/explosion/projects/)!

## 🚀 Get started with a demo project

The
[`pipelines/ner_demo`](https://github.com/explosion/projects/blob/v3/pipelines/ner_demo)
project converts the spaCy v2
[`train_ner.py`](https://github.com/explosion/spaCy/blob/v2.3.x/examples/training/train_ner.py)
demo script into a spaCy v3 project.

1. Clone the project:

   ```bash
   python -m spacy project clone pipelines/ner_demo
   ```

2. Install requirements and download any data assets:

   ```bash
   cd ner_demo
   python -m pip install -r requirements.txt
   python -m spacy project assets
   ```

3. Run the default workflow to convert, train and evaluate:

   ```bash
   python -m spacy project run all
   ```

   Sample output:

   ```none
   ℹ Running workflow 'all'
   
   ================================== convert ==================================
   Running command: /home/user/venv/bin/python scripts/convert.py en assets/train.json corpus/train.spacy
   Running command: /home/user/venv/bin/python scripts/convert.py en assets/dev.json corpus/dev.spacy
   
   =============================== create-config ===============================
   Running command: /home/user/venv/bin/python -m spacy init config --lang en --pipeline ner configs/config.cfg --force
   ℹ Generated config template specific for your use case
   - Language: en
   - Pipeline: ner
   - Optimize for: efficiency
   - Hardware: CPU
   - Transformer: None
   ✔ Auto-filled config with all values
   ✔ Saved config
   configs/config.cfg
   You can now add your data and train your pipeline:
   python -m spacy train config.cfg --paths.train ./train.spacy --paths.dev ./dev.spacy
   
   =================================== train ===================================
   Running command: /home/user/venv/bin/python -m spacy train configs/config.cfg --output training/ --paths.train corpus/train.spacy --paths.dev corpus/dev.spacy --training.eval_frequency 10 --training.max_steps 100 --gpu-id -1
   ℹ Using CPU
   
   =========================== Initializing pipeline ===========================
   [2021-03-11 19:34:59,101] [INFO] Set up nlp object from config
   [2021-03-11 19:34:59,109] [INFO] Pipeline: ['tok2vec', 'ner']
   [2021-03-11 19:34:59,113] [INFO] Created vocabulary
   [2021-03-11 19:34:59,113] [INFO] Finished initializing nlp object
   [2021-03-11 19:34:59,265] [INFO] Initialized pipeline components: ['tok2vec', 'ner']
   ✔ Initialized pipeline
   
   ============================= Training pipeline =============================
   ℹ Pipeline: ['tok2vec', 'ner']
   ℹ Initial learn rate: 0.001
   E    #       LOSS TOK2VEC  LOSS NER  ENTS_F  ENTS_P  ENTS_R  SCORE 
   ---  ------  ------------  --------  ------  ------  ------  ------
     0       0          0.00      7.90    0.00    0.00    0.00    0.00
    10      10          0.11     71.07    0.00    0.00    0.00    0.00
    20      20          0.65     22.44   50.00   50.00   50.00    0.50
    30      30          0.22      6.38   80.00   66.67  100.00    0.80
    40      40          0.00      0.00   80.00   66.67  100.00    0.80
    50      50          0.00      0.00   80.00   66.67  100.00    0.80
    60      60          0.00      0.00  100.00  100.00  100.00    1.00
    70      70          0.00      0.00  100.00  100.00  100.00    1.00
    80      80          0.00      0.00  100.00  100.00  100.00    1.00
    90      90          0.00      0.00  100.00  100.00  100.00    1.00
   100     100          0.00      0.00  100.00  100.00  100.00    1.00
   ✔ Saved pipeline to output directory
   training/model-last
   ```

4. Package the model:

   ```bash
   python -m spacy project run package
   ```

5. Visualize the model's output with [Streamlit](https://streamlit.io):

   ```bash
   python -m spacy project run visualize-model
   ```
