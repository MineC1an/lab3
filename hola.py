import streamlit as st
import pandas as pd
datos= {"netflix": pd.read_csv("Data/netflix_titles.csv"),
        "gym": pd.read_csv("Data/GymExerciseTracking.csv"),
        "electric_vehicle": pd.read_csv("Data/Electric_Vehicle_Population.csv"),
        "steam": pd.read_csv("Data/steam_store_data_2024.csv")}
def tabla(Dataset):
    nombres_columnas = datos[Dataset].columns#busacamos las columnas del dataframe
    ##se agrega code x
    nuevoDato= st.selectbox("Desea agregar un nuevo gasto?",["Seleciona","Sí", "No"])
    if nuevoDato == "Sí":
        st.session_state.expenses = pd.DataFrame(datos[Dataset])
        DatasenterValue = []
        st.session_state.cantidadvalores=  len(nombres_columnas)
        for categoria in range(st.session_state.cantidadvalores):
            tipo = datos[Dataset][nombres_columnas[categoria]].dtype
            #st.text(f"{nombres_columnas[categoria]}: {DatasenterValue.get(nombres_columnas[categoria], 'No especificado')}")
            if tipo == 'int64':
                numero = st.number_input(f"Selecciona un valor para la categoría {nombres_columnas[categoria]}", min_value=0, format="%d")
                DatasenterValue.append({nombres_columnas[categoria]: numero })
            elif tipo == 'float64':
                numero = st.number_input(f"Selecciona un valor para la categoría {nombres_columnas[categoria]}", min_value=0.0, format="%.2f")
                DatasenterValue.append({nombres_columnas[categoria]: numero})
            elif tipo == 'str':
                texto = st.text_input(f"Selecciona un valor para la categoría {nombres_columnas[categoria]}")
                DatasenterValue.append({nombres_columnas[categoria]: texto })
        #st.text(f"Valor ingresado: {DatasenterValue}")

        noEstaEnBlanco = [i for i in DatasenterValue if  "" in i.values()]
        if st.button("Agregar Gasto"):
            if not noEstaEnBlanco:
                datos_ingresados=[]
                for valores in DatasenterValue:
                    datos_ingresados.extend(valores.values())
                nuevo_gasto = pd.DataFrame([datos_ingresados], columns=nombres_columnas)
                st.session_state.expenses = pd.concat([st.session_state.expenses, nuevo_gasto], ignore_index=True)
                st.success("Gasto agregado!")
            else:
                st.warning("Por favor ingresa un nombre y un monto válido.")
        
        st.subheader("Datos agregados")
        st.dataframe(st.session_state.expenses)
        ##termina code x
    elif nuevoDato == "No":
        st.warning("Perfecto, si cambia de opinión, siempre puedes agregar un nuevos datos.")
    else:
        st.info("Selecciona 'Sí' para agregar un nuevo gasto o 'No' para continuar viendo los datos.")
    st.subheader(f"Datos de: {Dataset}")
    st.dataframe(datos[Dataset].head(6))

    columna = ", ".join(nombres_columnas)#join se usa para saber donde pegar la coma osea si hay otro elemento antes y o despues si pone de lo contrario no.
    col1, col2 = st.columns(2)
    with col1:#with se usa para decirle a streamlit que lo que esta dentro de este bloque de codigo se va a mostrar en la columna 1 y asi sucesivamente.
        st.markdown(f"**Lista de los nombres de las columnas:** \n\n :red[{columna}]")
    with col2:
        st.markdown(f"**Cantidad de columnas:** :red[{datos[Dataset].shape[1]}]\n\n **Cantidad de filas:** :red[{datos[Dataset].shape[0]}]") #shape cuando es 0 es filas, cuando es 1 es columnas
        st.dataframe(datos[Dataset].describe())
    return nombres_columnas


st.title("Trabajo de Barrera y Ajú")



selection = st.selectbox("Selecciona un dataset para mostrar su información:", ["Seleccionar"] + list(datos.keys()))
if selection == "netflix":
    tabla("netflix")
elif selection == "gym":
    tabla("gym")        
elif selection == "electric_vehicle":
    tabla("electric_vehicle")
elif selection == "steam":
    tabla("steam")