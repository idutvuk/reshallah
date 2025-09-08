# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typst",
# ]
# ///

import argparse

import typst

import tempfile
import shutil
import os


def main():
    parser = argparse.ArgumentParser(description="Compile typst files")
    parser.add_argument("-f", "--files", nargs="*", help="Send files (.typ and all needed, space-separatd). Last .typ will be compiled")
    parser.add_argument("-d", "--directory", nargs="?", help="Directory to process")
    parser.add_argument("-o", "--output", help="Output filename (overrides!)", default="output")
    parser.add_argument("-t", "--type-format", help="Export type", choices=["pdf", "png", "svg"], default="pdf")
    args = parser.parse_args()
    outfile_name=f"{args.output}.{args.type_format}"

    with tempfile.TemporaryDirectory() as temp_dir, open(outfile_name, "wb") as output_file:
        if args.directory:
            shutil.copytree(args.directory, temp_dir,  dirs_exist_ok=True)
            typ_file = [f for f in os.listdir(temp_dir) if f.endswith(".typ")][0]
        elif args.files:
            for f in args.files:
                shutil.copy(f, temp_dir)
                if f.endswith(".typ"):
                    typ_file = f
        else:
            raise ValueError("nothing provided")
        output = typst.compile(
            os.path.join(temp_dir, typ_file),
            format=args.type_format,
            ppi=144.0
            )

        output_file.write(output)
        print(f"compiled, output at {outfile_name}")

if __name__ == "__main__":
    main()
