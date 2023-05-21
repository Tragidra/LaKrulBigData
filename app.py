from cmath import nan
from datetime import date
import streamlit as st
from helper import data, seconddata, match_elements, describe, outliers, drop_items, download_data, filter_data, num_filter_data, rename_columns, clear_image_cache, handling_missing_values, data_wrangling
import numpy as np
import pandas as pd

st.set_page_config(
     page_title="Модуль работы с данными веб-приложения ЛаКрул",
     # page_icon="",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://school.easy-mo.ru/',
         'Report a bug': "https://school.easy-mo.ru/",
         'About': "Реализована базовая работа с данными, добавить больше графиков и анализ, переписать кофиг чтобы добавить больше подменю в меню"
     }
)

st.sidebar.title("Веб-модуль для работы с данными ЛаКрул")

file_format_type = ["csv", "xls", "xlsx", "ods", "odt"]
functions = ["Обзор", "Удалить столбцы", "Удалить строки", "Удалить числовые значения", "Переименовать столбцы", "Построить график", "Заполнить утерянные данные", "Слияние данных"]
excel_type =["vnd.ms-excel","vnd.openxmlformats-officedocument.spreadsheetml.sheet", "vnd.oasis.opendocument.spreadsheet", "vnd.oasis.opendocument.text"]

uploaded_file = st.sidebar.file_uploader("Загрузите ваш файл", type=file_format_type) #Настройки, в том числе и ограничение 200 мб, по умолчанию

if uploaded_file is not None:

    file_type = uploaded_file.type.split("/")[1]
    
    if file_type == "plain":
        seperator = st.sidebar.text_input("Введите разделители ваших данных: ", max_chars=5)
        data = data(uploaded_file, file_type,seperator)

    elif file_type in excel_type:
        data = data(uploaded_file, file_type)

    else:
        data = data(uploaded_file, file_type)
    
    describe, shape, columns, num_category, str_category, null_values, dtypes, unique, str_category, column_with_null_values = describe(data)

    multi_function_selector = st.sidebar.multiselect("Выберите опцию: ",functions, default=["Обзор"])

    st.subheader("Обзор данных")
    st.dataframe(data)

    st.text(" ")
    st.text(" ")
    st.text(" ")

    if "Обзор" in multi_function_selector:
        st.subheader("Содержимое набора данных")
        st.write(describe)

        st.text(" ")
        st.text(" ")
        st.text(" ")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.text("Основная информация")
            st.write("Название набора данных")
            st.text(uploaded_file.name)

            st.write("Размер данных(MB)")
            number = round((uploaded_file.size*0.000977)*0.000977,2)
            st.write(number)

            st.write("Размерность набора данных")
            st.write(shape)
            
        with col2:
            st.text("Столбцы набора данных")
            st.write(columns)
        
        with col3:
            st.text("Числовые столбцы данных")
            st.dataframe(num_category)
        
        with col4:
            st.text("Текстовые столбцы данных")
            st.dataframe(str_category)
            

        col5, col6, col7, col8= st.columns(4)

        with col6:
            st.text("Столбцы типа дата и время")
            st.dataframe(dtypes)
        
        with col7:
            st.text("Количество уникальных записей")
            st.write(unique)
        
        with col5:
            st.write("Количество пустых записей")
            st.dataframe(null_values)

    if "Удалить столбцы" in multi_function_selector:
        
        multiselected_drop = st.multiselect("Выберите столбцы для удаления: ", data.columns)
        
        droped = drop_items(data, multiselected_drop)
        st.write(droped)
        
        drop_export = download_data(droped, label="Уделны(отредактированы)")

    if "Удалить строки" in multi_function_selector:

        filter_column_selection = st.selectbox("Выберите столбец: ", options=data.columns)
        filtered_value_selection = st.multiselect("Выберите значения: ".format(filter_column_selection), data[filter_column_selection].unique())
        
        filtered_data = filter_data(data, filter_column_selection, filtered_value_selection)
        st.write(filtered_data)
        
        filtered_export = download_data(filtered_data, label="filtered")

    if "Удалить числовые значения" in multi_function_selector:

        option = st.radio(
        "Как вы хотите организовать удаление?",
        ('Удалить данные в промежутке', 'Удалить данные за промежутком'))

        num_filter_column_selection = st.selectbox("Выберите столбец: ", options=num_category)
        selection_range = data[num_filter_column_selection].unique()

        for i in range(0, len(selection_range)) :
            selection_range[i] = selection_range[i]
        selection_range.sort()

        selection_range = [x for x in selection_range if np.isnan(x) == False]

        start_value, end_value = st.select_slider(
        'Выберите промежуток значения для изменения(сохранения)',
        options=selection_range,
        value=(min(selection_range), max(selection_range)))
        
        if option == "Удалить значения в промежутке":
            st.write('Будут удалены все значения между ', int(start_value), 'и', int(end_value))
            num_filtered_data = num_filter_data(data, start_value, end_value, num_filter_column_selection, param=option)
        else:
            st.write('Будут сохранены все значения между', int(start_value), 'и', int(end_value))
            num_filtered_data = num_filter_data(data, start_value, end_value, num_filter_column_selection, param=option)

        st.write(num_filtered_data)
        num_filtered_export = download_data(num_filtered_data, label="num_filtered")

    if "Переименовать столбцы" in multi_function_selector:

        if 'rename_dict' not in st.session_state:
            st.session_state.rename_dict = {}

        rename_dict = {}
        rename_column_selector = st.selectbox("Выберите столбец для переименовывания: ", options=data.columns)
        rename_text_data = st.text_input("Введите новое название".format(rename_column_selector), max_chars=50)


        if st.button("Сохранить изменения", help="Перед тем как переименовать столбец/столбцы вы должны нажать на кнопку Сохранить изменения, только потом на кнопку Переименовать столбцы"):
            st.session_state.rename_dict[rename_column_selector] = rename_text_data
        st.code(st.session_state.rename_dict)

        if st.button("Переименовать столбцы", help="Берет ваши данные и переименовывает столбцы по вашему желанию.."):
            rename_column = rename_columns(data, st.session_state.rename_dict)
            st.write(rename_column)
            export_rename_column = download_data(rename_column, label="rename_column")
            st.session_state.rename_dict = {}
 
    if "Построить график" in multi_function_selector:

        multi_bar_plotting = st.multiselect("Введите название для графика: ", str_category)
        
        for i in range(len(multi_bar_plotting)):
            column = multi_bar_plotting[i]
            st.markdown("#### Столбик графика для {} столбца".format(column))
            bar_plot = data[column].value_counts().reset_index().sort_values(by=column, ascending=False)
            st.bar_chart(bar_plot)

    if "Заполнить утерянные данные" in multi_function_selector:
        handling_missing_value_option = st.radio("Выберите, что вы хотите сделать", ("Удалить все пустые/нулевые значения", "Заполнить пропущенные значения"))

        if handling_missing_value_option == "Удалить все пустые/нулевые значения":

            drop_null_values_option = st.radio("Выберите опцию: ", ("Удалить все пустые строки", "Удалить только те строки, которые полностью заполнены пустыми значениями"))
            droped_null_value = handling_missing_values(data, drop_null_values_option)
            st.write(droped_null_value)
            export_rename_column = download_data(droped_null_value, label="fillna_column")
        
        elif handling_missing_value_option == "Заполнить пропущенные значения":
            
            if 'missing_dict' not in st.session_state:
                st.session_state.missing_dict = {}
            
            fillna_column_selector = st.selectbox("Выберите столбец, в котором вы хотите заполнить NaN значения: ", options=column_with_null_values)
            fillna_text_data = st.text_input("Выберите значение для заполнения {} столбца с NaN значениями".format(fillna_column_selector), max_chars=50)

            if st.button("Сохранить черновик", help="когда вы хотите заполнить несколько столбцов/один столбец нулевыми значениями, поэтому сначала вам нужно нажать кнопку «Сохранить черновик», чтобы обновить данные, а затем нажать кнопку «Переименовать столбцы»."):
                
                if fillna_column_selector in num_category:
                    try:
                        st.session_state.missing_dict[fillna_column_selector] = float(fillna_text_data)
                    except:
                        st.session_state.missing_dict[fillna_column_selector] = int(fillna_text_data)
                else:
                    st.session_state.missing_dict[fillna_column_selector] = fillna_text_data

            st.code(st.session_state.missing_dict)

            if st.button("Заполнить нулевые значения", help="Принимает ваши данные и заполняет значения NaN для столбцов по вашему желанию"):

                fillna_column = handling_missing_values(data,handling_missing_value_option, st.session_state.missing_dict)
                st.write(fillna_column)
                export_rename_column = download_data(fillna_column, label="fillna_column")
                st.session_state.missing_dict = {}

# ==========================================================================================================================================

    if "Слияние данных" in multi_function_selector:
        data_wrangling_option = st.radio("Выберите, что вы хотите сделать: ", ("Слияние по индексу", "Объединение по оси"))

        if data_wrangling_option == "Слияние по индексу":
            data_wrangling_merging_uploaded_file = st.file_uploader("Загрузите второй файл для слияния по индексу", type=uploaded_file.name.split(".")[1])

            if data_wrangling_merging_uploaded_file is not None:

                second_data = seconddata(data_wrangling_merging_uploaded_file, file_type=data_wrangling_merging_uploaded_file.type.split("/")[1])
                same_columns = match_elements(data, second_data)
                merge_key_selector = st.selectbox("Выберите столбец(столбцы) для объединения со вторым набором данных", options=same_columns)
                
                merge_data = data_wrangling(data, second_data, merge_key_selector, data_wrangling_option)
                st.write(merge_data)
                download_data(merge_data, label="merging_on_index")

        if data_wrangling_option == "Объединение по оси":

            data_wrangling_concatenating_uploaded_file = st.file_uploader("Загрузите второй файл для объединения по оси", type=uploaded_file.name.split(".")[1])

            if data_wrangling_concatenating_uploaded_file is not None:

                second_data = seconddata(data_wrangling_concatenating_uploaded_file, file_type=data_wrangling_concatenating_uploaded_file.type.split("/")[1])
                concatenating_data = data_wrangling(data, second_data, None, data_wrangling_option)
                st.write(concatenating_data)
                download_data(concatenating_data, label="concatenating_on_axis")
        
# ==========================================================================================================================================
    st.sidebar.info("После использования модуля нажмите кнопку «Очистить кэш», чтобы удалить все данные из папки.")
    if st.sidebar.button("Очистить кэш"):
        clear_image_cache()

else:
    with open('test.csv', 'rb') as f:
        st.sidebar.download_button(
                label="Скачайте образец данных и используйте его",
                data=f,
                file_name='test.csv',
                help = "Загрузите некоторые образцы данных и используйте их для изучения этого веб-приложения.."
            )