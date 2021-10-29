import logging
import pandas as pd

def log_counts(df : pd.DataFrame, df_name : str) -> None:
    """
    Utils function for debugging dataframes counts
    """
    count_dict = { k : v for k,v in zip(df.columns, df.count().values) }
    logging.debug(f'{df_name} counts : {count_dict}')

def rating_over_budget(row) -> float:
    """
    Utils function for dataframe manipulation
    """
    if row['budget'] == 0 or row['budget'] == 1 :
        return -1
    else:
        return float(row['average_rating'])/(float(row['budget']) / 10**6)

def load_wiki_dataframe(xml_path : str) -> pd.DataFrame:
    """
    Util to parse Wikipedia xml file and return a DataFrame with informations
    """
    logging.debug(f'Extracting wikipedia informations')
    titles = []
    wiki_urls = []
    size = 0
    next_line = False
    with open(xml_path, encoding = 'utf8') as f:
        for line in f:
            if line.find('<title>') != -1 or next_line:
                if line.find('<title>') != -1:
                    size = size + 1
                    title = line.replace('<title>Wikipedia: ', '').replace('</title>', '').replace('\n', '')
                if next_line:
                    url = line.replace('<url>', '').replace('</url>', '').replace('\n', '')
                    titles.append(title)
                    wiki_urls.append(url)
                    next_line = False
                else:
                    next_line = True

    df_wiki_urls = pd.DataFrame(data = {'original_title' : titles, 'wiki_urls' : wiki_urls})

    return df_wiki_urls