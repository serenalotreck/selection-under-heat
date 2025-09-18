"""
Prefetch and download files from SRA.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath
import pandas as pd
from tqdm import tqdm
import subprocess


def main(prefetch_path, accession_df, temp_loc, outpath):

    # Load df
    df = pd.read_csv(accession_df)
    runs_to_download = df.run_accession.tolist()

    # Prefetch
    print('Prefetching...')
    for sra_id in tqdm(runs_to_download):
        prefetch = "prefetch " + sra_id + " -O " + prefetch_path + "/" + sra_id
        print('Trying to write ', prefetch_path + "/" + sra_id)
        subprocess.call(prefetch, shell=True)

    # Download
    print('Downloading...')
    for sra_id in tqdm(runs_to_download):
        fastq_dump = "fasterq-dump --outdir " + outpath + " -t " + temp_loc + prefetch_path + "/" + sra_id
        subprocess.call(fastq_dump, shell=True)

    print('\nDone!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download SRA')

    parser.add_argument('prefetch_path', type=str,
                       help='Path to save prefetched files')
    parser.add_argument('accession_df', type=str,
                       help='Path to the dataframe with the run numbers to download')
    parser.add_argument('temp_loc', type=str,
                       help='Path to put tempfiles, should be somewhere with a ton '
                       'of space')
    parser.add_argument('outpath', type=str,
                       help='Where to save the downloaded files')

    args = parser.parse_args()

    args.prefetch_path = abspath(args.prefetch_path)
    args.accession_df = abspath(args.accession_df)
    args.temp_loc = abspath(args.temp_loc)
    args.outpath = abspath(args.outpath)

    main(args.prefetch_path, args.accession_df, args.temp_loc, args.outpath)
