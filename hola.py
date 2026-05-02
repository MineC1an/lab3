import streamlit as st
import pandas as pd
st.title("Hola Mundo")
datos= {"netflix": pd.read_csv("netflix_titles.csv"),
        "gym": pd.read_csv("GymExerciseTracking.csv"),
        "electric_vehicle": pd.read_csv("Electric_Vehicle_Population.csv"),
        "steam": pd.read_csv("steam_store_data_2024.csv")}
for csv in datos:
    st.subheader(f"Datos de: {csv}")
    st.dataframe(datos[csv].head(6))
    nombres_columnas = datos[csv].columns#busacamos las columnas del dataframe
   
    columna = ", ".join(nombres_columnas)#join se usa para saber donde pegar la coma osea si hay otro elemento antes y o despues si pone de lo contrario no.
    col1, col2 = st.columns(2)
    with col1:#with se usa para decirle a streamlit que lo que esta dentro de este bloque de codigo se va a mostrar en la columna 1 y asi sucesivamente.
        st.markdown(f"**Lista de los nombres de las columnas:** \n\n :red[{columna}]")
    with col2:
        st.markdown(f"**Cantidad de columnas:** :red[{datos[csv].shape[1]}]\n\n **Cantidad de filas:** :red[{datos[csv].shape[0]}]") #shape cuando es 0 es filas, cuando es 1 es columnas
        st.dataframe(datos[csv].describe())