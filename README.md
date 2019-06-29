# vrProjector

## About
vrProjector package that does something

## Installing
```console
$ pip install .
```

## Usage
```python
>>> import vrProjector
>> vrProjector.DummySpit()
'BLARGH'
>>> import vrProjector.core.base
>>> vrProjector.core.base.DummySpit()
'BLARGH_BASE'
```

## Runing tests:

```console
$ python setup.py test
running test
running egg_info
creating vrProjector.egg-info
writing vrProjector.egg-info/PKG-INFO
writing dependency_links to vrProjector.egg-info/dependency_links.txt
writing top-level names to vrProjector.egg-info/top_level.txt
writing manifest file 'vrProjector.egg-info/SOURCES.txt'
reading manifest file 'vrProjector.egg-info/SOURCES.txt'
writing manifest file 'vrProjector.egg-info/SOURCES.txt'
running build_ext
test_base (vrProjector.tests.test_base.TestBase) ... ok
test_root (vrProjector.tests.test_base.TestBase) ... ok

----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
```

^`Built using [miniPyProjectMaker](https://github.com/bhautikj/miniPyProjectMaker)`^