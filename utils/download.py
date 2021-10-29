import requests, zipfile, io
import logging


def downloadFromURL(zip_file_url : str, destination_dir : str = '../dataSource/'):

    r = requests.get(zip_file_url)
    if r.status_code != 200:
        logging.warning(f'Problem with download of file {zip_file_url}, full response : {r.text}')
        return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(destination_dir)