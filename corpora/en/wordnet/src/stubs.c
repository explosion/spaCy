/* This file acts as a gateway between Tcl and the Wordnet C library.  It
** contains stubs for all the commands added to the default Tcl and Tk set
** for this Wordnet application, as well as the routine that initializes them.
*/

#ifdef _WINDOWS
#include <windows.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tcl.h>
#include <tk.h>
#include <wn.h>

static char *Id = "$Id: stubs.c,v 1.7 2005/04/29 19:01:57 wn Exp $";

static char resultbuf[SEARCHBUF];

#ifndef HAVE_LANGINFO_CODESET

char *nl_langinfo(int item) {

   static char val[4] = "Sun";
   return(val);
}
#endif 

/* This command (accessed by the name "findvalidsearches" in Tcl) returns
** a bitfield that describes all the available searches for a given word
** as the given part of speech.  The calls to morphstr are used to extract
** the search word's base form.
*/

int wn_findvalidsearches (ClientData clientData, Tcl_Interp *interp, 
   int argc, char *argv[]) {
   unsigned int bitfield;
   static char bitfieldstr[32];
   char *morph;
   int pos;
   if (argc != 3) {
      interp -> result = 
         "usage: findvalidsearches searchword partofspeechnum";
      return TCL_ERROR;
   }
   pos = atoi (argv[2]);
   bitfield = is_defined (argv[1], pos);
   if ((morph = morphstr (argv[1], pos)) != NULL) {
      do {
         bitfield |= is_defined (morph, pos);
      } while ((morph = morphstr (NULL, pos)) != NULL);
   }
   sprintf (bitfieldstr, "%u", bitfield);
   interp -> result = bitfieldstr;
   return TCL_OK;
}

/* This command returns a bitfield of unsigned integer length with all bits
** zero except for the specified bit, which is one.  This can be binary
** and-ed with another bitfield to check if the other bitfield has the
** specified bit set to one.  This is particularly useful for interpreting
** the results of findvalidsearches.  Invoked from Tcl as "bit".
*/

int wn_bit (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   unsigned int bitfield;
   static char bitfieldstr[32];
   int whichbit;
   if (argc != 2) {
      interp -> result = "usage: bit bitnum";
      return TCL_ERROR;
   }
   whichbit = atoi (argv[1]);
   bitfield = bit (whichbit);
   sprintf (bitfieldstr, "%u", bitfield);
   interp -> result = bitfieldstr;
   return TCL_OK;
} 

/* This command performs the requested search and returns the results in 
** a string buffer.  This is the primary purpose of the whole program.
** It is invoked from Tcl simply as "search".
*/

int wn_search (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   int pos, searchtype, sense;
   char *morph;
   if (argc != 5) {
      interp -> result = 
         "usage: search searchword partofspeechnum searchtypenum sensenum";
      return TCL_ERROR;
   }
   pos = atoi (argv[2]);
   searchtype = atoi (argv[3]);
   sense = atoi (argv[4]);
   strcpy (resultbuf, findtheinfo (argv[1], pos, searchtype, sense));
   if ((morph = morphstr (argv[1], pos)) != NULL) {
      do {
         strcat (resultbuf, findtheinfo (morph, pos, searchtype, sense));
      } while ((morph = morphstr (NULL, pos)) != NULL);
   }
   interp -> result = resultbuf;
   return TCL_OK;
}

/* This command, accessed in Tcl as "glosses" sets the flag that tells the
** search engine whether or not to include textual glosses in the search
** results.
*/
 
int wn_glosses (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 2) {
      interp -> result = "usage: glosses [1 | 0]";
      return TCL_ERROR;
   }
   dflag = atoi (argv[1]);
   return TCL_OK;
}

/* This command, accessed in Tcl as "fileinfo" sets the flag that tells the
** search engine whether or not to include lex filenames in the search
** results.
*/
 
int wn_fileinfo (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 2) {
      interp -> result = "usage: fileinfo [1 | 0]";
      return TCL_ERROR;
   }
   fileinfoflag = atoi (argv[1]);
   return TCL_OK;
}

/* This command, accessed in Tcl as "byteoffset" sets the flag that tells the
** search engine whether or not to include byte offsets into the lex files 
** in the search results.
*/
 
int wn_byteoffset (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 2) {
      interp -> result = "usage: byteoffset [1 | 0]";
      return TCL_ERROR;
   }
   offsetflag = atoi (argv[1]);
   return TCL_OK;
}

/* This command, accessed in Tcl as "senseflag" sets the flag that tells the
** search engine whether or not to report the WordNet sense for each word
** returned.
*/
 
int wn_senseflag (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 2) {
      interp -> result = "usage: senseflag [1 | 0]";
      return TCL_ERROR;
   }
   wnsnsflag = atoi (argv[1]);
   return TCL_OK;
}

/* This command, accessed in Tcl as "contextualhelp" returns a string of
** text which describes, to the less-experienced user, exactly what each
** type of search does.
*/

int wn_contextualhelp (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   int pos, searchtype;
   if (argc != 3) {
      interp -> result = "usage: contextualhelp partofspeechnum searchtypenum";
      return TCL_ERROR;
   }
   pos = atoi (argv[1]);
   searchtype = atoi (argv[2]);
   interp -> result = helptext[pos][searchtype];
   return TCL_OK;
}

/* This command, accessed in Tcl as "reopendb" reopens the WordNet database.
*/

int wn_reopendb (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 1) {
      interp -> result = "usage: reopendb";
      return TCL_ERROR;
   }
   re_wninit ();
   return TCL_OK;
}

/* This command, accessed in Tcl as "abortsearch" causes the library to
** stop whatever search it is currently in the middle of performing.
*/

int wn_abortsearch (ClientData clientData, Tcl_Interp *interp,
   int argc, char *argv[]) {
   if (argc != 1) {
      interp -> result = "usage: abortsearch";
      return TCL_ERROR;
   }
   abortsearch = 1;
   return TCL_OK;
}

/* This is a callback function invoked by the WordNet search engine every so
** often, to allow the interface to respond to events (especially the pressing
** of a stop button) during the search.
*/

void tkwn_doevents (void) {
   while (Tcl_DoOneEvent (TCL_WINDOW_EVENTS | TCL_DONT_WAIT) != 0) {}
}

/* This is a callback function invoked by the WordNet search engine whenever
** it needs to display an error message.  Its implementation is platform
** specific, since it uses the native error reporting mechanism.
*/

int tkwn_displayerror (char *msg) {
#ifdef _WINDOWS
   MessageBeep (MB_ICONEXCLAMATION);
   MessageBox (NULL, msg, "WordNet Library Error",
      MB_ICONEXCLAMATION | MB_OK | MB_TASKMODAL | MB_SETFOREGROUND);
#else
   fprintf (stderr, "%s", msg);
#endif
   return -1;
}

/* This is the initialization routine, which is called from tkAppInit.c 
** when the program starts.  It registers each new command with the Tcl
** interpreter.
*/ 

int Wordnet_Init (Tcl_Interp *interp) {
   interface_doevents_func = tkwn_doevents;
   display_message = tkwn_displayerror;
   wninit ();
   Tcl_CreateCommand (interp, "findvalidsearches", (void *) 
      wn_findvalidsearches, (ClientData) NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "bit", (void *) wn_bit, (ClientData) NULL, 
      (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "search", (void *) wn_search, (ClientData) 
      NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "glosses", (void *) wn_glosses, (ClientData) 
      NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "fileinfo", (void *) wn_fileinfo, (ClientData) 
      NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "byteoffset", (void *) wn_byteoffset, 
      (ClientData) NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "senseflag", (void *) wn_senseflag, 
      (ClientData) NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "contextualhelp", (void *) wn_contextualhelp,
      (ClientData) NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "reopendb", (void *) wn_reopendb, (ClientData)
      NULL, (Tcl_CmdDeleteProc *) NULL);
   Tcl_CreateCommand (interp, "abortsearch", (void *) wn_abortsearch, 
      (ClientData) NULL, (Tcl_CmdDeleteProc *) NULL);
   return TCL_OK;
}

