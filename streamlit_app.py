# 0.1 Imports
import numpy            as np
import pandas           as pd
import streamlit        as st
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# 0.2 Config
st.set_page_config( layout='centered' )
# Set the principal title
st.markdown("<h1 style='text-align: center;'>Star Jeans Company</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center;'>Welcome to Star Jeans Data Analysis!</h4>", unsafe_allow_html=True)

# 1.0 Data Collection
def data_collection( path, database ):
    conn = create_engine('sqlite:///' + path + database, echo=False)
    query = """
        SELECT * FROM vitrine
    """
    df_raw = pd.read_sql(query, con=conn)

    return df_raw

# 2.0 Feature Engineering
def feature_engineering(data):
    # product color
    data['product_color'] = data['product_color'].apply(lambda x: x.replace('denim_', ''))

    # transform composition in binary
    data['cotton'] = data['cotton'].apply(lambda x: 1 if x > 0 else 0)
    data['polyester'] = data['polyester'].apply(lambda x: 1 if x > 0 else 0)
    data['spandex'] = data['spandex'].apply(lambda x: 1 if x > 0 else 0)

    return data

# 3.0 Data Filtering
def data_filtering(data):
    # ----- Overview -----
    st.sidebar.title('Filters to Overview')

    # fit
    f_fit = st.sidebar.multiselect('Fit', data['product_fit'].sort_values().unique())
    if f_fit != []:
        df1 = data.loc[data['product_fit'].isin(f_fit), :]
    else:
        df1 = data.copy()

    # color
    f_color = st.sidebar.multiselect('Color', df1['product_color'].sort_values().unique())
    if f_color != []:
        df1 = df1.loc[df1['product_color'].isin(f_color), :]
    else:
        df1 = df1.copy()

    # price
    min_price = int(df1['product_price'].min())
    max_price = int(df1['product_price'].max() + 1)
    f_price = st.sidebar.slider('Maximum price ($)', min_price, max_price, max_price)
    df1 = df1.loc[df1['product_price'] <= f_price, :]

    # ----- Cases -----
    st.sidebar.title('Filter to Cases')

    case_01 = data.loc[(data['product_fit'] == 'regular_fit') & ((data['product_color'] == 'black') |
                                                         (data['product_color'] == 'blue')), :]
    case_02 = data.loc[(data['product_fit'] == 'regular_fit') &
                      ((data['product_color'] == 'black') | (data['product_color'] == 'blue') |
                       (data['product_color'] == 'dark_blue') | (data['product_color'] == 'light_blue')), :]
    case_03 = data.loc[((data['product_fit'] == 'regular_fit') | (data['product_fit'] == 'skinny_fit')) &
                      ((data['product_color'] == 'black') | (data['product_color'] == 'blue')), :]

    f_cases = st.sidebar.radio("Occasion", ('Case 01', 'Case 02', 'Case 03'))
    if f_cases == 'Case 01':
        df2 = case_01.copy()
    elif f_cases == 'Case 02':
        df2 = case_02.copy()
    else:
        df2 = case_03.copy()

    return df1, df2


# 4.0 Data Overview
def data_overview(data, tab):
    with tab:
        # table
        st.markdown("<h4 style='text-align: center;'>Data Display</h4>", unsafe_allow_html=True)
        df_print = data[['product_id', 'product_name','product_color', 'product_fit', 'product_price', 'cotton', 'polyester', 'spandex']]
        st.dataframe(df_print)

        # fit chart
        st.markdown("<h4 style='text-align: center;'>Amount per fit</h4>", unsafe_allow_html=True)
        fig_fit = plt.figure(figsize=(14,7))
        fit = data[['product_fit', 'product_id']].groupby('product_fit').count().sort_values('product_id', ascending=False).reset_index()
        plt.bar(fit['product_fit'], fit['product_id'])
        st.pyplot(fig_fit)

        # color chart
        st.markdown("<h4 style='text-align: center;'>Amount per color</h4>", unsafe_allow_html=True)
        fig_color = plt.figure(figsize=(14,7))
        color = data[['product_color', 'product_id']].groupby('product_color').count().sort_values('product_id', ascending=False ).reset_index()
        plt.bar(color['product_color'].head(8), color['product_id'].head(8))
        st.pyplot(fig_color)

        # polyester chart
        st.markdown("<h4 style='text-align: center;'>Amount with or without polyester</h4>", unsafe_allow_html=True)
        fig_polyester = plt.figure(figsize=(14,7))
        polyester = data[['polyester', 'product_id']].groupby('polyester').count().reset_index()
        plt.pie([polyester.iloc[1, 1], polyester.iloc[0, 1]], labels=['with', 'without'], autopct='%.2f%%')
        st.pyplot(fig_polyester)

        return None

# 5.0 Data Cases
def data_cases(data, tab):
    with tab:
        c1, c2 = st.columns((1,5))

        # description
        mean_price = round( data['product_price'].mean(), 2)
        min_price = round( data['product_price'].min(), 2)
        max_price = round( data['product_price'].max(), 2)

        c1.markdown('\n')
        c1.markdown('\n')
        c1.metric(label="Mean price:", value=mean_price)
        c1.metric(label="Min price:", value=min_price)
        c1.metric(label="Max price:", value=max_price)

        # table
        df = data[['product_fit', 'product_color', 'product_price']].groupby( ['product_fit', 'product_color']).mean().reset_index()
        df.columns = ['description', 'color', 'mean_price']
        df['description'] = df['description'] + ' ' + df['color']
        df['description'] = df['description'].str.replace('_', ' ')
        df = df.drop(columns=['color'])

        fig_chart = plt.figure(figsize=(14, 7))
        plt.bar(df['description'], df['mean_price'])
        plt.title('Mean Price', fontsize=25)
        c2.pyplot(fig_chart)

        # histogram
        fig_hist = plt.figure(figsize=(14, 7))
        plt.hist(data['product_price'])
        plt.title('Price Distribution', fontsize=25)
        st.pyplot(fig_hist)

        return None

if __name__ == "__main__":
    # parameters
    path = '/home/luizmaycon/Documentos/repos/python_ds_ao_dev/database/'
    database = 'database_hm.sqlite'
    tabs = st.tabs(['Overview', 'Cases'])

    # data collection
    data = data_collection(path, database)

    # feature engineering
    data = feature_engineering(data)

    # data filtering
    df1, df2 = data_filtering(data)

    # data overview
    data_overview(df1, tabs[0])

    # data_cases
    data_cases(df2, tabs[1])
