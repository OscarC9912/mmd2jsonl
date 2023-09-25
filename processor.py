from utils import _mmd_reader, _errorBlk_check, _dash_checker, _intext_dash_remover
from utils import _titleLine_check, _final_remover, _data_exporter

import multiprocessing as mtp
import os
import tqdm
import json

table_start, table_end = r'\begin{table}', r'\end{table}'
tabular_start, tabular_end = r'\begin{tabular}', 'end{tabular}'

jsonl_dir = None
NUM_worker = None
SRC_dir = None

with open('config.json') as file:
    config = json.load(file)
    jsonl_dir = config['dir']['dest_path']
    SRC_dir = config['dir']['source_dir']
    NUM_worker = config['hardware']['num_work']

    if jsonl_dir is None or SRC_dir is None or NUM_worker is None:
        raise Exception('Conversion Setting Incomplete: Check the Config')


def _single_processor(src_path, desti_path=jsonl_dir):
    """ Converts a single markdown file into jsonl file. """

    print('We are processing: ', src_path)

    # compute some constants
    buffer_table, table_mode = '', False
    buffer_tabular, tabular_mode = '', False
    meta = ''

    table_count = 1

    file_data = _mmd_reader(src_path)

    for line in file_data:

        if table_mode:
            buffer_table += line
            table_count += 1
            if line.strip() == table_end or table_count == 10:
                meta += buffer_table
                buffer_table, table_mode = '', False
            continue

        if tabular_mode:
            buffer_tabular += line
            if len(line) > 12 and line[-13:] == tabular_end + '\n':
                meta += buffer_tabular
                buffer_tabular, tabular_mode = '', False
            continue


        if not table_mode and not tabular_mode:

            if not _errorBlk_check(line):  # if missing or blank
                line = ''
                continue

            if _dash_checker(line):
                line=''
                continue


            line = line[line.find(' ') + 1:] if _titleLine_check(line) else line

            line = _intext_dash_remover(line) if line.count('-') > 2 else line

            # Case1: the current line is start of table
            if line.strip() == table_start:
                buffer_table += line
                table_mode = True
                continue

            # Case2: the current line is the start of a independent Tabular model
            if not table_mode and line[0:15] == tabular_start:

                if line[-13:] == tabular_end + '\n':
                    meta += line
                    continue

                else:
                    buffer_tabular += line
                    tabular_mode = True
                    continue
            
            meta += line
    

    meta = _final_remover(meta=meta)

    _data_exporter(desti_path, meta)



def multiprocess_handler(num_worker=NUM_worker, src_dir=SRC_dir):

    # Deal with files paths
    file_paths = os.listdir(src_dir)
    src_dir += '/' if src_dir[-1] != '/' else src_dir
    file_paths = [src_dir + path for path in file_paths]

    cpu_num = mtp.cpu_count()

    if num_worker > cpu_num:
        print('Number of Worker Exceed CPU Core Number')
        num_worker = cpu_num

    with mtp.Pool(processes=num_worker) as pool:
        for _ in tqdm.tqdm(pool.map(_single_processor, file_paths), total=len(file_paths)):
            pass

    # pool = mtp.Pool(processes=num_worker)
    # pool.map(_single_processor, file_paths)

    pool.close()
    pool.join()


