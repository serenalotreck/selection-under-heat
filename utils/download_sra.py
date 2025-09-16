"""
Download files from SRA that have already been prefetched.

Author: Serena G. Lotreck
"""
import argparse
from os.path import abspath
import pandas as pd
from tqdm import tqdm
import subprocess


def main(prefetched_path, accession_df, outpath):

    # Load df
    df = pd.read_csv(accession_df)
    runs_to_download = df.run_accession.tolist()

    # Download
    print('Downloading...')
    for sra_id in tqdm(runs_to_download):
        fastq_dump = "fastq-dump --outdir " + outpath + " --gzip --skip-technical  --readids --read-filter pass --dumpbase --split-3 --clip " + prefetched_path + "/" + sra_id + ".sra"
        subprocess.call(fastq_dump, shell=True)

    print('\nDone!')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download SRA')

    parser.add_argument('prefetched_path', type=str,
                       help='Path to the prefetched files')
    parser.add_argument('accession_df', type=str,
                       help='Path to the dataframe with the run numbers to download')
    parser.add_argument('outpath', type=str,
                       help='Where to save the downloaded files')

    args = parser.parse_args()

    args.prefetched_path = abspath(args.prefetched_path)
    args.accession_df = abspath(args.accession_df)
    args.outpath = abspath(args.outpath)

    main(args.prefetched_path, args.accession_df, args.outpath)