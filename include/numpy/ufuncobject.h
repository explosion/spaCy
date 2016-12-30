#ifndef Py_UFUNCOBJECT_H
#define Py_UFUNCOBJECT_H

#include <numpy/npy_math.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * The legacy generic inner loop for a standard element-wise or
 * generalized ufunc.
 */
typedef void (*PyUFuncGenericFunction)
            (char **args,
             npy_intp *dimensions,
             npy_intp *strides,
             void *innerloopdata);

/*
 * The most generic one-dimensional inner loop for
 * a standard element-wise ufunc. This typedef is also
 * more consistent with the other NumPy function pointer typedefs
 * than PyUFuncGenericFunction.
 */
typedef void (PyUFunc_StridedInnerLoopFunc)(
                char **dataptrs, npy_intp *strides,
                npy_intp count,
                NpyAuxData *innerloopdata);

/*
 * The most generic one-dimensional inner loop for
 * a masked standard element-wise ufunc. "Masked" here means that it skips
 * doing calculations on any items for which the maskptr array has a true
 * value.
 */
typedef void (PyUFunc_MaskedStridedInnerLoopFunc)(
                char **dataptrs, npy_intp *strides,
                char *maskptr, npy_intp mask_stride,
                npy_intp count,
                NpyAuxData *innerloopdata);

/* Forward declaration for the type resolver and loop selector typedefs */
struct _tagPyUFuncObject;

/*
 * Given the operands for calling a ufunc, should determine the
 * calculation input and output data types and return an inner loop function.
 * This function should validate that the casting rule is being followed,
 * and fail if it is not.
 *
 * For backwards compatibility, the regular type resolution function does not
 * support auxiliary data with object semantics. The type resolution call
 * which returns a masked generic function returns a standard NpyAuxData
 * object, for which the NPY_AUXDATA_FREE and NPY_AUXDATA_CLONE macros
 * work.
 *
 * ufunc:             The ufunc object.
 * casting:           The 'casting' parameter provided to the ufunc.
 * operands:          An array of length (ufunc->nin + ufunc->nout),
 *                    with the output parameters possibly NULL.
 * type_tup:          Either NULL, or the type_tup passed to the ufunc.
 * out_dtypes:        An array which should be populated with new
 *                    references to (ufunc->nin + ufunc->nout) new
 *                    dtypes, one for each input and output. These
 *                    dtypes should all be in native-endian format.
 *
 * Should return 0 on success, -1 on failure (with exception set),
 * or -2 if Py_NotImplemented should be returned.
 */
typedef int (PyUFunc_TypeResolutionFunc)(
                                struct _tagPyUFuncObject *ufunc,
                                NPY_CASTING casting,
                                PyArrayObject **operands,
                                PyObject *type_tup,
                                PyArray_Descr **out_dtypes);

/*
 * Given an array of DTypes as returned by the PyUFunc_TypeResolutionFunc,
 * and an array of fixed strides (the array will contain NPY_MAX_INTP for
 * strides which are not necessarily fixed), returns an inner loop
 * with associated auxiliary data.
 *
 * For backwards compatibility, there is a variant of the inner loop
 * selection which returns an inner loop irrespective of the strides,
 * and with a void* static auxiliary data instead of an NpyAuxData *
 * dynamically allocatable auxiliary data.
 *
 * ufunc:             The ufunc object.
 * dtypes:            An array which has been populated with dtypes,
 *                    in most cases by the type resolution funciton
 *                    for the same ufunc.
 * fixed_strides:     For each input/output, either the stride that
 *                    will be used every time the function is called
 *                    or NPY_MAX_INTP if the stride might change or
 *                    is not known ahead of time. The loop selection
 *                    function may use this stride to pick inner loops
 *                    which are optimized for contiguous or 0-stride
 *                    cases.
 * out_innerloop:     Should be populated with the correct ufunc inner
 *                    loop for the given type.
 * out_innerloopdata: Should be populated with the void* data to
 *                    be passed into the out_innerloop function.
 * out_needs_api:     If the inner loop needs to use the Python API,
 *                    should set the to 1, otherwise should leave
 *                    this untouched.
 */
typedef int (PyUFunc_LegacyInnerLoopSelectionFunc)(
                            struct _tagPyUFuncObject *ufunc,
                            PyArray_Descr **dtypes,
                            PyUFuncGenericFunction *out_innerloop,
                            void **out_innerloopdata,
                            int *out_needs_api);
typedef int (PyUFunc_InnerLoopSelectionFunc)(
                            struct _tagPyUFuncObject *ufunc,
                            PyArray_Descr **dtypes,
                            npy_intp *fixed_strides,
                            PyUFunc_StridedInnerLoopFunc **out_innerloop,
                            NpyAuxData **out_innerloopdata,
                            int *out_needs_api);
typedef int (PyUFunc_MaskedInnerLoopSelectionFunc)(
                            struct _tagPyUFuncObject *ufunc,
                            PyArray_Descr **dtypes,
                            PyArray_Descr *mask_dtype,
                            npy_intp *fixed_strides,
                            npy_intp fixed_mask_stride,
                            PyUFunc_MaskedStridedInnerLoopFunc **out_innerloop,
                            NpyAuxData **out_innerloopdata,
                            int *out_needs_api);

typedef struct _tagPyUFuncObject {
        PyObject_HEAD
        /*
         * nin: Number of inputs
         * nout: Number of outputs
         * nargs: Always nin + nout (Why is it stored?)
         */
        int nin, nout, nargs;

        /* Identity for reduction, either PyUFunc_One or PyUFunc_Zero */
        int identity;

        /* Array of one-dimensional core loops */
        PyUFuncGenericFunction *functions;
        /* Array of funcdata that gets passed into the functions */
        void **data;
        /* The number of elements in 'functions' and 'data' */
        int ntypes;

        /* Does not appear to be used */
        int check_return;

        /* The name of the ufunc */
        char *name;

        /* Array of type numbers, of size ('nargs' * 'ntypes') */
        char *types;

        /* Documentation string */
        char *doc;

        void *ptr;
        PyObject *obj;
        PyObject *userloops;

        /* generalized ufunc parameters */

        /* 0 for scalar ufunc; 1 for generalized ufunc */
        int core_enabled;
        /* number of distinct dimension names in signature */
        int core_num_dim_ix;

        /*
         * dimension indices of input/output argument k are stored in
         * core_dim_ixs[core_offsets[k]..core_offsets[k]+core_num_dims[k]-1]
         */

        /* numbers of core dimensions of each argument */
        int *core_num_dims;
        /*
         * dimension indices in a flatted form; indices
         * are in the range of [0,core_num_dim_ix)
         */
        int *core_dim_ixs;
        /*
         * positions of 1st core dimensions of each
         * argument in core_dim_ixs
         */
        int *core_offsets;
        /* signature string for printing purpose */
        char *core_signature;

        /*
         * A function which resolves the types and fills an array
         * with the dtypes for the inputs and outputs.
         */
        PyUFunc_TypeResolutionFunc *type_resolver;
        /*
         * A function which returns an inner loop written for
         * NumPy 1.6 and earlier ufuncs. This is for backwards
         * compatibility, and may be NULL if inner_loop_selector
         * is specified.
         */
        PyUFunc_LegacyInnerLoopSelectionFunc *legacy_inner_loop_selector;
        /*
         * A function which returns an inner loop for the new mechanism
         * in NumPy 1.7 and later. If provided, this is used, otherwise
         * if NULL the legacy_inner_loop_selector is used instead.
         */
        PyUFunc_InnerLoopSelectionFunc *inner_loop_selector;
        /*
         * A function which returns a masked inner loop for the ufunc.
         */
        PyUFunc_MaskedInnerLoopSelectionFunc *masked_inner_loop_selector;
} PyUFuncObject;

#include "arrayobject.h"

#define UFUNC_ERR_IGNORE 0
#define UFUNC_ERR_WARN   1
#define UFUNC_ERR_RAISE  2
#define UFUNC_ERR_CALL   3
#define UFUNC_ERR_PRINT  4
#define UFUNC_ERR_LOG    5

        /* Python side integer mask */

#define UFUNC_MASK_DIVIDEBYZERO 0x07
#define UFUNC_MASK_OVERFLOW 0x3f
#define UFUNC_MASK_UNDERFLOW 0x1ff
#define UFUNC_MASK_INVALID 0xfff

#define UFUNC_SHIFT_DIVIDEBYZERO 0
#define UFUNC_SHIFT_OVERFLOW     3
#define UFUNC_SHIFT_UNDERFLOW    6
#define UFUNC_SHIFT_INVALID      9


/* platform-dependent code translates floating point
   status to an integer sum of these values
*/
#define UFUNC_FPE_DIVIDEBYZERO  1
#define UFUNC_FPE_OVERFLOW      2
#define UFUNC_FPE_UNDERFLOW     4
#define UFUNC_FPE_INVALID       8

/* Error mode that avoids look-up (no checking) */
#define UFUNC_ERR_DEFAULT       0

#define UFUNC_OBJ_ISOBJECT      1
#define UFUNC_OBJ_NEEDS_API     2

   /* Default user error mode */
#define UFUNC_ERR_DEFAULT2                               \
        (UFUNC_ERR_WARN << UFUNC_SHIFT_DIVIDEBYZERO) +  \
        (UFUNC_ERR_WARN << UFUNC_SHIFT_OVERFLOW) +      \
        (UFUNC_ERR_WARN << UFUNC_SHIFT_INVALID)

#if NPY_ALLOW_THREADS
#define NPY_LOOP_BEGIN_THREADS do {if (!(loop->obj & UFUNC_OBJ_NEEDS_API)) _save = PyEval_SaveThread();} while (0);
#define NPY_LOOP_END_THREADS   do {if (!(loop->obj & UFUNC_OBJ_NEEDS_API)) PyEval_RestoreThread(_save);} while (0);
#else
#define NPY_LOOP_BEGIN_THREADS
#define NPY_LOOP_END_THREADS
#endif

/*
 * UFunc has unit of 1, and the order of operations can be reordered
 * This case allows reduction with multiple axes at once.
 */
#define PyUFunc_One 1
/*
 * UFunc has unit of 0, and the order of operations can be reordered
 * This case allows reduction with multiple axes at once.
 */
#define PyUFunc_Zero 0
/*
 * UFunc has no unit, and the order of operations cannot be reordered.
 * This case does not allow reduction with multiple axes at once.
 */
#define PyUFunc_None -1
/*
 * UFunc has no unit, and the order of operations can be reordered
 * This case allows reduction with multiple axes at once.
 */
#define PyUFunc_ReorderableNone -2

#define UFUNC_REDUCE 0
#define UFUNC_ACCUMULATE 1
#define UFUNC_REDUCEAT 2
#define UFUNC_OUTER 3


typedef struct {
        int nin;
        int nout;
        PyObject *callable;
} PyUFunc_PyFuncData;

/* A linked-list of function information for
   user-defined 1-d loops.
 */
typedef struct _loop1d_info {
        PyUFuncGenericFunction func;
        void *data;
        int *arg_types;
        struct _loop1d_info *next;
} PyUFunc_Loop1d;


#include "__ufunc_api.h"

#define UFUNC_PYVALS_NAME "UFUNC_PYVALS"

#define UFUNC_CHECK_ERROR(arg) \
        do {if ((((arg)->obj & UFUNC_OBJ_NEEDS_API) && PyErr_Occurred()) || \
            ((arg)->errormask && \
             PyUFunc_checkfperr((arg)->errormask, \
                                (arg)->errobj, \
                                &(arg)->first))) \
                goto fail;} while (0)

/* This code checks the IEEE status flags in a platform-dependent way */
/* Adapted from Numarray  */

#if (defined(__unix__) || defined(unix)) && !defined(USG)
#include <sys/param.h>
#endif

/*  OSF/Alpha (Tru64)  ---------------------------------------------*/
#if defined(__osf__) && defined(__alpha)

#include <machine/fpu.h>

#define UFUNC_CHECK_STATUS(ret) { \
        unsigned long fpstatus; \
         \
        fpstatus = ieee_get_fp_control(); \
        /* clear status bits as well as disable exception mode if on */ \
        ieee_set_fp_control( 0 ); \
        ret = ((IEEE_STATUS_DZE & fpstatus) ? UFUNC_FPE_DIVIDEBYZERO : 0) \
                | ((IEEE_STATUS_OVF & fpstatus) ? UFUNC_FPE_OVERFLOW : 0) \
                | ((IEEE_STATUS_UNF & fpstatus) ? UFUNC_FPE_UNDERFLOW : 0) \
                | ((IEEE_STATUS_INV & fpstatus) ? UFUNC_FPE_INVALID : 0); \
        }

/* MS Windows -----------------------------------------------------*/
#elif defined(_MSC_VER)

#include <float.h>

  /* Clear the floating point exception default of Borland C++ */
#if defined(__BORLANDC__)
#define UFUNC_NOFPE _control87(MCW_EM, MCW_EM);
#endif

#define UFUNC_CHECK_STATUS(ret) { \
        int fpstatus = (int) _clearfp(); \
         \
        ret = ((SW_ZERODIVIDE & fpstatus) ? UFUNC_FPE_DIVIDEBYZERO : 0) \
                | ((SW_OVERFLOW & fpstatus) ? UFUNC_FPE_OVERFLOW : 0) \
                | ((SW_UNDERFLOW & fpstatus) ? UFUNC_FPE_UNDERFLOW : 0) \
                | ((SW_INVALID & fpstatus) ? UFUNC_FPE_INVALID : 0); \
        }

/* Solaris --------------------------------------------------------*/
/* --------ignoring SunOS ieee_flags approach, someone else can
**         deal with that! */
#elif defined(sun) || defined(__BSD__) || defined(__OpenBSD__) || \
      (defined(__FreeBSD__) && (__FreeBSD_version < 502114)) || \
      defined(__NetBSD__)
#include <ieeefp.h>

#define UFUNC_CHECK_STATUS(ret) { \
        int fpstatus; \
         \
        fpstatus = (int) fpgetsticky(); \
        ret = ((FP_X_DZ  & fpstatus) ? UFUNC_FPE_DIVIDEBYZERO : 0) \
                | ((FP_X_OFL & fpstatus) ? UFUNC_FPE_OVERFLOW : 0) \
                | ((FP_X_UFL & fpstatus) ? UFUNC_FPE_UNDERFLOW : 0) \
                | ((FP_X_INV & fpstatus) ? UFUNC_FPE_INVALID : 0); \
        (void) fpsetsticky(0); \
        }

#elif defined(__GLIBC__) || defined(__APPLE__) || \
      defined(__CYGWIN__) || defined(__MINGW32__) || \
      (defined(__FreeBSD__) && (__FreeBSD_version >= 502114))

#if defined(__GLIBC__) || defined(__APPLE__) || \
    defined(__MINGW32__) || defined(__FreeBSD__)
#include <fenv.h>
#endif

#define UFUNC_CHECK_STATUS(ret) { \
        int fpstatus = (int) fetestexcept(FE_DIVBYZERO | FE_OVERFLOW | \
                                          FE_UNDERFLOW | FE_INVALID); \
        ret = ((FE_DIVBYZERO  & fpstatus) ? UFUNC_FPE_DIVIDEBYZERO : 0) \
                | ((FE_OVERFLOW   & fpstatus) ? UFUNC_FPE_OVERFLOW : 0) \
                | ((FE_UNDERFLOW  & fpstatus) ? UFUNC_FPE_UNDERFLOW : 0) \
                | ((FE_INVALID    & fpstatus) ? UFUNC_FPE_INVALID : 0); \
        (void) feclearexcept(FE_DIVBYZERO | FE_OVERFLOW | \
                             FE_UNDERFLOW | FE_INVALID); \
}

#elif defined(_AIX)

#include <float.h>
#include <fpxcp.h>

#define UFUNC_CHECK_STATUS(ret) { \
        fpflag_t fpstatus; \
 \
        fpstatus = fp_read_flag(); \
        ret = ((FP_DIV_BY_ZERO & fpstatus) ? UFUNC_FPE_DIVIDEBYZERO : 0) \
                | ((FP_OVERFLOW & fpstatus) ? UFUNC_FPE_OVERFLOW : 0)   \
                | ((FP_UNDERFLOW & fpstatus) ? UFUNC_FPE_UNDERFLOW : 0) \
                | ((FP_INVALID & fpstatus) ? UFUNC_FPE_INVALID : 0); \
        fp_swap_flag(0); \
}

#else

#define NO_FLOATING_POINT_SUPPORT
#define UFUNC_CHECK_STATUS(ret) { \
    ret = 0; \
  }

#endif

/*
 * THESE MACROS ARE DEPRECATED.
 * Use npy_set_floatstatus_* in the npymath library.
 */
#define generate_divbyzero_error() npy_set_floatstatus_divbyzero()
#define generate_overflow_error() npy_set_floatstatus_overflow()

  /* Make sure it gets defined if it isn't already */
#ifndef UFUNC_NOFPE
#define UFUNC_NOFPE
#endif


#ifdef __cplusplus
}
#endif
#endif /* !Py_UFUNCOBJECT_H */
