import itertools
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
    if not src.exists():
        logger.error("File %s doesn't exists", src)
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def find_java_classes(repo_dir: Path, path: Path):
    name = path.name
    base_class_name = name.rstrip('.java')
    
    # find class files
    class_name = f'{base_class_name}.class'
    # find inner class files
    inner_class_name = f'{base_class_name}$*.class'

    logger.debug('find class file %s and inner class files %s', class_name, inner_class_name)
    
    class_generator = repo_dir.rglob(class_name)
    inner_class_generator = repo_dir.rglob(inner_class_name)
    
    for found_class in itertools.chain(class_generator, inner_class_generator):
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

    if 'WEB-INF' in path.parts:
        path_parts = list(path.parts)
        web_inf_index = path_parts.index('WEB-INF')
        dest_path = Path(output_dir) / Path(*path_parts[web_inf_index:])
    else:
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
                        required=False, help='Commit hash code')
    parser.add_argument('-d', '--debug', action='store_true',
                        default=False, help='Show debug messages')

    return parser.parse_args()

def is_xml_file(name):
    return name.endswith('.xml') and name != 'pom.xml' and name != 'build.xml'

def is_java_file(name):
    return name.endswith('.java') and 'Test' not in name

def make_diff_file(repo: git.Repo, path: Path, output_dir: str):
    repo_dir = Path(repo.working_dir)
    src_path = repo_dir / path
    logger.debug('make diff file for %s', src_path)

    if 'WEB-INF' in path.parts:
        path_parts = list(path.parts)
        web_inf_index = path_parts.index('WEB-INF')
        dest_path = Path(output_dir) / Path(*path_parts[web_inf_index:])
    else:
        dest_path = Path(output_dir) / path

    diff = repo.git.diff('master', repo.head.commit, path)
    dest_diff = str(dest_path) + '.diff'

    logger.debug('save diff file to %s', dest_diff)
    with open(dest_diff, 'w') as f:
        f.write(diff)

def main():
    args = parse_arguments()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logger.info('Repository directory: %s', args.repository_path)
    logger.info('Output directory: %s', args.output_directory)

    repo = git.Repo(args.repository_path)
    commit_hash = args.commit if args.commit else repo.head.commit
    logger.info('Commit hash: %s', commit_hash)
    commit = repo.commit(commit_hash)
    repo_dir = Path(args.repository_path)

    for item in commit.diff(commit.parents or None):
        path = Path(item.a_path)
        name = path.name
        if is_xml_file(name):
            copy_file(repo_dir, path, args.output_directory)
            make_diff_file(repo, path, args.output_directory)
        elif is_java_file(name):
            copy_java_class(repo_dir, path, args.output_directory)
        else:
            logger.debug('pass file %s', path)


if __name__ == '__main__':
    main()
