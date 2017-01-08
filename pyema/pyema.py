"""zip化された画像ファイルを解凍し、再圧縮するスクリプト."""
import glob
import hashlib
import mimetypes
import shutil
import subprocess
import sys
import time
import zipfile
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


def time_to_md5():
    md5 = hashlib.md5(str(time.time()).encode('ascii')).hexdigest()
    return md5


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
        self.target_path, target_filename_ext = split(self.target_file)
        self.target_filename, _ = splitext(target_filename_ext)
        # outputpathの指定がなければ、
        # そのファイルがあるディレクトリに解凍
        if not output_path:
            self.output_path = self.target_path
        else:
            self.output_path = output_path

    def archive_path(self):
        """tmpディレクトリを用いて、その中で解凍。"""
        self.tmp_dir_name = 'tmp_ema_' + time_to_md5()
        self.tmp_path = join(self.output_path, self.tmp_dir_name)
        mkdir(self.tmp_path)
        Archive(self.target_file).extractall(self.tmp_path)

    def mogrify_archive(self, extracted_path=None, compress_method='zip'):
        if not extracted_path:
            extracted_path = self.tmp_path

        print('Checking this directory: ', extracted_path)
        path, dir_name = split(extracted_path)
        glob_name = dir_name.translate(
            {ord('['): '[[]', ord(']'): '[]]'})
        glob_path = join(path, glob_name)
        files = glob.glob(glob_path + '/*')

        img_list = []
        for f in files:
            if is_archived(f):
                print('Executing EMA for this file:')
                print(f)
                execute_ema(f, output_path=self.output_path)
            elif isdir(f):
                self.mogrify_archive(f)
            elif is_img(f):
                img_list.append(f)
            else:
                print('Ignore this file:')
                print(f)

        if img_list:
            img_list = [f.replace(' ', '\ ') for f in img_list]
            # mogrify images
            self.mogrify(img_list)
            # archive images
            archived_name = self.get_archived_name(extracted_path, compress_method)
            archived_name = join(self.output_path, archived_name)
            print('archiving images ...')
            if compress_method == 'rar':
                cmd = 'rar a -r -m5 -ep1 ' + rar_name + ' ' + ' '.join(img_list)
                print(cmd)
                for line in get_lines(cmd):
                    sys.stdout.buffer.write(line)
            else:
                # TODO
                zipFile = zipfile.ZipFile('./compress_2.zip', 'w', zipfile.ZIP_DEFLATED)
                for img_name in img_list:
                    zipFile.write(img_name)
                zipFile.close()

    def get_archived_name(self, path, ext='zip'):
        archived_name = basename(path)
        if archived_name == self.tmp_dir_name:
            archived_name = self.target_filename
        archived_name = archived_name.replace(' ', '\ ') + '[Archived].' + ext
        return archived_name

    def mogrify(self, img_list):
        print('mogrifing images ...')
        cmd = 'mogrify -quality 75 -verbose ' + ' '.join(img_list)
        for line in get_lines(cmd):
            sys.stdout.buffer.write(line)

    def rm_tmpdir(self):
        """remove temporary directory and files."""
        print("remove temporary directory and files.")
        shutil.rmtree(self.tmp_path)
