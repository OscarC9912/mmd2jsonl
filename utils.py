""" Contains some utility functions. """


import jsonlines
import re


missingErr = '[MISSING_PAGE' 
startSign1, startSign2, startSign3, startSign4, startSign5 = '#', '##', '###', '####', '#####'
blank, blank2, blank3, blank4 = '\n', '\n\n', '\n\n\n', '\n\n\n\n'



def _titleLine_check(line_data):
    title_line \
                = line_data.startswith(startSign1) or line_data.startswith(startSign2) or \
                line_data.startswith(startSign3) or line_data.startswith(startSign4) or \
                line_data.startswith(startSign5)
    return title_line


def _errorBlk_check(line):

    if line.count(missingErr) > 0:
        return False
    
    blank_line = line == blank or line == blank2 or line == blank3 or line == blank4
    if blank_line:
        return False
    
    return True


def _mmd_reader(mmd_path, mode='r'):
    with open(mmd_path, mode) as mmd_src:
        file_data = mmd_src.readlines()
    mmd_src.close()
    return file_data


def _data_exporter(jsonl_path, file_data, mode='a'):
    with jsonlines.open(jsonl_path, mode) as jsonl_file:
        jsonl_file.write({
                        'text': file_data,
                        'meta': {'author': 'none', 'date': 'none'}
                        })
        
        jsonl_file.close()


def _dash_checker(line_data):

    if len(line_data) == 1 and line_data == '-':
        return False
    
    elif all(char == '-' for char in line_data[0:len(line_data) - 1]):
        return True
    
    return False


def _intext_dash_remover(line_data):
    output = ''
    for i in range(len(line_data)):
        temp = line_data[i]
        if temp != '-':
            output += temp
    return output



def _final_remover(meta):
    pattern1 = r'\[MISSING_PAGE_FAIL:\d+\]'
    pattern2 = r'\[MISSING_PAGE_EMPTY:\d+\]'
    pattern3 = '-'
    pattern4 = '*'
    pattern5 = '\n'
    pattern6 = '='
    meta = re.sub(pattern1, '', meta)
    meta = re.sub(pattern2, '', meta)

    meta = re.sub(pattern3, '', meta)
    meta = meta.replace(pattern4, '')
    meta = meta.replace(pattern5, '.')
    meta = meta.replace(pattern6, '')

    return meta