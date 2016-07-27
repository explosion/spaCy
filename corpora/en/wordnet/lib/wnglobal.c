/*

   wnglobal.c - global variables used by various WordNet applications

   $Id: wnglobal.c,v 1.56 2006/11/14 21:00:34 wn Exp $

*/

#ifndef NULL
#define NULL	0
#endif

char *wnrelease = "3.0";

/* Lexicographer file names and numbers */

char *lexfiles[] = {
    "adj.all",			/* 0 */
    "adj.pert",			/* 1 */
    "adv.all",			/* 2 */
    "noun.Tops",		/* 3 */
    "noun.act",			/* 4 */
    "noun.animal",		/* 5 */
    "noun.artifact",		/* 6 */
    "noun.attribute",		/* 7 */
    "noun.body",		/* 8 */
    "noun.cognition",		/* 9 */
    "noun.communication",	/* 10 */
    "noun.event",		/* 11 */
    "noun.feeling",		/* 12 */
    "noun.food",		/* 13 */
    "noun.group",		/* 14 */
    "noun.location",		/* 15 */
    "noun.motive",		/* 16 */
    "noun.object",		/* 17 */
    "noun.person",		/* 18 */
    "noun.phenomenon",		/* 19 */
    "noun.plant",		/* 20 */
    "noun.possession",		/* 21 */
    "noun.process",		/* 22 */
    "noun.quantity",		/* 23 */
    "noun.relation",		/* 24 */
    "noun.shape",		/* 25 */
    "noun.state",		/* 26 */
    "noun.substance",		/* 27 */
    "noun.time",		/* 28 */
    "verb.body",		/* 29 */
    "verb.change",		/* 30 */
    "verb.cognition",		/* 31 */
    "verb.communication",	/* 32 */
    "verb.competition",		/* 33 */
    "verb.consumption",		/* 34 */
    "verb.contact",		/* 35 */
    "verb.creation",		/* 36 */
    "verb.emotion",		/* 37 */
    "verb.motion",		/* 38 */
    "verb.perception",		/* 39 */
    "verb.possession",		/* 40 */
    "verb.social",		/* 41 */
    "verb.stative",		/* 42 */
    "verb.weather",		/* 43 */
    "adj.ppl",			/* 44 */
};

/* Pointer characters and searches */

char *ptrtyp[]={
    "",				/* 0 not used */
    "!",			/* 1 ANTPTR */
    "@",			/* 2 HYPERPTR */
    "~",			/* 3 HYPOPTR */
    "*",			/* 4 ENTAILPTR */
    "&",			/* 5 SIMPTR */
    "#m",			/* 6 ISMEMBERPTR */
    "#s",			/* 7 ISSTUFFPTR */
    "#p",			/* 8 ISPARTPTR */
    "%m",			/* 9 HASMEMBERPTR */
    "%s",			/* 10 HASSTUFFPTR */
    "%p",			/* 11 HASPARTPTR */
    "%",			/* 12 MERONYM */
    "#",			/* 13 HOLONYM */
    ">",			/* 14 CAUSETO */
    "<",			/* 15 PPLPTR */
    "^",			/* 16 SEEALSO */
    "\\",			/* 17 PERTPTR */
    "=",			/* 18 ATTRIBUTE */
    "$",			/* 19 VERBGROUP */
    "+",		        /* 20 NOMINALIZATIONS */
    ";",			/* 21 CLASSIFICATION */
    "-",			/* 22 CLASS */
/* additional searches, but not pointers.  */
    "",				/* SYNS */
    "",				/* FREQ */
    "+",			/* FRAMES */
    "",				/* COORDS */
    "",				/* RELATIVES */
    "",				/* HMERONYM */
    "",				/* HHOLONYM */
    "",				/* WNGREP */
    "",				/* OVERVIEW */
    ";c",			/* CLASSIF_CATEGORY */
    ";u",			/* CLASSIF_USAGE */
    ";r",			/* CLASSIF_REGIONAL */
    "-c",			/* CLASS_CATEGORY */
    "-u",			/* CLASS_USAGE */
    "-r",			/* CLASS_REGIONAL */
    "@i",			/* INSTANCE */
    "~i",			/* INSTANCES */
    NULL,
};

char *partnames[]={ "", "noun", "verb", "adj", "adv", NULL };
char partchars[] = " nvara";	/* add char for satellites to end */
char *adjclass[] = { "", "(p)", "(a)", "(ip)" };

/* Text of verb sentence frames */

char *frametext[] = {
    "",
    "Something ----s",
    "Somebody ----s",
    "It is ----ing",
    "Something is ----ing PP",
    "Something ----s something Adjective/Noun",
    "Something ----s Adjective/Noun",
    "Somebody ----s Adjective",
    "Somebody ----s something",
    "Somebody ----s somebody",
    "Something ----s somebody",
    "Something ----s something",
    "Something ----s to somebody",
    "Somebody ----s on something",
    "Somebody ----s somebody something",
    "Somebody ----s something to somebody",
    "Somebody ----s something from somebody",
    "Somebody ----s somebody with something",
    "Somebody ----s somebody of something",
    "Somebody ----s something on somebody",
    "Somebody ----s somebody PP",
    "Somebody ----s something PP",
    "Somebody ----s PP",
    "Somebody's (body part) ----s",
    "Somebody ----s somebody to INFINITIVE",
    "Somebody ----s somebody INFINITIVE",
    "Somebody ----s that CLAUSE",
    "Somebody ----s to somebody",
    "Somebody ----s to INFINITIVE",
    "Somebody ----s whether INFINITIVE",
    "Somebody ----s somebody into V-ing something",
    "Somebody ----s something with something",
    "Somebody ----s INFINITIVE",
    "Somebody ----s VERB-ing",
    "It ----s that CLAUSE",
    "Something ----s INFINITIVE",
    ""
};
