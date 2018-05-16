import unittest
import pandas as pd
import numpy as np
import os
import sys
import subprocess
import shutil

import pymcpsc.mcpsc as m1
import pymcpsc.run as run


def setUpClass(cls):
    '''
    Setup class data to be used in multiple tests to avoid duplication. Also
    include any heavy initializations here.
    '''
    cls.FNULL = open(os.devnull, 'w')
    cls.base_dir = os.path.dirname(m1.__file__)
    cls.exec_dir = os.path.join(cls.base_dir, 'ext', 'x86_64', 'linux')


class TestPymcpsc(unittest.TestCase):

    def test_W1(self):
        '''
        Test method that generates weight vector based on size of non-null
        values in column data.
        '''
        df = pd.DataFrame([[1, 1, 1], [1, 1, 1], [1, None, 1]])
        cols = ['a', 'b', 'c']
        df.columns = cols
        self.assertListEqual(
            list(m1.get_wv_dataset_size(df, cols)), [1., 2. / 3, 1.])

    def test_W21(self):
        '''
        Test method that generates weight vector based on RMSD of column pairs.
        '''
        df = pd.DataFrame([[0, 1, 2], [0, 1, 2], [0, 1, 2]])
        cols = ['a', 'b', 'c']
        df.columns = cols
        self.assertListEqual(
            list(m1.get_wv_dataset_col_rmsd(df, cols)), [1., 0.4, 1.])

    def test_W22(self):
        '''
        Test method that generates weight vector based on RMSD of column pairs.
        '''
        df = pd.DataFrame([[0, 1, 2], [0, 1, 3], [0, 1, None]])
        cols = ['a', 'b', 'c']
        df.columns = cols
        self.assertListEqual(list(m1.get_wv_dataset_col_rmsd(df, cols)), [
                             0.83333333333333337, 0.3888888888888889, 1.0])

    def test_Wmean1(self):
        '''
        Test method that calculates weighted mean given values and sparse
        data (missing PSC score scenario).
        '''
        x = np.array([1., 1., 0])
        w = np.array([1., 1., 2.])
        self.assertEqual(m1.wmean(x, w), 0.5)

    def test_Wmean2(self):
        '''
        Test method that calculates weighted mean given values and sparse
        data (missing PSC score scenario).
        '''
        x = np.array([1., 1., np.nan])
        w = np.array([1., 1., 2.])
        self.assertEqual(m1.wmean(x, w), 1)

    def test_Binaries_CE(self):
        '''
        Test if the CE PSC binaries are reachable and runable.
        '''
        exec_prog = os.path.join(self.exec_dir, 'ce')
        self.assertEqual(
            subprocess.call(exec_prog,
                            stdout=self.FNULL,
                            stderr=subprocess.STDOUT),
            0)

    def test_Binaries_FAST(self):
        '''
        Test if the FAST PSC binaries are reachable and runable.
        '''
        exec_prog = os.path.join(self.exec_dir, 'fast')
        self.assertEqual(
            subprocess.call(exec_prog,
                            stdout=self.FNULL,
                            stderr=subprocess.STDOUT),
            1)

    def test_Binaries_GRALIGN(self):
        '''
        Test if the GRALIGN PSC binaries are reachable and runable.
        '''
        exec_prog = os.path.join(self.exec_dir, 'gralign')
        self.assertEqual(
            subprocess.call(exec_prog,
                            stdout=self.FNULL,
                            stderr=subprocess.STDOUT),
            1)
        exec_prog = os.path.join(self.exec_dir, 'CMap')
        self.assertEqual(
            subprocess.call(exec_prog,
                            stdout=self.FNULL,
                            stderr=subprocess.STDOUT),
            1)

    def test_Binaries_TMALIGN(self):
        '''
        Test if the TMALIGN PSC binaries are reachable and runable.
        '''
        exec_prog = os.path.join(self.exec_dir, 'tmalign')
        self.assertEqual(
            subprocess.call(exec_prog,
                            stdout=self.FNULL,
                            stderr=subprocess.STDOUT),
            0)

    def test_Binaries_Exec_CE(self):
        pom_path = os.path.join(
            self.exec_dir, 'pom')
        shutil.copytree(pom_path, 'pom')

        pdb_file_path = os.path.dirname(os.path.abspath(__file__))
        pdb_file1 = os.path.join(pdb_file_path, 'd1a04a2.ent')
        pdb_file2 = os.path.join(pdb_file_path, 'd1cqxa1.ent')

        ce_runner = run.CE_HANDLER(
            os.path.join(self.exec_dir, 'ce'), 'tmp')
        run_output = ce_runner.process_pair(
            pdb_file1,
            pdb_file2,
            'ent')
        self.assertEqual(run_output,
                         [['d1a04a2.', 'd1cqxa1.', 'A', '138', 'A', '150', '55', '4.16', '2.6', '45(81.8%)', '12.7%']])
        shutil.rmtree('pom')
        shutil.rmtree('tmp')

    def test_Binaries_Exec_TMALIGN(self):
        pdb_file_path = os.path.dirname(os.path.abspath(__file__))
        pdb_file1 = os.path.join(pdb_file_path, 'd1a04a2.ent')
        pdb_file2 = os.path.join(pdb_file_path, 'd1cqxa1.ent')

        tm_runner = run.TM_HANDLER(
            os.path.join(self.exec_dir, 'tmalign'))
        run_output = tm_runner.process_pair(
            pdb_file1,
            pdb_file2,
            'ent')
        self.assertEqual(run_output,
                         [['d1a04a2.', 'd1cqxa1.', '138', '150', '75,', '4.47,', '0.107', '0.32736', '0.30897']])

    def test_Binaries_Exec_FAST(self):
        pdb_file_path = os.path.dirname(os.path.abspath(__file__))
        pdb_file1 = os.path.join(pdb_file_path, 'd1a04a2.ent')
        pdb_file2 = os.path.join(pdb_file_path, 'd1cqxa1.ent')

        fast_runner = run.FAST_HANDLER(
            os.path.join(self.exec_dir, 'fast'))
        run_output = fast_runner.process_pair(
            pdb_file1,
            pdb_file2,
            'ent')
        self.assertEqual(run_output,
                         [['d1a04a2.', 'd1cqxa1.', '45', '138', '150', '4.970']])

if __name__ == '__main__':
    setUpClass(TestPymcpsc)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPymcpsc)
    unittest.TextTestRunner(verbosity=2).run(suite)
