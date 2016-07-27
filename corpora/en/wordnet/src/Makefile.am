EXTRA_DIST = wnb
bin_PROGRAMS = wn wishwn
bin_SCRIPTS = wnb
wishwn_SOURCES = tkAppInit.c stubs.c
wishwn_CPPFLAGS = $(INCLUDES) 
wishwn_LDADD = $(LDADD) $(TK_LIB_SPEC) $(TCL_LIB_SPEC) $(TK_LIBS)
wn_SOURCES = wn.c
wn_CPPFLAGS = $(INCLUDES)
wn_LDADD = $(LDADD)
LDADD = -L$(top_srcdir)/lib -lWN
INCLUDES = -I$(top_srcdir) -I$(top_srcdir)/include $(TCL_INCLUDE_SPEC) $(TK_XINCLUDES) -I$(TK_PREFIX)/include

