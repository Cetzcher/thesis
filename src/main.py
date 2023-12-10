from loader.graph_loader import GraphLoader
from argparse import ArgumentParser
from pathlib import Path
import os

data_dir = Path(__file__).parent.parent / "data"
assert data_dir.exists()


if __name__ == "__main__":
    parser = ArgumentParser(
        usage=(
            "Creates a visualization of one of the provided networks given as argument and writes it"
            "to the output file"
            )
    )
    valid_file_names = [
        "infovis",
        "pgp",
        "ramp_min",
        "ramp",
        "ramp_large"
    ]
    parser.add_argument(
        "--infile", help=f"input network must be one of: {','.join(valid_file_names)}"
    )

    parser.add_argument(
        "--out", help="output directory to use"
    )

    args = parser.parse_args()
    assert args.infile in valid_file_names
    
    data_file: Path = data_dir / args.infile
    assert data_file.exists() and data_file.is_file()
    print("Reading input file")

    out_path = Path(args.out)
    if not out_path.exists():
        os.mkdir(str(out_path))
    
    print("outputting to ", out_path.resolve().absolute())
            

