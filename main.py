import streamlit as st
import pandas as pd
import scipy.stats as stats

# Configuración para pantalla completa
st.set_page_config(layout="wide")

st.title("Generador Chi Cuadrada")
st.divider()

# Función para realizar las operaciones
def multiplicador_constante(constante, semilla1, iteraciones):
    # Lista para almacenar los resultados
    resultados = []
    
    for i in range(iteraciones):
        # Calcula el producto de la semilla
        producto = semilla1 * constante
        longitud = len(str(producto))
        
        # Asegurándonos de que producto tenga 0 a la izquierda si es necesario
        if longitud <= 8:
            producto = f"{producto:08}"
        elif longitud <= 16:
            producto = f"{producto:016}"
        elif longitud <= 32:
            producto = f"{producto:032}"
        
        # Tomando los 4 dígitos de en medio según la longitud
        if longitud <= 8:
            medio = producto[2:6]
        elif longitud <= 16:
            medio = producto[6:10]
        elif longitud <= 32:
            medio = producto[14:18]
        
        # Convirtiendo a int()
        medio = int(medio)
        
        # Obteniendo ri
        ri = medio / 10000
        
        # Guardamos los resultados en una lista
        resultados.append({
            'Semilla 1': semilla1,
            'Constante': constante,
            'Producto': producto,
            'Longitud': longitud,
            'Medio': medio,
            'ri': ri
        })
                
        # La nueva semilla será el valor de 'medio' calculado en esta iteración
        semilla1 = medio
        
    return resultados

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":

    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.5, 3])

    with col1:
        st.header("1. Ingresa los datos")
        semilla1_input = st.text_input("Ingresa tu semilla (número de dígitos pares y mayor a 0):")
        constante_input = st.text_input("Ingresa tu constante (número de dígitos pares y mayor a 0):")
        iteraciones_input = st.text_input("Ingresa las iteraciones:")
    

    # Si ambos inputs están llenos, hacer las validaciones y mostrar los resultados
    if semilla1_input and constante_input and iteraciones_input:
        try:
            semilla1 = int(semilla1_input)  # Convertir la semilla a entero
            constante = int(constante_input)  # Convertir la semilla a entero
            iteraciones = int(iteraciones_input)  # Convertir las iteraciones a entero

            # Validación de las condiciones de entrada
            if semilla1 > 0 and len(str(semilla1)) % 2 == 0 and constante > 0 and len(str(constante)) % 2 == 0 and iteraciones > 0:
                # Obtener los resultados de las operaciones
                resultados = multiplicador_constante(constante, semilla1, iteraciones) 
                
                # Guardar los resultados en session_state para usarlos en otra página
                st.session_state.datos = resultados
                            
                # Mostrar la tabla en la columna derecha
                with col2:
                    st.header("Tabla Generada con Multiplicador Constante")
                                    
                    # Convertir la lista de diccionarios en un DataFrame
                    df = pd.DataFrame(resultados)
                    
                    df.index = df.index + 1
                    df = df.rename_axis("Iteración")
                    st.dataframe(df, use_container_width = True)                

            else:
                st.error("Recuerda que la semilla debe tener un número de dígitos pares y mayor a 0, y las iteraciones deben ser mayores a 0.")
        except ValueError:
            st.error("Por favor, ingresa valores numéricos válidos para la semilla y las iteraciones.")
            
            
    with col1:
        if iteraciones_input:
            st.divider()
            st.header("2. Genera")
            if st.button("Ir a Chi Cuadrada"):
                st.session_state.pagina = "Resolver"
                st.rerun()  # Recarga la página 
                        
# Página de resolución
elif st.session_state.pagina == "Resolver":

    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.2, 3])
    
    if "resultados" in st.session_state:  # Verifica que los datos existan
        resultados = st.session_state.resultados

    if "datos" in st.session_state:  # Verifica que los datos existan
        datos = st.session_state["datos"]
        
        with col1:
            # Crear un DataFrame solo con la columna 'ri'
            df_ri = pd.DataFrame(datos)[['ri']]
            
            # Mostrar la tabla con solo la columna 'ri'
            st.subheader("Números Pseudoaleatorios")
            df_ri.index = df_ri.index + 1
            df = df_ri.rename_axis("Intervalos")
            st.dataframe(df, use_container_width = True)
            
        with col2:
            st.subheader("Ingreso de datos")
            
            # Intervalo de confianza
            intervalo_de_cf = st.number_input("Ingresa el intervalo de confianza:", min_value = 0, max_value = 100, step = 1)
            
            if intervalo_de_cf:
                # Alpha
                alpha = (100 - intervalo_de_cf)/100
                            
                # Contar número de elementos
                n = df_ri.shape[0]
                
                # Número de intervalos         
                m = round(n**0.5)

                # En caso de ser siempre al número de arriba
                #m = math.ceil(n**0.5)
                
                # Grados de libertad
                grados_de_libertad = m - 1
                
                # Amplitud de intervalos
                amplitud = 1 / m
                
                # Generando tabla de Chi Cuadrada
                resultados = []
                
                # Limites de los intervalos
                lim_inf = 0
                lim_sup = amplitud
                
                # Chi
                chi_cuadrada = 0
                
                # Frecuencia observada
                frecuencia_o = 0
                
                # Accediendo solo a la columna 'ri' de los datos
                for i in range(1, m + 1):
                    oi = 0  # Reiniciar el contador de Oi para cada intervalo
                    
                    if i == m:
                        lim_sup = 1
                    
                    # Iterar solo sobre los valores de 'ri'
                    for num in df_ri['ri']:  # Accedemos directamente a la columna 'ri'
                        if num >= lim_inf and num < lim_sup:
                            oi += 1  # Incrementar Oi si cae en el intervalo
                            
                    # Frecuencia total  
                    frecuencia_o += oi
                    
                    # Valor esperado
                    ei = n//m
                    
                    # Formula chi cuadrada
                    form = (oi-ei)**2/ei
                    
                    # Agregar los resultados a la lista
                    resultados.append({
                        'Limite Inferior': lim_inf,
                        'Limite Superior': lim_sup,
                        'Oi': oi,
                        'Ei': ei,
                        '(Ei-Oi)^2/Ei': form,
                    })
                    
                    # Valor total de chi cuadrada
                    chi_cuadrada += form

                    # Actualizar los límites del intervalo
                    lim_inf = lim_sup
                    lim_sup += amplitud
                
                # Convertir los resultados en un DataFrame para mostrar
                df_resultados = pd.DataFrame(resultados)
                
                # Ajustar el índice de df_resultados para empezar desde 1
                df_resultados.index = df_resultados.index + 1
                df_resultados = df_resultados.rename_axis("Intervalo")

                # Crear la nueva fila con valores totales
                nueva_fila = pd.DataFrame({
                    'Limite Inferior': [""],  # Dejar vacío en lugar de None para evitar problemas de visualización
                    'Limite Superior': [""],
                    'Oi': [frecuencia_o],
                    'Ei': [""],  # También dejar en blanco
                    '(Ei-Oi)^2/Ei': [chi_cuadrada],
                }, index = ["Total"]) 

                # Concatenar manteniendo el índice nombrado
                df_final = pd.concat([df_resultados, nueva_fila]).rename_axis("Intervalo")

                # Mostrar la tabla con la fila extra
                st.subheader("Tabla de Chi Cuadrada")
                st.table(df_final)
                
                # Muestra la imagen de la tabla Chi Cuadrada            
                st.image("chi_cuadrada.png", caption = "Tabla de Chi Cuadrada.")
                
                chi2_critico = stats.chi2.ppf(1 - alpha, grados_de_libertad)

                # Estadístico de chi cuadrada
                st.write(f"El estadístico de chi cuadrada fue {chi_cuadrada}")
                
                # Mostrar el valor crítico para referencia
                st.write(f"Valor crítico de chi-cuadrada: {chi2_critico}")

                # Ahora compara el valor calculado (chi_cuadrada) con el valor crítico
                if chi_cuadrada < chi2_critico:
                    st.success("Se acepta la hipótesis nula")
                else:
                    st.error("Hipótesis nula rechazada")
            
    else:
        st.error("No hay datos disponibles. Regresa a la página principal.")

    with st.expander("Hecho por:"):
        st.write("Rodrigo González López S4A")