# Icescreen results compare with `diff-icescreen`

Main goal : to show the diff between two ICEscreen results.

## Installation

```bash
pip install git+https://.../diff-icescreen.git
```

## Usage

cli is accessible with either the `icediff` cli (if your user bin is in $PATH,
usually `~/.local/bin`) or `python -m diff_icescreen.cli` from the proper python
environment.

See extensive help `diff-icescreen --help`

usage example :

```bash
icediff --ref=data/datasetref.csv --col=CDS_locus_tag,Profile_name -o data/diff.csv data/v0/ data/v1/
```

in the ref data :

```bash
icediff --ref=data/5-complete_datasetref.csv --col=CDS_locus_tag,Profile_name,Id_of_blast_most_similar_ref_SP data/ICEscreen_raw_output_v0/ data/ICEscreen_raw_output_v1/
```

Will output the tabular diff in the stdout :

```
                        CDS_locus_tag   CDS_locus_tag   Profile_name    Profile_name    Id_of_blast_most_similar_ref_SP Id_of_blast_most_similar_ref_SP
                        ref     cmp     ref     cmp     ref     cmp
phylum  Genome_accession        CDS_num
Actinomycetota  CP002802        5449            Merci_5527              T4SS_MOBP1
Bacillota       NC_004368       241     GBS_RS01565             PHA_IME_A1              CAD45884
Bacillota       NC_004368       978                     t4cp1_MODIF     t4cp1
Bacillota       NC_004368       990                     T4SS_MOBP2_MODIF        T4SS_MOBP2      CAD46654_MODIF  CAD46654
Bacillota       NC_004368       1350    GBS_RS07190             t4cp1           CAD47023
Bacillota       NC_004368       4770            Mesci_4836              Phage_integrase         CCC18874
Bacillota       NC_004368       4843            Mesci_4912              t4cp2
Pseudomonadota  CP002447        3785                                    AAO80999        AAO80333
Pseudomonadota  CP002447        3846                    t4cp1   Phage_integrase
```

You can then use tooling like csvtools, csvkit or tabview to investigate the
diff.

```bash
icediff ... | tabview -
```

## Development

The project use [poetry] to manage
dependencies. You can install the project in dev mode with:

```bash
poetry install
```

In the root of the project.

This will create an environment dedicated to the project in
`~/.cache/pypoetry/virtualenvs/` with the dependencies needed installed.

You can then run the cli with:

```bash
poetry run icediff
```

All the files should use [black] formatting and [ruff] linting.

[poetry]: https://github.com/python-poetry/poetry
[black]: https://github.com/psf/black
[ruff]: https://github.com/charliermarsh/ruff