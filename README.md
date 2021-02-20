# Valheim FCH Editor
## _A Character editor for Valheim_

A very simple python3 character editor. Instead of dealing with editing in-script, it exports an FCH file to a directory containing JSON and PBM files which can be edited by external utilities before re-assembling into a new FCH file.

## Get file info

```sh
python3 main.py input_file.fch
```
The above command will print the data found in the file (except for minimap visibility data) to stdout.

## Export to a directory

```sh
python3 main.py input_file.fch --destruct=output-directory [--overwrite]
```
The above command will create a number of JSON and PBM files in the specified output-directory. To overwrite existing files, provide the --overwrite flag.

## Import from a directory

```sh
python3 main.py output_file.fch --costruct=input-directory [--overwrite]
```
The above command will take a series of JSON and PBM files found in the input-directory and construct a new FCH file from them. To overwrite existing files, provide the --overwrite flag.

## Requirements

There are currently no requirements aside from python3 version 3.4 or higher.

## License

MIT

