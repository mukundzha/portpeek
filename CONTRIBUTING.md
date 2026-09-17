# Contributing

Install the editable package with test dependencies:

```sh
python3 -m pip install -e '.[test]'
```

Run the test suite with `python3 -m pytest`. Keep platform-specific behavior in `src/portpeek/discovery/` and keep CLI behavior platform-independent.
