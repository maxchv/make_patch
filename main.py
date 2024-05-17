import git
import argparse
from pathlib import Path
import os
import shutil
import logging

logger = logging.getLogger(__name__)

sep = os.path.sep
TARGET_CLASSES = f'{sep}target{sep}classes{sep}'


def copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def find_java_classes(repo_dir: Path, path: Path):
    name = path.name
    class_name = name.replace('.java', '.class')
    logger.debug('find class file %s', class_name)
    for found_class in repo_dir.rglob(class_name):
        full_path = str(found_class)
        if TARGET_CLASSES in full_path:
            logger.debug('found file %s', full_path)
            yield full_path


def copy_java_class(repo_dir: Path, path: Path, output_dir: str):
    for full_path in find_java_classes(repo_dir, path):
        found_class = Path(full_path)
        logger.debug('copy from %s', found_class)
        target_file = full_path.split(TARGET_CLASSES)[1]
        target_path = Path(output_dir, target_file)
        logger.debug('copy to %s', target_path)
        copy(found_class, target_path)


def copy_file(repo_dir: Path, path: Path, output_dir: str):
    src_path = repo_dir / path
    logger.debug('copy from %s', src_path)
    dest_path = Path(output_dir) / path
    logger.debug('copy to %s', dest_path)
    copy(src_path, dest_path)


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='main.py',
        description="Create patch from commit"
    )

    parser.add_argument('-r', '--repository-path', type=str,
                        required=True, help='Repository directory')
    parser.add_argument('-o', '--output-directory', type=str,
                        required=True, help='Output directory')
    parser.add_argument('-c', '--commit', type=str,
                        required=True, help='Commit hash code')
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='Show debug messages')

    return parser.parse_args()


def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logger.info('Repository directory: %s', args.repository_path)
    logger.info('Output directory: %s', args.output_directory)
    logger.info('Commit hash: %s', args.commit)

    repo = git.Repo(args.repository_path)
    commit = repo.commit(args.commit)
    repo_dir = Path(args.repository_path)

    for item in commit.diff(commit.parents or None):
        path = Path(item.a_path)
        name = path.name
        if name.endswith('.xml'):
            copy_file(repo_dir, path, args.output_directory)
        elif name.endswith('.java') and 'Test' not in name:
            copy_java_class(repo_dir, path, args.output_directory)
        else:
            logger.debug('pass file %s', path)


if __name__ == '__main__':
    main()
