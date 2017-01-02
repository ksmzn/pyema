import sys
import pyema

def execute_ema(target_files, output_path=None, extracted_pathes=None):
    for target_file in target_files:
        print('Processing {} file start ...'.format(basename(target_file)))
        ema = pyema.EMA(target_file, output_path, extracted_pathes)
        ema.archive_path()
        ema.mogrify_archive()
        ema.rm_tmpdir()
        print('Done!')

# args = sys.argv
# if len(args) < 2:
#     raise ValueError('You need at least 1 argument')
#
# for target_file in args[1:]:
#     execute_ema(target_file)
