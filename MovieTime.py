import pandas as pd
"""No me agarra el csv jaja salu2"""
Funciones = ["codigo", "nombre", "hora", "precio"]
Ventas = ["codigo", "nombre", "cantidad", "total"]

df_funciones = pd.DataFrame(Funciones, ["codigo", "nombre", "hora", "precio"])
df_ventas = pd.DataFrame(Ventas ["codigo", "nombre", "cantidad", "total"])
df_funciones.to_csv("Funciones.csv", index=False)
df_ventas.to_csv("Ventas.csv", index=False)

def Mostrar_Menu():
    print("==========================")
    print("          Menu MovieTime")
    print("==========================")
    print("1. Registrar Funciones")
    print("2. Listar Funciones Disponibles")
    print("3. Vender Boletos")
    print("4. Resumen de Ventas Diaria")
    print("5. Salir")

def Registrar_Funciones():
    global df_funciones
    print("Nueva Funcion :D")
    nuevo_codigo = input("Ingrese el código de la función: ")

    if nuevo_codigo in df_funciones["codigo"].values:
        print("El código ya existe usar otro")
        return
    
    nuevo_nombre = input("Ingrese el nombre de la función: ")
    nueva_hora = input("La hora de la función es: ")
    
    while True:
        try:
            nuevo_precio = float(input("El precio de la función es de: "))
            break
        except ValueError:
            print("Error: Ingrese un número válido para el precio")

    nueva_funcion = pd.DataFrame([{"codigo": nuevo_codigo, "nombre": nuevo_nombre, "hora": nueva_hora, "precio": nuevo_precio}])
    df_funciones = pd.concat([df_funciones, nueva_funcion], ignore_index=True)
    print("Nueva Funcion agregada")

def Listar_Funciones():
    if df_funciones.empty:
        print("\nNo hay funciones disponibles.")
    else:
        print("\nFunciones Disponibles: ")
        print(df_funciones)

def Vender_Boletos():
    global df_ventas
    
    if df_funciones.empty:
        print("\nNo hay funciones registradas para vender boletos")
        return

    Listar_Funciones()
    print("\nVenta de Boletos: ")
    codigo_funcion = input("Ingrese el código de la función para la venta: ")

    funcion_seleccionada = df_funciones[df_funciones["codigo"] == codigo_funcion]

    if funcion_seleccionada.empty:
        print("Codigo no encontrado")
        return
    else:
        cantidad = int(input("¿Cuántos boletos desea comprar?: "))
        if cantidad <= 0 <= 200:
            print("Cantidad invalida")
            return

    precio = funcion_seleccionada["precio"].iloc[0]
    nombre = funcion_seleccionada["nombre"].iloc[0]

    total_venta = cantidad * precio
    print(f"\nEl total a pagar es: ${total_venta}")

    nueva_venta = pd.DataFrame([{"codigo": codigo_funcion, "nombre": nombre, "cantidad": cantidad, "total": total_venta}])
    df_ventas = pd.concat([df_ventas, nueva_venta], ignore_index=True)
    print("Venta registrada exitosamente.")

def Resumen_Ventas_Diaria():
    if df_ventas.empty:
        print("\nNo se hicieron ventas")
        return
    else:
        print("No alcanzo a hacer esta funcion :(")

def main():
    while True:
        Mostrar_Menu()
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            Registrar_Funciones()
        elif opcion == "2":
            Listar_Funciones()
        elif opcion == "3":
            Vender_Boletos()
        elif opcion == "4":
            Resumen_Ventas_Diaria()
        else:
            print("Bye bye")
            break


main()