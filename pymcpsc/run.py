# This code is part of the pymcpsc distribution and governed by its
# license.  Please see the LICENSE.md file.
""" Classes for pairwise PSC using different methods.

Classes:
    - *GRALIGN_PRE_PROCESSOR*: run preprocessing step for GR-align
    - *CE_HANDLER*: pairwise ce execution handler
    - *TM_HANDLER*: pairwise tm-align execution handler
    - *FAST_HANDLER: pairwise fast execution handler
    - *GR_HANDLER*: gr-align execution handler
    - *USM_HANDLER*: pairwise usm execution handler
    - *RunPairwisePSC*: main execution class for generating pairwise PSC scores
    
Functions:
    - *fast_process_pair*: convinience wrapper for fast pairwise processing
    - *usm_process_pair*: convinience wrapper for usm pairwise processing
    - *tm_process_pair*: convinience wrapper for tm-align pairwise processing
    - *ce_process_pair*: convinience wrapper for ce pairwise processing
"""
import sys
import os
import subprocess
import re
import zlib
from multiprocessing import Pool
from timeit import default_timer as timer
import shutil
from time import sleep

# PRE-PROCESS


class GRALIGN_PRE_PROCESSOR:

    def __init__(self, binPath1, binPath2, tmpDir):
        """ Set paths for the class

        :param binPath1: (string) Path to CMap binary
        :param binPath2: (string) Path to Dcount binary
        :param tmpDir: (string) Path where intermediate processing files may be stored
        :rtype: None
        """
        self._binPath1 = os.path.abspath(binPath1)
        self._binPath2 = os.path.abspath(binPath2)
        self._tmpDir = '%s%sgralign' % (tmpDir, os.path.sep)
        if not os.path.exists(self._tmpDir):
            os.makedirs(self._tmpDir)

    def pre_process_all_to_all(self, pdbDir, pdbextn):
        """ Execute the pre-processing steps of GR-align that generate the 
        contact maps used for generating similarity scores.

        :param pdbDir: (string) Path where PDB files are stored
        :param pdbextn: (string) The extension of PDB files
        :rtype: None
        """
        for file1 in os.listdir(pdbDir):
            # ./CMap -i 1amk.pdb -c A -o 1amkA.gw -d 12.0
            # ./DCount -i 1amkA.gw -o 1amkA.ndump
            f1 = file1.replace(pdbextn, '.gw')
            f2 = file1.replace(pdbextn, '.ndump')
            cmd = '%s -i %s%s%s -c A -o %s%s%s -d 12.0' % (
                self._binPath1, pdbDir, os.path.sep, file1, self._tmpDir, os.path.sep, f1)
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            # print proc.stdout.readlines()
            cmd = '%s -i %s%s%s -o %s%s%s' % (self._binPath2,
                                              self._tmpDir,
                                              os.path.sep,
                                              f1,
                                              self._tmpDir,
                                              os.path.sep,
                                              f2)
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            # print proc.stdout.readlines()
        l1 = len(os.listdir(pdbDir))
        l2 = len(
            list(
                filter(
                    lambda x: x.endswith(".gw"),
                    os.listdir(
                        self._tmpDir))))
        l3 = len(list(
            filter(
                lambda x: x.endswith(".ndump"),
                os.listdir(
                    self._tmpDir))))
        pstr = 'pdb file count: %d, contact map count: %d, signature file count: %d' % (
            l1, l2, l3)
        print(pstr)


# END OF PRE-PROCESS

# HANDLERS
class CE_HANDLER:

    def __init__(self, binPath, tmpDir):
        """ Set paths for the class

        :param binPath: Path to ce binary
        :param tmpDir: Path for storing intermediate files
        :rtype: None
        """
        self._binPath = os.path.abspath(binPath)
        self._tmpDir = tmpDir
        if not os.path.exists(self._tmpDir):
            os.makedirs(self._tmpDir)

    def process_pair(self, fname1, fname2, pdbextn):
        """ Process a pair of domains using the CE external binary

        :param fname1: (string) Path to file containing structure of domain 1
        :param fname2: (string) Path to file containing structure of domain 2
        :param pdbextn: (string) Extension of PDB files
        :rtype: (list) Output data collected from CE execution
        """
        # note special requirement for pom/mkDB from exec location
        # ./CE - $PDB_DIR/$1 - $PDB_DIR/$2 - $TMP_DIR
        f1 = fname1.split(os.path.sep)[-1].replace(pdbextn, '')
        f2 = fname2.split(os.path.sep)[-1].replace(pdbextn, '')
        wdir = '%s%s%s_%s' % (self._tmpDir, os.path.sep, f1, f2)
        os.makedirs(wdir)
        cmd = '%s - %s - %s - %s' % (self._binPath, fname1, fname2, wdir)
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        new_pair = True
        res = []
        for line in proc.stdout.readlines():
            line = str(line)
            line = line.replace('\n', '')
            if line.find('Size=') != -1:
                if new_pair:
                    new_pair = False
                    res.append([f1, f2])
                data = line.split(' ')
                dom_chain = data[2]
                chain = dom_chain.split(':')[1]
                dlen = data[3].replace(
                    '(',
                    '').replace(
                    ')',
                    '').replace(
                    '=',
                    '').replace(
                    'Size',
                    '')
                res[len(res) - 1] += [chain, dlen]

            if line.find('Alignment length') != -1:
                new_pair = True
                data = line.split(' ')
                res[len(res) - 1] += [data[3], data[6].replace('A', ''),
                                      data[9], data[12], data[19]]
        if len(res) > 1:
            pstr = 'pair: %s-%s has multi chain domain' % (fname1, fname2)
            print(pstr)
            # each entry in res: fname1, fname2, chain1, len1, chain2, len2,
            # Alignment length, Rmsd, Z-Score, Gaps, Sequence identities
        if len(res) == 0:
            res.append([f1, f2])
        # with lock:
        #  ofile.write('%s\n' %' '.join(res[0]))
        shutil.rmtree(wdir, ignore_errors=True)
        return res


class TM_HANDLER:

    def __init__(self, binPath):
        """ Set paths for the class

        :param binPath: Path to ce binary
        :rtype: None
        """
        self._binPath = os.path.abspath(binPath)

    def process_pair(self, fname1, fname2, pdbextn):
        """ Process a pair of domains using the TM-align external binary

        :param fname1: (string) Path to file containing structure of domain 1
        :param fname2: (string) Path to file containing structure of domain 2
        :rtype: (list) Output data collected from CE execution
        """
        # ./$prg $dir/$x $dir/$y
        cmd = '%s %s %s' % (self._binPath, fname1, fname2)
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        f1 = fname1.split(os.path.sep)[-1].replace(pdbextn, '')
        f2 = fname2.split(os.path.sep)[-1].replace(pdbextn, '')
        ret = [[f1, f2]]
        for line in proc.stdout.readlines():
            line = str(line)
            line = line.replace('\n', '')
            if line.find('Length of Chain_') != -1:
                ret[0].append(
                    line.split(':')[1].replace(
                        'residues', '').strip())
            if line.find('Aligned length') != -1:
                data = re.split('\s+', line)
                ret[0] += [data[2], data[4], data[6]]
            if line.find('TM-score=') != -1:
                ret[0].append(line.split(' ')[1])
        # each entry in res: fname1, fname2, len1, len2, aligned length, RMSD,
        # sequence id, tm1, tm2
        if len(ret) == 0:
            ret.append([f1, f2])
        # with lock:
        #  ofile.write('%s\n' %' '.join(ret[0]))
        return ret


class FAST_HANDLER:

    def __init__(self, binPath):
        """ Set paths for the class

        :param binPath: Path to ce binary
        :rtype: None
        """
        self._binPath = os.path.abspath(binPath)

    def process_pair(self, fname1, fname2, pdbextn):
        """ Process a pair of domains using the FAST external binary

        :param fname1: (string) Path to file containing structure of domain 1
        :param fname2: (string) Path to file containing structure of domain 2
        :param pdbextn: (string) Extension of PDB files
        :rtype: (list) Output data collected from FAST execution
        """
        cmd = '%s %s %s' % (self._binPath, fname1, fname2)
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        ret = [[fname1.split(os.path.sep)[-1].replace(pdbextn, ''),
                fname2.split(os.path.sep)[-1].replace(pdbextn, '')]]
        for line in proc.stdout.readlines():
            line = str(line)
            if line.find('RMSD=') != -1:
                data = line.replace('\n', '').split(' ')
                ret[0] += [data[0].split('=')[1],
                           data[3].split('=')[1],
                           data[4].split('=')[1],
                           data[5].split('=')[1]]
        return ret


class GR_HANDLER:

    def __init__(self, binPath):
        """ Set paths for the class

        :param binPath: Path to ce binary
        :rtype: None
        """
        self._binPath = os.path.abspath(binPath)

    def process_alltoall(self, dirName):
        """ Process all pairs of domains using the GR-align external binary

        :param dirName: (string) Path to contact map files
        :rtype: None
        """
        q = '%s%spairs.lst' % (dirName, os.path.sep)
        f = open(q, 'w')
        for file1 in list(filter(
                lambda x: x.endswith(".ndump"),
                os.listdir(dirName))):
            f.write('%s\n' % file1.replace('.ndump', ''))
        f.close()
        # ./GR-Align -q skolnick.lst -r ./skolnick -o results.txt
        cmd = '%s -q %s -r %s -o %s' % (self._binPath,
                                        q,
                                        dirName,
                                        '%s%sresults.txt' % (dirName,
                                                             os.path.sep))
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        for line in proc.stdout.readlines():
            line = str(line)
            print(line)


class USM_HANDLER:

    def __init__(self):
        """ Set maximum number of contacts to keep in contact map

        :rtype: None
        """
        self._MAX_CONTACTS = 1000

    def _trunc(self, x):
        """ Truncate contacts to max size

        :param x: (list) Contacts
        :rtype: (list) Contacts truncated to max size
        """
        if len(x) < self._MAX_CONTACTS:
            return x
        return x[:self._MAX_CONTACTS]

    def process_pair(self, fname1, fname2):
        """ Process a pair of domains using USM

        :param fname1: (string) Path to domain 1 contact map file
        :param fname2: (string) Path to domain 2 contact map file
        :rtype: (list) Output data collected from USM execution
        """
        def reader(x): return not x.startswith('|')
        cm1 = ''.join(
            self._trunc(
                list(
                    filter(
                        reader,
                        open(fname1).readlines()))))
        cm2 = ''.join(
            self._trunc(
                list(
                    filter(
                        reader,
                        open(fname2).readlines()))))
        if sys.version_info < (3, 0):
            def comp(x): return float(len(zlib.compress(x)))
        else:
            def comp(x): return float(len(zlib.compress(x.encode('utf-8'))))
        x = comp(cm1)
        y = comp(cm2)
        xy = comp(cm1 + cm2)
        yx = comp(cm2 + cm1)
        f1 = fname1.split(os.path.sep)[-1].replace('.gw', '')
        f2 = fname2.split(os.path.sep)[-1].replace('.gw', '')
        return [[f1, f2, '%f' % (max(yx - y, xy - x) / max(x, y))]]

# END OF HANDLERS


def fast_process_pair(ps):
    """ Convinience wrapper for fast pairwise processing

    :param ps: tuple containing object to call and data to call it with
    :rtype: (list) program output
    """
    try:
        return ps[0].process_pair(ps[1][0], ps[1][1], ps[1][2])
    except KeyboardInterrupt:
        raise ValueError('worker user exit in FAST')


def usm_process_pair(ps):
    """ Convinience wrapper for usm pairwise processing

    :param ps: tuple containing object to call and data to call it with
    :rtype: (list) program output
    """
    try:
        return ps[0].process_pair(ps[1][0], ps[1][1])
    except KeyboardInterrupt:
        raise ValueError('worker user exit in USM')


def tm_process_pair(ps):
    """ Convinience wrapper for tm-align pairwise processing

    :param ps: tuple containing object to call and data to call it with
    :rtype: (list) program output
    """
    try:
        return ps[0].process_pair(ps[1][0], ps[1][1], ps[1][2])
    except KeyboardInterrupt:
        raise ValueError('worker user exit in TMALIGN')


def ce_process_pair(ps):
    """ Convinience wrapper for ce pairwise processing

    :param ps: tuple containing object to call and data to call it with
    :rtype: (list) program output
    """
    try:
        return ps[0].process_pair(ps[1][0], ps[1][1], ps[1][2])
    except KeyboardInterrupt:
        raise ValueError('worker user exit in CE')


class RunPairwisePSC:

    def __init__(self):
        pass

    def run(self, config=None):
        """ Main pairwise psc processing function

        :param config: (Config) Paths and settings to use during PSC processing
        """
        PROGRAMS = ['ce', 'tmalign', 'fast', 'gralign', 'usm']

        if config is None:
            # CONFIGURATION
            PROGDIR = 'programs'
            DATADIR = 'scop_cath_reduced/'
            WORKDIR = 'work/'
            PDBEXTN = 'ent'
            THREADS = 16
            # END OF CONFIGURATIOAN
        else:
            # PROGRAMS = config['PROGRAMS']
            PROGDIR = config.PROGDIR
            DATADIR = config.DATADIR
            WORKDIR = config.WORKDIR
            PDBEXTN = config.PDBEXTN
            THREADS = int(config.THREADS)

        if os.path.exists(WORKDIR):
            shutil.rmtree(WORKDIR)
        os.makedirs(WORKDIR)

        if os.path.exists('figures'):
            shutil.rmtree('figures')
        os.makedirs('figures')

        # PROCESS
        start = timer()
        gralign_pre_processor = GRALIGN_PRE_PROCESSOR(
            '%s%sCMap' %
            (PROGDIR, os.path.sep), '%s%sDCount' %
            (PROGDIR, os.path.sep), WORKDIR)
        gralign_pre_processor.pre_process_all_to_all(DATADIR, PDBEXTN)
        end = timer()
        print('gralign preprocessing took %d seconds' % (end - start))

        ce = CE_HANDLER(
            '%s%s%s' %
            (PROGDIR, os.path.sep, PROGRAMS[0]), '%s%sce' %
            (WORKDIR, os.path.sep))

        tm = TM_HANDLER('%s%s%s' % (PROGDIR, os.path.sep, PROGRAMS[1]))

        fast = FAST_HANDLER('%s%s%s' % (PROGDIR, os.path.sep, PROGRAMS[2]))

        usm = USM_HANDLER()

        gr = GR_HANDLER('%s%s%s' % (PROGDIR, os.path.sep, PROGRAMS[3]))

        pdb_files = list(
            filter(
                lambda x: x.endswith(
                    '.%s' %
                    PDBEXTN),
                os.listdir(DATADIR)))

        if len(pdb_files) == 0:
            print('No PDB files found.')
            return False

        psc_pairs = []
        for x in range(0, len(pdb_files)):
            for y in range(x, len(pdb_files)):
                psc_pairs.append(
                    ('%s%s%s' %
                     (DATADIR, os.path.sep, pdb_files[x]), '%s%s%s' %
                        (DATADIR, os.path.sep, pdb_files[y]), PDBEXTN))
        cm_files = list(filter(
            lambda x: x.endswith(".gw"), os.listdir(
                '%s%sgralign' %
                (WORKDIR, os.path.sep))))
        cm_pairs = []
        for x in range(0, len(cm_files)):
            for y in range(x, len(cm_files)):
                cm_pairs.append(
                    ('%s%sgralign%s%s' %
                     (WORKDIR, os.path.sep, os.path.sep, cm_files[x]), '%s%sgralign%s%s' %
                        (WORKDIR, os.path.sep, os.path.sep, cm_files[y]), PDBEXTN))

        # Do Serial
        start = timer()
        print('gralign started:')
        gr.process_alltoall('%s/gralign' % WORKDIR)
        end = timer()
        print('gralign processed in %d seconds' % (end - start))

        def doMulti(
                outfilename,
                procmethod,
                pairs,
                threads,
                pscmethod,
                methodname):
            """ Execute job list in parallel using Pool

            :param outfilename: (string)
            :param procmethod: PSC convinience method to call
            :param pairs: (list) Pairs of domains to be processed
            :param pscmethod: (object) PSC handler object
            :param methodname: (string) PSC method name string
            :rtype: (boolean) 
            """
            start = timer()
            p = Pool(threads)
            mlen = len(pairs) - 1
            print('%s started:' % methodname)
            results = []
            try:
                reduced = p.map_async(
                    procmethod, map(
                        lambda x: (
                            pscmethod, x, None), pairs), callback=results.append)
            except ValueError as error:
                print(error)
                sys.exit(-1)

            prev = -1
            while not reduced.ready():
                remaining = reduced._number_left * reduced._chunksize
                rpct = max([mlen - remaining, 0]) * 100. / mlen
                if prev != rpct:
                    prev = rpct
                    print('\t' + str(round(rpct, 0)) + '%')
                sleep(5)
            print('\t100%')

            out = open(outfilename, 'w')
            for res in results[0]:
                out.write(
                    '%s\n' %
                    ' '.join(
                        res[0]).replace(
                        '\\n',
                        '').replace(
                        "'",
                        ''))
            out.close()
            return timer() - start

        # Run multi-threaded jobs for pairwise PSC processing of the
        # PSC methods
        usm_seconds = doMulti(
            '%s%susm_results.txt' %
            (WORKDIR,
             os.path.sep),
            usm_process_pair,
            cm_pairs,
            THREADS,
            usm,
            'usm')
        print('usm processed in %d seconds' % usm_seconds)
        fast_seconds = doMulti(
            '%s%sfast_results_1.txt' %
            (WORKDIR,
             os.path.sep),
            fast_process_pair,
            psc_pairs,
            THREADS,
            fast,
            'fast')
        print('fast processed in %d seconds' % fast_seconds)
        tm_seconds = doMulti(
            '%s%stm_results_1.txt' %
            (WORKDIR,
             os.path.sep),
            tm_process_pair,
            psc_pairs,
            THREADS,
            tm,
            'tmalign')
        print('tmalign processed in %d seconds' % tm_seconds)
        try:
            pom_path = os.path.join(
                os.path.dirname(
                    os.path.realpath(__file__)),
                'ext',
                'x86_64',
                'linux',
                'pom')
            shutil.copytree(pom_path, 'pom')
        except:
            print('pom exists?')

        ce_seconds = doMulti(
            '%s%sce_results_1.txt' %
            (WORKDIR,
             os.path.sep),
            ce_process_pair,
            psc_pairs,
            THREADS,
            ce,
            'ce')
        shutil.rmtree('pom')
        print('ce processed in %d seconds' % ce_seconds)

        return True

        # END OF PROCESS


if __name__ == '__main__':
    RunPairwisePSC().run()
