## Entity Linking with Wikipedia and Wikidata

### Step 1: Create a Knowledge Base (KB) and training data

Run  `wikipedia_pretrain_kb.py` 
* This takes as input the locations of a **Wikipedia and a Wikidata dump**, and produces a **KB directory** + **training file**
  * WikiData: get `latest-all.json.bz2` from https://dumps.wikimedia.org/wikidatawiki/entities/
  * Wikipedia: get `enwiki-latest-pages-articles-multistream.xml.bz2` from https://dumps.wikimedia.org/enwiki/latest/ (or for any other language)
* You can set the filtering parameters for KB construction:
  * `max_per_alias`: (max) number of candidate entities in the KB per alias/synonym
  * `min_freq`: threshold of number of times an entity should occur in the corpus to be included in the KB
  * `min_pair`: threshold of number of times an entity+alias combination should occur in the corpus to be included in the KB
* Further parameters to set:
  * `descriptions_from_wikipedia`: whether to parse descriptions from Wikipedia (`True`) or Wikidata (`False`)
  * `entity_vector_length`: length of the pre-trained entity description vectors
  * `lang`: language for which to fetch Wikidata information (as the dump contains all languages)

Quick testing and rerunning: 
* When trying out the pipeline for a quick test, set `limit_prior`, `limit_train` and/or `limit_wd` to read only parts of the dumps instead of everything. 
* If you only want to (re)run certain parts of the pipeline, just remove the corresponding files and they will be recalculated or reparsed.


### Step 2: Train an Entity Linking model

Run  `wikidata_train_entity_linker.py` 
* This takes the **KB directory** produced by Step 1, and trains an **Entity Linking model**
* You can set the learning parameters for the EL training:
  * `epochs`: number of training iterations
  * `dropout`: dropout rate
  * `lr`: learning rate
  * `l2`: L2 regularization
* Specify the number of training and dev testing entities with `train_inst` and `dev_inst` respectively
* Further parameters to set:
  * `labels_discard`: NER label types to discard during training
