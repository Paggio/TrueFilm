import logging
import gzip
import traceback
import shutil
from zipfile import ZipFile

def unzip_file(type : str, input_file : str, output_dir : str = './') -> None:
    """
    Utils for decompressing files
    type: 'zip' or 'gz'
    input_file: relative path to the file to unpack
    output_dir: relative path to the directory where the unzipped files must be put
    """

    assert type in ['zip', 'gz'], 'Type must be in (zip, gz)'

    if output_dir[-1] != -1 : output_dir = output_dir + '/'
    if input_file[0:2] != './' : input_file = './' + input_file
    if type == '.gz' and input_file[-3:] != '.gz' : input_file = input_file + '.gz'

    if type == 'zip':
        logging.debug(f'Unzipping {input_file}')
        with ZipFile(input_file, 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            zipObj.extractall(path=output_dir)

    if type == 'gz':
        output_file = output_dir + input_file.split('/')[-1].replace('.gz', '')
        logging.debug(f'Unzipping {input_file}')
        with gzip.open(input_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)