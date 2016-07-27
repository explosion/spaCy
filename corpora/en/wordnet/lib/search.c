/*
  
  search.c - WordNet library of search code
  
*/

#ifdef _WINDOWS
#include <windows.h>
#include <windowsx.h>
#endif
#include <stdio.h>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "wn.h"

static char *Id = "$Id: search.c,v 1.166 2006/11/14 20:52:45 wn Exp $";

/* For adjectives, indicates synset type */

#define DONT_KNOW	0
#define DIRECT_ANT	1	/* direct antonyms (cluster head) */
#define INDIRECT_ANT	2	/* indrect antonyms (similar) */
#define PERTAINYM	3	/* no antonyms or similars (pertainyms) */

/* Flags for printsynset() */

#define ALLWORDS	0	/* print all words */
#define SKIP_ANTS	0	/* skip printing antonyms in printsynset() */
#define PRINT_ANTS	1	/* print antonyms in printsynset() */
#define SKIP_MARKER	0	/* skip printing adjective marker */
#define PRINT_MARKER	1	/* print adjective marker */

/* Trace types used by printspaces() to determine print sytle */

#define TRACEP		1	/* traceptrs */
#define TRACEC		2	/* tracecoords() */
#define TRACEI		3	/* traceinherit() */

#define DEFON 1
#define DEFOFF 0

/* Forward function declarations */

static void WNOverview(char *, int);
static void findverbgroups(IndexPtr);
static void add_relatives(int, IndexPtr, int, int);
static void free_rellist(void);
static void printsynset(char *, SynsetPtr, char *, int, int, int, int);
static void printantsynset(SynsetPtr, char *, int, int);
static char *printant(int, SynsetPtr, int, char *, char *);
static void printbuffer(char *);
static void printsns(SynsetPtr, int);
static void printsense(SynsetPtr, int);
static void catword(char *, SynsetPtr, int, int, int);
static void printspaces(int, int);
static void printrelatives(IndexPtr, int);
static int HasHoloMero(IndexPtr, int);
static int HasPtr(SynsetPtr, int);
static int getsearchsense(SynsetPtr, int);
static int depthcheck(int, SynsetPtr);
static void interface_doevents();
static void getexample(char *, char *);
static int findexample(SynsetPtr);

/* Static variables */

static int prflag, sense, prlexid;
static int overflag = 0;	/* set when output buffer overflows */
static char searchbuffer[SEARCHBUF];
static int lastholomero;	/* keep track of last holo/meronym printed */
#define TMPBUFSIZE 1024*10
static char tmpbuf[TMPBUFSIZE];	/* general purpose printing buffer */
static char wdbuf[WORDBUF];	/* general purpose word buffer */
static char msgbuf[256];	/* buffer for constructing error messages */
static int adj_marker;

extern long last_bin_search_offset;


/* Find word in index file and return parsed entry in data structure.
   Input word must be exact match of string in database. */

IndexPtr index_lookup(char *word, int dbase)
{
    IndexPtr idx = NULL;
    FILE *fp;
    char *line;

    if ((fp = indexfps[dbase]) == NULL) {
	sprintf(msgbuf, "WordNet library error: %s indexfile not open\n",
		partnames[dbase]);
	display_message(msgbuf);
	return(NULL);
    }

    if ((line = bin_search(word, fp)) != NULL) {
	idx = parse_index( last_bin_search_offset, dbase, line);
    } 
    return (idx);
}

/* This function parses an entry from an index file into an Index data
 * structure. It takes the byte offset and file number, and optionally the
 * line. If the line is NULL, parse_index will get the line from the file.
 * If the line is non-NULL, parse_index won't look at the file, but it still
 * needs the dbase and offset parameters to be set, so it can store them in
 * the Index struct.
 */

IndexPtr parse_index(long offset, int dbase, char *line) {
    
    IndexPtr idx = NULL;
    char *ptrtok;
    int j;

    if ( !line )
      line = read_index( offset, indexfps[dbase] );
    
    idx = (IndexPtr)malloc(sizeof(Index));
    assert(idx);

    /* set offset of entry in index file */
    idx->idxoffset = offset;
    
    idx->wd='\0';
    idx->pos='\0';
    idx->off_cnt=0;
    idx->tagged_cnt = 0;
    idx->sense_cnt=0;
    idx->offset='\0';
    idx->ptruse_cnt=0;
    idx->ptruse='\0';
    
    /* get the word */
    ptrtok=strtok(line," \n");
    
    idx->wd = malloc(strlen(ptrtok) + 1);
    assert(idx->wd);
    strcpy(idx->wd, ptrtok);
    
    /* get the part of speech */
    ptrtok=strtok(NULL," \n");
    idx->pos = malloc(strlen(ptrtok) + 1);
    assert(idx->pos);
    strcpy(idx->pos, ptrtok);
    
    /* get the collins count */
    ptrtok=strtok(NULL," \n");
    idx->sense_cnt = atoi(ptrtok);
    
    /* get the number of pointers types */
    ptrtok=strtok(NULL," \n");
    idx->ptruse_cnt = atoi(ptrtok);
    
    if (idx->ptruse_cnt) {
	idx->ptruse = (int *) malloc(idx->ptruse_cnt * (sizeof(int)));
	assert(idx->ptruse);
	
	/* get the pointers types */
	for(j=0;j < idx->ptruse_cnt; j++) {
	    ptrtok=strtok(NULL," \n");
	    idx->ptruse[j] = getptrtype(ptrtok);
	}
    }
    
    /* get the number of offsets */
    ptrtok=strtok(NULL," \n");
    idx->off_cnt = atoi(ptrtok);
    
    /* get the number of senses that are tagged */
    ptrtok=strtok(NULL," \n");
    idx->tagged_cnt = atoi(ptrtok);
        
    /* make space for the offsets */
    idx->offset = (long *) malloc(idx->off_cnt * (sizeof(long)));
    assert(idx->offset);
    
    /* get the offsets */
    for(j=0;j<idx->off_cnt;j++) {
	ptrtok=strtok(NULL," \n");
	idx->offset[j] = atol(ptrtok);
    }
    return(idx);
}

/* 'smart' search of index file.  Find word in index file, trying different
   techniques - replace hyphens with underscores, replace underscores with
   hyphens, strip hyphens and underscores, strip periods. */

IndexPtr getindex(char *searchstr, int dbase)
{
    int i, j, k;
    char c;
    char strings[MAX_FORMS][WORDBUF]; /* vector of search strings */
    static IndexPtr offsets[MAX_FORMS];
    static int offset;
    
    /* This works like strrok(): if passed with a non-null string,
       prepare vector of search strings and offsets.  If string
       is null, look at current list of offsets and return next
       one, or NULL if no more alternatives for this word. */

    if (searchstr != NULL) {

	offset = 0;
	strtolower(searchstr);
	for (i = 0; i < MAX_FORMS; i++) {
	    strcpy(strings[i], searchstr);
	    offsets[i] = 0;
	}

	strsubst(strings[1], '_', '-');
	strsubst(strings[2], '-', '_');

	/* remove all spaces and hyphens from last search string, then
	   all periods */
	for (i = j = k = 0; (c = searchstr[i]) != '\0'; i++) {
	    if (c != '_' && c != '-')
		strings[3][j++] = c;
	    if (c != '.')
		strings[4][k++] = c;
	}
	strings[3][j] = '\0';
	strings[4][k] = '\0';

	/* Get offset of first entry.  Then eliminate duplicates
	   and get offsets of unique strings. */

	if (strings[0][0] != NULL)
	    offsets[0] = index_lookup(strings[0], dbase);

	for (i = 1; i < MAX_FORMS; i++)
	    if ((strings[i][0]) != NULL && (strcmp(strings[0], strings[i])))
		offsets[i] = index_lookup(strings[i], dbase);
    }


    for (i = offset; i < MAX_FORMS; i++)
	if (offsets[i]) {
	    offset = i + 1;
	    return(offsets[i]);
	}

    return(NULL);
}

/* Read synset from data file at byte offset passed and return parsed
   entry in data structure. */

SynsetPtr read_synset(int dbase, long boffset, char *word)
{
    FILE *fp;

    if((fp = datafps[dbase]) == NULL) {
	sprintf(msgbuf, "WordNet library error: %s datafile not open\n",
		partnames[dbase]);
	display_message(msgbuf);
	return(NULL);
    }
    
    fseek(fp, boffset, 0);	/* position file to byte offset requested */

    return(parse_synset(fp, dbase, word)); /* parse synset and return */
}

/* Read synset at current byte offset in file and return parsed entry
   in data structure. */

SynsetPtr parse_synset(FILE *fp, int dbase, char *word)
{
    static char line[LINEBUF];
    char tbuf[SMLINEBUF];
    char *ptrtok;
    char *tmpptr;
    int foundpert = 0;
    char wdnum[3];
    int i;
    SynsetPtr synptr;
    long loc;			/* sanity check on file location */

    loc = ftell(fp);

    if ((tmpptr = fgets(line, LINEBUF, fp)) == NULL)
	return(NULL);
    
    synptr = (SynsetPtr)malloc(sizeof(Synset));
    assert(synptr);
    
    synptr->hereiam = 0;
    synptr->sstype = DONT_KNOW;
    synptr->fnum = 0;
    synptr->pos = '\0';
    synptr->wcount = 0;
    synptr->words = '\0';
    synptr->whichword = 0;
    synptr->ptrcount = 0;
    synptr->ptrtyp = '\0';
    synptr->ptroff = '\0';
    synptr->ppos = '\0';
    synptr->pto = '\0';
    synptr->pfrm = '\0';
    synptr->fcount = 0;
    synptr->frmid = '\0';
    synptr->frmto = '\0';
    synptr->defn = '\0';
    synptr->key = 0;
    synptr->nextss = NULL;
    synptr->nextform = NULL;
    synptr->searchtype = -1;
    synptr->ptrlist = NULL;
    synptr->headword = NULL;
    synptr->headsense = 0;

    ptrtok = line;
    
    /* looking at offset */
    ptrtok = strtok(line," \n");
    synptr->hereiam = atol(ptrtok);

    /* sanity check - make sure starting file offset matches first field */
    if (synptr->hereiam != loc) {
	sprintf(msgbuf, "WordNet library error: no synset at location %d\n",
		loc);
	display_message(msgbuf);
	free(synptr);
	return(NULL);
    }
    
    /* looking at FNUM */
    ptrtok = strtok(NULL," \n");
    synptr->fnum = atoi(ptrtok);
    
    /* looking at POS */
    ptrtok = strtok(NULL, " \n");
    synptr->pos = malloc(strlen(ptrtok) + 1);
    assert(synptr->pos);
    strcpy(synptr->pos, ptrtok);
    if (getsstype(synptr->pos) == SATELLITE)
	synptr->sstype = INDIRECT_ANT;
    
    /* looking at numwords */
    ptrtok = strtok(NULL, " \n");
    synptr->wcount = strtol(ptrtok, NULL, 16);
    
    synptr->words = (char **)malloc(synptr->wcount  * sizeof(char *));
    assert(synptr->words);
    synptr->wnsns = (int *)malloc(synptr->wcount * sizeof(int));
    assert(synptr->wnsns);
    synptr->lexid = (int *)malloc(synptr->wcount * sizeof(int));
    assert(synptr->lexid);
    
    for (i = 0; i < synptr->wcount; i++) {
	ptrtok = strtok(NULL, " \n");
	synptr->words[i] = malloc(strlen(ptrtok) + 1);
	assert(synptr->words[i]);
	strcpy(synptr->words[i], ptrtok);
	
	/* is this the word we're looking for? */
	
	if (word && !strcmp(word,strtolower(ptrtok)))
	    synptr->whichword = i+1;
	
	ptrtok = strtok(NULL, " \n");
	sscanf(ptrtok, "%x", &synptr->lexid[i]);
    }
    
    /* get the pointer count */
    ptrtok = strtok(NULL," \n");
    synptr->ptrcount = atoi(ptrtok);

    if (synptr->ptrcount) {

	/* alloc storage for the pointers */
	synptr->ptrtyp = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->ptrtyp);
	synptr->ptroff = (long *)malloc(synptr->ptrcount * sizeof(long));
	assert(synptr->ptroff);
	synptr->ppos = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->ppos);
	synptr->pto = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->pto);
	synptr->pfrm = (int *)malloc(synptr->ptrcount * sizeof(int));
	assert(synptr->pfrm);
    
	for(i = 0; i < synptr->ptrcount; i++) {
	    /* get the pointer type */
	    ptrtok = strtok(NULL," \n");
	    synptr->ptrtyp[i] = getptrtype(ptrtok);
	    /* For adjectives, set the synset type if it has a direct
	       antonym */
	    if (dbase == ADJ &&	synptr->sstype == DONT_KNOW) {
		if (synptr->ptrtyp[i] == ANTPTR)
		    synptr->sstype = DIRECT_ANT;
		else if (synptr->ptrtyp[i] == PERTPTR)
		    foundpert = 1;
	    }

	    /* get the pointer offset */
	    ptrtok = strtok(NULL," \n");
	    synptr->ptroff[i] = atol(ptrtok);
	
	    /* get the pointer part of speech */
	    ptrtok = strtok(NULL, " \n");
	    synptr->ppos[i] = getpos(ptrtok);
	
	    /* get the lexp to/from restrictions */
	    ptrtok = strtok(NULL," \n");
	
	    tmpptr = ptrtok;
	    strncpy(wdnum, tmpptr, 2);
	    wdnum[2] = '\0';
	    synptr->pfrm[i] = strtol(wdnum, (char **)NULL, 16);
	
	    tmpptr += 2;
	    strncpy(wdnum, tmpptr, 2);
	    wdnum[2] = '\0';
	    synptr->pto[i] = strtol(wdnum, (char **)NULL, 16);
	}
    }

    /* If synset type is still not set, see if it's a pertainym */

    if (dbase == ADJ && synptr->sstype == DONT_KNOW && foundpert == 1)
	synptr->sstype = PERTAINYM;

    /* retireve optional information from verb synset */
    if(dbase == VERB) {
	ptrtok = strtok(NULL," \n");
	synptr->fcount = atoi(ptrtok);
	
	/* allocate frame storage */
	
	synptr->frmid = (int *)malloc(synptr->fcount * sizeof(int));  
	assert(synptr->frmid);
	synptr->frmto = (int *)malloc(synptr->fcount * sizeof(int));  
	assert(synptr->frmto);
	
	for(i=0;i<synptr->fcount;i++) {
	    /* skip the frame pointer (+) */
	    ptrtok = strtok(NULL," \n");
	    
	    ptrtok = strtok(NULL," \n");
	    synptr->frmid[i] = atoi(ptrtok);
	    
	    ptrtok = strtok(NULL," \n");
	    synptr->frmto[i] = strtol(ptrtok, NULL, 16);
	}
    }
    
    /* get the optional definition */
    
    ptrtok = strtok(NULL," \n");
    if (ptrtok) {
	ptrtok = strtok(NULL," \n");
	sprintf(tbuf, "");
	while (ptrtok != NULL) {
	    strcat(tbuf,ptrtok);
	    ptrtok = strtok(NULL, " \n");
	    if(ptrtok)
		strcat(tbuf," ");
	}
	assert((1 + strlen(tbuf)) < sizeof(tbuf));
	synptr->defn = malloc(strlen(tbuf) + 4);
	assert(synptr->defn);
	sprintf(synptr->defn,"(%s)",tbuf);
    }

    if (keyindexfp) { 		/* we have unique keys */
	sprintf(tmpbuf, "%c:%8.8d", partchars[dbase], synptr->hereiam);
	synptr->key = GetKeyForOffset(tmpbuf);
    }

    /* Can't do earlier - calls indexlookup which messes up strtok calls */

    for (i = 0; i < synptr->wcount; i++)
	synptr->wnsns[i] = getsearchsense(synptr, i + 1);

    return(synptr);
}

/* Free a synset linked list allocated by findtheinfo_ds() */

void free_syns(SynsetPtr synptr)
{
    SynsetPtr cursyn, nextsyn;

    if (synptr) {
	cursyn = synptr;
	while(cursyn) {
	    if (cursyn->nextform)
		free_syns(cursyn->nextform);
	    nextsyn = cursyn->nextss;
	    free_synset(cursyn);
	    cursyn = nextsyn;
	}
    }
}

/* Free a synset */

void free_synset(SynsetPtr synptr)
{
    int i;
    
    free(synptr->pos);
    for (i = 0; i < synptr->wcount; i++){
	free(synptr->words[i]);
    }
    free(synptr->words);
    free(synptr->wnsns);
    free(synptr->lexid);
    if (synptr->ptrcount) {
	free(synptr->ptrtyp);
	free(synptr->ptroff);
	free(synptr->ppos);
	free(synptr->pto);
	free(synptr->pfrm);
    }
    if (synptr->fcount) {
	free(synptr->frmid);
	free(synptr->frmto);
    }
    if (synptr->defn)
	free(synptr->defn);
    if (synptr->headword)
	free(synptr->headword);
    if (synptr->ptrlist)
	free_syns(synptr->ptrlist); /* changed from free_synset() */
    free(synptr);
}

/* Free an index structure */

void free_index(IndexPtr idx)
{
    free(idx->wd);
    free(idx->pos);
    if (idx->ptruse)
	free(idx->ptruse);
    free(idx->offset);
    free(idx);
}

/* Recursive search algorithm to trace a pointer tree */

static void traceptrs(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    int extraindent = 0;
    SynsetPtr cursyn;
    char prefix[40], tbuf[20];
    int realptr;

    interface_doevents();
    if (abortsearch)
	return;

    if (ptrtyp < 0) {
	ptrtyp = -ptrtyp;
	extraindent = 2;
    }
    
    for (i = 0; i < synptr->ptrcount; i++) {
	if ((ptrtyp == HYPERPTR && (synptr->ptrtyp[i] == HYPERPTR ||
				    synptr->ptrtyp[i] == INSTANCE)) ||
	    (ptrtyp == HYPOPTR && (synptr->ptrtyp[i] == HYPOPTR ||
				   synptr->ptrtyp[i] == INSTANCES)) ||
	    ((synptr->ptrtyp[i] == ptrtyp) &&
	     ((synptr->pfrm[i] == 0) ||
	      (synptr->pfrm[i] == synptr->whichword)))) {

	    realptr = synptr->ptrtyp[i]; /* deal with INSTANCE */

	    if(!prflag) {	/* print sense number and synset */
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEP, depth + extraindent);

	    switch(realptr) {
	    case PERTPTR:
		if (dbase == ADV) 
		    sprintf(prefix, "Derived from %s ",
			    partnames[synptr->ppos[i]]);
		else
		    sprintf(prefix, "Pertains to %s ",
			    partnames[synptr->ppos[i]]);
		break;
	    case ANTPTR:
		if (dbase != ADJ)
		    sprintf(prefix, "Antonym of ");
		break;
	    case PPLPTR:
		sprintf(prefix, "Participle of verb ");
		break;
	    case INSTANCE:
		sprintf(prefix, "INSTANCE OF=> ");
		break;
	    case INSTANCES:
		sprintf(prefix, "HAS INSTANCE=> ");
		break;
	    case HASMEMBERPTR:
		sprintf(prefix, "   HAS MEMBER: ");
		break;
	    case HASSTUFFPTR:
		sprintf(prefix, "   HAS SUBSTANCE: ");
		break;
	    case HASPARTPTR:
		sprintf(prefix, "   HAS PART: ");
		break;
	    case ISMEMBERPTR:
		sprintf(prefix, "   MEMBER OF: ");
		break;
	    case ISSTUFFPTR:
		sprintf(prefix, "   SUBSTANCE OF: ");
		break;
	    case ISPARTPTR:
		sprintf(prefix, "   PART OF: ");
		break;
	    default:
		sprintf(prefix, "=> ");
		break;
	    }

	    /* Read synset pointed to */
	    cursyn=read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    /* For Pertainyms and Participles pointing to a specific
	       sense, indicate the sense then retrieve the synset
	       pointed to and other info as determined by type.
	       Otherwise, just print the synset pointed to. */

	    if ((ptrtyp == PERTPTR || ptrtyp == PPLPTR) &&
		synptr->pto[i] != 0) {
		sprintf(tbuf, " (Sense %d)\n",
			cursyn->wnsns[synptr->pto[i] - 1]);
		printsynset(prefix, cursyn, tbuf, DEFOFF, synptr->pto[i],
			    SKIP_ANTS, PRINT_MARKER);
		if (ptrtyp == PPLPTR) { /* adjective pointing to verb */
		    printsynset("      =>", cursyn, "\n",
				DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
		} else if (dbase == ADV) { /* adverb pointing to adjective */
		    printsynset("      =>", cursyn, "\n",DEFON, ALLWORDS, 
				((getsstype(cursyn->pos) == SATELLITE)
				 ? SKIP_ANTS : PRINT_ANTS), PRINT_MARKER);
#ifdef FOOP
 		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
#endif
		} else {	/* adjective pointing to noun */
		    printsynset("      =>", cursyn, "\n",
				DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
		    traceptrs(cursyn, HYPERPTR, getpos(cursyn->pos), 0);
		}
	    } else if (ptrtyp == ANTPTR && dbase != ADJ && synptr->pto[i] != 0) {
		sprintf(tbuf, " (Sense %d)\n",
			cursyn->wnsns[synptr->pto[i] - 1]);
		printsynset(prefix, cursyn, tbuf, DEFOFF, synptr->pto[i],
			    SKIP_ANTS, PRINT_MARKER);
		printsynset("      =>", cursyn, "\n", DEFON, ALLWORDS,
			    PRINT_ANTS, PRINT_MARKER);
	    } else 
		printsynset(prefix, cursyn, "\n", DEFON, ALLWORDS,
			    PRINT_ANTS, PRINT_MARKER);

	    /* For HOLONYMS and MERONYMS, keep track of last one
	       printed in buffer so results can be truncated later. */

	    if (ptrtyp >= ISMEMBERPTR && ptrtyp <= HASPARTPTR)
		lastholomero = strlen(searchbuffer);

	    if(depth) {
		depth = depthcheck(depth, cursyn);
		traceptrs(cursyn, ptrtyp, getpos(cursyn->pos), (depth+1));

		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }
}

static void tracecoords(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn;

    interface_doevents();
    if (abortsearch)
	return;

    for(i = 0; i < synptr->ptrcount; i++) {
	if((synptr->ptrtyp[i] == HYPERPTR || synptr->ptrtyp[i] == INSTANCE) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    if(!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEC, depth);

	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    printsynset("-> ", cursyn, "\n", DEFON, ALLWORDS,
			SKIP_ANTS, PRINT_MARKER);

	    traceptrs(cursyn, ptrtyp, getpos(cursyn->pos), depth);
	    
	    if(depth) {
		depth = depthcheck(depth, cursyn);
		tracecoords(cursyn, ptrtyp, getpos(cursyn->pos), (depth+1));
		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }
}

static void traceclassif(SynsetPtr synptr, int dbase, int search)
{
    int i, j, idx;
    SynsetPtr cursyn;
    long int prlist[1024];
    char head[60];
    int svwnsnsflag;

    interface_doevents();
    if (abortsearch)
	return;

    idx = 0;

    for (i = 0; i < synptr->ptrcount; i++) {
	if (((synptr->ptrtyp[i] >= CLASSIF_START) &&
	     (synptr->ptrtyp[i] <= CLASSIF_END) && search == CLASSIFICATION) ||
	    
	    ((synptr->ptrtyp[i] >= CLASS_START) &&
	     (synptr->ptrtyp[i] <= CLASS_END) && search == CLASS) ) {

	    if (!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    
	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    for (j = 0; j < idx; j++) {
		if (synptr->ptroff[i] == prlist[j]) {
		    break;
		}
	    }

	    if (j == idx) {
		prlist[idx++] = synptr->ptroff[i];
		printspaces(TRACEP, 0);

		if (synptr->ptrtyp[i] == CLASSIF_CATEGORY)
		    strcpy(head, "TOPIC->(");
		else if (synptr->ptrtyp[i] == CLASSIF_USAGE)
		    strcpy(head, "USAGE->(");
		else if (synptr->ptrtyp[i] == CLASSIF_REGIONAL)
		    strcpy(head, "REGION->(");
		else if (synptr->ptrtyp[i] == CLASS_CATEGORY)
		    strcpy(head, "TOPIC_TERM->(");
		else if (synptr->ptrtyp[i] == CLASS_USAGE)
		    strcpy(head, "USAGE_TERM->(");
		else if (synptr->ptrtyp[i] == CLASS_REGIONAL)
		    strcpy(head, "REGION_TERM->(");

		strcat(head, partnames[synptr->ppos[i]]);
		strcat(head, ") ");

		svwnsnsflag = wnsnsflag;
		wnsnsflag = 1;

		printsynset(head, cursyn, "\n", DEFOFF, ALLWORDS,
			    SKIP_ANTS, SKIP_MARKER);

		wnsnsflag = svwnsnsflag;
	    }

	    free_synset(cursyn);
	}
    }
}

static void tracenomins(SynsetPtr synptr, int dbase)
{
    int i, j, idx;
    SynsetPtr cursyn;
    long int prlist[1024];
    char prefix[40], tbuf[20];

    interface_doevents();
    if (abortsearch)
	return;

    idx = 0;

    for (i = 0; i < synptr->ptrcount; i++) {
	if ((synptr->ptrtyp[i] == DERIVATION) &&
	    (synptr->pfrm[i] == synptr->whichword)) {

	    if (!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }

	    printspaces(TRACEP, 0);

	    sprintf(prefix, "RELATED TO->(%s) ",
		    partnames[synptr->ppos[i]]);
	    	    
	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    sprintf(tbuf, "#%d\n",
		    cursyn->wnsns[synptr->pto[i] - 1]);
	    printsynset(prefix, cursyn, tbuf, DEFOFF, synptr->pto[i],
			SKIP_ANTS, SKIP_MARKER);

	    /* only print synset once, even if more than one link */

	    for (j = 0; j < idx; j++) {
#ifdef FOOP
		if (synptr->ptroff[i] == prlist[j]) {
		    break;
		}
#endif
	    }

	    if (j == idx) {
		prlist[idx++] = synptr->ptroff[i];
		printspaces(TRACEP, 2);
		printsynset("=> ", cursyn, "\n", DEFON, ALLWORDS,
			    SKIP_ANTS, PRINT_MARKER);
	    }

	    free_synset(cursyn);
	}
    }
}

/* Trace through the hypernym tree and print all MEMBER, STUFF
   and PART info. */

static void traceinherit(SynsetPtr synptr, int ptrbase, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn;

    interface_doevents();
    if (abortsearch)
	return;
    
    for(i=0;i<synptr->ptrcount;i++) {
	if((synptr->ptrtyp[i] == HYPERPTR) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    if(!prflag) {
		printsns(synptr, sense + 1);
		prflag = 1;
	    }
	    printspaces(TRACEI, depth);
	    
	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    printsynset("=> ", cursyn, "\n", DEFON, ALLWORDS,
			SKIP_ANTS, PRINT_MARKER);
	    
	    traceptrs(cursyn, ptrbase, NOUN, depth);
	    traceptrs(cursyn, ptrbase + 1, NOUN, depth);
	    traceptrs(cursyn, ptrbase + 2, NOUN, depth);
	    
	    if(depth) {
		depth = depthcheck(depth, cursyn);
		traceinherit(cursyn, ptrbase, getpos(cursyn->pos), (depth+1));
		free_synset(cursyn);
	    } else
		free_synset(cursyn);
	}
    }

    /* Truncate search buffer after last holo/meronym printed */
    searchbuffer[lastholomero] = '\0';
}

static void partsall(SynsetPtr synptr, int ptrtyp)
{
    int ptrbase;
    int i, hasptr = 0;
    
    ptrbase = (ptrtyp == HMERONYM) ? HASMEMBERPTR : ISMEMBERPTR;
    
    /* First, print out the MEMBER, STUFF, PART info for this synset */

    for (i = 0; i < 3; i++) {
	if (HasPtr(synptr, ptrbase + i)) {
	    traceptrs(synptr, ptrbase + i, NOUN, 1);
	    hasptr++;
	}
	interface_doevents();
	if (abortsearch)
	    return;
    }

    /* Print out MEMBER, STUFF, PART info for hypernyms on
       HMERONYM search only */
	
/*    if (hasptr && ptrtyp == HMERONYM) { */
    if (ptrtyp == HMERONYM) {
	lastholomero = strlen(searchbuffer);
	traceinherit(synptr, ptrbase, NOUN, 1);
    }
}

static void traceadjant(SynsetPtr synptr)
{
    SynsetPtr newsynptr;
    int i, j;
    int anttype = DIRECT_ANT;
    SynsetPtr simptr, antptr;
    static char similar[] = "        => ";

    /* This search is only applicable for ADJ synsets which have
       either direct or indirect antonyms (not valid for pertainyms). */
    
    if (synptr->sstype == DIRECT_ANT || synptr->sstype == INDIRECT_ANT) {
	printsns(synptr, sense + 1);
	printbuffer("\n");
	
	/* if indirect, get cluster head */
	
	if(synptr->sstype == INDIRECT_ANT) {
	    anttype = INDIRECT_ANT;
	    i = 0;
	    while (synptr->ptrtyp[i] != SIMPTR) i++;
	    newsynptr = read_synset(ADJ, synptr->ptroff[i], "");
	} else
	    newsynptr = synptr;
	
	/* find antonyms - if direct, make sure that the antonym
	   ptr we're looking at is from this word */
	
	for (i = 0; i < newsynptr->ptrcount; i++) {

	    if (newsynptr->ptrtyp[i] == ANTPTR &&
		((anttype == DIRECT_ANT &&
		  newsynptr->pfrm[i] == newsynptr->whichword) ||
		 (anttype == INDIRECT_ANT))) {
		
		/* read the antonym's synset and print it.  if a
		   direct antonym, print it's satellites. */
		
		antptr = read_synset(ADJ, newsynptr->ptroff[i], "");
    
		if (anttype == DIRECT_ANT) {
		    printsynset("", antptr, "\n", DEFON, ALLWORDS,
				PRINT_ANTS, PRINT_MARKER);
		    for(j = 0; j < antptr->ptrcount; j++) {
			if(antptr->ptrtyp[j] == SIMPTR) {
			    simptr = read_synset(ADJ, antptr->ptroff[j], "");
			    printsynset(similar, simptr, "\n", DEFON,
					ALLWORDS, SKIP_ANTS, PRINT_MARKER);
			    free_synset(simptr);
			}
		    }
		} else
		    printantsynset(antptr, "\n", anttype, DEFON);

		free_synset(antptr);
	    }
	}
	if (newsynptr != synptr)
	    free_synset(newsynptr);
    }
}


/* Fetch the given example sentence from the example file and print it out */

void getexample(char *offset, char *wd)
{
    char *line;
    char sentbuf[512];
    
    if (vsentfilefp != NULL) {
	if (line = bin_search(offset, vsentfilefp)) {
	    while(*line != ' ') 
		line++;

	    printbuffer("          EX: ");
	    sprintf(sentbuf, line, wd);
	    printbuffer(sentbuf);
	}
    }
}

/* Find the example sentence references in the example sentence index file */

int findexample(SynsetPtr synptr)
{
    char tbuf[256], *temp, *offset;
    int wdnum;
    int found = 0;
    
    if (vidxfilefp != NULL) {
	wdnum = synptr->whichword - 1;

	sprintf(tbuf,"%s%%%-1.1d:%-2.2d:%-2.2d::",
		synptr->words[wdnum],
		getpos(synptr->pos),
		synptr->fnum,
		synptr->lexid[wdnum]);

	if ((temp = bin_search(tbuf, vidxfilefp)) != NULL) {

	    /* skip over sense key and get sentence numbers */

	    temp += strlen(synptr->words[wdnum]) + 11;
	    strcpy(tbuf, temp);

	    offset = strtok(tbuf, " ,\n");

	    while (offset) {
		getexample(offset, synptr->words[wdnum]);
		offset = strtok(NULL, ",\n");
	    }
	    found = 1;
	}
    }
    return(found);
}

static void printframe(SynsetPtr synptr, int prsynset)
{
    int i;

    if (prsynset)
	printsns(synptr, sense + 1);
    
    if (!findexample(synptr)) {
	for(i = 0; i < synptr->fcount; i++) {
	    if ((synptr->frmto[i] == synptr->whichword) ||
		(synptr->frmto[i] == 0)) {
		if (synptr->frmto[i] == synptr->whichword)
		    printbuffer("          => ");
		else
		    printbuffer("          *> ");
		printbuffer(frametext[synptr->frmid[i]]);
		printbuffer("\n");
	    }
	}
    }
}

static void printseealso(SynsetPtr synptr)
{
    SynsetPtr cursyn;
    int i, first = 1;
    int svwnsnsflag;
    char firstline_v[] = "          Phrasal Verb-> ";
    char firstline_nar[] = "          Also See-> ";
    char otherlines[] = "; ";
    char *prefix;

    if ( getpos( synptr->pos ) == VERB )
	prefix = firstline_v;
    else
	prefix = firstline_nar;

    /* Find all SEEALSO pointers from the searchword and print the
       word or synset pointed to. */

    for(i = 0; i < synptr->ptrcount; i++) {
	if ((synptr->ptrtyp[i] == SEEALSOPTR) &&
	    ((synptr->pfrm[i] == 0) ||
	     (synptr->pfrm[i] == synptr->whichword))) {

	    cursyn = read_synset(synptr->ppos[i], synptr->ptroff[i], "");

	    svwnsnsflag = wnsnsflag;
	    wnsnsflag = 1;
	    printsynset(prefix, cursyn, "", DEFOFF,
			synptr->pto[i] == 0 ? ALLWORDS : synptr->pto[i],
			SKIP_ANTS, SKIP_MARKER);
	    wnsnsflag = svwnsnsflag;

	    free_synset(cursyn);

	    if (first) {
		prefix = otherlines;
		first = 0;
	    }
	}
    }
    if (!first)
	printbuffer("\n");
}

static void freq_word(IndexPtr index)
{
    int familiar=0;
    int cnt;
    static char *a_an[] = {
	"", "a noun", "a verb", "an adjective", "an adverb" };
    static char *freqcats[] = {
	"extremely rare","very rare","rare","uncommon","common",
	"familiar","very familiar","extremely familiar"
    };

    if(index) {
	cnt = index->sense_cnt;
	if (cnt == 0) familiar = 0;
	if (cnt == 1) familiar = 1;
	if (cnt == 2) familiar = 2;
	if (cnt >= 3 && cnt <= 4) familiar = 3;
	if (cnt >= 5 && cnt <= 8) familiar = 4;
	if (cnt >= 9 && cnt <= 16) familiar = 5;
	if (cnt >= 17 && cnt <= 32) familiar = 6;
	if (cnt > 32 ) familiar = 7;
	
	sprintf(tmpbuf,
		"\n%s used as %s is %s (polysemy count = %d)\n",
		index->wd, a_an[getpos(index->pos)], freqcats[familiar], cnt);
	printbuffer(tmpbuf);
    }
}

void wngrep (char *word_passed, int pos) {
   FILE *inputfile;
   char word[256];
   int wordlen, linelen, loc;
   char line[1024];
   int count = 0;

   inputfile = indexfps[pos];
   if (inputfile == NULL) {
      sprintf (msgbuf, "WordNet library error: Can't perform compounds "
         "search because %s index file is not open\n", partnames[pos]);
      display_message (msgbuf);
      return;
   }
   rewind(inputfile);

   strcpy (word, word_passed);
   ToLowerCase(word);		/* map to lower case for index file search */
   strsubst (word, ' ', '_');	/* replace spaces with underscores */
   wordlen = strlen (word);

   while (fgets (line, 1024, inputfile) != NULL) {
      for (linelen = 0; line[linelen] != ' '; linelen++) {}
      if (linelen < wordlen)
	  continue;
      line[linelen] = '\0';
      strstr_init (line, word);
      while ((loc = strstr_getnext ()) != -1) {
         if (
            /* at the start of the line */
            (loc == 0) ||
            /* at the end of the line */
            ((linelen - wordlen) == loc) ||
            /* as a word in the middle of the line */
            (((line[loc - 1] == '-') || (line[loc - 1] == '_')) &&
            ((line[loc + wordlen] == '-') || (line[loc + wordlen] == '_')))
         ) {
            strsubst (line, '_', ' ');
            sprintf (tmpbuf, "%s\n", line);
            printbuffer (tmpbuf);
            break;
         }
      }
      if (count++ % 2000 == 0) {
         interface_doevents ();
         if (abortsearch) break;
      }
   }
}

/* Stucture to keep track of 'relative groups'.  All senses in a relative
   group are displayed together at end of search.  Transitivity is
   supported, so if either of a new set of related senses is already
   in a 'relative group', the other sense is added to that group as well. */

struct relgrp {
    int senses[MAXSENSE];
    struct relgrp *next;
};
static struct relgrp *rellist;

static struct relgrp *mkrellist(void);

/* Simple hash function */
#define HASHTABSIZE	1223	/* Prime number. Must be > 2*MAXTOPS */
#define hash(n) ((n) % HASHTABSIZE)

/* Find relative groups for all senses of target word in given part
   of speech. */

static void relatives(IndexPtr idx, int dbase)
{
    rellist = NULL;

    switch(dbase) {

    case VERB:
	findverbgroups(idx);
	interface_doevents();
	if (abortsearch)
	    break;
	printrelatives(idx, VERB);
	break;
    default:
	break;
    }

    free_rellist();
}

static void findverbgroups(IndexPtr idx)
{
     int i, j, k;
     SynsetPtr synset;

     assert(idx);

     /* Read all senses */
     
     for (i = 0; i < idx->off_cnt; i++) {

	 synset = read_synset(VERB, idx->offset[i], idx->wd);
	
	 /* Look for VERBGROUP ptr(s) for this sense.  If found,
	    create group for senses, or add to existing group. */

	 for (j = 0; j < synset->ptrcount; j++) {
	       if (synset->ptrtyp[j] == VERBGROUP) {
		   /* Need to find sense number for ptr offset */
		   for (k = 0; k < idx->off_cnt; k++) {
		       if (synset->ptroff[j] == idx->offset[k]) {
			   add_relatives(VERB, idx, i, k);
			   break;
		       }
		   }
	       }
	   }
	 free_synset(synset);
     }
}

static void add_relatives(int pos, IndexPtr idx, int rel1, int rel2)
{
    int i;
    struct relgrp *rel, *last, *r;

    /* If either of the new relatives are already in a relative group,
       then add the other to the existing group (transitivity).
       Otherwise create a new group and add these 2 senses to it. */

    for (rel = rellist; rel; rel = rel->next) {
	if (rel->senses[rel1] == 1 || rel->senses[rel2] == 1) {
	    rel->senses[rel1] = rel->senses[rel2] = 1;

	    /* If part of another relative group, merge the groups */
	    for (r = rellist; r; r = r->next) {
		if (r != rel &&
		    (r->senses[rel1] == 1 || r->senses[rel2] == 1)) {
		    for (i = 0; i < MAXSENSE; i++)
			rel->senses[i] |= r->senses[i];
		}
	    }
	    return;
	}
	last = rel;
    }
    rel = mkrellist();
    rel->senses[rel1] = rel->senses[rel2] = 1;
    if (rellist == NULL)
	rellist = rel;
    else
	last->next = rel;
}

static struct relgrp *mkrellist(void)
{
    struct relgrp *rel;
    int i;

    rel = (struct relgrp *) malloc(sizeof(struct relgrp));
    assert(rel);
    for (i = 0; i < MAXSENSE; i++)
	rel->senses[i] = 0;
    rel->next = NULL;
    return(rel);
}

static void free_rellist(void)
{
    struct relgrp *rel, *next;

    rel = rellist;
    while(rel) {
	next = rel->next;
	free(rel);
	rel = next;
    }
}

static void printrelatives(IndexPtr idx, int dbase)
{
    SynsetPtr synptr;
    struct relgrp *rel;
    int i, flag;
    int outsenses[MAXSENSE];

    for (i = 0; i < idx->off_cnt; i++)
	outsenses[i] = 0;
    prflag = 1;

    for (rel = rellist; rel; rel = rel->next) {
	flag = 0;
	for (i = 0; i < idx->off_cnt; i++) {
	    if (rel->senses[i] && !outsenses[i]) {
		flag = 1;
		synptr = read_synset(dbase, idx->offset[i], "");
		printsns(synptr, i + 1);
		traceptrs(synptr, HYPERPTR, dbase, 0);
		outsenses[i] = 1;
		free_synset(synptr);
	    }
	}
	if (flag)
	    printbuffer("--------------\n");
    }

    for (i = 0; i < idx->off_cnt; i++) {
	if (!outsenses[i]) {
	    synptr = read_synset(dbase, idx->offset[i], "");
	    printsns(synptr, i + 1);
	    traceptrs(synptr, HYPERPTR, dbase, 0);
	    printbuffer("--------------\n");
	    free_synset(synptr);
	}
    }
}

/*
  Search code interfaces to WordNet database

  findtheinfo() - print search results and return ptr to output buffer
  findtheinfo_ds() - return search results in linked list data structrure
*/

char *findtheinfo(char *searchstr, int dbase, int ptrtyp, int whichsense)
{
    SynsetPtr cursyn;
    IndexPtr idx = NULL;
    int depth = 0;
    int i, offsetcnt;
    char *bufstart;
    unsigned long offsets[MAXSENSE];
    int skipit;

    /* Initializations -
       clear output buffer, search results structure, flags */

    searchbuffer[0] = '\0';

    wnresults.numforms = wnresults.printcnt = 0;
    wnresults.searchbuf = searchbuffer;
    wnresults.searchds = NULL;

    abortsearch = overflag = 0;
    for (i = 0; i < MAXSENSE; i++)
	offsets[i] = 0;

    switch (ptrtyp) {
    case OVERVIEW:
	WNOverview(searchstr, dbase);
	break;
    case FREQ:
	while ((idx = getindex(searchstr, dbase)) != NULL) {
	    searchstr = NULL;
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    freq_word(idx);
	    free_index(idx);
	    wnresults.numforms++;
	}
	break;
    case WNGREP:
	wngrep(searchstr, dbase);
	break;
    case RELATIVES:
    case VERBGROUP:
	while ((idx = getindex(searchstr, dbase)) != NULL) {
	    searchstr = NULL;
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    relatives(idx, dbase);
	    free_index(idx);
	    wnresults.numforms++;
	}
	break;
    default:

	/* If negative search type, set flag for recursive search */
	if (ptrtyp < 0) {
	    ptrtyp = -ptrtyp;
	    depth = 1;
	}
	bufstart = searchbuffer;
	offsetcnt = 0;

	/* look at all spellings of word */

	while ((idx = getindex(searchstr, dbase)) != NULL) {

	    searchstr = NULL;	/* clear out for next call to getindex() */
	    wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	    wnresults.OutSenseCount[wnresults.numforms] = 0;

	    /* Print extra sense msgs if looking at all senses */
	    if (whichsense == ALLSENSES)
		printbuffer(
"                                                                         \n");

	    /* Go through all of the searchword's senses in the
	       database and perform the search requested. */

	    for (sense = 0; sense < idx->off_cnt; sense++) {

		if (whichsense == ALLSENSES || whichsense == sense + 1) {
		    prflag = 0;

		    /* Determine if this synset has already been done
		       with a different spelling. If so, skip it. */
		    for (i = 0, skipit = 0; i < offsetcnt && !skipit; i++) {
			if (offsets[i] == idx->offset[sense])
			    skipit = 1;
		    }
		    if (skipit != 1) {
		    	offsets[offsetcnt++] = idx->offset[sense];
		    	cursyn = read_synset(dbase, idx->offset[sense], idx->wd);
		    	switch(ptrtyp) {
		    	case ANTPTR:
			    if(dbase == ADJ)
			    	traceadjant(cursyn);
			    else
			    	traceptrs(cursyn, ANTPTR, dbase, depth);
			    break;
		   	 
		    	case COORDS:
			    tracecoords(cursyn, HYPOPTR, dbase, depth);
			    break;
		   	 
		    	case FRAMES:
			    printframe(cursyn, 1);
			    break;
			    
		    	case MERONYM:
			    traceptrs(cursyn, HASMEMBERPTR, dbase, depth);
			    traceptrs(cursyn, HASSTUFFPTR, dbase, depth);
			    traceptrs(cursyn, HASPARTPTR, dbase, depth);
			    break;
			    
		    	case HOLONYM:
			    traceptrs(cursyn, ISMEMBERPTR, dbase, depth);
			    traceptrs(cursyn, ISSTUFFPTR, dbase, depth);
			    traceptrs(cursyn, ISPARTPTR, dbase, depth);
			    break;
			   	 
		    	case HMERONYM:
			    partsall(cursyn, HMERONYM);
			    break;
			   	 
		    	case HHOLONYM:
			    partsall(cursyn, HHOLONYM);
			    break;
			   	 
		    	case SEEALSOPTR:
			    printseealso(cursyn);
			    break;
	
#ifdef FOOP
			case PPLPTR:
			    traceptrs(cursyn, ptrtyp, dbase, depth);
			    traceptrs(cursyn, PPLPTR, dbase, depth);
			    break;
#endif
		    
		    	case SIMPTR:
		    	case SYNS:
		    	case HYPERPTR:
			    printsns(cursyn, sense + 1);
			    prflag = 1;
		    
			    traceptrs(cursyn, ptrtyp, dbase, depth);
		    
			    if (dbase == ADJ) {
/*			    	traceptrs(cursyn, PERTPTR, dbase, depth); */
			    	traceptrs(cursyn, PPLPTR, dbase, depth);
			    } else if (dbase == ADV) {
/*			    	traceptrs(cursyn, PERTPTR, dbase, depth);*/
			    }

			    if (saflag)	/* print SEE ALSO pointers */
			    	printseealso(cursyn);
			    
			    if (dbase == VERB && frflag)
			    	printframe(cursyn, 0);
			    break;

			case PERTPTR:
			    printsns(cursyn, sense + 1);
			    prflag = 1;
		    
			    traceptrs(cursyn, PERTPTR, dbase, depth);
			    break;

			case DERIVATION:
			    tracenomins(cursyn, dbase);
			    break;

			case CLASSIFICATION:
			case CLASS:
			    traceclassif(cursyn, dbase, ptrtyp);
			    break;

		    	default:
			    traceptrs(cursyn, ptrtyp, dbase, depth);
			    break;

		    	} /* end switch */

		    	free_synset(cursyn);

		    } /* end if (skipit) */

		} /* end if (whichsense) */

		if (skipit != 1) {
		    interface_doevents();
		    if ((whichsense == sense + 1) || abortsearch || overflag)
		    	break;	/* break out of loop - we're done */
		}

	    } /* end for (sense) */

	    /* Done with an index entry - patch in number of senses output */

	    if (whichsense == ALLSENSES) {
		i = wnresults.OutSenseCount[wnresults.numforms];
		if (i == idx->off_cnt && i == 1)
		    sprintf(tmpbuf, "\n1 sense of %s", idx->wd);
		else if (i == idx->off_cnt)
		    sprintf(tmpbuf, "\n%d senses of %s", i, idx->wd);
		else if (i > 0)	/* printed some senses */
		    sprintf(tmpbuf, "\n%d of %d senses of %s",
			    i, idx->off_cnt, idx->wd);

		/* Find starting offset in searchbuffer for this index
		   entry and patch string in.  Then update bufstart
		   to end of searchbuffer for start of next index entry. */

		if (i > 0) {
		    if (wnresults.numforms > 0) {
			bufstart[0] = '\n';
			bufstart++;
		    }
		    strncpy(bufstart, tmpbuf, strlen(tmpbuf));
		    bufstart = searchbuffer + strlen(searchbuffer);
		}
	    }

	    free_index(idx);

	    interface_doevents();
	    if (overflag || abortsearch)
		break;		/* break out of while (idx) loop */

	    wnresults.numforms++;

	} /* end while (idx) */

    } /* end switch */

    interface_doevents();
    if (abortsearch)
	printbuffer("\nSearch Interrupted...\n");
    else if (overflag)
	sprintf(searchbuffer,
		"Search too large.  Narrow search and try again...\n");

    /* replace underscores with spaces before returning */

    return(strsubst(searchbuffer, '_', ' '));
}

SynsetPtr findtheinfo_ds(char *searchstr, int dbase, int ptrtyp, int whichsense)
{
    IndexPtr idx;
    SynsetPtr cursyn;
    SynsetPtr synlist = NULL, lastsyn = NULL;
    int depth = 0;
    int newsense = 0;

    wnresults.numforms = 0;
    wnresults.printcnt = 0;

    while ((idx = getindex(searchstr, dbase)) != NULL) {

	searchstr = NULL;	/* clear out for next call */
	newsense = 1;
	
	if(ptrtyp < 0) {
	    ptrtyp = -ptrtyp;
	    depth = 1;
	}

	wnresults.SenseCount[wnresults.numforms] = idx->off_cnt;
	wnresults.OutSenseCount[wnresults.numforms] = 0;
	wnresults.searchbuf = NULL;
	wnresults.searchds = NULL;

	/* Go through all of the searchword's senses in the
	   database and perform the search requested. */
	
	for(sense = 0; sense < idx->off_cnt; sense++) {
	    if (whichsense == ALLSENSES || whichsense == sense + 1) {
		cursyn = read_synset(dbase, idx->offset[sense], idx->wd);
		if (lastsyn) {
		    if (newsense)
			lastsyn->nextform = cursyn;
		    else
			lastsyn->nextss = cursyn;
		}
		if (!synlist)
		    synlist = cursyn;
		newsense = 0;
	    
		cursyn->searchtype = ptrtyp;
		cursyn->ptrlist = traceptrs_ds(cursyn, ptrtyp, 
					       getpos(cursyn->pos),
					       depth);
	    
		lastsyn = cursyn;

		if (whichsense == sense + 1)
		    break;
	    }
	}
	free_index(idx);
	wnresults.numforms++;

	if (ptrtyp == COORDS) {	/* clean up by removing hypernym */
	    lastsyn = synlist->ptrlist;
	    synlist->ptrlist = lastsyn->ptrlist;
	    free_synset(lastsyn);
	}
    }
    wnresults.searchds = synlist;
    return(synlist);
}

/* Recursive search algorithm to trace a pointer tree and return results
  in linked list of data structures. */

SynsetPtr traceptrs_ds(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    int i;
    SynsetPtr cursyn, synlist = NULL, lastsyn = NULL;
    int tstptrtyp, docoords;
    
    /* If synset is a satellite, find the head word of its
       head synset and the head word's sense number. */

    if (getsstype(synptr->pos) == SATELLITE) {
	for (i = 0; i < synptr->ptrcount; i++)
	    if (synptr->ptrtyp[i] == SIMPTR) {
		cursyn = read_synset(synptr->ppos[i],
				      synptr->ptroff[i],
				      "");
		synptr->headword = malloc(strlen(cursyn->words[0]) + 1);
		assert(synptr->headword);
		strcpy(synptr->headword, cursyn->words[0]);
		synptr->headsense = cursyn->lexid[0];
		free_synset(cursyn);
		break;
	    }
    }

    if (ptrtyp == COORDS) {
	tstptrtyp = HYPERPTR;
	docoords = 1;
    } else {
	tstptrtyp = ptrtyp;
	docoords = 0;
    }

    for (i = 0; i < synptr->ptrcount; i++) {
	if((synptr->ptrtyp[i] == tstptrtyp) &&
	   ((synptr->pfrm[i] == 0) ||
	    (synptr->pfrm[i] == synptr->whichword))) {
	    
	    cursyn=read_synset(synptr->ppos[i], synptr->ptroff[i], "");
	    cursyn->searchtype = ptrtyp;

	    if (lastsyn)
		lastsyn->nextss = cursyn;
	    if (!synlist)
		synlist = cursyn;
	    lastsyn = cursyn;

	    if(depth) {
		depth = depthcheck(depth, cursyn);
		cursyn->ptrlist = traceptrs_ds(cursyn, ptrtyp,
					       getpos(cursyn->pos),
					       (depth+1));
	    } else if (docoords) {
		cursyn->ptrlist = traceptrs_ds(cursyn, HYPOPTR, NOUN, 0);
	    }
	}
    }
    return(synlist);
}

static void WNOverview(char *searchstr, int pos)
{
    SynsetPtr cursyn;
    IndexPtr idx = NULL;
    char *cpstring = searchstr, *bufstart;
    int sense, i, offsetcnt;
    int svdflag, skipit;
    unsigned long offsets[MAXSENSE];

    cpstring = searchstr;
    bufstart = searchbuffer;
    for (i = 0; i < MAXSENSE; i++)
	offsets[i] = 0;
    offsetcnt = 0;

    while ((idx = getindex(cpstring, pos)) != NULL) {

	cpstring = NULL;	/* clear for next call to getindex() */
	wnresults.SenseCount[wnresults.numforms++] = idx->off_cnt;
	wnresults.OutSenseCount[wnresults.numforms] = 0;

	printbuffer(
"                                                                                                   \n");

	/* Print synset for each sense.  If requested, precede
	   synset with synset offset and/or lexical file information.*/

	for (sense = 0; sense < idx->off_cnt; sense++) {

	    for (i = 0, skipit = 0; i < offsetcnt && !skipit; i++)
		if (offsets[i] == idx->offset[sense])
		    skipit = 1;

	    if (!skipit) {
		offsets[offsetcnt++] = idx->offset[sense];
		cursyn = read_synset(pos, idx->offset[sense], idx->wd);
		if (idx->tagged_cnt != -1 &&
		    ((sense + 1) <= idx->tagged_cnt)) {
		  sprintf(tmpbuf, "%d. (%d) ",
			  sense + 1, GetTagcnt(idx, sense + 1));
		} else {
		  sprintf(tmpbuf, "%d. ", sense + 1);
		}

		svdflag = dflag;
		dflag = 1;
		printsynset(tmpbuf, cursyn, "\n", DEFON, ALLWORDS,
			    SKIP_ANTS, SKIP_MARKER);
		dflag = svdflag;
		wnresults.OutSenseCount[wnresults.numforms]++;
		wnresults.printcnt++;

		free_synset(cursyn);
	    }
	}

	/* Print sense summary message */

	i = wnresults.OutSenseCount[wnresults.numforms];

	if (i > 0) {
	    if (i == 1)
		sprintf(tmpbuf, "\nThe %s %s has 1 sense",
			partnames[pos], idx->wd);
	    else
		sprintf(tmpbuf, "\nThe %s %s has %d senses",
			partnames[pos], idx->wd, i);
	    if (idx->tagged_cnt > 0)
		sprintf(tmpbuf + strlen(tmpbuf),
			" (first %d from tagged texts)\n", idx->tagged_cnt);
	    else if (idx->tagged_cnt == 0) 
		sprintf(tmpbuf + strlen(tmpbuf),
			" (no senses from tagged texts)\n");

	    strncpy(bufstart, tmpbuf, strlen(tmpbuf));
	    bufstart = searchbuffer + strlen(searchbuffer);
	} else
	    bufstart[0] = '\0';

	wnresults.numforms++;
	free_index(idx);
    }
}

/* Do requested search on synset passed, returning output in buffer. */

char *do_trace(SynsetPtr synptr, int ptrtyp, int dbase, int depth)
{
    searchbuffer[0] = '\0';	/* clear output buffer */
    traceptrs(synptr, ptrtyp, dbase, depth);
    return(searchbuffer);
}

/* Set bit for each search type that is valid for the search word
   passed and return bit mask. */
  
unsigned int is_defined(char *searchstr, int dbase)
{
    IndexPtr index;
    int i;
    unsigned long retval = 0;

    wnresults.numforms = wnresults.printcnt = 0;
    wnresults.searchbuf = NULL;
    wnresults.searchds = NULL;

    while ((index = getindex(searchstr, dbase)) != NULL) {
	searchstr = NULL;	/* clear out for next getindex() call */

	wnresults.SenseCount[wnresults.numforms] = index->off_cnt;
	
	/* set bits that must be true for all words */
	
	retval |= bit(SIMPTR) | bit(FREQ) | bit(SYNS)|
	    bit(WNGREP) | bit(OVERVIEW);

	/* go through list of pointer characters and set appropriate bits */

	for(i = 0; i < index->ptruse_cnt; i++) {

	    if (index->ptruse[i] <= LASTTYPE) {
		retval |= bit(index->ptruse[i]);
	    } else if (index->ptruse[i] == INSTANCE) {
		retval |= bit(HYPERPTR);
	    } else if (index->ptruse[i] == INSTANCES) {
		retval |= bit(HYPOPTR);
	    }
	    
	    if (index->ptruse[i] == SIMPTR) {
		retval |= bit(ANTPTR);
	    } 
#ifdef FOOP

	    if (index->ptruse[i] >= CLASSIF_START &&
		 index->ptruse[i] <= CLASSIF_END) {
		retval |= bit(CLASSIFICATION);
	    }


	    if (index->ptruse[i] >= CLASS_START &&
		 index->ptruse[i] <= CLASS_END) {
		retval |= bit(CLASS);
	    }
#endif

	    if (index->ptruse[i] >= ISMEMBERPTR &&
	       index->ptruse[i] <= ISPARTPTR)
		retval |= bit(HOLONYM);
	    else if (index->ptruse[i] >= HASMEMBERPTR &&
		    index->ptruse[i] <= HASPARTPTR)
		retval |= bit(MERONYM);
	 
	}

	if (dbase == NOUN) {

	    /* check for inherited holonyms and meronyms */

	    if (HasHoloMero(index, HMERONYM))
		retval |= bit(HMERONYM);
	    if (HasHoloMero(index, HHOLONYM))
		retval |= bit(HHOLONYM);

	    /* if synset has hypernyms, enable coordinate search */

	    if (retval & bit(HYPERPTR))
		retval |= bit(COORDS);
	} else if (dbase == VERB) {

	    /* if synset has hypernyms, enable coordinate search */
	    if (retval & bit(HYPERPTR))
		retval |= bit(COORDS);

	    /* enable grouping of related synsets and verb frames */

	    retval |= bit(RELATIVES) | bit(FRAMES);
	}

	free_index(index);
	wnresults.numforms++;
    }
    return(retval);
}

/* Determine if any of the synsets that this word is in have inherited
   meronyms or holonyms. */

static int HasHoloMero(IndexPtr index, int ptrtyp)
{
    int i, j;
    SynsetPtr synset, psynset;
    int found=0;
    int ptrbase;

    ptrbase = (ptrtyp == HMERONYM) ? HASMEMBERPTR : ISMEMBERPTR;
    
    for(i = 0; i < index->off_cnt; i++) {
	synset = read_synset(NOUN, index->offset[i], "");
	for (j = 0; j < synset->ptrcount; j++) {
	    if (synset->ptrtyp[j] == HYPERPTR) {
		psynset = read_synset(NOUN, synset->ptroff[j], "");
		found += HasPtr(psynset, ptrbase);
		found += HasPtr(psynset, ptrbase + 1);
		found += HasPtr(psynset, ptrbase + 2);

		free_synset(psynset);
	    }
	}
	free_synset(synset);
    }
    return(found);
}

static int HasPtr(SynsetPtr synptr, int ptrtyp)
{
    int i;
    
    for(i = 0; i < synptr->ptrcount; i++) {
        if(synptr->ptrtyp[i] == ptrtyp) {
	    return(1);
	}
    }
    return(0);
}

/* Set bit for each POS that search word is in.  0 returned if
   word is not in WordNet. */

unsigned int in_wn(char *word, int pos)
{
    int i;
    unsigned int retval = 0;

    if (pos == ALL_POS) {
	for (i = 1; i < NUMPARTS + 1; i++)
	    if (indexfps[i] != NULL && bin_search(word, indexfps[i]) != NULL)
		retval |= bit(i);
    } else if (indexfps[pos] != NULL && bin_search(word,indexfps[pos]) != NULL)
	    retval |= bit(pos);
    return(retval);
}

static int depthcheck(int depth, SynsetPtr synptr)
{
    if(depth >= MAXDEPTH) {
	sprintf(msgbuf,
		"WordNet library error: Error Cycle detected\n   %s\n",
		synptr->words[0]);
	display_message(msgbuf);
	depth = -1;		/* reset to get one more trace then quit */
    }
    return(depth);
}

/* Strip off () enclosed comments from a word */

static char *deadjify(char *word)
{
    char *y;
    
    adj_marker = UNKNOWN_MARKER; /* default if not adj or unknown */
    
    y=word;
    while(*y) {
	if(*y == '(') {
	    if (!strncmp(y, "(a)", 3))
		adj_marker = ATTRIBUTIVE;
	    else if (!strncmp(y, "(ip)", 4))
		adj_marker = IMMED_POSTNOMINAL;
	    else if (!strncmp(y, "(p)", 3))
		adj_marker = PREDICATIVE;
	    *y='\0';
	} else 
	    y++;
    }
    return(word);
}

static int getsearchsense(SynsetPtr synptr, int whichword)
{
    IndexPtr idx;
    int i;

    strsubst(strcpy(wdbuf, synptr->words[whichword - 1]), ' ', '_');
    strtolower(wdbuf);
		       
    if (idx = index_lookup(wdbuf, getpos(synptr->pos))) {
	for (i = 0; i < idx->off_cnt; i++)
	    if (idx->offset[i] == synptr->hereiam) {
		free_index(idx);
		return(i + 1);
	    }
	free_index(idx);
    }
    return(0);
}

static void printsynset(char *head, SynsetPtr synptr, char *tail, int definition, int wdnum, int antflag, int markerflag)
{
    int i, wdcnt;
    char tbuf[SMLINEBUF];

    tbuf[0] = '\0';		/* clear working buffer */

    strcat(tbuf, head);		/* print head */

    /* Precede synset with additional information as indiecated
       by flags */

    if (offsetflag)		/* print synset offset */
	sprintf(tbuf + strlen(tbuf),"{%8.8d} ", synptr->hereiam);
    if (fileinfoflag) {		/* print lexicographer file information */
	sprintf(tbuf + strlen(tbuf), "<%s> ", lexfiles[synptr->fnum]);
	prlexid = 1;		/* print lexicographer id after word */
    } else
	prlexid = 0;

    if (wdnum)			/* print only specific word asked for */
	catword(tbuf, synptr, wdnum - 1, markerflag, antflag);
    else			/* print all words in synset */
	for(i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	    catword(tbuf, synptr, i, markerflag, antflag);
	    if (i < wdcnt - 1)
		strcat(tbuf, ", ");
	}
    
    if(definition && dflag && synptr->defn) {
	strcat(tbuf," -- ");
	strcat(tbuf,synptr->defn);
    }

    strcat(tbuf,tail);
    printbuffer(tbuf);
}

static void printantsynset(SynsetPtr synptr, char *tail, int anttype, int definition)
{
    int i, wdcnt;
    char tbuf[SMLINEBUF];
    char *str;
    int first = 1;

    tbuf[0] = '\0';

    if (offsetflag)
	sprintf(tbuf,"{%8.8d} ", synptr->hereiam);
    if (fileinfoflag) {
	sprintf(tbuf + strlen(tbuf),"<%s> ", lexfiles[synptr->fnum]);
	prlexid = 1;
    } else
	prlexid = 0;
    
    /* print anotnyms from cluster head (of indirect ant) */
    
    strcat(tbuf, "INDIRECT (VIA ");
    for(i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	if (first) {
	    str = printant(ADJ, synptr, i + 1, "%s", ", ");
	    first = 0;
	} else
	    str = printant(ADJ, synptr, i + 1, ", %s", ", ");
	if (*str)
	    strcat(tbuf, str);
    }
    strcat(tbuf, ") -> ");
    
    /* now print synonyms from cluster head (of indirect ant) */
    
    for (i = 0, wdcnt = synptr->wcount; i < wdcnt; i++) {
	catword(tbuf, synptr, i, SKIP_MARKER, SKIP_ANTS);
	if (i < wdcnt - 1)
	    strcat(tbuf, ", ");
    }
    
    if(dflag && synptr->defn && definition) {
	strcat(tbuf," -- ");
	strcat(tbuf,synptr->defn);
    }
    
    strcat(tbuf,tail);
    printbuffer(tbuf);
}

static void catword(char *buf, SynsetPtr synptr, int wdnum, int adjmarker, int antflag)
{
    static char vs[] = " (vs. %s)";
    static char *markers[] = {
	"",			/* UNKNOWN_MARKER */
	"(predicate)",		/* PREDICATIVE */
	"(prenominal)",		/* ATTRIBUTIVE */
	"(postnominal)",	/* IMMED_POSTNOMINAL */
    };

    /* Copy the word (since deadjify() changes original string),
       deadjify() the copy and append to buffer */
    
    strcpy(wdbuf, synptr->words[wdnum]);
    strcat(buf, deadjify(wdbuf));

    /* Print additional lexicographer information and WordNet sense
       number as indicated by flags */
	
    if (prlexid && (synptr->lexid[wdnum] != 0))
	sprintf(buf + strlen(buf), "%d", synptr->lexid[wdnum]);
    if (wnsnsflag)
	sprintf(buf + strlen(buf), "#%d", synptr->wnsns[wdnum]);

    /* For adjectives, append adjective marker if present, and
       print antonym if flag is passed */

    if (getpos(synptr->pos) == ADJ) {
	if (adjmarker == PRINT_MARKER)
	    strcat(buf, markers[adj_marker]); 
	if (antflag == PRINT_ANTS)
	    strcat(buf, printant(ADJ, synptr, wdnum + 1, vs, ""));
    }
}

static char *printant(int dbase, SynsetPtr synptr, int wdnum, char *template, char *tail)
{
    int i, j, wdoff;
    SynsetPtr psynptr;
    char tbuf[WORDBUF];
    static char retbuf[SMLINEBUF];
    int first = 1;
    
    retbuf[0] = '\0';
    
    /* Go through all the pointers looking for anotnyms from the word
       indicated by wdnum.  When found, print all the antonym's
       antonym pointers which point back to wdnum. */
    
    for (i = 0; i < synptr->ptrcount; i++) {
	if (synptr->ptrtyp[i] == ANTPTR && synptr->pfrm[i] == wdnum) {

	    psynptr = read_synset(dbase, synptr->ptroff[i], "");

	    for (j = 0; j < psynptr->ptrcount; j++) {
		if (psynptr->ptrtyp[j] == ANTPTR &&
		    psynptr->pto[j] == wdnum &&
		    psynptr->ptroff[j] == synptr->hereiam) {

		    wdoff = (psynptr->pfrm[j] ? (psynptr->pfrm[j] - 1) : 0);

		    /* Construct buffer containing formatted antonym,
		       then add it onto end of return buffer */

		    strcpy(wdbuf, psynptr->words[wdoff]);
		    strcpy(tbuf, deadjify(wdbuf));

		    /* Print additional lexicographer information and
		       WordNet sense number as indicated by flags */
	
		    if (prlexid && (psynptr->lexid[wdoff] != 0))
			sprintf(tbuf + strlen(tbuf), "%d",
				psynptr->lexid[wdoff]);
		    if (wnsnsflag)
			sprintf(tbuf + strlen(tbuf), "#%d",
				psynptr->wnsns[wdoff]);
		    if (!first)
			strcat(retbuf, tail);
		    else
			first = 0;
		    sprintf(retbuf + strlen(retbuf), template, tbuf);
		}
	    }
	    free_synset(psynptr);
	}
    }
    return(retbuf);
}

static void printbuffer(char *string)
{
    if (overflag)
	return;
    if (strlen(searchbuffer) + strlen(string) >= SEARCHBUF)
        overflag = 1;
    else 
	strcat(searchbuffer, string);
}

static void printsns(SynsetPtr synptr, int sense)
{
    printsense(synptr, sense);
    printsynset("", synptr, "\n", DEFON, ALLWORDS, PRINT_ANTS, PRINT_MARKER);
}

static void printsense(SynsetPtr synptr, int sense)
{
    char tbuf[256];

    /* Append lexicographer filename after Sense # if flag is set. */

    if (fnflag)
	sprintf(tbuf,"\nSense %d in file \"%s\"\n",
		sense, lexfiles[synptr->fnum]);
    else
	sprintf(tbuf,"\nSense %d\n", sense);

    printbuffer(tbuf);

    /* update counters */
    wnresults.OutSenseCount[wnresults.numforms]++; 
    wnresults.printcnt++;
}

static void printspaces(int trace, int depth)
{
    int j;

    for (j = 0; j < depth; j++)
	printbuffer("    ");

    switch(trace) {
    case TRACEP:		/* traceptrs(), tracenomins() */
	if (depth)
	    printbuffer("   ");
	else
	    printbuffer("       ");
	break;

    case TRACEC:		/* tracecoords() */
	if (!depth)
	    printbuffer("    ");
	break;

    case TRACEI:			/* traceinherit() */
	if (!depth)
	    printbuffer("\n    ");
	break;
    }
}

/* Dummy function to force Tcl/Tk to look at event queue to see of
   the user wants to stop the search. */

static void interface_doevents (void) {
   if (interface_doevents_func != NULL) interface_doevents_func ();
}

/*
  Revision log: (since version 1.5)
  
  $Log: search.c,v $
  Revision 1.166  2006/11/14 20:52:45  wn
  for 2.1

  Revision 1.165  2005/02/24 15:36:00  wn
  fixed bug - coordinate search was missing INSTANCE pointers

  Revision 1.164  2005/01/27 16:32:32  wn
  removed 1.6 stuff and cleaned up #ifdefs

  Revision 1.163  2004/10/25 15:25:18  wn
  added instances code

  Revision 1.162  2004/01/12 16:32:52  wn
  changed "CATEGORY" to "TOPIC"

  Revision 1.161  2003/06/23 15:52:27  wn
  cleaned up format of nomin output

  Revision 1.160  2003/06/05 15:29:45  wn
  added pos and sense number for domains

  Revision 1.159  2003/04/15 13:54:16  wn
  *** empty log message ***

  Revision 1.158  2003/03/20 19:31:36  wn
  removed NOMIN_START/NOMIN_END range and replaced with DERIVATION

  Revision 1.157  2003/02/06 19:01:36  wn
  added code to print out word pointed to in derivational links.

  Revision 1.156  2003/02/06 18:03:30  wn
  work on classifications

  Revision 1.155  2002/10/29 15:46:27  wn
  added CLASSIFICATION code

  Revision 1.154  2002/09/16 15:43:01  wn
  allow "grep" string to be in upper case

  Revision 1.153  2002/09/16 15:39:16  wn
  *** empty log message ***

  Revision 1.152  2002/03/22 19:39:15  wn
  fill in key field in SynsetPtr if key file found

  Revision 1.151  2002/03/07 18:47:52  wn
  updates for 1.7.1

  Revision 1.150  2001/12/04 17:48:21  wn
  added test to tracenomins to only print nominalizations of serach
  word and not all words in synset

  Revision 1.149  2001/11/27 19:53:24  wn
  removed check for version on verb example sentence stuff. only
  needed for 1.5

  Revision 1.148  2001/11/06 18:51:04  wn
  fixed bug in getindex when passed "."
  added code to skip classification

  Revision 1.147  2001/10/11 18:00:56  wn
  fixed bug in free_syns - wasn't freeing synset pointed to by nextform

  Revision 1.146  2001/07/27 14:32:41  wn
  fixed order of adjective markers

  Revision 1.145  2001/06/19 15:01:22  wn
  commed out include for setutil.h

  Revision 1.144  2001/05/30 16:24:17  wn
  changed is_defined to return unsigned int

  Revision 1.143  2001/03/30 17:13:00  wn
  fixed is_defined - wasn't setting coords for verbs

  Revision 1.142  2001/03/29 16:18:03  wn
  added newline before output from FREQ search

  Revision 1.141  2001/03/29 16:11:39  wn
  added code to tractptrs to print direct antonyms nicer

  Revision 1.140  2001/03/27 18:47:41  wn
  removed tcflag

  Revision 1.139  2001/03/27 16:47:44  wn
  updated is_defined for holonyms and meronyms

  Revision 1.138  2000/08/14 16:04:24  wn
  changed 'get_index' to call sub to do work
  added code for nominalizations

  Revision 1.137  1998/08/11 18:07:11  wn
  minor fixes: free synptr space before rreturning if error; remove
  useless statement in free_syns

 * Revision 1.136  1998/08/07  17:51:32  wn
 * added COORDS to traceptrs_ds and findtheinfo_ds
 * fixed getsearchsense code to only happen in parse_synset
 *
 * Revision 1.135  1998/08/07  13:04:24  wn
 * *** empty log message ***
 *
 * Revision 1.134  1997/11/07  16:27:36  wn
 * cleanup calls to traceptrs
 *
 * Revision 1.133  1997/10/16  17:13:08  wn
 * fixed bug in add_topnode when index == 0
 *
 * Revision 1.132  1997/09/05  15:33:18  wn
 * change printframes to only print generic frames if specific example not found
 *
 * Revision 1.131  1997/09/02  16:31:18  wn
 * changed includes
 *
 * Revision 1.130  1997/09/02  14:43:23  wn
 * added code to test wnrelease in parse_synset and WNOverview
 *
 * Revision 1.129  1997/08/29  20:45:25  wn
 * added location sanity check on parse_synset
 *
 * Revision 1.128  1997/08/29  18:35:03  wn
 * a bunch of additional cleanups; added code to traceptrs_ds to
 * tore wordnet sense number for each word; added wnresults structure;
 * terminate holo/mero search at highest level having holo/mero
 *
 * Revision 1.127  1997/08/28  17:26:46  wn
 * Changed "n senses from tagged data" to "n senses from tagged texts"
 * in the overview.
 *
 * Revision 1.126  1997/08/27  13:26:07  wn
 * trivial change in wngrep (initialized count to zero)
 *
 * Revision 1.125  1997/08/26  21:13:14  wn
 * Grep now runs quickly because it doesn't call the doevents callback
 * after each line of the search.
 *
 * Revision 1.124  1997/08/26  20:11:23  wn
 * massive cleanups to print functions
 *
 * Revision 1.123  1997/08/26  15:04:18  wn
 * I think I got it this time; replaced goto skipit with int skipit flag
 * to make compiling easier on the Mac.
 *
 * Revision 1.122  1997/08/26  14:43:40  wn
 * In an effort to avoid compilation errors on the
 * Mac caused by the use of a "goto", I had tried to replace it with
 * an if block, but had done so improperly.  This is the restored version
 * from before.  Next check-in will have it properly replaced with flags.
 *
 * Revision 1.121  1997/08/25  15:54:21  wn
 * *** empty log message ***
 *
 * Revision 1.120  1997/08/22  21:06:02  wn
 * added code to use wnsnsflag to print wn sense number after each word
 *
 * Revision 1.119  1997/08/22  20:52:09  wn
 * cleaned up findtheinfo and other fns a bit
 *
 * Revision 1.118  1997/08/21  20:59:20  wn
 * grep now uses strstr instead of regexp searches.  the old version is
 * still there but commented out.
 *
 * Revision 1.117  1997/08/21  18:41:30  wn
 * now eliminates duplicates on search returns, but not yet in overview
 *
  Revision 1.116  1997/08/13 17:23:45  wn
  fixed mac defines

 * Revision 1.115  1997/08/08  20:56:33  wn
 * now uses built-in grep
 *
 * Revision 1.114  1997/08/08  19:15:41  wn
 * added code to read attest_cnt field in index file.
 * made searchbuffer fixed size
 * added WNOverview (OVERVIEW) search
 * added offsetflag to print synset offset before synset
 *
 * Revision 1.113  1997/08/05  14:20:29  wn
 * changed printbuffer to not realloc space, removed calls to stopsearch()
 *
 * Revision 1.112  1997/07/25  17:30:03  wn
 * various cleanups for release 1.6
 *
  Revision 1.111  1997/07/11 20:20:04  wn
  Added interface_doevents code for making searches interruptable in single-threaded environments.

 * Revision 1.110  1997/07/10  19:01:57  wn
 * changed evca stuff
 *
  Revision 1.109  1997/04/22 19:59:08  wn
  allow pertainyms to have antonyms

 * Revision 1.108  1996/09/17  20:05:01  wn
 * cleaned up EVCA code
 *
 * Revision 1.107  1996/08/16  18:34:13  wn
 * fixed minor bug in findcousins
 *
 * Revision 1.106  1996/07/17  14:02:17  wn
 * Added Kohl's verb example sentences. See getexample() and findExample().
 *
 * Revision 1.105  1996/06/14  18:49:49  wn
 * upped size of tmpbuf
 *
 * Revision 1.104  1996/02/08  16:42:30  wn
 * added some newlines to separate output and clear out tmpbuf
 * so invalid searches return empty string
 *
 * Revision 1.103  1995/11/30  14:54:53  wn
 * added grouped search for verbs
 *
 * Revision 1.102  1995/07/19  13:17:38  bagyenda
 * *** empty log message ***
 *
 * Revision 1.101  1995/07/18  19:15:30  wn
 * *** empty log message ***
 *
 * Revision 1.100  1995/07/18  18:56:24  bagyenda
 * New implementation of grouped searches --Paul.
 *
 * Revision 1.99  1995/06/30  19:21:23  wn
 * added code to findtheinfo_ds to link additional word forms
 * onto synset chain
 *
 * Revision 1.98  1995/06/12  18:33:51  wn
 * Minor change to getindex() -- Paul.
 *
 * Revision 1.97  1995/06/09  14:46:42  wn
 * *** empty log message ***
 *
 * Revision 1.96  1995/06/09  14:32:49  wn
 * changed code for PPLPTR and PERTPTR to print synsets pointed to
 *
 * Revision 1.95  1995/06/01  15:50:34  wn
 * cleanup of code dealing with various hyphenations
 * 
 */
