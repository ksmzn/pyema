# import sys
from pyema import pyema
from os.path import basename
from argparse import ArgumentParser

def execute_ema(args, output_path=None, extracted_pathes=None, compless_method='rar'):
    target_files = args['fname']
    ext = args['compressed_file_extention']
    for target_file in target_files:
        print('Processing {} file start ...'.format(basename(target_file)))
        ema = pyema.EMA(target_file, output_path, extracted_pathes)
        ema.archive_path()
        ema.mogrify_archive(None, compless_method)
        ema.rm_tmpdir()
        print('Done!')


def main(prog=None, args=None):
    parser = ArgumentParser(prog='pyema')
    parser.add_argument('fname', type=str, nargs='*', help='ema fname')
    parser.add_argument('-e', '--compressed-file-extention', action='store_true', help='extention of compressed file', default=['zip'])
    args = vars(parser.parse_args())
    print(args)
    execute_ema(args)
# args = sys.argv
# if len(args) < 2:
#     raise ValueError('You need at least 1 argument')
#
# for target_file in args[1:]:
#     execute_ema(target_file)
