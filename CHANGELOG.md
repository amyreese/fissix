fissix
======

v21.11.13
---------

Bug fix release:

* Fix: except fixer checks against the value of a node (#42, #43)
* Improved urllib fixer to include `__version__` (#44)
* Tested against Python 3.9 (#32, #45)

```
$ git shortlog -s v21.6.6...v21.11.13
     1	Chris Elion
     3	David Grant
     5	John Reese
     2	Thomas Grainger
```


v21.6.6
-------

Feature release:

- New fixer for `sorted()` and `list.sort()` (#25)
- Token helpers for LBrace, RBrace, and Colon (#34)
- Fix for `long` used as keyword argument name (#28)
- Fix for exceptions with "as" keyword (#40)
- Support for running tests outside of source tree (#31)
- Documentation for fixers, general API, and usage (#23, #24, #29)

```
$ git shortlog -s v20.8.0...v21.6.6
     1	Ashley Whetter
     1	David Grant
    16	John Reese
     1	Langston Barrett
     5	Larry Huang
     1	Nicholas D Steeves
     1	Stefano Rivera
     2	Thomas Grainger
```


v20.8.0
-------

Bugfix release:

- Include dict in iterating contexts (#17)
- Better testing (#14, #21)
- Clarified license permissions (#11)

```
$ git shortlog -s v20.5.1...v20.8.0
     1	Ashley Whetter
     8	John Reese
     7	Thomas Grainger
```


v20.5.1
-------

Feature release

- Imported upstream changes from 3.9
- Support for 3.8 syntax changes

```
$ git shortlog -s v19.2b1...v20.5.1
    19	John Reese
     1	Thomas Grainger
     1	Tim Hatch
```


v20.5.0
-------

Feature release

- Imported upstream changes from 3.9
- Support for 3.8 syntax changes

```
$ git shortlog -s v19.2b1...v20.5.0
    19	John Reese
     1	Thomas Grainger
     1	Tim Hatch
```


v19.2b1
-------

Update 19.2b1:

- Merge upstream v3.8.0a2-22-ged1deb0719

```
$ git shortlog -s v19.1b1...v19.2b1
     4	John Reese
```


v19.1b1
-------

Beta release 19.1b1:

- Merged lib2to3 v3.7.0a4-1294-ge0b5b2096e

```
$ git shortlog -s v18.6a6...v19.1b1
     7	John Reese
```


v18.6a6
-------

Feature release:

- Base/Leaf/Node now all share the same type information for `.children`

```
$ git shortlog -s v18.6a5...v18.6a6
     1	John Reese
```


v18.6a5
-------

Bugfix:

- Include grammar text files in source distribution

```
$ git shortlog -s v18.6a4...v18.6a5
     1	John Reese
```


v18.6a4
-------

Bugfix:

- generated pickle helper now returns string instead of Path object

```
$ git shortlog -s v18.6a3...v18.6a4
     1	John Reese
```


v18.6a3
-------

Fix MANIFEST

```
$ git shortlog -s v18.6a2...v18.6a3
     1	John Reese
```


v18.6a2
-------

Minor release:

- Add manifest file to include readme/license/requirements

```
$ git shortlog -s v18.6a1...v18.6a2
     2	John Reese
```


v18.6a1
-------

Feature release:

- store grammar pickles in user cache dir
- smoke tests

```
$ git shortlog -s v18.6a0...v18.6a1
    13	John Reese
```


v18.6a0
-------

Initial release:

- straight import of lib2to3, renamed to fissix

```
$ git shortlog -s v18.6a0
     5	John Reese
```

