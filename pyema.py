"""zip化された画像ファイルを解凍し、再圧縮するスクリプト."""
import glob
import mimetypes
import shutil
import subprocess
import sys
from os import mkdir
from os.path import basename, dirname, expanduser, isdir, join, split, splitext

from pyunpack import Archive


def is_img(path):
    """mimetypeから画像かどうかを判定する関数."""
    mt, _ = mimetypes.guess_type(path)
    return isinstance(mt, str) and mt[:5] == 'image'


def is_archived(path):
    """mimetypeからzipもしくはrarかどうかを判定する関数."""
    mt, _ = mimetypes.guess_type(path)
    if isinstance(mt, str):
        return False
    else:
        return mt == 'application/zip' or mt == 'application/x-rar-compressed'


def get_lines(cmd):
    '''
    :param cmd: str 実行するコマンド.
    :rtype: generator
    :return: 標準出力 (行毎).
    '''
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proc.stdout.readline()
        if line:
            yield line

        if not line and proc.poll() is not None:
            break


class EMA:

    def __init__(self, target_file, output_path=None, extracted_pathes=None):
        self.target_file = expanduser(target_file)
        # outputpathの指定がなければ、
        # そのファイルがあるディレクトリに解凍
        if not output_path:
            self.output_path, _ = split(self.target_file)
        else:
            self.output_path = output_path

    def execute(self):
        """zip解凍→画像圧縮→rar."""
        print('extracting archive file ...')
        extracted_pathes = self.archive_path()
        for p in extracted_pathes:
            self.mogrify_archive(p)

    def archive_path(self):
        """tmpディレクトリを用いて、その中で解凍。"""
        tmp_path = join(self.output_path, 'tmp_ema')
        mkdir(tmp_path)

        Archive(self.target_file).extractall(tmp_path)
        self.tmp_path = tmp_path
        extracted_pathes = glob.glob(join(tmp_path, '*'))
        return extracted_pathes

    def mogrify_archive(self, extracted_path):
        print("Mogrify_archive: ", extracted_path)
        glob_path = extracted_path.translate({ord('['): '[[]', ord(']'): '[]]'})
        files = glob.glob(glob_path + '/*')
        #files = [f.replace(' ', '\ ') for f in path_allfiles]
        img_list = []
        for f in files:
            if is_archived(f):
                print("Executing EMA for this file:")
                print(f)
                execute_ema(f, output_path=self.output_path)
            elif isdir(f):
                self.mogrify_archive(f)
            elif is_img(f):
                img_list.append(f)
            else:
                print("Ignore this file:")
                print(f)

        if img_list:
            img_list = [f.replace(' ', '\ ') for f in img_list]
            # mogrify images
            self.mogrify(img_list)
            # archive images
            rar_name = basename(extracted_path.replace(
                ' ', '\ ')) + '[Archived].rar'
            rar_name = join(self.output_path, rar_name)
            cmd = 'rar a -r -m5 -ep1 ' + rar_name + ' ' + ' '.join(img_list)
            print('archiving images ...')
            print(cmd)
            for line in get_lines(cmd):
                sys.stdout.buffer.write(line)

    def mogrify(self, img_list):
        print('mogrifing images ...')
        cmd = 'mogrify -quality 75 -verbose ' + ' '.join(img_list)
        for line in get_lines(cmd):
            sys.stdout.buffer.write(line)

    def rm_tmpdir(self):
        """remove temporary directory and files."""
        shutil.rmtree(self.tmp_path)


def execute_ema(target_file, output_path=None, extracted_pathes=None):
    print('Processing {} file start ...'.format(basename(target_file)))
    ema = EMA(target_file, output_path, extracted_pathes)
    ema.execute()
    ema.rm_tmpdir()
    print('Done!')

args = sys.argv
if len(args) < 2:
    raise ValueError("You need at least 1 argument")

for target_file in args[1:]:
    execute_ema(target_file)
