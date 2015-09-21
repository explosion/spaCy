/*
  
  wnhelp.c 

*/

/* $Id: wnhelp.c,v 1.14 2005/02/01 17:03:46 wn Rel $ */

#include "wn.h"

#ifndef NULL
#define NULL	0
#endif

/* Help Strings */

static char freq_help[] =	/* FREQ */
"Display familiarity and polysemy information for the search string. \n\
The polysemy count is the number of senses in WordNet. \n\
";

static char grep_help[] =	/* WNGREP */
"Print all strings in the database containing the search string \n\
as an individual word, or as the first or last string in a word or \n\
collocation. \n\
";

static char coord_help[] =	/* COORDS */
"Display the coordinates (sisters) of the search string.  This search \n\
prints the immediate hypernym for each synset that contains the \n\
search string and the hypernym's immediate `hyponyms'. \n\
\n\
Hypernym is the generic term used to designate a whole class of \n\
specific instances.  Y is a hypernym of X if X is a (kind of) Y. \n\
\n\
Hyponym is the generic term used to designate a member of a class. \n\
X is a hyponym of Y if X is a (kind of) Y.  \n\
\n\
Coordinate words are words that have the same hypernym.\n\
\n\
Hypernym synsets are preceded by \"->\", and hyponym synsets are \n\
preceded by \"=>\". \n\
";

static char hyper_help[] =	/* HYPERPTR */
"Display synonyms and immediate hypernyms of synsets containing \n\
the search string.  Synsets are ordered by frequency of occurrence.  \n\
\n\
Hypernym is the generic term used to designate a whole class of \n\
specific instances.  Y is a hypernym of X if X is a (kind of) Y. \n\
\n\
Hypernym synsets are preceded by \"=>\". \n\
";

static char relatives_help[] =	/* RELATIVES */
"Display synonyms and immediate hypernyms of synsets containing \n\
the search string.  Synsets are grouped by similarity of meaning. \n\
\n\
Hypernym is the generic term used to designate a whole class of \n\
specific instances.  Y is a hypernym of X if X is a (kind of) Y. \n\
\n\
Hypernym synsets are preceded by \"=>\". \n\
";

static char ant_help[] =	/* ANTPTR */
"Display synsets containing direct anotnyms of the search string.  \n\
\n\
Direct antonyms are a pair of words between which there is an \n\
associative bond built up by co-occurrences. \n\
\n\
Antonym synsets are preceded by \"=>\". \n\
";

static char hypertree_help[] =	/* -HYPERPTR */
"Recursively display hypernym (superordinate) tree for the search \n\
string. \n\
\n\
Hypernym is the generic term used to designate a whole class of \n\
specific instances.  Y is a hypernym of X if X is a (kind of) Y. \n\
\n\
Hypernym synsets are preceded by \"=>\", and are indented from \n\
the left according to their level in the hierarchy. \n\
";

static char hypo_help[] =	/* HYPONYM */
"Display immediate hyponyms (subordinates) for the search string. \n\
\n\
Hyponym is the generic term used to designate a member of a class. \n\
X is a hyponym of Y if X is a (kind of) Y.  \n\
\n\
Hyponym synsets are preceded by \"=>\". \n\
";

static char hypotree_help[] =	/* -HYPONYM */
"Display hyponym (subordinate) tree for the search string.  This is \n\
a recursive search that finds the hyponyms of each hyponym.  \n\
\n\
Hyponym is the generic term used to designate a member of a class. \n\
X is a hyponym of Y if X is a (kind of) Y.  \n\
\n\
Hyponym synsets are preceded by \"=>\", and are indented from the left \n\
according to their level in the hierarchy. \n\
";

static char holo_help[] =	/* HOLONYM */
"Display all holonyms of the search string. \n\
\n\
A holonym is the name of the whole of which the 'meronym' names a part. \n\
Y is a holonym of X if X is a part of Y. \n\
\n\
A meronym is the name of a constituent part, the substance of, or a \n\
member of something.  X is a meronym of Y if X is a part of Y. \n\
\n\
Holonym synsets are preceded with either the string \"MEMBER OF\", \n\
\"PART OF\" or \"SUBSTANCE OF\" depending on the specific type of holonym. \n\
";

static char holotree_help[] =	/* -HOLONYM */
"Display holonyms for search string tree.  This is a recursive search \n\
that prints all the holonyms of the search string and all of the \n\
holonym's holonyms. \n\
\n\
A holonym is the name of the whole of which the meronym names a part. \n\
Y is a holonym of X if X is a part of Y. \n\
\n\
A meronym is the name of a constituent part, the substance of, or a \n\
member of something.  X is a meronym of Y if X is a part of Y. \n\
\n\
Holonym synsets are preceded with either the string \"MEMBER OF\", \n\
\"PART OF\" or \"SUBSTANCE OF\" depending on the specific \n\
type of holonym.  Synsets are indented from the left according to \n\
their level in the hierarchy. \n\
";

static char mero_help[] =	/* MERONYM */
"Display all meronyms of the search string.  \n\
\n\
A meronym is the name of a constituent part, the substance of, or a \n\
member of something.  X is a meronym of Y if X is a part of Y. \n\
\n\
A holonym is the name of the whole of which the meronym names a part. \n\
Y is a holonym of X if X is a part of Y. \n\
\n\
Meronym synsets are preceded with either the string \"HAS MEMBER\", \n\
\"HAS PART\" or \"HAS SUBSTANCE\" depending on the specific type of holonym. \n\
";

static char merotree_help[] =	/* -HMERONYM */
"Display meronyms for search string tree.  This is a recursive search \n\
the prints all the meronyms of the search string and all of its \n\
hypernyms.  \n\
\n\
A meronym is the name of a constituent part, the substance of, or a \n\
member of something.  X is a meronym of Y if X is a part of Y. \n\
\n\
A holonym is the name of the whole of which the meronym names a part. \n\
Y is a holonym of X if X is a part of Y. \n\
\n\
Hypernym is the generic term used to designate a whole class of \n\
specific instances.  Y is a hypernym of X if X is a (kind of) Y. \n\
\n\
Meronym synsets are preceded with either the string \"HAS MEMBER\", \n\
\"HAS PART\" or \"HAS SUBSTANCE\" depending on the specific type of \n\
holonym.  Synsets are indented from the left according to their level \n\
in the hierarchy. \n\
";

static char deriv_help[] =	/* DERIVATION */
"Display derived forms - nouns and verbs that are related morphologically. \n\
Each related synset is preceeded by its part of speech. Each word in the \n\
synset is followed by its sense number. \n\
";

static char domain_help[] = 	/* CLASSIFICATION */
"Display domain to which this synset belongs. \n\
\n\
Each domain synset is preceeded by \"TOPIC\", \"REGION\", or \"USAGE\" to \n\
distinguish topical, geographic and functional classifications, and \n\
it's part of speech.  Each word is followed by its sense number. \n\
";

static char domainterms_help[] = /* CLASS */
"Display all synsets belonging to the domain. \n\
\n\
Each domain term synset is preceeded by \"TOPIC TERM\", \"REGION TERM\", or \n\
\"USAGE TERM\" to distinguish topical, geographic and functional classes, \n\
and its part of speech. Each word is followed by its sense number. \n\
";

static char nattrib_help[] =	/* ATTRIBUTE */
"Display adjectives for which search string is an attribute. \n\
";

static char aattrib_help[] =	/* ATTRIBUTE */
"Display nouns that are attributes of search string. \n\
";

static char tropo_help[] =	/* -HYPOPTR */
"Display hyponym tree for the search string.  This is \n\
a recursive search that finds the hyponyms of each hyponym.  \n\
\n\
For verbs, hyponyms are refered to as troponyms.  Troponyms indicate particular ways \n\
to perform a function.  X is a hyponym of Y if to X is a particular way to Y. \n\
\n\
Troponym synsets are preceded by \"=>\", and are indented from the left \n\
according to their level in the hierarchy. \n\
";

static char entail_help[] =	/* ENTAILPTR */
"Recursively display entailment relations of the search string.  \n\
\n\
The action represented by the verb X entails Y if X cannot be done \n\
unless Y is, or has been, done. \n\
\n\
Entailment synsets are preceded by \"=>\", and are indented from the left \n\
according to their level in the hierarchy. \n\
";

static char causeto_help[] =	/* CAUSETO */
"Recursively display CAUSE TO relations of the search string. \n\
\n\
The action represented by the verb X causes the action represented by \n\
the verb Y. \n\
\n\
CAUSE TO synsets are preceded by \"=>\", and are indented from the left \n\
according to their level in the hierarch.  \n\
";

static char frames_help[] =	/* FRAMES */
"Display applicable verb sentence frames for the search string. \n\
\n\
A frame is a sentence template illustrating the usage of a verb. \n\
\n\
Verb sentence frames are preceded with the string \"*>\" if a sentence \n\
frame is acceptable for all of the words in the synset, and with \"=>\" \n\
if a sentence frame is acceptable for the search string only.  \n\
\n\
Some verb senses have example sentences.  These are preceeded with \"EX:\". \n\
";

static char *nounhelps[] = {
hyper_help,
relatives_help,
ant_help,
coord_help,
hypertree_help,
hypo_help,
hypotree_help,
holo_help,
holotree_help,
mero_help,
merotree_help,
deriv_help,
nattrib_help,
domain_help,
domainterms_help,
freq_help,
grep_help
};

static char *verbhelps[] = { 
hyper_help,
relatives_help,
ant_help,
coord_help,
hypertree_help,
tropo_help,
entail_help,
causeto_help,
deriv_help,
frames_help,
domain_help,
domainterms_help,
freq_help,
grep_help
 };

static char *adjhelps[] = { 
/* SIMPTR */
"Display synonyms and synsets related to synsets containing \n\
the search string.  If the search string is in a head synset \n\
the 'cluster's' satellite synsets are displayed.  If the search \n\
string is in a satellite synset, its head synset is displayed. \n\
If the search string is a pertainym the word or synset that it \n\
pertains to is displayed. \n\
\n\
A cluster is a group of adjective synsets that are organized around \n\
antonymous pairs or triplets.  An adjective cluster contains two or more \n\
head synsets that contan antonyms.  Each head synset has one or more \n\
satellite synsets. \n\
\n\
A head synset contains at least one word that has a direct antonym \n\
in another head synset of the same cluster. \n\
\n\
A satellite synset represents a concept that is similar in meaning to \n\
the concept represented by its head synset. \n\
\n\
Direct antonyms are a pair of words between which there is an \n\
associative bond built up by co-occurrences. \n\
\n\
Direct antonyms are printed in parentheses following the adjective. \n\
The position of an adjective in relation to the noun may be restricted \n\
to the prenominal, postnominal or predicative position.  Where present \n\
these restrictions are noted in parentheses. \n\
\n\
A pertainym is a relational adjective, usually defined by such phrases \n\
as \"of or pertaining to\" and that does not have an antonym.  It pertains \n\
to a noun or another pertainym. \n\
\n\
Senses contained in head synsets are displayed above the satellites, \n\
which are indented and preceded by \"=>\".  Senses contained in \n\
satellite synsets are displayed with the head synset below.  The head \n\
synset is preceded by \"=>\". \n\
\n\
Pertainym senses display the word or synsets that the search string \n\
pertains to. \n\
",
/* ANTPTR */
"Display synsets containing antonyms of the search string. If the \n\
search string is in a head synset the direct antonym is displayed \n\
along with the head synset's satellite synsets.  If the search \n\
string is in a satellite synset, its indirect antonym is displayed \n\
via the head synset \n\
\n\
A head synset contains at least one word that has a direct antonym \n\
in another head synset of the same cluster. \n\
\n\
A satellite synset represents a concept that is similar in meaning to \n\
the concept represented by its head synset. \n\
\n\
Direct antonyms are a pair of words between which there is an \n\
associative bond built up by co-occurrences. \n\
\n\
Direct antonyms are printed in parentheses following the adjective. \n\
The position of an adjective in relation to the noun may be restricted \n\
to the prenominal, postnominal or predicative position.  Where present \n\
these restrictions are noted in parentheses. \n\
\n\
Senses contained in head synsets are displayed, followed by the \n\
head synset containing the search string's direct antonym and its \n\
similar synsets, which are indented and preceded by \"=>\".  Senses \n\
contained in satellite synsets are displayed followed by the indirect \n\
antonym via the satellite's head synset. \n\
",
aattrib_help,
domain_help,
domainterms_help,
freq_help,
grep_help

};

static char *advhelps[] = {
/* SIMPTR */
"Display synonyms and synsets related to synsets containing \n\
the search string.  If the search string is a pertainym the word \n\
or synset that it pertains to is displayed. \n\
\n\
A pertainym is a relational adverb that is derived from an adjective. \n\
\n\
Pertainym senses display the word that the search string is derived from \n\
and the adjective synset that contains the word.  If the adjective synset \n\
is a satellite synset, its head synset is also displayed. \n\
",
ant_help,
domain_help,
domainterms_help,
freq_help,
grep_help
};

char **helptext[NUMPARTS + 1] = {
    NULL,  nounhelps, verbhelps, adjhelps, advhelps 
};

