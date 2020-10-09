..
   Fixer documentation originally from CPython/Doc/library/2to3.rst
   Modified here to render in standard Sphinx directives


Fixers
------

Each step of transforming code is encapsulated in a fixer.  The command
``python -m fissix -l`` lists them.  Each can be turned on
and off individually.  They are described here in more detail.


.. attribute:: apply

   Removes usage of :func:`apply`.  For example ``apply(function, *args,
   **kwargs)`` is converted to ``function(*args, **kwargs)``.

.. attribute:: asserts

   Replaces deprecated :mod:`unittest` method names with the correct ones.

   ================================  ==========================================
   From                              To
   ================================  ==========================================
   ``failUnlessEqual(a, b)``         :meth:`assertEqual(a, b)
                                     <unittest.TestCase.assertEqual>`
   ``assertEquals(a, b)``            :meth:`assertEqual(a, b)
                                     <unittest.TestCase.assertEqual>`
   ``failIfEqual(a, b)``             :meth:`assertNotEqual(a, b)
                                     <unittest.TestCase.assertNotEqual>`
   ``assertNotEquals(a, b)``         :meth:`assertNotEqual(a, b)
                                     <unittest.TestCase.assertNotEqual>`
   ``failUnless(a)``                 :meth:`assertTrue(a)
                                     <unittest.TestCase.assertTrue>`
   ``assert_(a)``                    :meth:`assertTrue(a)
                                     <unittest.TestCase.assertTrue>`
   ``failIf(a)``                     :meth:`assertFalse(a)
                                     <unittest.TestCase.assertFalse>`
   ``failUnlessRaises(exc, cal)``    :meth:`assertRaises(exc, cal)
                                     <unittest.TestCase.assertRaises>`
   ``failUnlessAlmostEqual(a, b)``   :meth:`assertAlmostEqual(a, b)
                                     <unittest.TestCase.assertAlmostEqual>`
   ``assertAlmostEquals(a, b)``      :meth:`assertAlmostEqual(a, b)
                                     <unittest.TestCase.assertAlmostEqual>`
   ``failIfAlmostEqual(a, b)``       :meth:`assertNotAlmostEqual(a, b)
                                     <unittest.TestCase.assertNotAlmostEqual>`
   ``assertNotAlmostEquals(a, b)``   :meth:`assertNotAlmostEqual(a, b)
                                     <unittest.TestCase.assertNotAlmostEqual>`
   ================================  ==========================================

.. attribute:: basestring

   Converts :class:`basestring` to :class:`str`.

.. attribute:: buffer

   Converts :class:`buffer` to :class:`memoryview`.  This fixer is optional
   because the :class:`memoryview` API is similar but not exactly the same as
   that of :class:`buffer`.

.. attribute:: dict

   Fixes dictionary iteration methods.  :meth:`dict.iteritems` is converted to
   :meth:`dict.items`, :meth:`dict.iterkeys` to :meth:`dict.keys`, and
   :meth:`dict.itervalues` to :meth:`dict.values`.  Similarly,
   :meth:`dict.viewitems`, :meth:`dict.viewkeys` and :meth:`dict.viewvalues` are
   converted respectively to :meth:`dict.items`, :meth:`dict.keys` and
   :meth:`dict.values`.  It also wraps existing usages of :meth:`dict.items`,
   :meth:`dict.keys`, and :meth:`dict.values` in a call to :class:`list`.

.. attribute:: except

   Converts ``except X, T`` to ``except X as T``.

.. attribute:: exec

   Converts the ``exec`` statement to the :func:`exec` function.

.. attribute:: execfile

   Removes usage of :func:`execfile`.  The argument to :func:`execfile` is
   wrapped in calls to :func:`open`, :func:`compile`, and :func:`exec`.

.. attribute:: exitfunc

   Changes assignment of :attr:`sys.exitfunc` to use of the :mod:`atexit`
   module.

.. attribute:: filter

   Wraps :func:`filter` usage in a :class:`list` call.

.. attribute:: funcattrs

   Fixes function attributes that have been renamed.  For example,
   ``my_function.func_closure`` is converted to ``my_function.__closure__``.

.. attribute:: future

   Removes ``from __future__ import new_feature`` statements.

.. attribute:: getcwdu

   Renames :func:`os.getcwdu` to :func:`os.getcwd`.

.. attribute:: has_key

   Changes ``dict.has_key(key)`` to ``key in dict``.

.. attribute:: idioms

   This optional fixer performs several transformations that make Python code
   more idiomatic.  Type comparisons like ``type(x) is SomeClass`` and
   ``type(x) == SomeClass`` are converted to ``isinstance(x, SomeClass)``.
   ``while 1`` becomes ``while True``.  This fixer also tries to make use of
   :func:`sorted` in appropriate places.  For example, this block ::

       L = list(some_iterable)
       L.sort()

   is changed to ::

      L = sorted(some_iterable)

.. attribute:: import

   Detects sibling imports and converts them to relative imports.

.. attribute:: imports

   Handles module renames in the standard library.

.. attribute:: imports2

   Handles other modules renames in the standard library.  It is separate from
   the :attribute:`imports` fixer only because of technical limitations.

.. attribute:: input

   Converts ``input(prompt)`` to ``eval(input(prompt))``.

.. attribute:: intern

   Converts :func:`intern` to :func:`sys.intern`.

.. attribute:: isinstance

   Fixes duplicate types in the second argument of :func:`isinstance`.  For
   example, ``isinstance(x, (int, int))`` is converted to ``isinstance(x,
   int)`` and ``isinstance(x, (int, float, int))`` is converted to
   ``isinstance(x, (int, float))``.

.. attribute:: itertools_imports

   Removes imports of :func:`itertools.ifilter`, :func:`itertools.izip`, and
   :func:`itertools.imap`.  Imports of :func:`itertools.ifilterfalse` are also
   changed to :func:`itertools.filterfalse`.

.. attribute:: itertools

   Changes usage of :func:`itertools.ifilter`, :func:`itertools.izip`, and
   :func:`itertools.imap` to their built-in equivalents.
   :func:`itertools.ifilterfalse` is changed to :func:`itertools.filterfalse`.

.. attribute:: long

   Renames :class:`long` to :class:`int`.

.. attribute:: map

   Wraps :func:`map` in a :class:`list` call.  It also changes ``map(None, x)``
   to ``list(x)``.  Using ``from future_builtins import map`` disables this
   fixer.

.. attribute:: metaclass

   Converts the old metaclass syntax (``__metaclass__ = Meta`` in the class
   body) to the new (``class X(metaclass=Meta)``).

.. attribute:: methodattrs

   Fixes old method attribute names.  For example, ``meth.im_func`` is converted
   to ``meth.__func__``.

.. attribute:: ne

   Converts the old not-equal syntax, ``<>``, to ``!=``.

.. attribute:: next

   Converts the use of iterator's :meth:`~iterator.next` methods to the
   :func:`next` function.  It also renames :meth:`next` methods to
   :meth:`~iterator.__next__`.

.. attribute:: nonzero

   Renames :meth:`__nonzero__` to :meth:`~object.__bool__`.

.. attribute:: numliterals

   Converts octal literals into the new syntax.

.. attribute:: operator

   Converts calls to various functions in the :mod:`operator` module to other,
   but equivalent, function calls.  When needed, the appropriate ``import``
   statements are added, e.g. ``import collections.abc``.  The following mapping
   are made:

   ==================================  =============================================
   From                                To
   ==================================  =============================================
   ``operator.isCallable(obj)``        ``callable(obj)``
   ``operator.sequenceIncludes(obj)``  ``operator.contains(obj)``
   ``operator.isSequenceType(obj)``    ``isinstance(obj, collections.abc.Sequence)``
   ``operator.isMappingType(obj)``     ``isinstance(obj, collections.abc.Mapping)``
   ``operator.isNumberType(obj)``      ``isinstance(obj, numbers.Number)``
   ``operator.repeat(obj, n)``         ``operator.mul(obj, n)``
   ``operator.irepeat(obj, n)``        ``operator.imul(obj, n)``
   ==================================  =============================================

.. attribute:: paren

   Add extra parenthesis where they are required in list comprehensions.  For
   example, ``[x for x in 1, 2]`` becomes ``[x for x in (1, 2)]``.

.. attribute:: print

   Converts the ``print`` statement to the :func:`print` function.

.. attribute:: raise

   Converts ``raise E, V`` to ``raise E(V)``, and ``raise E, V, T`` to ``raise
   E(V).with_traceback(T)``.  If ``E`` is a tuple, the translation will be
   incorrect because substituting tuples for exceptions has been removed in 3.0.

.. attribute:: raw_input

   Converts :func:`raw_input` to :func:`input`.

.. attribute:: reduce

   Handles the move of :func:`reduce` to :func:`functools.reduce`.

.. attribute:: reload

   Converts :func:`reload` to :func:`importlib.reload`.

.. attribute:: renames

   Changes :data:`sys.maxint` to :data:`sys.maxsize`.

.. attribute:: repr

   Replaces backtick repr with the :func:`repr` function.

.. attribute:: set_literal

   Replaces use of the :class:`set` constructor with set literals.  This fixer
   is optional.

.. attribute:: standarderror

   Renames :exc:`StandardError` to :exc:`Exception`.

.. attribute:: sys_exc

   Changes the deprecated :data:`sys.exc_value`, :data:`sys.exc_type`,
   :data:`sys.exc_traceback` to use :func:`sys.exc_info`.

.. attribute:: throw

   Fixes the API change in generator's :meth:`throw` method.

.. attribute:: tuple_params

   Removes implicit tuple parameter unpacking.  This fixer inserts temporary
   variables.

.. attribute:: types

   Fixes code broken from the removal of some members in the :mod:`types`
   module.

.. attribute:: unicode

   Renames :class:`unicode` to :class:`str`.

.. attribute:: urllib

   Handles the rename of :mod:`urllib` and :mod:`urllib2` to the :mod:`urllib`
   package.

.. attribute:: ws_comma

   Removes excess whitespace from comma separated items.  This fixer is
   optional.

.. attribute:: xrange

   Renames :func:`xrange` to :func:`range` and wraps existing :func:`range`
   calls with :class:`list`.

.. attribute:: xreadlines

   Changes ``for x in file.xreadlines()`` to ``for x in file``.

.. attribute:: zip

   Wraps :func:`zip` usage in a :class:`list` call.  This is disabled when
   ``from future_builtins import zip`` appears.

.. attribute:: sorted

   Wraps the argument :meth:`cmp` in :func:`sorted` by
   :function:`functools.cmp_to_key` and pass it to :func:`sorted` through
   the :meth:`key` argument.
