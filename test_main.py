import unittest
from pathlib import Path
import os
import shutil
import git
from main import copy
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import os
from main import is_xml_file, is_java_file, copy, find_java_classes, copy_java_class, copy_file, make_diff_file, TARGET_CLASSES

class TestMain(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.test_dir, 'output')
        os.mkdir(self.output_dir)

        self.mock_repo = MagicMock()
        self.mock_repo.working_dir = self.test_dir
        self.mock_repo.git.diff.return_value = 'mock diff'

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_is_xml_file(self):
        self.assertTrue(is_xml_file('config.xml'))
        self.assertFalse(is_xml_file('pom.xml'))
        self.assertFalse(is_xml_file('Main.java'))
        self.assertFalse(is_xml_file('application.properties'))

    def test_is_java_file(self):
        self.assertTrue(is_java_file('Main.java'))
        self.assertFalse(is_java_file('MainTest.java'))
        self.assertFalse(is_java_file('config.xml'))
        self.assertFalse(is_java_file('application.properties'))

    def test_find_java_classes(self):
        path = Path('src/main/java/com/example/Main.java')

        with tempfile.TemporaryDirectory() as repo_dir:
            output_dir = Path(repo_dir)
            target_classes = Path(TARGET_CLASSES.strip(os.path.sep))
            class_file = output_dir / target_classes / 'com' / 'example' / 'Main.class'
            class_file.parent.mkdir(parents=True, exist_ok=True)
            class_file.touch()

            result = list(find_java_classes(Path(repo_dir), path))

            self.assertEqual(result, [str(class_file)])


class CopyTestCase(unittest.TestCase):
    def setUp(self):
        self.src_dir = Path('source')
        self.dst_dir = Path('destination')
        self.src_file = self.src_dir / 'file.txt'
        self.dst_file = self.dst_dir / 'file.txt'

        self.src_dir.mkdir(parents=True, exist_ok=True)
        self.dst_dir.mkdir(parents=True, exist_ok=True)
        with open(self.src_file, 'w') as f:
            f.write('Test content')

    def tearDown(self):
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dst_dir)

    def test_copy_existing_file(self):
        copy(self.src_file, self.dst_file)
        self.assertTrue(self.dst_file.exists())
        with open(self.dst_file, 'r') as f:
            content = f.read()
            self.assertEqual(content, 'Test content')

    def test_copy_non_existing_file(self):
        non_existing_file = self.src_dir / 'non_existing_file.txt'
        copy(non_existing_file, self.dst_file)
        self.assertFalse(self.dst_file.exists())


class TestCopyJavaClass(unittest.TestCase):
    def setUp(self):
        self.repo_dir = Path('/path/to/repo')
        self.path = Path('src/main/java/com/example/Main.java')
        self.output_dir = '/path/to/output'

        self.mock_find_java_classes = MagicMock()
        self.mock_copy = MagicMock()

    def test_copy_java_class(self):
        example_class_path = TARGET_CLASSES + 'com/example/Example.class'.replace('/', os.path.sep)
        self.mock_find_java_classes.return_value = [example_class_path]
        with patch('main.find_java_classes', self.mock_find_java_classes), \
                patch('main.copy', self.mock_copy):
            copy_java_class(self.repo_dir, self.path, self.output_dir)

        self.mock_find_java_classes.assert_called_once_with(self.repo_dir, self.path)
        self.mock_copy.assert_called_once_with(Path(example_class_path), Path('/path/to/output/com/example/Example.class'))


class TestCopyFile(unittest.TestCase):
    def setUp(self):
        self.repo_dir = Path('/path/to/repo')
        self.path = Path('src/main/webapp/WEB-INF/file.xml')
        self.output_dir = '/path/to/output'

        self.mock_copy = MagicMock()

    @patch('main.copy')
    def test_copy_file(self, mock_copy):
        copy_file(self.repo_dir, self.path, self.output_dir)

        mock_copy.assert_called_once_with(
            Path('/path/to/repo/src/main/webapp/WEB-INF/file.xml'),
            Path('/path/to/output/WEB-INF/file.xml')
        )


class TestMakeDiffFile(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=git.Repo)
        self.repo.working_dir = '/path/to/repo'
        self.repo.git.diff.return_value = 'mock diff'

    @patch('builtins.open', create=True)
    def test_make_diff_file(self, mock_open):
        path = Path('src/main/webapp/WEB-INF/file.xml')
        output_dir = '/path/to/output'

        mock_write = MagicMock()
        mock_open.return_value.__enter__.return_value.write = mock_write

        make_diff_file(self.repo, path, output_dir)

        mock_open.assert_called_once_with('/path/to/output/WEB-INF/file.xml.diff'.replace('/', os.path.sep), 'w')
        mock_write.assert_called_once_with('mock diff')


if __name__ == '__main__':
    unittest.main()
