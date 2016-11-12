"""
zip化された画像ファイルを解凍し、再圧縮するスクリプト
"""
import sys
import subprocess
import mimetypes
import glob
import shutil
from os import mkdir
from os.path import join, split, splitext, isdir, dirname, basename, expanduser
from pyunpack import Archive

def is_img(path):
    """
    mimetypeから画像かどうかを判定する関数
    """
    mt, _ = mimetypes.guess_type(path)
    return isinstance(mt, str) and mt[:5] == 'image'

def is_archived(path):
    """
    mimetypeからzipもしくはrarかどうかを判定する関数
    """
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
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = proc.stdout.readline()
#         print(line)
        if line:
            yield line

        if not line and proc.poll() is not None:
            break

class EMA:
    def __init__(self, arc_file):
        self.arc_file = expanduser(arc_file)
        self.basepath, _ = split(self.arc_file)
#         self.file_name, self.file_ext = splitext(self.file_name_ext)

    def execute(self):
        """
        zip解凍→画像圧縮→rar化
        """
        print("extracting archive file ...")
        extracted_pathes = self.archive_path()
        for p in extracted_pathes:
            self.mogrify_archive(p)

    def archive_path(self):
        """
        tmpディレクトリを用いて、その中で解凍。
        """
        tmp_path = join(self.basepath, 'tmp_ema')
        mkdir(tmp_path)

        Archive(self.arc_file).extractall(tmp_path)
        self.tmp_path = tmp_path
        extracted_pathes = glob.glob(join(tmp_path, '*'))
        return extracted_pathes


    def mogrify_archive(self, extracted_path):
        path_allfiles = glob.glob(extracted_path + '/*')
        files = [f.replace(' ', '\ ') for f in path_allfiles]
        dir_list = []
        img_list = []
        for f in files:
            if is_archived(f):
                execute_ema(f)
            elif isdir(f):
                self.mogrify_archive(f)
            elif is_img(f):
                img_list.append(f)

        # mogrify images
        self.mogrify(img_list)

        # archive images
#         files = [f.replace(' ', '\ ') for f in img_list]
#         files = [f.replace(' ', '\ ') for f in path_allfiles]
        rar_name = basename(extracted_path.replace(' ', '\ ')) + "[Archived].rar"
        rar_name = join(self.basepath, rar_name)
#         cmd = "rar a -r -m5 -ep1 " + rar_name + " " + " ".join(files)
        cmd = "rar a -r -m5 -ep1 " + rar_name + " " + " ".join(img_list)
        print("archive images ...")
        for line in get_lines(cmd):
            sys.stdout.buffer.write(line)

    def mogrify(self, img_list):
        print("mogrifing images ...")
        cmd = "mogrify -quality 75 -verbose " + " ".join(img_list)
        for line in get_lines(cmd):
            sys.stdout.buffer.write(line)

    def rm_tmpdir(self):
        """
        remove temporary directory and files
        """
        shutil.rmtree(self.tmp_path)

def execute_ema(arc_file):
    print("Processing {} file start ...".format(basename(arc_file)))
    ema = EMA(arc_file)
    ema.execute()
    ema.rm_tmpdir()
    print("Done!")

# arc_file = "/path/to/somefile.rar"
arc_file = "~/Downloads/somefile.rar"

args = sys.argv
if len(args) < 2:
    print("")

for arc_file in args[1:]:
    execute_ema(arc_file)
