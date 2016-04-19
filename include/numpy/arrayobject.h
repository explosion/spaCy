
/* This expects the following variables to be defined (besides
   the usual ones from pyconfig.h

   SIZEOF_LONG_DOUBLE -- sizeof(long double) or sizeof(double) if no
                         long double is present on platform.
   CHAR_BIT       --     number of bits in a char (usually 8)
                         (should be in limits.h)

*/

#ifndef Py_ARRAYOBJECT_H
#define Py_ARRAYOBJECT_H

#include "ndarrayobject.h"
#include "npy_interrupt.h"

#ifdef NPY_NO_PREFIX
#include "noprefix.h"
#endif

#endif
