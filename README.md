# Create patch for the commit

## Usage

```cmd
usage: python main.py [-h] -r REPOSITORY_PATH -o OUTPUT_DIRECTORY -c COMMIT [-d]

Create patch from commit

arguments:
  -h, --help            show this help message and exit
  -r REPOSITORY_PATH, --repository-path REPOSITORY_PATH
                        Repository directory
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Output directory
  -c COMMIT, --commit COMMIT
                        Commit hash code
  -d, --debug           Show debug messages
```

## Example

```cmd
python .\main.py -r D:\Projects\meona\ -o D:\Projects\work\ATESTHV-140 -c 1d2f02e0 -v
```