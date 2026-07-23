# tree-dataset-explorer

A small, dependency-free command-line tool for exploring a dataset of trees. It reads `trees_data.csv` (200 trees) and lets you look up individual records, draw random samples, filter by criteria, and compute summary statistics (mean, median, standard deviation, etc.).

Uses only the Python standard library (`argparse`, `csv`, `random`, `statistics`).

## Data

`trees_data.csv` has 200 rows with these columns:

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
python trees.py <command> [options]
```

The numeric columns available to `--field` are: `Girth`, `Age`, `Height`, `Value`.

### `show` - print records by id

```
python trees.py show 1 3 42
```

### `sample` - random sample + statistics

Pulls a random sample (default 20) and summarises the chosen field for both the sample and the whole population. It also prints the type mix (count and percentage per species) for the sample and the population, so you can see how representative the draw is.

```
python trees.py sample                    # 20 trees, Girth
python trees.py sample -n 30 --field Age  # 30 trees, summarise Age
python trees.py sample --seed 7           # reproducible sample
python trees.py sample --replace          # allow duplicates
python trees.py sample -n 40 --stratified # keep each species' population share
```

You normally get exactly `-n` results. Without `--replace` they are all distinct trees; with `--replace` picks can repeat (so you may get fewer unique trees, and can request more than the 200 in the dataset). `--stratified` is the one exception (see below).

**`--stratified`** draws the sample so each species' share matches its share of the whole population, allocating the sample size across types in proportion to their size (largest-remainder rounding). Every species that exists in the data is guaranteed at least one tree: a rare type whose proportional share would round to zero (e.g. Yew at 2.5%, only ~0.5 of a 20-tree sample) is rounded up to 1 instead. That seat is added on top, so the actual sample can be slightly larger than the requested `-n` -- the output says so, e.g. "sample of 21 trees (rounded up from 20)". Use a larger `n` if you want the percentages to line up more tightly.

### `stats` - population statistics

```
python trees.py stats                     # every numeric column
python trees.py stats --by-type           # type mix + Girth broken down by species
python trees.py stats --by-type --field Value
```

`--by-type` prints a "Type mix" table (count and percentage per species) followed by the chosen field summarised for each species.

### `filter` - list trees matching criteria

```
python trees.py filter --type Oak --min-girth 3.0
python trees.py filter --diseased --field Girth
python trees.py filter --min-age 100 --max-girth 5.0
```

Filter options: `--type`, `--min-girth`, `--max-girth`, `--min-age`, `--diseased`, `--healthy`, `--field`.

## Requirements

Python 3.8+ - no third-party packages.
