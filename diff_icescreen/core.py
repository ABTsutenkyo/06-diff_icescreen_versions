from typing import Dict, List, Optional, Union
import pandas as pd
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AccessionDiff:
    ref_file: Path
    cmp_file: Path
    col_subset: Optional[Union[str, List[str]]] = None

    def __post_init__(self):
        self.ref_file = Path(self.ref_file)
        self.cmp_file = Path(self.cmp_file)
        if isinstance(self.col_subset, str):
            self.col_subset = [self.col_subset]
        self._check_existence()

    @property
    def ref_df(self) -> pd.DataFrame:
        df = pd.read_csv(self.ref_file, sep="\t").set_index("CDS_num")
        if self.col_subset is not None:
            df = df[self.col_subset]
        return df

    @property
    def cmp_df(self) -> pd.DataFrame:
        df = pd.read_csv(self.cmp_file, sep="\t").set_index("CDS_num")
        if self.col_subset is not None:
            df = df[self.col_subset]
        return df

    def compare(self, *args, **kwargs) -> pd.DataFrame:
        kwargs.setdefault("result_names", ("ref", "cmp"))
        ref_df, cmp_df = self.ref_df.align(self.cmp_df, join="outer")
        return ref_df.compare(cmp_df, *args, **kwargs)

    def _check_existence(self):
        for file in [self.ref_file, self.cmp_file]:
            if not file.exists():
                raise ValueError(f"{file} does not exist")


def extract_file_from_acc_folder(folder: Path):
    acc = folder.stem
    try:
        return next(
            folder.rglob(
                f"ICEscreen_results/results/{acc}.*/icescreen_detection_ME/"
                f"{acc}.*_detected_SP_withMEIds.tsv"
            )
        )
    except StopIteration:
        raise ValueError(f"detected_SP_withMEIds file not found in {folder}")


@dataclass
class IceScreenCompare:
    ref: Path
    cmp: Path
    col_subset: Optional[Union[str, List[str]]] = None

    def __post_init__(self):
        self.ref = Path(self.ref)
        self.cmp = Path(self.cmp)
        if isinstance(self.col_subset, str):
            self.col_subset = [self.col_subset]
        self._check_accessions()

    @property
    def accessions(self) -> List[str]:
        return [str(file.stem) for file in self.ref.glob("*")]

    @property
    def ref_files(self) -> List[Path]:
        return {
            acc: extract_file_from_acc_folder(self.ref / acc) for acc in self.accessions
        }

    @property
    def cmp_files(self) -> List[Path]:
        return {
            acc: extract_file_from_acc_folder(self.cmp / acc) for acc in self.accessions
        }

    @property
    def comparators(self) -> Dict[str, AccessionDiff]:
        cmp_files = self.cmp_files
        ref_files = self.ref_files
        return {
            acc: AccessionDiff(
                ref_files[acc], cmp_files[acc], col_subset=self.col_subset
            )
            for acc in self.accessions
        }

    def compare_all(self) -> pd.DataFrame:
        return pd.concat(
            [self.comparators[acc].compare() for acc in self.accessions],
            keys=self.accessions,
            names=["Genome_accession"],
            axis=0,
        )

    def _check_accessions(self):
        acc_ref = set(self.accessions)
        acc_cmp = set([str(file.stem) for file in self.cmp.glob("*")])
        if acc_ref != acc_cmp:
            raise ValueError(
                "Accessions available in in ref and cmp folders do not match.\n"
                f"{acc_ref} != {acc_cmp}"
            )
