## Entity Linking with Wikipedia and Wikidata

### Step 1: Create a Knowledge Base (KB) and training data

Run  `wikipedia_pretrain_kb.py` 
* This takes as input the locations of a **Wikipedia and a Wikidata dump**, and produces a **KB directory** + **training file**
  * WikiData: get `latest-all.json.bz2` from https://dumps.wikimedia.org/wikidatawiki/entities/
  * Wikipedia: get `enwiki-latest-pages-articles-multistream.xml.bz2` from https://dumps.wikimedia.org/enwiki/latest/ (or for any other language)
* You can set the filtering parameters for KB construction:
  * `max_per_alias` (`-a`): (max) number of candidate entities in the KB per alias/synonym
  * `min_freq` (`-f`): threshold of number of times an entity should occur in the corpus to be included in the KB
  * `min_pair` (`-c`): threshold of number of times an entity+alias combination should occur in the corpus to be included in the KB
* Further parameters to set:
  * `descriptions_from_wikipedia` (`-wp`): whether to parse descriptions from Wikipedia (`True`) or Wikidata (`False`)
  * `entity_vector_length` (`-v`): length of the pre-trained entity description vectors
  * `lang` (`-la`): language for which to fetch Wikidata information (as the dump contains all languages)

Quick testing and rerunning: 
* When trying out the pipeline for a quick test, set `limit_prior` (`-lp`), `limit_train` (`-lt`) and/or `limit_wd` (`-lw`) to read only parts of the dumps instead of everything. 
  * e.g. set `-lt 20000 -lp 2000 -lw 3000 -f 1`
* If you only want to (re)run certain parts of the pipeline, just remove the corresponding files and they will be recalculated or reparsed.


### Step 2: Train an Entity Linking model

Run  `wikidata_train_entity_linker.py` 
* This takes the **KB directory** produced by Step 1, and trains an **Entity Linking model**
* Specify the output directory (`-o`) in which the final, trained model will be saved
* You can set the learning parameters for the EL training:
  * `epochs` (`-e`): number of training iterations
  * `dropout` (`-p`): dropout rate
  * `lr` (`-n`): learning rate
  * `l2` (`-r`): L2 regularization
* Specify the number of training and dev testing articles with `train_articles` (`-t`) and `dev_articles` (`-d`) respectively
  * If not specified, the full dataset will be processed - this may take a LONG time !
* Further parameters to set:
  * `labels_discard` (`-l`): NER label types to discard during training
