/*
  
  morph.c - WordNet search code morphology functions
  
*/

#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif
#include "wn.h"

#ifdef _WINDOWS
#include <windows.h>
#include <windowsx.h>
#define EXCFILE	"%s\\%s.exc"
#else
#define EXCFILE	"%s/%s.exc"
#endif

static char *Id = "$Id: morph.c,v 1.67 2006/11/14 21:00:23 wn Exp $";

static char *sufx[] ={ 
    /* Noun suffixes */
    "s", "ses", "xes", "zes", "ches", "shes", "men", "ies",
    /* Verb suffixes */
    "s", "ies", "es", "es", "ed", "ed", "ing", "ing",
    /* Adjective suffixes */
    "er", "est", "er", "est"
};

static char *addr[] ={ 
    /* Noun endings */
    "", "s", "x", "z", "ch", "sh", "man", "y",
    /* Verb endings */
    "", "y", "e", "", "e", "", "e", "",
    /* Adjective endings */
    "", "", "e", "e"
};

static int offsets[NUMPARTS] = { 0, 0, 8, 16 };
static int cnts[NUMPARTS] = { 0, 8, 8, 4 };
static char msgbuf[256];

#define NUMPREPS	15

static struct {
    char *str;
    int strlen;
} prepositions[NUMPREPS] = {
    "to", 2,
    "at", 2,
    "of", 2,
    "on", 2,
    "off", 3,
    "in", 2,
    "out", 3,
    "up", 2,
    "down", 4,
    "from", 4,
    "with", 4,
    "into", 4,
    "for", 3,
    "about", 5,
    "between", 7,
};

static FILE *exc_fps[NUMPARTS + 1];

static int do_init();
static int strend(char *, char *);
static char *wordbase(char *, int);
static int hasprep(char *, int);
static char *exc_lookup(char *, int);
static char *morphprep(char *);

/* Open exception list files */

int morphinit(void)
{
    static int done = 0;
    static int openerr = 0;

    if (!done) {
      if (OpenDB) {		/* make sure WN database files are open */
            if (!(openerr = do_init()))
	        done = 1;
	} else
	    openerr = -1;
    }

    return(openerr);
}

/* Close exception list files and reopen */
int re_morphinit(void)
{
    int i;

    for (i = 1; i <= NUMPARTS; i++) {
	if (exc_fps[i] != NULL) {
	    fclose(exc_fps[i]); exc_fps[i] = NULL;
	}
    }

    return(OpenDB ? do_init() : -1);
}

static int do_init(void)
{
    int i, openerr;
#ifdef _WINDOWS
    HKEY hkey;
    DWORD dwType, dwSize;
#else
    char *env;
#endif
    char searchdir[256], fname[256];

    openerr = 0;

    /* Find base directory for database.  If set, use WNSEARCHDIR.
       If not set, check for WNHOME/dict, otherwise use DEFAULTPATH. */

#ifdef _WINDOWS
    if (RegOpenKeyEx(HKEY_LOCAL_MACHINE, TEXT("Software\\WordNet\\3.0"),
		     0, KEY_READ, &hkey) == ERROR_SUCCESS) {
	dwSize = sizeof(searchdir);
	RegQueryValueEx(hkey, TEXT("WNHome"),
			NULL, &dwType, searchdir, &dwSize);
	RegCloseKey(hkey);
	strcat(searchdir, DICTDIR);
    }
    else if (RegOpenKeyEx(HKEY_CURRENT_USER, TEXT("Software\\WordNet\\3.0"),
		     0, KEY_READ, &hkey) == ERROR_SUCCESS) {
	dwSize = sizeof(searchdir);
	RegQueryValueEx(hkey, TEXT("WNHome"),
			NULL, &dwType, searchdir, &dwSize);
	RegCloseKey(hkey);
	strcat(searchdir, DICTDIR);
    } else
	sprintf(searchdir, DEFAULTPATH);
#else
    if ((env = getenv("WNSEARCHDIR")) != NULL)
	strcpy(searchdir, env);
    else if ((env = getenv("WNHOME")) != NULL)
	sprintf(searchdir, "%s%s", env, DICTDIR);
    else
	strcpy(searchdir, DEFAULTPATH);
#endif

    for (i = 1; i <= NUMPARTS; i++) {
	sprintf(fname, EXCFILE, searchdir, partnames[i]);
	if ((exc_fps[i] = fopen(fname, "r")) == NULL) {
	    sprintf(msgbuf,
		    "WordNet library error: Can't open exception file(%s)\n\n",
		    fname);
	    display_message(msgbuf);
	    openerr = -1;
	}
    }
    return(openerr);
}

/* Try to find baseform (lemma) of word or collocation in POS.
   Works like strtok() - first call is with string, subsequent calls
   with NULL argument return additional baseforms for original string. */

char *morphstr(char *origstr, int pos)
{
    static char searchstr[WORDBUF], str[WORDBUF];
    static int svcnt, svprep;
    char word[WORDBUF], *tmp;
    int cnt, st_idx = 0, end_idx;
    int prep;
    char *end_idx1, *end_idx2;
    char *append;
    
    if (pos == SATELLITE)
	pos = ADJ;

    /* First time through for this string */

    if (origstr != NULL) {
	/* Assume string hasn't had spaces substitued with '_' */
	strtolower(strsubst(strcpy(str, origstr), ' ', '_'));
	searchstr[0] = '\0';
	cnt = cntwords(str, '_');
	svprep = 0;

	/* first try exception list */

	if ((tmp = exc_lookup(str, pos)) && strcmp(tmp, str)) {
	    svcnt = 1;		/* force next time to pass NULL */
	    return(tmp);
	}

	/* Then try simply morph on original string */

	if (pos != VERB && (tmp = morphword(str, pos)) && strcmp(tmp, str))
	    return(tmp);

	if (pos == VERB && cnt > 1 && (prep = hasprep(str, cnt))) {
	    /* assume we have a verb followed by a preposition */
	    svprep = prep;
	    return(morphprep(str));
	} else {
	    svcnt = cnt = cntwords(str, '-');
	    while (origstr && --cnt) {
		end_idx1 = strchr(str + st_idx, '_');
		end_idx2 = strchr(str + st_idx, '-');
		if (end_idx1 && end_idx2) {
		    if (end_idx1 < end_idx2) {
			end_idx = (int)(end_idx1 - str);
			append = "_";
		    } else {
			end_idx = (int)(end_idx2 - str);
			append = "-";
		    }
		} else {
		    if (end_idx1) {
			end_idx = (int)(end_idx1 - str);
			append = "_";
		    } else {
			end_idx = (int)(end_idx2 - str);
			append = "-";
		    }
		}	
		if (end_idx < 0) return(NULL);		/* shouldn't do this */
		strncpy(word, str + st_idx, end_idx - st_idx);
		word[end_idx - st_idx] = '\0';
		if(tmp = morphword(word, pos))
		    strcat(searchstr,tmp);
		else
		    strcat(searchstr,word);
		strcat(searchstr, append);
		st_idx = end_idx + 1;
	    }
	    
	    if(tmp = morphword(strcpy(word, str + st_idx), pos)) 
		strcat(searchstr,tmp);
	    else
		strcat(searchstr,word);
	    if(strcmp(searchstr, str) && is_defined(searchstr,pos))
		return(searchstr);
	    else
		return(NULL);
	}
    } else {			/* subsequent call on string */
	if (svprep) {		/* if verb has preposition, no more morphs */
	    svprep = 0;
	    return(NULL);
	} else if (svcnt == 1)
	    return(exc_lookup(NULL, pos));
	else {
	    svcnt = 1;
	    if ((tmp = exc_lookup(str, pos)) && strcmp(tmp, str))
		return(tmp);
	    else
		return(NULL);
	}
    }
}

/* Try to find baseform (lemma) of individual word in POS */
char *morphword(char *word, int pos)
{
    int offset, cnt;
    int i;
    static char retval[WORDBUF];
    char *tmp, tmpbuf[WORDBUF], *end;
    
    sprintf(retval,"");
    sprintf(tmpbuf, "");
    end = "";
    
    if(word == NULL) 
	return(NULL);

    /* first look for word on exception list */
    
    if((tmp = exc_lookup(word, pos)) != NULL)
	return(tmp);		/* found it in exception list */

    if (pos == ADV) {		/* only use exception list for adverbs */
	return(NULL);
    }
    if (pos == NOUN) {
	if (strend(word, "ful")) {
	    cnt = strrchr(word, 'f') - word;
	    strncat(tmpbuf, word, cnt);
	    end = "ful";
	} else 
	    /* check for noun ending with 'ss' or short words */
	    if (strend(word, "ss") || (strlen(word) <= 2))
		return(NULL);
    }

/* If not in exception list, try applying rules from tables */

    if (tmpbuf[0] == '\0')
	strcpy(tmpbuf, word);

    offset = offsets[pos];
    cnt = cnts[pos];

    for(i = 0; i < cnt; i++){
	strcpy(retval, wordbase(tmpbuf, (i + offset)));
	if(strcmp(retval, tmpbuf) && is_defined(retval, pos)) {
	    strcat(retval, end);
	    return(retval);
	}
    }
    return(NULL);
}

static int strend(char *str1, char *str2)
{
    char *pt1;
    
    if(strlen(str2) >= strlen(str1))
	return(0);
    else {
	pt1=str1;
	pt1=strchr(str1,0);
	pt1=pt1-strlen(str2);
	return(!strcmp(pt1,str2));
    }
}

static char *wordbase(char *word, int ender)
{
    char *pt1;
    static char copy[WORDBUF];
    
    strcpy(copy, word);
    if(strend(copy,sufx[ender])) {
	pt1=strchr(copy,'\0');
	pt1 -= strlen(sufx[ender]);
	*pt1='\0';
	strcat(copy,addr[ender]);
    }
    return(copy);
}

static int hasprep(char *s, int wdcnt)
{
    /* Find a preposition in the verb string and return its
       corresponding word number. */

    int i, wdnum;

    for (wdnum = 2; wdnum <= wdcnt; wdnum++) {
	s = strchr(s, '_');
	for (s++, i = 0; i < NUMPREPS; i++)
	    if (!strncmp(s, prepositions[i].str, prepositions[i].strlen) &&
		(s[prepositions[i].strlen] == '_' ||
		 s[prepositions[i].strlen] == '\0'))
		return(wdnum);
    }
    return(0);
}
 
static char *exc_lookup(char *word, int pos)
{
    static char line[WORDBUF], *beglp, *endlp;
    char *excline;
    int found = 0;

    if (exc_fps[pos] == NULL)
	return(NULL);

    /* first time through load line from exception file */
    if(word != NULL){
	if ((excline = bin_search(word, exc_fps[pos])) != NULL) {
	    strcpy(line, excline);
	    endlp = strchr(line,' ');
	} else
	    endlp = NULL;
    }
    if(endlp && *(endlp + 1) != ' '){
	beglp = endlp + 1;
	while(*beglp && *beglp == ' ') beglp++;
	endlp = beglp;
	while(*endlp && *endlp != ' ' && *endlp != '\n') endlp++;
	if(endlp != beglp){
	    *endlp='\0';
	    return(beglp);
	}
    }
    beglp = NULL;
    endlp = NULL;
    return(NULL);
}

static char *morphprep(char *s)
{
    char *rest, *exc_word, *lastwd = NULL, *last;
    int i, offset, cnt;
    char word[WORDBUF], end[WORDBUF];
    static char retval[WORDBUF];

    /* Assume that the verb is the first word in the phrase.  Strip it
       off, check for validity, then try various morphs with the
       rest of the phrase tacked on, trying to find a match. */

    rest = strchr(s, '_');
    last = strrchr(s, '_');
    if (rest != last) {		/* more than 2 words */
	if (lastwd = morphword(last + 1, NOUN)) {
	    strncpy(end, rest, last - rest + 1);
	    end[last-rest+1] = '\0';
	    strcat(end, lastwd);
	}
    }
    
    strncpy(word, s, rest - s);
    word[rest - s] = '\0';
    for (i = 0, cnt = strlen(word); i < cnt; i++)
	if (!isalnum((unsigned char)(word[i]))) return(NULL);

    offset = offsets[VERB];
    cnt = cnts[VERB];

    /* First try to find the verb in the exception list */

    if ((exc_word = exc_lookup(word, VERB)) &&
	strcmp(exc_word, word)) {

	sprintf(retval, "%s%s", exc_word, rest);
	if(is_defined(retval, VERB))
	    return(retval);
	else if (lastwd) {
	    sprintf(retval, "%s%s", exc_word, end);
	    if(is_defined(retval, VERB))
		return(retval);
	}
    }
    
    for (i = 0; i < cnt; i++) {
	if ((exc_word = wordbase(word, (i + offset))) &&
	    strcmp(word, exc_word)) { /* ending is different */

	    sprintf(retval, "%s%s", exc_word, rest);
	    if(is_defined(retval, VERB))
		return(retval);
	    else if (lastwd) {
		sprintf(retval, "%s%s", exc_word, end);
		if(is_defined(retval, VERB))
		    return(retval);
	    }
	}
    }
    sprintf(retval, "%s%s", word, rest);
    if (strcmp(s, retval))
	return(retval);
    if (lastwd) {
	sprintf(retval, "%s%s", word, end);
	if (strcmp(s, retval))
	    return(retval);
    }
    return(NULL);
}

/* 
 * Revision 1.1  91/09/25  15:39:47  wn
 * Initial revision
 * 
 */
