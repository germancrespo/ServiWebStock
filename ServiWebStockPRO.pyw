import os
import sqlite3
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

class ServiWebPro:
    def __init__(self, root):
        self.root = root
        self.root.title("ServiWeb Stock Pro - Gestión Comercial con Lector")
        self.root.geometry("950x720")
        
        self.usuario_actual = None
        self.inicializar_base_datos()
        self.pantalla_login()

    def inicializar_base_datos(self):
        # Conexión a Base de Datos SQLite (Soporta más de 1,000 productos de forma segura)
        self.conn = sqlite3.connect("inventario_pro.db")
        self.cursor = self.conn.cursor()
        
        # Estructura de la tabla de productos con código de barras
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre TEXT,
                stock INTEGER,
                vendidos INTEGER DEFAULT 0,
                precio_costo REAL,
                precio_venta REAL
            )
        ''')
        
        # Tabla de Usuarios y Empleados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password TEXT,
                rol TEXT
            )
        ''')
        
        # Usuarios iniciales de prueba (Admin y Empleado)
        self.cursor.execute("SELECT COUNT(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany("INSERT INTO usuarios VALUES (?, ?, ?)", [
                ("admin", "admin123", "Administrador"),
                ("empleado1", "venta123", "Empleado")
            ])
        self.conn.commit()

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- PANTALLA 1: INICIO DE SESIÓN ---
    def pantalla_login(self):
        self.limpiar_pantalla()
        self.root.geometry("400x300")
        frame = tk.Frame(self.root, pady=20)
        frame.pack(expand=True)
        
        tk.Label(frame, text="🌐 SERVIWEB STOCK PRO", font=("Arial", 14, "bold"), fg="#0056b3").pack(pady=10)
        tk.Label(frame, text="Usuario:").pack(anchor="w")
        self.entry_user = tk.Entry(frame, width=30)
        self.entry_user.pack(pady=5)
        tk.Label(frame, text="Contraseña:").pack(anchor="w")
        self.entry_pass = tk.Entry(frame, show="*", width=30)
        self.entry_pass.pack(pady=5)
        
        tk.Button(frame, text="Ingresar al Sistema", bg="#0056b3", fg="white", font=("Arial", 10, "bold"), width=25, command=self.procesar_login).pack(pady=15)

    def procesar_login(self):
        user = self.entry_user.get().strip()
        pas = self.entry_pass.get().strip()
        
        self.cursor.execute("SELECT username, rol FROM usuarios WHERE username=? AND password=?", (user, pas))
        resultado = self.cursor.fetchone()
        
        if resultado:
            self.usuario_actual = f"{resultado[0]} ({resultado[1]})"
            self.root.geometry("950x720")
            self.pantalla_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    # --- PANTALLA 2: PANEL DE CONTROL PRINCIPAL ---
    def pantalla_principal(self):
        self.limpiar_pantalla()
        
        # Encabezado Corporativo
        frame_header = tk.Frame(self.root, bg="#0056b3", height=50)
        frame_header.pack(fill="x", padx=0, pady=0)
        tk.Label(frame_header, text="🌐 SERVIWEB STOCK PRO (Modo Lector Activo)", font=("Arial", 16, "bold"), fg="white", bg="#0056b3").pack(side="left", padx=15, pady=10)
        tk.Label(frame_header, text=f"Sesión: {self.usuario_actual}", font=("Arial", 10, "italic"), fg="lightgray", bg="#0056b3").pack(side="right", padx=15, pady=15)

        # Buscador / Escáner de Venta Rápida (Para pistola de códigos de barras)
        frame_buscar = tk.LabelFrame(self.root, text=" Buscador / Escáner de Venta Rápida ")
        frame_buscar.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_buscar, text="🔍 Escanee código o escriba nombre:").pack(side="left", padx=5, pady=5)
        self.entry_buscar = tk.Entry(frame_buscar, width=40, bg="#eef7ff", font=("Arial", 10, "bold"))
        self.entry_buscar.pack(side="left", padx=5, pady=5)
        self.entry_buscar.focus_set() # Foco automático aquí para escanear de inmediato
        
        # Enlaces de eventos del teclado y lector
        self.entry_buscar.bind("<KeyRelease>", lambda event: self.actualizar_tabla())
        self.entry_buscar.bind("<Return>", self.buscar_y_autocompletar_por_codigo)

        # Formulario de Datos del Producto
        frame_inputs = tk.LabelFrame(self.root, text=" Información del Producto ")
        frame_inputs.pack(fill="x", padx=15, pady=5)
        
        tk.Label(frame_inputs, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_codigo = tk.Entry(frame_inputs, width=25, font=("Arial", 9, "bold"))
        self.entry_codigo.grid(row=0, column=1, padx=5, pady=5)
        self.entry_codigo.bind("<Return>", self.buscar_en_formulario_por_codigo)
        
        tk.Label(frame_inputs, text="Nombre Producto:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_nombre = tk.Entry(frame_inputs, width=25)
        self.entry_nombre.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(frame_inputs, text="Cantidad / Stock:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_cantidad = tk.Entry(frame_inputs, width=25)
        self.entry_cantidad.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_inputs, text="P. Costo ($):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_costo = tk.Entry(frame_inputs, width=12)
        self.entry_costo.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_inputs, text="P. Venta ($):").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.entry_venta = tk.Entry(frame_inputs, width=12)
        self.entry_venta.grid(row=1, column=5, padx=5, pady=5)
        
        # Botones de Control Operativo
        tk.Button(frame_inputs, text="📥 Registrar Entrada", bg="#d4edda", font=("Arial", 9, "bold"), command=self.registrar_entrada).grid(row=2, column=1, pady=10)
        tk.Button(frame_inputs, text="📤 Registrar Venta", bg="#f8d7da", font=("Arial", 9, "bold"), command=self.registrar_venta).grid(row=2, column=3, pady=10)
        tk.Button(frame_inputs, text="🗑️ Eliminar", bg="#fff3cd", command=self.eliminar_producto).grid(row=2, column=0, pady=10, padx=5)
        tk.Button(frame_inputs, text="📊 Generar Reporte", bg="#cff4fc", font=("Arial", 9, "bold"), command=self.generar_reporte).grid(row=2, column=4, pady=10, padx=10)
        tk.Button(frame_inputs, text="🚪 Cerrar Sesión", bg="#e2e3e5", command=self.pantalla_login).grid(row=2, column=5, pady=10, padx=10)

        # Tabla del Almacén con barra de desplazamiento (Scroll)
        frame_tabla = tk.LabelFrame(self.root, text=" Base de Datos de Inventario ")
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=5)
        
        columnas = ("Código", "Producto", "Stock", "Vendidos", "P. Costo", "P. Venta", "Ganancia")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor="center", width=110)
            
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_producto)

        # Barra inferior de indicador verde de Ganancia Total
        self.label_ganancia_total = tk.Label(self.root, text="GANANCIA TOTAL: $0.00", font=("Arial", 14, "bold"), fg="#155724", bg="#d4edda", bd=2, relief="groove")
        self.label_ganancia_total.pack(fill="x", padx=15, pady=10)
        
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
            
        filtro = self.entry_buscar.get().strip()
        
        if filtro:
            self.cursor.execute("SELECT codigo, nombre, stock, vendidos, precio_costo, precio_venta FROM productos WHERE nombre LIKE ? OR codigo = ?", (f"%{filtro}%", filtro))
        else:
            self.cursor.execute("SELECT codigo, nombre, stock, vendidos, precio_costo, precio_venta FROM productos")
            
        items = self.cursor.fetchall()
        
        # Calcular sumatoria total de ganancias netas en tiempo real
        self.cursor.execute("SELECT SUM(vendidos * (precio_venta - precio_costo)) FROM productos")
        res_ganancia = self.cursor.fetchone()
        total_ganancia = res_ganancia[0] if res_ganancia[0] is not None else 0.0
        
        for item in items:
            cod, nom, stock, vend, costo, venta = item
            ganancia_ind = vend * (venta - costo)
            self.tabla.insert("", "end", values=(cod, nom, stock, vend, f"${costo:.2f}", f"${venta:.2f}", f"${ganancia_ind:.2f}"))
            
        self.label_ganancia_total.config(text=f"GANANCIA TOTAL EN SISTEMA: ${total_ganancia:.2f}")

    def buscar_y_autocompletar_por_codigo(self, event):
        codigo = self.entry_buscar.get().strip()
        if not codigo: return
        
        self.cursor.execute("SELECT codigo, nombre, precio_costo, precio_venta FROM productos WHERE codigo=?", (codigo,))
        prod = self.cursor.fetchone()
        
        if prod:
            self.limpiar_campos()
            self.entry_codigo.insert(0, prod[0])
            self.entry_nombre.insert(0, prod[1])
            self.entry_costo.insert(0, prod[2])
            self.entry_venta.insert(0, prod[3])
            self.entry_cantidad.focus_set()
            self.entry_buscar.delete(0, tk.END)
        else:
            self.limpiar_campos()
            self.entry_codigo.insert(0, codigo)
            self.entry_nombre.focus_set()
            self.entry_buscar.delete(0, tk.END)
            messagebox.showinfo("Nuevo", "Código no registrado. Rellene los datos para agregarlo.")

    def buscar_en_formulario_por_codigo(self, event):
        codigo = self.entry_codigo.get().strip()
        if not codigo: return
        self.cursor.execute("SELECT nombre, precio_costo, precio_venta FROM productos WHERE codigo=?", (codigo,))
        prod = self.cursor.fetchone()
        if prod:
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, prod[0])
            self.entry_costo.delete(0, tk.END)
            self.entry_costo.insert(0, prod[1])
            self.entry_venta.delete(0, tk.END)
            self.entry_venta.insert(0, prod[2])
            self.entry_cantidad.focus_set()

    def seleccionar_producto(self, event):
        seleccion = self.tabla.selection()
        if seleccion:
            valores = self.tabla.item(seleccion, "values")
            self.limpiar_campos()
            self.entry_codigo.insert(0, valores[0])
            self.entry_nombre.insert(0, valores[1])
            self.entry_cantidad.insert(0, valores[2])

    def registrar_entrada(self):
        cod = self.entry_codigo.get().strip()
        nom = self.entry_nombre.get().strip()
        cant_str = self.entry_cantidad.get().strip()
        costo_str = self.entry_costo.get().strip()
        venta_str = self.entry_venta.get().strip()
        
        if not nom or not cant_str or not costo_str or not venta_str:
            messagebox.showwarning("Error", "Nombre, cantidad y precios son obligatorios.")
            return
        try:
            cant = int(cant_str)
            costo = float(costo_str)
            venta = float(venta_str)
            if cant <= 0 or costo < 0 or venta < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Los números ingresados son incorrectos.")
            return

        self.cursor.execute("SELECT id, stock FROM productos WHERE (codigo=? AND codigo!='') OR nombre=?", (cod, nom))
        existe = self.cursor.fetchone()
        
        if existe:
            self.cursor.execute("UPDATE productos SET stock = stock + ?, precio_costo = ?, precio_venta = ?, codigo = ? WHERE id = ?", (cant, costo, venta, cod, existe[0]))
        else:
            self.cursor.execute("INSERT INTO productos (codigo, nombre, stock, precio_costo, precio_venta) VALUES (?, ?, ?, ?, ?)", (cod, nom, cant, costo, venta))
            
        self.conn.commit()
        self.actualizar_tabla()
        self.limpiar_campos()
        self.entry_buscar.focus_set()

    def registrar_venta(self):
        cod = self.entry_codigo.get().strip()
        nom = self.entry_nombre.get().strip()
        cant_str = self.entry_cantidad.get().strip()
        
        if not cant_str or (not cod and not nom):
            messagebox.showwarning("Error", "Debe identificar el producto e ingresar una cantidad.")
            return
        try:
            cant = int(cant_str)
            if cant <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "La cantidad ingresada no es válida.")
            return

        self.cursor.execute("SELECT id, stock FROM productos WHERE (codigo=? AND codigo!='') OR nombre=?", (cod, nom))
        res = self.cursor.fetchone()
        
        if not res:
            messagebox.showerror("Error", "El producto buscado no existe.")
            return
        if res[1] < cant:
            messagebox.showerror("Sin Stock", f"No hay stock suficiente. Quedan {res[1]} unidades.")
            return
            
        self.cursor.execute("UPDATE productos SET stock = stock - ?, vendidos = vendidos + ? WHERE id = ?", (cant, cant, res[0]))
        self.conn.commit()
        self.actualizar_tabla()
        self.limpiar_campos()
        self.entry_buscar.focus_set()

    def eliminar_producto(self):
        nom = self.entry_nombre.get().strip()
        if not nom: return
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar permanentemente '{nom}' del almacén?"):
            self.cursor.execute("DELETE FROM productos WHERE nombre=?", (nom,))
            self.conn.commit()
            self.actualizar_tabla()
            self.limpiar_campos()

    def generar_reporte(self):
        try:
            self.cursor.execute("SELECT codigo, nombre, stock, vendidos, precio_costo, precio_venta FROM productos")
            filas = self.cursor.fetchall()
            if not filas:
                messagebox.showwarning("Aviso", "No hay datos para exportar.")
                return
            
            fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M")
            nombre_archivo = f"Reporte_ServiWeb_{fecha_hoy}.csv"
            
            with open(nombre_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
                escritor = csv.writer(f, delimiter=";")
                escritor.writerow(["REPORTE DE INVENTARIO - SERVIWEB STOCK PRO"])
                escritor.writerow([f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                escritor.writerow([])
                escritor.writerow(["Código", "Producto", "Stock Actual", "Unidades Vendidas", "Precio Costo", "Precio Venta", "Inversión Stock", "Ventas Totales", "Ganancia Neta"])
                
                tot_inversion, tot_ventas, tot_ganancias = 0, 0, 0
                for fila in filas:
                    cod, nom, stock, vend, costo, venta = fila
                    inv, vts, gnc = stock*costo, vend*venta, vend*(venta-costo)
                    tot_inversion += inv; tot_ventas += vts; tot_ganancias += gnc
                    escritor.writerow([cod, nom, stock, vend, f"${costo:.2f}", f"${venta:.2f}", f"${inv:.2f}", f"${vts:.2f}", f"${gnc:.2f}"])
                
                escritor.writerow([])
                escritor.writerow(["TOTALES GENERALES DEL COMERCIO"])
                escritor.writerow(["Valor de Mercancía en Stock (Inversión)", f"${tot_inversion:.2f}"])
                escritor.writerow(["Caja Bruta Recaudada", f"${tot_ventas:.2f}"])
                escritor.writerow(["Utilidad Real Limpia", f"${tot_ganancias:.2f}"])
                
            messagebox.showinfo("Reporte Exitoso", f"El archivo se guardó como:\n'{nombre_archivo}'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo escribir el reporte: {str(e)}")

    def limpiar_campos(self):
        self.entry_codigo.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_cantidad.delete(0, tk.END)
        self.entry_costo.delete(0, tk.END)
        self.entry_venta.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiWebPro(root)
    root.mainloop()