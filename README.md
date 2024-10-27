# Reference Manager

This project helps manage academic references, allowing users to download papers, resolve references, and process CSV files containing reference information.

## Installation

```
git clone git@github.com:fedemengo/paperetriever.git && cd paperetriever
pip install -e .
```


## Usage

Download article

```
> paperetriever download "ref-here" -o ./test_papers
```

Download refs for an articles

```
> paperetriever resolve-references "ref-here" -o ./test_refs --download-refs
```

