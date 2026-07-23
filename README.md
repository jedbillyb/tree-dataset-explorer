# tree-dataset-explorer

A small, dependency-free command-line tool for exploring a dataset of trees. It reads `trees\_data.csv` (200 trees) and lets you look up individual records, draw random samples, filter by criteria, and compute summary statistics (mean, median, standard deviation, etc.).

Uses only the Python standard library (`argparse`, `csv`, `random`, `statistics`).

## Data

`trees\_data.csv` has 200 rows with these columns:

| Column | Meaning |
| - | - |
| Tree | Unique tree id |
| Type | Species (Oak, Elm, Birch, Beech, Yew) |
| Girth | Trunk girth in metres |
| Age | Age in years |
| Disease | 1 = diseased, 0 = healthy |
| Height | Height (relative scale) |
| Value | Estimated value |


## Usage

```
python trees.py \<command\> \[options\]
```

The numeric columns available to `--field` are: `Girth`, `Age`, `Height`, `Value`.

### `show` - print records by id

```
python trees.py show 1 3 42
```

### `sample` - random sample + statistics

Pulls a random sample (default 20) and summarises the chosen field for both the sample and the whole population.

```
python trees.py sample                    \# 20 trees, Girth  
python trees.py sample -n 30 --field Age  \# 30 trees, summarise Age  
python trees.py sample --seed 7           \# reproducible sample  
python trees.py sample --replace          \# allow duplicates
```

### `stats` - population statistics

```
python trees.py stats                     \# every numeric column  
python trees.py stats --by-type           \# Girth broken down by species  
python trees.py stats --by-type --field Value
```

### `filter` - list trees matching criteria

```
python trees.py filter --type Oak --min-girth 3.0  
python trees.py filter --diseased --field Girth  
python trees.py filter --min-age 100 --max-girth 5.0
```

Filter options: `--type`, `--min-girth`, `--max-girth`, `--min-age`, `--diseased`, `--healthy`, `--field`.

## Requirements

Python 3.8+ - no third-party packages.

