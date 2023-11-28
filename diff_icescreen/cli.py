from pathlib import Path
from typing import Annotated, Optional
import pandas as pd
import typer
from .core import IceScreenCompare


DEFAULT_COL_SUBSET = "CDS_locus_tag,Profile_name,Id_of_blast_most_similar_ref_SP"

app = typer.Typer()


def read_dataset_ref(path: str) -> dict[str, str]:
    phylum_mapping = (
        pd.read_csv(path)[["h_accession", "tax_phylum"]]
        .drop_duplicates()
        .set_index("h_accession")["tax_phylum"]
        .to_dict()
    )
    return phylum_mapping


def add_phylum_column(df: pd.DataFrame, phylum_mapping: dict[str, str]) -> pd.DataFrame:
    df["phylum"] = df.index.get_level_values("Genome_accession").map(phylum_mapping)
    df = df.set_index("phylum", append=True).reorder_levels(
        ["phylum", "Genome_accession", "CDS_num"]
    )
    return df


@app.command()
def main(
    ref_folder: Annotated[Path, typer.Argument(help="Path to the ref folder.")],
    cmp_folder: Annotated[Path, typer.Argument(help="Path to the cmp folder.")],
    col_subset: Annotated[
        str,
        typer.Option(
            "--col", "-c", help="Specify the columns to compare, separated by comma."
        ),
    ] = DEFAULT_COL_SUBSET,
    output_file: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Specify the output file.")
    ] = None,
    dataset_ref_file: Annotated[
        Optional[Path],
        typer.Option(
            "--ref",
            "-r",
            help=(
                "Specify the dataset ref file that contain at least the columns "
                "h_accession and tax_phylum. Used to add the phylum column to the "
                "output. If not specified, the phylum column will be missing."
            ),
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Quiet mode. In that case no output will be printed to stdout.",
        ),
    ] = False,
):
    col_subset = col_subset.split(",")
    comparator = IceScreenCompare(
        ref_folder.absolute(), cmp_folder.absolute(), col_subset=col_subset
    )
    df_diff = comparator.compare_all()

    if dataset_ref_file is not None:
        phylum_mapping = read_dataset_ref(dataset_ref_file.absolute())
        df_diff = add_phylum_column(df_diff, phylum_mapping)

    df_diff = df_diff.sort_index()

    if output_file:
        df_diff.to_csv(output_file.absolute(), sep="\t")
    if not quiet:
        typer.echo(df_diff.to_csv(sep="\t"))


if __name__ == "__main__":
    app()
