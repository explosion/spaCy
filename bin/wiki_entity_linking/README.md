## Entity Linking with Wikipedia and Wikidata

### Step 1: Create a Knowledge Base (KB)

Run  `wikipedia_pretrain_kb` 
* This takes as input the locations of a Wikipedia and Wikidata dump, and produces a KB directory + training filee
* When trying out the pipeline for a quick test, set `-l` to read only parts of the dumps instead of everything
* You can set the filtering parameters for KB construction:
** `max_per_alias`: (max) number of candidate entities in the KB per alias/synonym
** `min_freq`: threshold of number of times an entity should occur in the corpus to be included in the KB
** `min_pair`: threshold of number of times an entity+alias combination should occur in the corpus to be included in the KB
* Further parameters to set:
** `descriptions_from_wikipedia`: whether to parse descriptions from Wikipedia (`True`) or Wikidata (`False`)
** `entity_vector_length`: length of the pre-trained entity description vectors
** `lang`: language for which to fetch Wikidata information (as the dump contains all languages)
