import streamlit as st
import pandas as pd
#Var/def frecuentes

DATASETS_CONOCIDOS = {"netflix", "gym", "electric_vehicle", "steam"}

rutas_csv = {
    "netflix":          "Data/netflix_titles.csv",
    "gym":              "Data/GymExerciseTracking.csv",
    "electric_vehicle": "Data/Electric_Vehicle_Population.csv",
    "steam":            "Data/steam_store_data_2024.csv",
}
datos = {
    "netflix": pd.read_csv(rutas_csv["netflix"]),
    "gym": pd.read_csv(rutas_csv["gym"]),
    "electric_vehicle": pd.read_csv(rutas_csv["electric_vehicle"]),
    "steam": pd.read_csv(rutas_csv["steam"]),
}
def tiene_simbolo(df, columna, simbolo):
    """Revisa si la primera celda de una columna contiene un símbolo dado."""
    if columna not in df.columns:
        return False
    primer_valor = str(df[columna].iloc[0]) if len(df) > 0 else ""
    return simbolo in primer_valor

def detectar_columna_por_simbolo(df, simbolo):
    """Retorna el nombre de la primera columna cuya primera celda tenga el símbolo."""
    for c in df.columns:
        if tiene_simbolo(df, c, simbolo):
            return c
    return None


def tabla(Dataset):
    # Inicializa expenses solo si no existe o si cambió el dataset
    if st.session_state.get("dataset_actual") != Dataset:
        st.session_state.mostrar_ultimo = False
        st.session_state.dataset_actual = Dataset
        st.session_state.expenses = pd.DataFrame(datos[Dataset])
        # Limpia columnas Steam detectadas para que se re-detecten con el nuevo df
        st.session_state.pop("steam_col_precio", None)
        st.session_state.pop("steam_col_descuento", None)

    if "expenses" not in st.session_state:
        st.session_state.expenses = pd.DataFrame(datos[Dataset])

    nombres_columnas = datos[Dataset].columns
    df_actual = st.session_state.expenses  # DataFrame vivo (con datos agregados)

    st.subheader(f"✅ {Dataset.replace('_', ' ').title()}")
    st.dataframe(datos[Dataset].head(6), use_container_width=True)

    if st.session_state.get("mostrar_ultimo", False):
        st.markdown("**📌 Último dato agregado:**")
        st.dataframe(st.session_state.expenses.tail(1), use_container_width=True)

    col_add, col_del, _ = st.columns([1, 1, 4])

    with col_add:
        with st.popover("➕ Agregar"):
            DatasenterValue = []
            for categoria in nombres_columnas:
                tipo = datos[Dataset][categoria].dtype
                with st.container(border=True):
                    st.markdown(f"**{categoria}**")
                    if tipo == "int64":
                        promedio = int(datos[Dataset][categoria].mean())
                        numero = st.number_input("Ingresa el valor:", min_value=0, format="%d", value=promedio, key=f"input_{categoria}")
                        DatasenterValue.append({categoria: numero})
                    elif tipo == "float64":
                        promedio = float(datos[Dataset][categoria].mean())
                        numero = st.number_input("Ingresa el valor:", min_value=0.0, format="%.2f", value=promedio, key=f"input_{categoria}")
                        DatasenterValue.append({categoria: numero})
                    elif tipo == "str":
                        ejemplos = datos[Dataset][categoria].dropna().unique()[:3]
                        ejemplos_str = ", ".join(str(e) for e in ejemplos)
                        texto = st.text_input("Ingresa el valor:", placeholder=f"Ej: {ejemplos_str}", key=f"input_{categoria}")
                        DatasenterValue.append({categoria: texto})

            noEstaEnBlanco = [i for i in DatasenterValue if any(isinstance(v, str) and v == "" for v in i.values())]

            if st.button("➕ Agregar Dato"):
                if not noEstaEnBlanco:
                    datos_ingresados = []
                    for valores in DatasenterValue:
                        datos_ingresados.extend(valores.values())
                    nuevo_gasto = pd.DataFrame([datos_ingresados], columns=nombres_columnas)
                    st.session_state.expenses = pd.concat([st.session_state.expenses, nuevo_gasto], ignore_index=True)
                    nuevo_gasto.to_csv(rutas_csv[Dataset], mode='a', header=False, index=False)
                    st.session_state.mostrar_ultimo = True
                    st.success("✅ Dato agregado y guardado!")
                    st.rerun()
                else:
                    st.warning("⚠️ Completa todos los campos.")

    with col_del:
        with st.popover("🗑️ Eliminar"):
            total_filas = len(st.session_state.expenses)
            with st.container(border=True):
                st.markdown("**🗑️ Eliminar fila**")
                st.caption(f"Filas disponibles: 0 - {total_filas - 1}")
                fila_eliminar = st.number_input("Número de fila:", min_value=0, max_value=total_filas - 1, format="%d", key="fila_eliminar")
                st.dataframe(st.session_state.expenses.iloc[[fila_eliminar]], use_container_width=True)

            if st.button("🗑️ Eliminar Dato"):
                st.session_state.expenses = st.session_state.expenses.drop(index=fila_eliminar).reset_index(drop=True)
                st.session_state.expenses.to_csv(rutas_csv[Dataset], index=False)
                st.success(f"✅ Fila {fila_eliminar} eliminada!")
                st.rerun()

    st.markdown("### 📋 Información del Dataset")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Columnas", datos[Dataset].shape[1])
    with col2:
        st.metric("📝 Filas", datos[Dataset].shape[0])
    with col3:
        st.metric("🔢 Total de celdas", datos[Dataset].shape[0] * datos[Dataset].shape[1])

    with st.container(border=True):
        st.markdown("**🏷️ Columnas disponibles**")
        st.pills("", nombres_columnas, disabled=True)

    with st.container(border=True):
        st.markdown("**📈 Estadísticas descriptivas**")
        st.dataframe(datos[Dataset].describe(), use_container_width=True)

    # ── RETURN: DataFrame actual + nombres de columnas ──────────────
    return df_actual, nombres_columnas


# ════════════════════════════════════════════════════════════════════
# Ejercicio 3 – Filtrado de datos
# ════════════════════════════════════════════════════════════════════
def filtros(Dataset, df):
    """Recibe el nombre del dataset y el DataFrame actualizado de tabla()."""

    if Dataset not in DATASETS_CONOCIDOS:
        st.info("ℹ️ Este dataset no tiene filtros definidos en el Ejercicio 3.")
        return

    st.markdown("---")
    st.markdown("## 🔍 Filtrado de Datos")

    # ── Electric Vehicle ────────────────────────────────────────────
    if Dataset == "electric_vehicle":
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("**🚗 Filtro 1 – Año de modelo anterior a:**")
                anio = st.number_input("Model_Year menor a:", min_value=2000, max_value=2025,
                                       value=2020, format="%d", key="ev_anio")
                resultado = df[df["Model_Year"] < anio]
                st.caption(f"{len(resultado)} registros encontrados")
                st.dataframe(resultado, use_container_width=True)

        with col2:
            with st.container(border=True):
                st.markdown("**💰 Filtro 2 – Base MSRP inferior a:**")
                msrp = st.number_input("Base_MSRP menor a ($):", min_value=0.0, max_value=845000.0,
                                       value=50000.0, format="%.2f", key="ev_msrp")
                resultado2 = df[df["Base_MSRP"] < msrp]
                st.caption(f"{len(resultado2)} registros encontrados")
                st.dataframe(resultado2, use_container_width=True)

    # ── Gym ─────────────────────────────────────────────────────────
    elif Dataset == "gym":
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("**🔥 Filtro 1 – Calorías quemadas ≥ a:**")
                calorias = st.number_input("Calories_Burned mínimo:", min_value=0.0,
                                           value=500.0, format="%.1f", key="gym_cal")
                resultado = df[df["Calories_Burned"] >= calorias]
                st.caption(f"{len(resultado)} registros encontrados")
                st.dataframe(resultado, use_container_width=True)

        with col2:
            with st.container(border=True):
                st.markdown("**🏋️ Filtro 2 – Porcentaje de grasa ≤ a:**")
                grasa = st.number_input("Fat_Percentage máximo (%):", min_value=0.0, max_value=100.0,
                                        value=25.0, format="%.1f", key="gym_fat")
                resultado2 = df[df["Fat_Percentage"] <= grasa]
                st.caption(f"{len(resultado2)} registros encontrados")
                st.dataframe(resultado2, use_container_width=True)

    # ── Steam (Videojuegos) ─────────────────────────────────────────
    elif Dataset == "steam":

        # Usa detectar_columna_por_simbolo() en lugar de los bucles manuales
        if "steam_col_precio" not in st.session_state:
            st.session_state.steam_col_precio = detectar_columna_por_simbolo(df, "$")

        if "steam_col_descuento" not in st.session_state:
            st.session_state.steam_col_descuento = detectar_columna_por_simbolo(df, "%")

        col_precio    = st.session_state.steam_col_precio
        col_descuento = st.session_state.steam_col_descuento

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("**🎮 Filtro 1 – Precio superior a:**")
                if col_precio:
                    df[col_precio] = (
                        df[col_precio]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True)
                        .replace("", "0")
                        .astype(float)
                    )
                    precio = st.number_input("Precio mayor a ($):", min_value=0.0,
                                             value=10.0, format="%.2f", key="steam_precio")
                    resultado = df[df[col_precio] > precio]
                    st.caption(f"{len(resultado)} registros encontrados")
                    st.dataframe(resultado, use_container_width=True)
                else:
                    st.error("No se encontró columna de precio en Steam.")

        with col2:
            with st.container(border=True):
                st.markdown("**🏷️ Filtro 2 – Descuento menor a (%):**")
                if col_descuento:
                    df[col_descuento] = (
                        df[col_descuento]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True)
                        .replace("", "0")
                        .astype(float)
                    )
                    descuento = st.number_input("Porcentaje de descuento menor a (%):", min_value=0.0,
                                                max_value=100.0, value=50.0, format="%.1f", key="steam_desc")
                    resultado2 = df[df[col_descuento] < descuento]
                    st.caption(f"{len(resultado2)} registros encontrados")
                    st.dataframe(resultado2, use_container_width=True)
                else:
                    st.error("No se encontró columna de descuento en Steam.")

    # ── Netflix ─────────────────────────────────────────────────────
    elif Dataset == "netflix":
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("**🎬 Filtro 1 – Duración mayor a (minutos):**")
                duracion = st.number_input("Duración mínima (min):", min_value=0,
                                           value=90, format="%d", key="nf_dur")
                df_peliculas = df[df["type"] == "Movie"].copy()
                df_peliculas["duracion_num"] = (
                    df_peliculas["duration"]
                    .str.extract(r"(\d+)")
                    .astype(float)
                )
                resultado = df_peliculas[df_peliculas["duracion_num"] > duracion]
                st.caption(f"{len(resultado)} películas encontradas")
                st.dataframe(resultado.drop(columns=["duracion_num"]), use_container_width=True)

        with col2:
            with st.container(border=True):
                st.markdown("**📅 Filtro 2 – Contenido añadido antes del año:**")
                anio_nf = st.number_input("Año límite:", min_value=2000, max_value=2025,
                                          value=2020, format="%d", key="nf_anio")
                df["anio_agregado"] = pd.to_datetime(df["date_added"], errors="coerce").dt.year
                resultado2 = df[df["anio_agregado"] < anio_nf].drop(columns=["anio_agregado"])
                st.caption(f"{len(resultado2)} títulos encontrados")
                st.dataframe(resultado2, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# Ejercicio 4 – Exploración Avanzada
# ════════════════════════════════════════════════════════════════════
def ExploracionAvanzada(Dataset, df):
    """Nueva variable categórica, conteo, gráfico de barras y análisis agrupado."""

    if Dataset not in DATASETS_CONOCIDOS:
        st.info("ℹ️ Este dataset no tiene exploración avanzada definida.")
        return

    st.markdown("---")
    st.markdown("## 📊 Exploración Avanzada")

    df = df.copy()  # No modificar el original

    # ── Electric Vehicle ────────────────────────────────────────────
    if Dataset == "electric_vehicle":
        def rango_categoria(val):
            try:
                val = float(val)
            except:
                return "Desconocido"
            if val < 100:
                return "Bajo"
            elif val <= 250:
                return "Medio"
            else:
                return "Alto"

        df["RangoCategoria"] = df["Electric_Range"].apply(rango_categoria)

        st.markdown("### 🏷️ Nueva variable: `RangoCategoria`")
        with st.container(border=True):
            st.dataframe(df[["Electric_Range", "RangoCategoria"]].head(10), use_container_width=True)

        st.markdown("### 🔢 Conteo por categoría")
        conteo = df["RangoCategoria"].value_counts().reset_index()
        conteo.columns = ["RangoCategoria", "Cantidad"]
        with st.container(border=True):
            st.dataframe(conteo, use_container_width=True)

        st.markdown("### 📈 Gráfico de barras – Vehículos Eléctricos por Rango")
        orden = ["Bajo", "Medio", "Alto"]
        conteo_ordenado = conteo.set_index("RangoCategoria").reindex(orden).reset_index()
        st.bar_chart(conteo_ordenado.set_index("RangoCategoria")["Cantidad"])

        st.markdown("### 🔬 Análisis agrupado por `RangoCategoria`")
        with st.container(border=True):
            agrupado = df.groupby("RangoCategoria").agg(
                Media_Base_MSRP   = ("Base_MSRP",       "mean"),
                Media_Model_Year  = ("Model_Year",      "mean"),
                Std_Electric_Range= ("Electric_Range",  "std"),
            ).reindex(orden).round(2)
            st.dataframe(agrupado, use_container_width=True)

    # ── Gym ─────────────────────────────────────────────────────────
    elif Dataset == "gym":
        def nivel_frecuencia(val):
            try:
                val = float(val)
            except:
                return "Desconocido"
            if val < 3:
                return "Baja"
            elif val <= 5:
                return "Moderada"
            else:
                return "Alta"

        df["NivelFrecuencia"] = df["Workout_Frequency (days/week)"].apply(nivel_frecuencia)

        st.markdown("### 🏷️ Nueva variable: `NivelFrecuencia`")
        with st.container(border=True):
            st.dataframe(df[["Workout_Frequency (days/week)", "NivelFrecuencia"]].head(10), use_container_width=True)

        st.markdown("### 🔢 Conteo por categoría")
        conteo = df["NivelFrecuencia"].value_counts().reset_index()
        conteo.columns = ["NivelFrecuencia", "Cantidad"]
        with st.container(border=True):
            st.dataframe(conteo, use_container_width=True)

        st.markdown("### 📈 Gráfico de barras – Registros por Nivel de Frecuencia")
        orden = ["Baja", "Moderada", "Alta"]
        conteo_ordenado = conteo.set_index("NivelFrecuencia").reindex(orden).reset_index()
        st.bar_chart(conteo_ordenado.set_index("NivelFrecuencia")["Cantidad"])

        st.markdown("### 🔬 Análisis agrupado por `NivelFrecuencia`")
        with st.container(border=True):
            agrupado = df.groupby("NivelFrecuencia").agg(
                Media_Session_Duration  = ("Session_Duration (hours)", "mean"),
                Media_Experience_Level  = ("Experience_Level",         "mean"),
                Std_BMI                 = ("BMI",                      "std"),
            ).reindex(orden).round(2)
            st.dataframe(agrupado, use_container_width=True)

    # ── Steam (Videojuegos) ─────────────────────────────────────────
    elif Dataset == "steam":
        col_precio    = st.session_state.get("steam_col_precio", None)
        col_descuento = st.session_state.get("steam_col_descuento", None)

        # Si filtros() no corrió antes, detecta las columnas aquí también
        if col_precio is None:
            col_precio = detectar_columna_por_simbolo(df, "$")
            st.session_state.steam_col_precio = col_precio
        if col_descuento is None:
            col_descuento = detectar_columna_por_simbolo(df, "%")
            st.session_state.steam_col_descuento = col_descuento

        if col_precio is None:
            st.error("No se encontró columna de precio en Steam.")
            return

        df[col_precio] = (
            df[col_precio].astype(str)
            .str.replace(r"[^\d.]", "", regex=True)
            .replace("", "0")
            .astype(float)
        )

        def gama_juego(val):
            try:
                val = float(val)
            except:
                return "Desconocido"
            if val < 10:
                return "Baja"
            elif val <= 24:
                return "Media"
            else:
                return "Alta"

        df["GamaJuego"] = df[col_precio].apply(gama_juego)

        st.markdown("### 🏷️ Nueva variable: `GamaJuego`")
        with st.container(border=True):
            st.dataframe(df[[col_precio, "GamaJuego"]].head(10), use_container_width=True)

        st.markdown("### 🔢 Conteo por categoría")
        conteo = df["GamaJuego"].value_counts().reset_index()
        conteo.columns = ["GamaJuego", "Cantidad"]
        with st.container(border=True):
            st.dataframe(conteo, use_container_width=True)

        st.markdown("### 📈 Gráfico de barras – Juegos por Gama de Precio")
        orden = ["Baja", "Media", "Alta"]
        conteo_ordenado = conteo.set_index("GamaJuego").reindex(orden).reset_index()
        st.bar_chart(conteo_ordenado.set_index("GamaJuego")["Cantidad"])

        st.markdown("### 🔬 Análisis agrupado por `GamaJuego`")
        with st.container(border=True):
            if col_descuento:
                df[col_descuento] = (
                    df[col_descuento].astype(str)
                    .str.replace(r"[^\d.]", "", regex=True)
                    .replace("", "0")
                    .astype(float)
                )
                agrupado = df.groupby("GamaJuego").agg(
                    Media_Precio    = (col_precio,    "mean"),
                    Media_Descuento = (col_descuento, "mean"),
                    Std_Precio      = (col_precio,    "std"),
                ).reindex(orden).round(2)
            else:
                agrupado = df.groupby("GamaJuego").agg(
                    Media_Precio = (col_precio, "mean"),
                    Std_Precio   = (col_precio, "std"),
                ).reindex(orden).round(2)
            st.dataframe(agrupado, use_container_width=True)

    # ── Netflix ─────────────────────────────────────────────────────
    elif Dataset == "netflix":
        ninos    = {"G", "TV-Y", "TV-G", "TV-Y7", "TV-Y7-FV"}
        adoles   = {"PG", "TV-PG"}
        ad_jov   = {"PG-13", "TV-14"}
        adultos  = {"R", "TV-MA", "NC-17"}

        def tipo_audiencia(rating):
            if pd.isna(rating):
                return "Desconocido"
            r = str(rating).strip()
            if r in ninos:   return "Niños"
            if r in adoles:  return "Adolescentes"
            if r in ad_jov:  return "Adultos Jóvenes"
            if r in adultos: return "Adultos"
            return "Desconocido"

        df["TipoAudiencia"] = df["rating"].apply(tipo_audiencia)

        st.markdown("### 🏷️ Nueva variable: `TipoAudiencia`")
        with st.container(border=True):
            st.dataframe(df[["title", "rating", "TipoAudiencia"]].head(10), use_container_width=True)

        st.markdown("### 🔢 Conteo por categoría")
        conteo = df["TipoAudiencia"].value_counts().reset_index()
        conteo.columns = ["TipoAudiencia", "Cantidad"]
        with st.container(border=True):
            st.dataframe(conteo, use_container_width=True)

        st.markdown("### 📈 Gráfico de barras – Títulos por Tipo de Audiencia")
        orden = ["Niños", "Adolescentes", "Adultos Jóvenes", "Adultos", "Desconocido"]
        conteo_ordenado = conteo.set_index("TipoAudiencia").reindex(orden).dropna().reset_index()
        st.bar_chart(conteo_ordenado.set_index("TipoAudiencia")["Cantidad"])

        st.markdown("### 🔬 Análisis agrupado por `TipoAudiencia`")
        with st.container(border=True):
            df_movies = df[df["type"] == "Movie"].copy()
            df_movies["duracion_num"] = (
                df_movies["duration"].str.extract(r"(\d+)").astype(float)
            )
            tipo_comun = (
                df.groupby("TipoAudiencia")["type"]
                .agg(lambda x: x.value_counts().idxmax())
                .rename("Tipo_Contenido_Mas_Comun")
            )
            dur_prom = (
                df_movies.groupby("TipoAudiencia")["duracion_num"]
                .mean()
                .round(2)
                .rename("Duracion_Promedio_min")
            )
            agrupado = pd.concat([tipo_comun, dur_prom], axis=1).reindex(orden).dropna(how="all")
            st.dataframe(agrupado, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# Ejercicio 6 – Guardado de Resultados
# ════════════════════════════════════════════════════════════════════

#Var/def frecuentes
rutas_csv_actualizado = {
    "netflix":          "Data/netflix_titles_Actualizado.csv",
    "gym":              "Data/GymExerciseTracking_Actualizado.csv",
    "electric_vehicle": "Data/Electric_Vehicle_Population_Actualizado.csv",
    "steam":            "Data/steam_store_data_2024_Actualizado.csv",
}

def Guardadoderesultados(Dataset, df):
    """Guarda el DataFrame actualizado (nuevos registros + columna categórica) en un CSV nuevo."""

    if Dataset not in DATASETS_CONOCIDOS:
        return

    st.markdown("---")
    st.markdown("## 💾 Guardado de Resultados")

    df = df.copy()

    # Agrega la columna categórica correspondiente según el dataset
    if Dataset == "electric_vehicle":
        def rango_categoria(val):
            try: val = float(val)
            except: return "Desconocido"
            if val < 100:   return "Bajo"
            elif val <= 250: return "Medio"
            else:            return "Alto"
        df["RangoCategoria"] = df["Electric_Range"].apply(rango_categoria)

    elif Dataset == "gym":
        def nivel_frecuencia(val):
            try: val = float(val)
            except: return "Desconocido"
            if val < 3:    return "Baja"
            elif val <= 5: return "Moderada"
            else:          return "Alta"
        df["NivelFrecuencia"] = df["Workout_Frequency (days/week)"].apply(nivel_frecuencia)

    elif Dataset == "steam":
        col_precio = st.session_state.get("steam_col_precio", None)
        if col_precio is None:
            col_precio = detectar_columna_por_simbolo(df, "$")
            st.session_state.steam_col_precio = col_precio
        if col_precio:
            df[col_precio] = (
                df[col_precio].astype(str)
                .str.replace(r"[^\d.]", "", regex=True)
                .replace("", "0")
                .astype(float)
            )
            def gama_juego(val):
                try: val = float(val)
                except: return "Desconocido"
                if val < 10:    return "Baja"
                elif val <= 24: return "Media"
                else:           return "Alta"
            df["GamaJuego"] = df[col_precio].apply(gama_juego)

    elif Dataset == "netflix":
        ninos   = {"G", "TV-Y", "TV-G", "TV-Y7", "TV-Y7-FV"}
        adoles  = {"PG", "TV-PG"}
        ad_jov  = {"PG-13", "TV-14"}
        adultos = {"R", "TV-MA", "NC-17"}
        def tipo_audiencia(rating):
            if pd.isna(rating): return "Desconocido"
            r = str(rating).strip()
            if r in ninos:   return "Niños"
            if r in adoles:  return "Adolescentes"
            if r in ad_jov:  return "Adultos Jóvenes"
            if r in adultos: return "Adultos"
            return "Desconocido"
        df["TipoAudiencia"] = df["rating"].apply(tipo_audiencia)

    ruta = rutas_csv_actualizado[Dataset]

    with st.container(border=True):
        st.markdown(f"**📄 Archivo a guardar:** `{ruta}`")
        st.caption(f"Filas: {len(df)} | Columnas: {len(df.columns)}")

        if st.button("💾 Guardar CSV Actualizado", key=f"guardar_{Dataset}"):
            df.to_csv(ruta, index=False)
            st.success(f"✅ Guardado exitosamente en `{ruta}`")
            st.dataframe(df.tail(3), use_container_width=True)
# ════════════════════════════════════════════════════════════════════
# App principal
# ════════════════════════════════════════════════════════════════════
st.title("Trabajo de Barrera y Ajú")
 
if "bottones" not in st.session_state:
    st.session_state.bottones = ""
 
st.sidebar.markdown("## 🗂️ Datasets")
 
for nombre_datasenter in datos:
    nombre_bonito = f"📁 {nombre_datasenter.replace('_', ' ').title()}"
    if st.sidebar.button(nombre_bonito, use_container_width=True):
        st.session_state.bottones = nombre_datasenter
 
st.sidebar.markdown("---")
 
with st.sidebar.popover("➕ Agregar nueva base de datos", use_container_width=True):
    st.markdown("**📂 Sube tu archivo CSV**")
    archivo_subido = st.file_uploader("Selecciona un archivo CSV", type=["csv"])
 
    if archivo_subido is not None:
        nombre_clave = archivo_subido.name.replace(".csv", "").lower().replace(" ", "_")
        if nombre_clave not in datos:
            df_nuevo = pd.read_csv(archivo_subido)
            datos[nombre_clave] = df_nuevo
            rutas_csv[nombre_clave] = f"Data/{archivo_subido.name}"
            rutas_csv_actualizado[nombre_clave] = f"Data/{archivo_subido.name.replace('.csv', '')}_Actualizado.csv"
            st.success(f"✅ Dataset **{nombre_clave}** agregado correctamente.")
        else:
            st.info(f"ℹ️ El dataset **{nombre_clave}** ya existe.")
 
        if st.button("📂 Abrir dataset", key="abrir_nuevo"):
            st.session_state.bottones = nombre_clave
            st.rerun()
 
if st.session_state.bottones in datos:
    df_resultado, cols = tabla(st.session_state.bottones)   # Ejercicio 1 y 2
    filtros(st.session_state.bottones, df_resultado)         # Ejercicio 3
    ExploracionAvanzada(st.session_state.bottones, df_resultado)      # Ejercicio 4
    Guardadoderesultados(st.session_state.bottones, df_resultado)      # Ejercicio 6