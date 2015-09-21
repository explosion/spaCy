#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)
AC_INIT(WordNet, 3.0, [wordnet@princeton.edu], wordnet)
AC_CONFIG_SRCDIR([config.h.in])
AC_CONFIG_HEADER([config.h])

# Checks for programs.
AC_PROG_CC
AC_PROG_RANLIB
AC_PROG_INSTALL

# Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADERS([locale.h malloc.h stdlib.h string.h])

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.
AC_FUNC_MALLOC
AC_CHECK_FUNCS([strchr strdup strrchr strstr strtol])

# Set HAVE_LANGINFO_CODESET if nl_langinfo is found

AC_LANGINFO_CODESET

AM_INIT_AUTOMAKE(WordNet, 3.0)

SC_PATH_TCLCONFIG
SC_PATH_TKCONFIG
SC_LOAD_TCLCONFIG
SC_LOAD_TKCONFIG

# Set default installation prefix.
AC_PREFIX_DEFAULT([/usr/local/WordNet-3.0])
ac_prefix=$prefix
if test "x$ac_prefix" = "xNONE"; then
    ac_prefix=$ac_default_prefix
fi
AC_SUBST(ac_prefix)
AH_TEMPLATE([DEFAULTPATH],[The default search path for WordNet data files])
AC_DEFINE_UNQUOTED(DEFAULTPATH, ["$ac_prefix/dict"], [Default installation prefix.])

#AC_DEFINE_UNQUOTED(DEFAULTPATH,"${prefix}/dict")

# This doesn't do anything
AC_CONFIG_COMMANDS([default])

AC_CONFIG_FILES(Makefile dict/Makefile doc/Makefile doc/html/Makefile doc/man/Makefile doc/pdf/Makefile doc/ps/Makefile include/Makefile include/tk/Makefile
src/Makefile lib/Makefile lib/wnres/Makefile)

AC_OUTPUT

AC_MSG_RESULT(
[
WordNet is now configured

  Installation directory:               ${prefix}

  To build and install WordNet:

    make
    make install

  To run, environment variables should be set as follows:

    PATH - include ${bindir}
    WNHOME - if not using default installation location, set to ${prefix}

    See INSTALL file for details and additional environment variables
    which may need to be set on your system.

])
