/*
   
   wn.h - header file needed to use WordNet Run Time Library

   $Id: wn.h,v 1.61 2006/11/14 20:58:30 wn Exp $

*/

#ifndef _WN_
#define _WN_

#include <stdio.h>

/* Platform specific path and filename specifications */

#ifdef _WINDOWS
#define DICTDIR         "\\dict"
#ifndef DEFAULTPATH
#define DEFAULTPATH	"C:\\Program Files\\WordNet\\3.0\\dict"
#endif
#define DATAFILE	"%s\\data.%s"
#define INDEXFILE	"%s\\index.%s"
#define SENSEIDXFILE	"%s\\index.sense"
#define KEYIDXFILE	"%s\\index.key"
#define REVKEYIDXFILE	"%s\\index.key.rev"
#define VRBSENTFILE  	"%s\\sents.vrb"
#define VRBIDXFILE	"%s\\sentidx.vrb"
#define CNTLISTFILE     "%s\\cntlist.rev"
#else
#define DICTDIR         "/dict"
#ifndef DEFAULTPATH
#define DEFAULTPATH	"/usr/local/WordNet-3.0/dict"
#endif
#define DATAFILE	"%s/data.%s"
#define INDEXFILE	"%s/index.%s"
#define SENSEIDXFILE	"%s/index.sense"
#define KEYIDXFILE	"%s/index.key"
#define REVKEYIDXFILE	"%s/index.key.rev"
#define VRBSENTFILE     "%s/sents.vrb"
#define VRBIDXFILE	"%s/sentidx.vrb"
#define CNTLISTFILE     "%s/cntlist.rev"
#endif

/* Various buffer sizes */

#define SEARCHBUF	((long)(200*(long)1024))
#define LINEBUF		(15*1024) /* 15K buffer to read index & data files */
#define SMLINEBUF	(3*1024) /* small buffer for output lines */
#define WORDBUF		(256)	/* buffer for one word or collocation */

#define ALLSENSES	0	/* pass to findtheinfo() if want all senses */
#define MAXID		15	/* maximum id number in lexicographer file */
#define MAXDEPTH	20	/* maximum tree depth - used to find cycles */
#define MAXSENSE	75	/* maximum number of senses in database */
#define MAX_FORMS	5	/* max # of different 'forms' word can have */
#define MAXFNUM		44	/* maximum number of lexicographer files */

/* Pointer type and search type counts */

/* Pointers */

#define ANTPTR           1	/* ! */
#define HYPERPTR         2	/* @ */
#define HYPOPTR          3	/* ~ */
#define ENTAILPTR        4	/* * */
#define SIMPTR           5	/* & */

#define ISMEMBERPTR      6	/* #m */
#define ISSTUFFPTR       7	/* #s */
#define ISPARTPTR        8	/* #p */

#define HASMEMBERPTR     9	/* %m */
#define HASSTUFFPTR     10	/* %s */
#define HASPARTPTR      11	/* %p */

#define MERONYM         12	/* % (not valid in lexicographer file) */
#define HOLONYM         13	/* # (not valid in lexicographer file) */
#define CAUSETO         14	/* > */
#define PPLPTR	        15	/* < */
#define SEEALSOPTR	16	/* ^ */
#define PERTPTR		17	/* \ */
#define ATTRIBUTE	18	/* = */
#define VERBGROUP	19	/* $ */
#define DERIVATION      20	/* + */
#define CLASSIFICATION  21	/* ; */
#define CLASS           22	/* - */

#define LASTTYPE	CLASS

/* Misc searches */

#define SYNS            (LASTTYPE + 1)
#define FREQ            (LASTTYPE + 2)
#define FRAMES          (LASTTYPE + 3)
#define COORDS          (LASTTYPE + 4)
#define RELATIVES	(LASTTYPE + 5)
#define HMERONYM        (LASTTYPE + 6)
#define HHOLONYM	(LASTTYPE + 7)
#define WNGREP		(LASTTYPE + 8)
#define OVERVIEW	(LASTTYPE + 9)

#define MAXSEARCH       OVERVIEW

#define CLASSIF_START    (MAXSEARCH + 1)

#define CLASSIF_CATEGORY (CLASSIF_START)        /* ;c */
#define CLASSIF_USAGE    (CLASSIF_START + 1)    /* ;u */
#define CLASSIF_REGIONAL (CLASSIF_START + 2)    /* ;r */

#define CLASSIF_END      CLASSIF_REGIONAL

#define CLASS_START      (CLASSIF_END + 1)

#define CLASS_CATEGORY   (CLASS_START)          /* -c */
#define CLASS_USAGE      (CLASS_START + 1)      /* -u */
#define CLASS_REGIONAL   (CLASS_START + 2)      /* -r */

#define CLASS_END        CLASS_REGIONAL

#define INSTANCE         (CLASS_END + 1)        /* @i */
#define INSTANCES        (CLASS_END + 2)        /* ~i */

#define MAXPTR          INSTANCES

/* WordNet part of speech stuff */

#define NUMPARTS	4	/* number of parts of speech */
#define NUMFRAMES	35	/* number of verb frames */

/* Generic names for part of speech */

#define NOUN		1
#define VERB		2
#define ADJ		3
#define ADV		4
#define SATELLITE	5	/* not really a part of speech */
#define ADJSAT		SATELLITE

#define ALL_POS		0	/* passed to in_wn() to check all POS */

#define bit(n) ((unsigned int)((unsigned int)1<<((unsigned int)n)))

/* Adjective markers */

#define PADJ		1	/* (p) */
#define NPADJ		2	/* (a) */
#define IPADJ		3	/* (ip) */

#define UNKNOWN_MARKER		0
#define ATTRIBUTIVE		NPADJ
#define PREDICATIVE		PADJ
#define IMMED_POSTNOMINAL	IPADJ

extern char *wnrelease;		/* WordNet release/version number */

extern char *lexfiles[];	/* names of lexicographer files */
extern char *ptrtyp[];		/* pointer characters */
extern char *partnames[];	/* POS strings */
extern char partchars[];	/* single chars for each POS */
extern char *adjclass[];	/* adjective class strings */
extern char *frametext[];	/* text of verb frames */

/* Data structures used by search code functions. */

/* Structure for index file entry */
typedef struct {
    long idxoffset;		/* byte offset of entry in index file */
    char *wd;			/* word string */
    char *pos;			/* part of speech */
    int sense_cnt;		/* sense (collins) count */
    int off_cnt;		/* number of offsets */
    int tagged_cnt;		/* number senses that are tagged */
    unsigned long *offset;	/* offsets of synsets containing word */
    int ptruse_cnt;		/* number of pointers used */
    int *ptruse;		/* pointers used */
} Index;

typedef Index *IndexPtr;

/* Structure for data file synset */
typedef struct ss {
    long hereiam;		/* current file position */
    int sstype;			/* type of ADJ synset */
    int fnum;			/* file number that synset comes from */
    char *pos;			/* part of speech */
    int wcount;			/* number of words in synset */
    char **words;		/* words in synset */
    int *lexid;			/* unique id in lexicographer file */
    int *wnsns;			/* sense number in wordnet */
    int whichword;		/* which word in synset we're looking for */
    int ptrcount;		/* number of pointers */
    int *ptrtyp;		/* pointer types */
    long *ptroff;		/* pointer offsets */
    int *ppos;			/* pointer part of speech */
    int *pto;			/* pointer 'to' fields */
    int *pfrm;			/* pointer 'from' fields */
    int fcount;			/* number of verb frames */
    int *frmid;			/* frame numbers */
    int *frmto;			/* frame 'to' fields */
    char *defn;			/* synset gloss (definition) */
    unsigned int key;		/* unique synset key */

    /* these fields are used if a data structure is returned
       instead of a text buffer */

    struct ss *nextss;		/* ptr to next synset containing searchword */
    struct ss *nextform;	/* ptr to list of synsets for alternate
				   spelling of wordform */
    int searchtype;		/* type of search performed */
    struct ss *ptrlist;		/* ptr to synset list result of search */
    char *headword;		/* if pos is "s", this is cluster head word */
    short headsense;		/* sense number of headword */
} Synset;

typedef Synset *SynsetPtr;

typedef struct si {
    char *sensekey;		/* sense key */
    char *word;			/* word string */
    long loc;			/* synset offset */
    int wnsense;		/* WordNet sense number */
    int tag_cnt;		/* number of semantic tags to sense */
    struct si *nextsi;		/* ptr to next sense index entry */
} SnsIndex;

typedef SnsIndex *SnsIndexPtr;
    
typedef struct {
    int SenseCount[MAX_FORMS];	/* number of senses word form has */
    int OutSenseCount[MAX_FORMS]; /* number of senses printed for word form */
    int numforms;		/* number of word forms searchword has */
    int printcnt;		/* number of senses printed by search */
    char *searchbuf;		/* buffer containing formatted results */
    SynsetPtr searchds;		/* data structure containing search results */
} SearchResults;

typedef SearchResults *SearchResultsPtr;

/* Global variables and flags */

extern SearchResults wnresults;	/* structure containing results of search */
extern int fnflag;		/* if set, print lex filename after sense */
extern int dflag;		/* if set, print definitional glosses */
extern int saflag;		/* if set, print SEE ALSO pointers */
extern int fileinfoflag;	/* if set, print lex file info on synsets */
extern int frflag;		/* if set, print verb frames after synset */
extern int abortsearch;		/* if set, stop search algorithm */
extern int offsetflag;		/* if set, print byte offset of each synset */
extern int wnsnsflag;		/* if set, print WN sense # for each word */

/* File pointers for database files */

extern int OpenDB;		/* if non-zero, database file are open */
extern FILE *datafps[NUMPARTS + 1], 
            *indexfps[NUMPARTS + 1],
            *sensefp,
            *cntlistfp,
            *keyindexfp, *revkeyindexfp,
            *vidxfilefp, *vsentfilefp;

/* Method for interface to check for events while search is running */

extern void (*interface_doevents_func)(void);  
                        /* callback for interruptable searches in */
                        /* single-threaded interfaces */

/* General error message handler - can be defined by interface.
   Default function provided in library returns -1 */

extern int default_display_message(char *);
extern int (*display_message)(char *);


/* Make all the functions compatible with c++ files */
#ifdef __cplusplus
extern "C" {
#endif

/* External library function prototypes */

/*** Search and database functions (search.c) ***/

/* Primry search algorithm for use with user interfaces */
extern char *findtheinfo(char *, int, int, int);	

/* Primary search algorithm for use with programs (returns data structure) */
extern SynsetPtr findtheinfo_ds(char *, int, int, int); 

/* Set bit for each search type that is valid for the search word
   passed and return bit mask. */
extern unsigned int is_defined(char *, int); 

/* Set bit for each POS that search word is in.  0 returned if
   word is not in WordNet. */
extern unsigned int in_wn(char *, int);	

/* Find word in index file and return parsed entry in data structure.
   Input word must be exact match of string in database. */
extern IndexPtr index_lookup(char *, int); 

/* 'smart' search of index file.  Find word in index file, trying different
   techniques - replace hyphens with underscores, replace underscores with
   hyphens, strip hyphens and underscores, strip periods. */
extern IndexPtr getindex(char *, int);	
extern IndexPtr parse_index(long, int, char *);

/* Read synset from data file at byte offset passed and return parsed
   entry in data structure. */
extern SynsetPtr read_synset(int, long, char *);

/* Read synset at current byte offset in file and return parsed entry
   in data structure. */
extern SynsetPtr parse_synset(FILE *, int, char *); 

/* Free a synset linked list allocated by findtheinfo_ds() */
extern void free_syns(SynsetPtr);	

/* Free a synset */
extern void free_synset(SynsetPtr);	

/* Free an index structure */
extern void free_index(IndexPtr);	

/* Recursive search algorithm to trace a pointer tree and return results
   in linked list of data structures. */
SynsetPtr traceptrs_ds(SynsetPtr, int, int, int);

/* Do requested search on synset passed, returning output in buffer. */
extern char *do_trace(SynsetPtr, int, int, int);

/*** Morphology functions (morph.c) ***/

/* Open exception list files */
extern int morphinit();	

/* Close exception list files and reopen */
extern int re_morphinit();	

/* Try to find baseform (lemma) of word or collocation in POS. */
extern char *morphstr(char *, int);	

/* Try to find baseform (lemma) of individual word in POS. */
extern char *morphword(char *, int);	

/*** Utility functions (wnutil.c) ***/

/* Top level function to open database files, initialize wn_filenames,
   and open exeception lists. */
extern int wninit();		

/* Top level function to close and reopen database files, initialize
   wn_filenames and open exception lists. */
extern int re_wninit();	

/* Count the number of underscore or space separated words in a string. */
extern int cntwords(char *, char);		

/* Convert string to lower case remove trailing adjective marker if found */
extern char *strtolower(char *);	

/* Convert string passed to lower case */
extern char *ToLowerCase(char *);	

/* Replace all occurrences of 'from' with 'to' in 'str' */
extern char *strsubst(char *, char, char);	

/* Return pointer code for pointer type characer passed. */
extern int getptrtype(char *);	

/* Return part of speech code for string passed */
extern int getpos(char *);		

/* Return synset type code for string passed. */
extern int getsstype(char *);		

/* Reconstruct synset from synset pointer and return ptr to buffer */
extern char *FmtSynset(SynsetPtr, int);	

/* Find string for 'searchstr' as it is in index file */
extern char *GetWNStr(char *, int);

/* Pass in string for POS, return corresponding integer value */
extern int StrToPos(char *);

/* Return synset for sense key passed. */
extern SynsetPtr GetSynsetForSense(char *);

/* Find offset of sense key in data file */
extern long GetDataOffset(char *);

/* Find polysemy (collins) count for sense key passed. */
extern int GetPolyCount(char *);

/* Return word part of sense key */
extern char *GetWORD(char *);

/* Return POS code for sense key passed. */
extern int GetPOS(char *);

/* Convert WordNet sense number passed of IndexPtr entry to sense key. */
extern char *WNSnsToStr(IndexPtr, int);

/* Search for string and/or baseform of word in database and return
   index structure for word if found in database. */
extern IndexPtr GetValidIndexPointer(char *, int);

/* Return sense number in database for word and lexsn passed. */
int GetWNSense(char *, char *);

SnsIndexPtr GetSenseIndex(char *);

char *GetOffsetForKey(unsigned int);
unsigned int GetKeyForOffset(char *);

char *SetSearchdir();

/* Return number of times sense is tagged */
int GetTagcnt(IndexPtr, int);

/*
** Wrapper functions for strstr that allow you to retrieve each
** occurance of a word within a longer string, not just the first.
**
** strstr_init is called with the same arguments as normal strstr,
** but does not return any value.
**
** strstr_getnext returns the position offset (not a pointer, as does
** normal strstr) of the next occurance, or -1 if none remain.
*/
extern void strstr_init (char *, char *);
extern int strstr_getnext (void);

/*** Binary search functions (binsearch.c) ***/

/* General purpose binary search function to search for key as first
   item on line in open file.  Item is delimited by space. */
extern char *bin_search(char *, FILE *);
extern char *read_index(long, FILE *);

/* Copy contents from one file to another. */
extern void copyfile(FILE *, FILE *);

/* Function to replace a line in a file.  Returns the original line,
   or NULL in case of error. */
extern char *replace_line(char *, char *, FILE *);

/* Find location to insert line at in file.  If line with this
   key is already in file, return NULL. */
extern char *insert_line(char *, char *, FILE *);

#ifdef __cplusplus
}
#endif

extern char **helptext[NUMPARTS + 1];

static char *license = "\
This software and database is being provided to you, the LICENSEE, by  \n\
Princeton University under the following license.  By obtaining, using  \n\
and/or copying this software and database, you agree that you have  \n\
read, understood, and will comply with these terms and conditions.:  \n\
  \n\
Permission to use, copy, modify and distribute this software and  \n\
database and its documentation for any purpose and without fee or  \n\
royalty is hereby granted, provided that you agree to comply with  \n\
the following copyright notice and statements, including the disclaimer,  \n\
and that the same appear on ALL copies of the software, database and  \n\
documentation, including modifications that you make for internal  \n\
use or for distribution.  \n\
  \n\
WordNet 3.0 Copyright 2006 by Princeton University.  All rights reserved.  \n\
  \n\
THIS SOFTWARE AND DATABASE IS PROVIDED \"AS IS\" AND PRINCETON  \n\
UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR  \n\
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON  \n\
UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT-  \n\
ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE  \n\
OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT  \n\
INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR  \n\
OTHER RIGHTS.  \n\
  \n\
The name of Princeton University or Princeton may not be used in  \n\
advertising or publicity pertaining to distribution of the software  \n\
and/or database.  Title to copyright in this software, database and  \n\
any associated documentation shall at all times remain with  \n\
Princeton University and LICENSEE agrees to preserve same.  \n"
;

static char dblicense[] = "\
  1 This software and database is being provided to you, the LICENSEE, by  \n\
  2 Princeton University under the following license.  By obtaining, using  \n\
  3 and/or copying this software and database, you agree that you have  \n\
  4 read, understood, and will comply with these terms and conditions.:  \n\
  5   \n\
  6 Permission to use, copy, modify and distribute this software and  \n\
  7 database and its documentation for any purpose and without fee or  \n\
  8 royalty is hereby granted, provided that you agree to comply with  \n\
  9 the following copyright notice and statements, including the disclaimer,  \n\
  10 and that the same appear on ALL copies of the software, database and  \n\
  11 documentation, including modifications that you make for internal  \n\
  12 use or for distribution.  \n\
  13   \n\
  14 WordNet 3.0 Copyright 2006 by Princeton University.  All rights reserved.  \n\
  15   \n\
  16 THIS SOFTWARE AND DATABASE IS PROVIDED \"AS IS\" AND PRINCETON  \n\
  17 UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR  \n\
  18 IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PRINCETON  \n\
  19 UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANT-  \n\
  20 ABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE  \n\
  21 OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT  \n\
  22 INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR  \n\
  23 OTHER RIGHTS.  \n\
  24   \n\
  25 The name of Princeton University or Princeton may not be used in  \n\
  26 advertising or publicity pertaining to distribution of the software  \n\
  27 and/or database.  Title to copyright in this software, database and  \n\
  28 any associated documentation shall at all times remain with  \n\
  29 Princeton University and LICENSEE agrees to preserve same.  \n"
;

#define DBLICENSE_SIZE 	(sizeof(dblicense))

#endif /*_WN_*/
