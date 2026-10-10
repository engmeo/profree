import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from fetch_public_instances import git_blob_sha
from check_extended_integrity import verify
class IntegrityTests(unittest.TestCase):
 def test_git_blob_checksum(self):
  self.assertEqual(git_blob_sha(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
 def test_missing_output_fails(self):
  with self.assertRaises(FileNotFoundError):verify(ROOT/'results/definitely_not_a_file')
