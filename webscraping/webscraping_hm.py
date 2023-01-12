# 0.0 Imports
import os
import re
import numpy as np
import pandas as pd
import logging
import requests
from bs4             import BeautifulSoup
from datetime        import datetime
from sqlalchemy      import create_engine

# 1.0 Data collection
def data_collection(url, headers):
    # request to URL
    page = requests.get(url, headers=headers)

    # Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # make pagination
    total_itens = soup.find_all('h2', class_='load-more-heading')[0].get('data-total')
    page_number = np.ceil(int(total_itens) / 36)
    url = url + '?page-size=' + str(int(page_number * 36))

    # new request to URL
    page = requests.get(url, headers=headers)

    # new Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')

    # ==================== Product Data ====================
    products = soup.find('ul', class_="products-listing small")

    # product id
    product_list = products.find_all('article', 'hm-product-item')
    product_id = [p.get('data-articlecode') for p in product_list]

    # product category
    product_category = [p.get('data-category') for p in product_list]

    # product name
    product_list = products.find_all('a', 'link')
    product_name = [p.get_text() for p in product_list]

    # product price
    product_list = products.find_all('span', 'price regular')
    product_price = [p.get_text() for p in product_list]

    # create dataframe
    data = pd.DataFrame([product_id, product_category, product_name, product_price]).T
    data.columns = ['product_id', 'product_category', 'product_name', 'product_price']

    return data

# Data Collection by Product
def data_collection_by_product(data, headers):
    # empty dataframe
    df_compositions = pd.DataFrame()

    # unique columns for all products
    df_pattern = pd.DataFrame(columns=['Art. No.', 'Composition', 'Fit', 'Size'])

    for i in range(len(data)):
        # API request
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] + '.html'
        logger.debug( 'Product: %s', url )
        page = requests.get(url, headers=headers)

        # Beautiful Soup object
        soup = BeautifulSoup(page.text, 'html.parser')

        # get product colors
        product_list = soup.find_all('a', class_=['filter-option miniature', 'filter-option miniature active'])
        product_id = [p.get('data-articlecode') for p in product_list]
        product_color = [p.get('data-color') for p in product_list]
        df_color = pd.DataFrame({'product_id': product_id, 'product_color': product_color})

        # get data for each color
        for j in range(len(df_color)):
            # API request
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j, 'product_id'] + '.html'
            logger.debug( 'Color: %s', url )
            page = requests.get(url, headers=headers)

            # Beautiful Soup object
            soup = BeautifulSoup(page.text, 'html.parser')

            # product name
            product_name = soup.find('section', class_='product-name-price').find_all('h1')
            product_name = product_name[0].get_text()

            # product price
            product_price = soup.find_all('span', class_='price-value')
            product_price = re.findall(r'\d+\.?\d+', product_price[0].get_text())[0]

            # ==================== compositions ====================
            product_composition_list = soup.find('div', class_='content pdp-text pdp-content').find_all('div')
            product_composition = [list(filter(None, p.get_text().splitlines())) for p in product_composition_list]

            # create dataframe
            df_composition = pd.DataFrame(product_composition).T
            df_composition.columns = df_composition.iloc[0]

            # delete first row
            df_composition = df_composition.iloc[1:].fillna(method='ffill')

            # Remove 'Shell:', 'Pocket lining:', 'Lining:', 'Pocket:'
            df_composition['Composition'] = df_composition['Composition'].replace('Shell: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace('Pocket lining: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace('Lining: ', '', regex=True)
            df_composition['Composition'] = df_composition['Composition'].replace('Pocket: ', '', regex=True)

            # garantee the same number of columns
            df_composition = pd.concat([df_pattern, df_composition], axis=0)

            # rename columns
            df_composition = df_composition[['Art. No.', 'Composition', 'Fit', 'Size']]
            df_composition.columns = ['product_id', 'product_composition', 'product_fit', 'product_size']
            df_composition['product_name'] = product_name
            df_composition['product_price'] = product_price

            # merge data
            df_composition = pd.merge(df_composition, df_color, how='left', on='product_id')

            # all products
            df_compositions = pd.concat([df_compositions, df_composition], axis=0)

    # final dataframe
    df_compositions['style_id'] = df_compositions['product_id'].apply( lambda x: x[:-3] )
    df_compositions['color_id'] = df_compositions['product_id'].apply( lambda x: x[-3:] )

    # scrapy_datetime
    df_compositions['scrapy_datetime'] = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )

    return df_compositions

# 3.0 Data Cleaning
def data_cleaning(data_product):
    # Read data
    df_data = data_product.dropna( subset=['product_id'] )

    # ==================== Product Attributes ====================
    # product_name
    df_data['product_name'] = df_data['product_name'].apply(lambda x: x.replace(' ', '_').lower())

    # product_price
    df_data['product_price'] = df_data['product_price'].astype(float)

    # product_color
    df_data['product_color'] = df_data['product_color'].str.replace(' ', '_').str.lower()

    # fit
    df_data['product_fit'] = df_data['product_fit'].apply(lambda x: x.replace(' ', '_').lower() if pd.notnull(x) else x)

    # size_number
    df_data['size_number'] = df_data['product_size'].apply(lambda x: re.search('\d{3}', x).group(0) if pd.notnull(x) else x)

    # size model
    df_data['size_model'] = df_data['product_size'].str.extract('(\d+/\\d+)')

    # # ==================== Composition ====================
    # break composition and create a new dataframe for it
    df1 = df_data['product_composition'].str.split(',', expand=True)
    df_ref = pd.DataFrame(index=np.arange(len(df_data)), columns=['cotton', 'polyester', 'spandex'])

    # cotton
    df_cotton0 = pd.DataFrame(df1.loc[df1[0].str.contains('Cotton', na=True), 0])
    df_cotton0.columns = ['cotton']
    df_cotton1 = pd.DataFrame(df1.loc[df1[1].str.contains('Cotton', na=True), 1])
    df_cotton1.columns = ['cotton']
    df_cotton = df_cotton0.combine_first(df_cotton1)
    df_ref = pd.concat([df_ref, df_cotton.reset_index(drop=True)], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # polyester
    df_polyester = df1.loc[df1[0].str.contains('Polyester', na=True), 0]
    df_polyester.name = 'polyester'
    df_ref = pd.concat([df_ref, df_polyester.reset_index(drop=True)], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # spandex
    df_spandex1 = pd.DataFrame(df1.loc[df1[1].str.contains('Spandex', na=True), 1])
    df_spandex1.columns = ['spandex']
    df_spandex2 = pd.DataFrame(df1.loc[df1[2].str.contains('Spandex', na=True), 2])
    df_spandex2.columns = ['spandex']
    df_spandex = df_spandex1.combine_first(df_spandex2)
    df_ref = pd.concat([df_ref, df_spandex.reset_index(drop=True)], axis=1)
    df_ref = df_ref.iloc[:, ~df_ref.columns.duplicated(keep='last')]

    # add product_id to df_ref
    df_aux = pd.concat([df_data['product_id'].reset_index(drop=True), df_ref], axis=1)

    # format composition
    df_aux['cotton'] = df_aux['cotton'].apply(lambda x: int(re.search('\d+', x).group(0)) / 100 if pd.notnull(x) else x)
    df_aux['polyester'] = df_aux['polyester'].apply(lambda x: int(re.search('\d+', x).group(0)) / 100 if pd.notnull(x) else x)
    df_aux['spandex'] = df_aux['spandex'].apply(lambda x: int(re.search('\d+', x).group(0)) / 100 if pd.notnull(x) else x)

    # final join
    df_aux = df_aux.groupby('product_id').max().reset_index().fillna(0)
    df_data = pd.merge(df_data, df_aux, on='product_id', how='left')

    # remove columns and duplicates
    df_data = df_data.drop(columns=['product_size', 'product_composition'], axis=1)
    df_data = df_data.drop_duplicates().reset_index(drop=True)

    return df_data

# 4.0 Data Insertion
def data_insert(data_cleaned, path_database):
    # reorganize columns
    data_insert = data_cleaned[[
        'product_id',
        'style_id',
        'color_id',
        'product_name',
        'product_color',
        'product_fit',
        'product_price',
        'size_number',
        'size_model',
        'cotton',
        'polyester',
        'spandex',
        'scrapy_datetime'
    ]]

    # create database connection
    conn = create_engine('sqlite:///' + path_database, echo=False)

    # insert
    data_insert.to_sql('vitrine', con=conn, if_exists='append', index=False)

    return None

def data_to_csv(path_database):
    conn = create_engine('sqlite:///' + path_database, echo=False)

    query = """
        SELECT * FROM vitrine
    """

    df_raw = pd.read_sql(query, con=conn)

    df_raw.to_csv('/home/luizmaycon/Documentos/repos/python_ds_ao_dev/database/dataset_hm.csv')

    return None

if __name__ == "__main__":
    # Parameters
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0'}
    path_database = '/home/luizmaycon/Documentos/repos/python_ds_ao_dev/database/database_hm.sqlite'
    path_logs = '/home/luizmaycon/Documentos/repos/python_ds_ao_dev/webscraping/'

    # Logging
    if not os.path.exists(path_logs + 'logs'):
        os.makedirs(path_logs + 'logs')
    logging.basicConfig(
        filename=path_logs + 'logs/webscraping_hm.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger('webscraping_hm')

    # Data Collection
    data = data_collection(url, headers)
    logger.info('data collection done')

    # Data Collection by Product
    data_product = data_collection_by_product(data, headers)
    logger.info('data collection by product done')

    # Data Cleaning
    data_cleaned = data_cleaning(data_product)
    logger.info('data cleaning done')

    # Data Insertion
    data_insert(data_cleaned, path_database)
    logger.info('data insertion done')

    # Data to CSV
    data_to_csv(path_database)
    logger.info('data to csv done')