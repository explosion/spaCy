/*

  grind.h - grinder include file

*/

/* $Id: wngrind.h,v 1.1 2005/02/01 17:58:21 wn Rel $ */

#ifndef _GRIND_

#include "wn.h"

#ifndef NULL
#define NULL	0
#endif

#define FALSE	0
#define TRUE	1

/* Bit positions for legalptrs[] */

#define P_NOUN	1
#define P_VERB	2
#define P_ADJ	4
#define P_ADV	8

/* Pointer status values */

#define UNRESOLVED	0
#define RESOLVED	1
#define DUPLICATE       2
#define SELF_REF        3

#define ALLWORDS	(short)0 
#define NOSENSE		(unsigned char)0xff

#ifdef FOOP
#define HASHSIZE	100003	/* some large prime # */
#endif
#define HASHSIZE	500009	/* some large prime # */
#define ptrkind(p)	arraypos(ptrsymbols, p)

/* Structure for representing a synset */

typedef struct synset {
    struct synset *ssnext;	/* next synset */
    struct synset *fans;	/* if adjective cluster head, list of fans
				   if fan, pointer to cluster head */
    struct synonym *syns;	/* list of synonyms in synset */
    struct pointer *ptrs;	/* list of pointers from this synset */
    struct framelist *frames;	/* for verbs - list of framelists */
    char *defn;			/* textual gloss (optional) */
    unsigned int key;		/* unique synset key */
    unsigned char part;		/* part of speech */
    unsigned char isfanss;	/* TRUE - synset is fan synset */
    unsigned char filenum;	/* file number (from cmdline) synset is in */
    int clusnum;		/* cluster # if synset is part of cluster */
    int lineno;			/* line number in file of synset */
    long filepos;		/* byte offset of synset in output file */
} G_Ss, *G_Synset;		/* Grinder Synset */

/* A pointer from one synset to another */

typedef struct pointer {
    struct pointer *pnext;	/* next pointer from synset */
    struct symbol *pword;	/* word used to identify target synset */
    struct symbol *pslite;	/* label of satellite pointed to (optional) */
    struct synset *psynset;	/* target synset */
    unsigned char pfilenum;	/* file containing target synset */
    unsigned char psensenum;	/* sense number of word */
    unsigned char pslite_sense; /* sense number of satellite (optional) */
    unsigned char phead;	/* TRUE - pointer is to cluster head word */
    unsigned char ptype;	/* pointer type */
    unsigned char status;	/* status of pointer */
    short fromwdnum;		/* word number in this synset ptr is from */
    short towdnum;		/* word number in target synset ptr is to */
} Ptr, *Pointer;

/* Verb frame list */

typedef struct framelist {
    struct framelist *fnext;	/* next framelist */
    unsigned long frames[(NUMFRAMES/32) + 1]; /* bits for verb frames */
    unsigned char frwdnum;	/* word number that frame list is for */
} Fr, *Framelist;

/* A word in a synset */

typedef struct synonym {
    struct synonym *synnext;	/* next word in synset */
    struct synset *ss;		/* synset this synonym is in */
    struct symbol *word;	/* symbol table entry for word string */
    short sswdnum;		/* word number in synset ( <0, headword ) */
    short tagcnt;		/* num times sense is tagged in concordance */
    unsigned char wnsensenum;	/* sense number in wn database */
    unsigned char sensenum;	/* sense number in lexicographer's file */
    unsigned char adjclass;	/* adjective class of word */
    unsigned char infanss;	/* TRUE - synonym is in fan synset */
				/* FALSE - synonym is not in fan */
    char *label;		/* only used if string is not lowercase
				   if lowercase, use word->label */
} Syn, *Synonym;

/* Structure for storing word strings */

typedef struct symbol {
    struct symbol *symnext;	/* next symbol in this slot */
    struct synlist *syns;	/* uses of this word as a synonym */
    unsigned char sensecnt[NUMPARTS + 1]; /* senses for all parts of speech */
    char *label;		/* word */
} Sym, *Symbol;

/* List of use of this word as a synonym */

typedef struct synlist {
    struct synlist *snext;	/* next item on synonym list */
    struct synonym *psyn;	/* pointer to synonym structure */
} Synl, *SynList;

typedef struct flist {
    char *fname;		/* file name */
    int present;		/* file entered on command line? */
} Flist;

extern Flist filelist[];
extern int yylineno;
extern G_Synset headss;
extern int pcount;
extern int errcount;
extern int verifyflag;
extern int nowarn;
extern int ordersenses;
extern int synsetkeys;
extern char *ptrsymbols[];
extern char *legalptrs;
extern char *legalptrsets[];
extern char *ptrreflects[];
extern char **Argv;
extern int Argc;
extern FILE *logfile;
extern char partprefix[];
extern char partseen[];
extern char *adjclass[];
extern Symbol hashtab[];

/* External functions */

extern int arraypos(char **, char *);
extern int filenum(char *);
extern char *strclone(char *);
extern char *strupper(char *);
extern char *strlower(char *);
extern char *PrintFileName(int);
extern char *PrintPointer(Pointer);
extern char *PrintSynonym(Synonym);
extern char *NextFile();
extern int filemode();
extern G_Synset CreateSynset(unsigned char, Synonym, Pointer,
		    Framelist, char *, unsigned int, int, unsigned char);
extern Pointer CreatePointer(Symbol, Symbol, unsigned char,
		      unsigned char, unsigned char, unsigned char,
		      short, short);
extern Synonym CreateSynonym(Symbol, unsigned char, short,
		      unsigned char, char *);
extern Framelist CreateFramelist(int);
extern Symbol CreateSymbol(char *);
extern Symbol FindSymbol(char *);
extern void ResolvePointers();
extern void FindOffsets();
extern void DumpData();	
extern void DumpIndex();
extern void DumpSenseIndex();
extern void ReadCntlist();

#endif /* _GRIND_ */
