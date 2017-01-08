# import sys
from pyema import pyema
from os.path import basename
from argparse import ArgumentParser

def execute_ema(filenames, compless_method='zip',
                output_path=None, extracted_pathes=None):
    for target_file in filenames:
        print('Processing {} file start ...'.format(basename(target_file)))
        ema = pyema.EMA(target_file, output_path, extracted_pathes)
        ema.archive_path()
        ema.mogrify_archive(None, compless_method)
        ema.rm_tmpdir()
        print('Done!')


def main(prog=None, args=None):
    parser = ArgumentParser(prog='pyema')
    parser.add_argument('files', type=str, nargs='*',
            help='files to ema')
    parser.add_argument('-e', '--compressed-file-extention', action='store_true',
            help='extention of compressed file', default=['zip'])
    args = vars(parser.parse_args())
    print(args)
    filenames = args['files']
    ext = args['compressed_file_extention']
    execute_ema(filenames, compless_method=ext)
