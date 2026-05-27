import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import simpledialog
import sqlite3
import os
from datetime import datetime

class ServiWebPro:
    def __init__(self, root):
        self.root = root
        self.root.title("SERVIWEB STOCK PRO + LECTOR Y VUELTO")
        self.root.geometry("1150x920")
        
        # Variables de estado inicial
        self.usuario_actual = "admin"
        self.caja_abierta = False
        
        # Configuración ARCA (Homologación / Pruebas)
        self.cuit_empresa = "20XXXXXXXXX"
        self.token_arca = None
        self.sign_arca = None
        
        # Inicializar base de datos y tablas
        self.inicializar_base_datos()
        
        # Estilos visuales para los separadores/marcos
        self.configurar_estilos()
        
        # Arrancar en el Login
        self.pantalla_login()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Caja.TLabelframe.Label", foreground="#0056b3", font=("Arial", 11, "bold"))
        style.configure("Ventas.TLabelframe.Label", foreground="#28a745", font=("Arial", 11, "bold"))
        style.configure("Stock.TLabelframe.Label", foreground="#fd7e14", font=("Arial", 11, "bold"))

    def inicializar_base_datos(self):
        # Esto busca el archivo .db en la misma carpeta que este sccript
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_db = os.path.join(directorio_actual, "serviweb_stock_pro.db")
        self.conn = sqlite3.connect(ruta_db)
        self.cursor = self.conn.cursor()
        
        # 1. Tabla de productos (Mercadería disponible)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre TEXT,
                stock INTEGER,
                precio_costo REAL,
                precio_venta REAL
            )
        ''')
        
        # 2. Tabla de ventas / Mercadería que SALIÓ
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT,
                codigo TEXT,
                nombre TEXT,
                cantidad INTEGER,
                total REAL,
                cae_arca TEXT,
                vencimiento_cae TEXT,
                estado TEXT DEFAULT 'ACTIVA'
            )
        ''')

        # 3. Tabla para historial de caja
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS historial_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                accion TEXT,
                fecha_hora TEXT
            )
        ''')
        self.conn.commit()

    def conectar_arca_wsaa(self):
        try:
            self.token_arca = "TOKEN_PROXY_ARCA_PRE_PROD_2026"
            self.sign_arca = "SIGN_PROXY_ARCA_PRE_PROD_2026"
            return True
        except Exception as e:
            messagebox.showerror("Error ARCA", f"Fallo al conectar con WSAA (AFIP): {e}")
            return False

    def solicitar_cae_arca(self, total_venta):
        if not self.token_arca:
            if not self.conectar_arca_wsaa():
                return None, None
        try:
            cae_generado = "76234589012345"
            vencimiento_cae = datetime.now().strftime("%d/%m/%Y")
            return cae_generado, vencimiento_cae
        except Exception as e:
            return None, None

    def solicitar_anulacion_arca(self, cae_original):
        try:
            return "88341278954321"
        except Exception as e:
            return None

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def pantalla_login(self):
        self.limpiar_pantalla()
        self.root.unbind("<F1>")
        self.root.unbind("<F2>")
        self.root.unbind("<Escape>")

        frame = tk.Frame(self.root, bd=2, relief="groove", 
                         padx=20, pady=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="SERVIWEB STOCK PRO", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(frame, text="Usuario:").pack(anchor="w")
        self.entry_user = tk.Entry(frame, font=("Arial", 11))
        self.entry_user.pack(pady=5)
        self.entry_user.insert(0, "admin")

        tk.Label(frame, text="Contraseña:").pack(anchor="w")
        self.entry_pass = tk.Entry(frame, font=("Arial", 11), show="*")
        self.entry_pass.pack(pady=5)
        self.entry_pass.focus()
        
        self.entry_pass.bind("<Return>", lambda e: self.procesar_login())
        tk.Button(frame, text="Ingresar al Sistema (Enter)", bg="#0056b3", fg="white", font=("Arial", 10, "bold"), command=self.procesar_login).pack(pady=15)

    def procesar_login(self):
        user = self.entry_user.get().strip()
        pas = self.entry_pass.get().strip()
        
        if user == "admin" and pas == "admin":
            self.usuario_actual = "admin"
            self.conectar_arca_wsaa()
            self.pantalla_principal()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def ejecutar_apertura_caja(self):
        if self.caja_abierta:
            return
        self.caja_abierta = True
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cursor.execute("INSERT INTO historial_caja (usuario, accion, fecha_hora) VALUES (?, ?, ?)", (self.usuario_actual, "APERTURA", ahora))
        self.conn.commit()
        messagebox.showinfo("Caja Abierta", f"La caja ha sido abierta exitosamente.\nHora de Apertura: {ahora}")
        self.pantalla_principal()

    def ejecutar_cierre_caja(self):
        if not self.caja_abierta:
            return
        self.caja_abierta = False
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.cursor.execute("INSERT INTO historial_caja (usuario, accion, fecha_hora) VALUES (?, ?, ?)", (self.usuario_actual, "CIERRE", ahora))
        self.conn.commit()
        messagebox.showinfo("Caja Cerrada", f"La caja ha sido cerrada exitosamente.\nHora de Cierre: {ahora}")
        self.pantalla_principal()

    def pantalla_principal(self):
        self.limpiar_pantalla()
        self.root.title("SERVIWEB STOCK PRO - Panel General")
        
        # ATAJOS DE TECLADO
        self.root.bind("<F1>", lambda event: self.guardar_producto())
        self.root.bind("<F2>", lambda event: self.procesar_venta_rapida())
        self.root.bind("<Escape>", lambda event: self.limpiar_buscador())
        
        # --- SECCIÓN 1: SEPARADOR AZUL (CONTROL DE CAJA CHICA) ---
        frame_caja = ttk.LabelFrame(self.root, text=" 🔵 CONTROL DE CAJA CHICA ", style="Caja.TLabelframe", padx=5)
        frame_caja.pack(fill="x", padx=15, pady=5)

        self.btn_abrir_caja = tk.Button(frame_caja, text="ABRIR CAJA", font=("Arial", 10, "bold"), bg="#28a745", fg="white", command=self.ejecutar_apertura_caja)
        self.btn_abrir_caja.pack(side="left", padx=5)

        self.btn_cerrar_caja = tk.Button(frame_caja, text="CERRAR CAJA", font=("Arial", 10, "bold"), bg="#dc3545", fg="white", command=self.ejecutar_cierre_caja)
        self.btn_cerrar_caja.pack(side="left", padx=5)

        if not self.caja_abierta:
            lbl_estado = tk.Label(frame_caja, text="ESTADO: CAJA CERRADA", font=("Arial", 11, "bold"), fg="#dc3545")
            self.btn_abrir_caja.config(state="normal")
            self.btn_cerrar_caja.config(state="disabled")
        else:
            lbl_estado = tk.Label(frame_caja, text="ESTADO: CAJA ABIERTA (Conectado a ARCA)", font=("Arial", 11, "bold"), fg="#28a745")
            self.btn_abrir_caja.config(state="disabled")
            self.btn_cerrar_caja.config(state="normal")
        lbl_estado.pack(side="left", padx=15)

        if not self.caja_abierta:
            lbl_aviso = tk.Label(self.root, text="DEBE ABRIR CAJA PARA OPERAR EL SISTEMA", font=("Arial", 14, "bold"), fg="gray")
            lbl_aviso.pack(pady=50)
            return

        # --- SECCIÓN 2: SEPARADOR VERDE (MERCADERÍA QUE SALE / COMPATIBLE CON LECTOR) ---
        frame_buscador = ttk.LabelFrame(self.root, text=" 🟢 ESCÁNER DE CÓDIGO DE BARRA Y CONTROL DE EFECTIVO ", style="Ventas.TLabelframe", padding=10)
        frame_buscador.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_buscador, text="Apoye el Lector aquí:").pack(side="left", padx=5)
        self.txt_buscar = tk.Entry(frame_buscador, font=("Arial", 12, "bold"), width=30, bg="#f8f9fa")
        self.txt_buscar.pack(side="left", padx=5)
        self.txt_buscar.focus()
        
        # Al pasar el lector, este manda un "Enter" (Return) automático al sistema
        self.txt_buscar.bind("<Return>", lambda e: self.procesar_venta_rapida())
        
        tk.Button(frame_buscador, text="Procesar Manual (F2)", bg="#007bff", fg="white", font=("Arial", 10, "bold"), command=self.procesar_venta_rapida).pack(side="left", padx=10)
        tk.Label(frame_buscador, text="(Esc para limpiar casillero)", fg="gray").pack(side="left", padx=5)

        # --- SECCIÓN 3: SEPARADOR NARANJA (INVENTARIO Y CONTROL GENERAL) ---
        frame_tablas = ttk.LabelFrame(self.root, text=" 🟠 CONTROL GENERAL DE MERCADERÍA (LO QUE QUEDA VS LO QUE SALIÓ) ", style="Stock.TLabelframe", padding=10)
        frame_tablas.pack(fill="both", expand=True, padx=15, pady=5)

        notebook = ttk.Notebook(frame_tablas)
        notebook.pack(fill="both", expand=True)

        # PESTAÑA A: Cuánta mercadería me queda (Almacén)
        tab_inventario = tk.Frame(notebook, bg="white")
        notebook.add(tab_inventario, text="📦 MOCK / LO QUE QUEDA EN STOCK")

        columnas = ("id", "codigo", "nombre", "stock", "precio")
        self.tabla = ttk.Treeview(tab_inventario, columns=columnas, show="headings")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("codigo", text="Código")
        self.tabla.heading("nombre", text="Descripción / Artículo")
        self.tabla.heading("stock", text="MERCADERÍA DISPONIBLE (STOCK)")
        self.tabla.heading("precio", text="Precio Público")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("codigo", width=120, anchor="center")
        self.tabla.column("nombre", width=300, anchor="w")
        self.tabla.column("stock", width=180, anchor="center")
        self.tabla.column("precio", width=100, anchor="e")
        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)

        # PESTAÑA B: Cuánta mercadería salió
        tab_salidas = tk.Frame(notebook, bg="white")
        notebook.add(tab_salidas, text="📤 HISTORIAL / MERCADERÍA QUE SALIÓ")

        cols_salidas = ("id", "fecha", "codigo", "nombre", "cantidad", "total", "cae", "estado")
        self.tabla_salidas = ttk.Treeview(tab_salidas, columns=cols_salidas, show="headings")
        
        self.tabla_salidas.heading("id", text="Factura N°")
        self.tabla_salidas.heading("fecha", text="Fecha/Hora Salida")
        self.tabla_salidas.heading("codigo", text="Código")
        self.tabla_salidas.heading("nombre", text="Artículo")
        self.tabla_salidas.heading("cantidad", text="Cant.")
        self.tabla_salidas.heading("total", text="Total ($)")
        self.tabla_salidas.heading("cae", text="CAE ARCA (AFIP)")
        self.tabla_salidas.heading("estado", text="Estado")

        self.tabla_salidas.column("id", width=70, anchor="center")
        self.tabla_salidas.column("fecha", width=130, anchor="center")
        self.tabla_salidas.column("codigo", width=100, anchor="center")
        self.tabla_salidas.column("nombre", width=220, anchor="w")
        self.tabla_salidas.column("cantidad", width=50, anchor="center")
        self.tabla_salidas.column("total", width=80, anchor="e")
        self.tabla_salidas.column("cae", width=120, anchor="center")
        self.tabla_salidas.column("estado", width=90, anchor="center")
        self.tabla_salidas.pack(fill="both", expand=True, padx=5, pady=5)

        # PESTAÑA C: Panel para anular comprobantes
        tab_anulacion = tk.Frame(notebook, padx=15, pady=15)
        notebook.add(tab_anulacion, text="❌ ANULAR FACTURA / NOTA DE CRÉDITO")

        tk.Label(tab_anulacion, text="Ingrese el Número de Factura (ID) a anular:", font=("Arial", 11)).pack(anchor="w", pady=5)
        self.entry_anular_id = tk.Entry(tab_anulacion, font=("Arial", 12), width=15)
        self.entry_anular_id.pack(anchor="w", pady=5)

        tk.Button(tab_anulacion, text="PROCESAR ANULACIÓN Y REINTEGRAR STOCK", bg="#dc3545", fg="white", font=("Arial", 11, "bold"), padding=8, command=self.anular_factura_por_id).pack(anchor="w", pady=15)

        # PESTAÑA D: Formulario de Carga
        tab_carga = tk.Frame(notebook, padx=10, pady=10)
        notebook.add(tab_carga, text="➕ CARGAR NUEVA MERCADERÍA")

        tk.Label(tab_carga, text="Código de Barra:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_cod = tk.Entry(tab_carga, font=("Arial", 11), width=20)
        self.entry_cod.grid(row=0, column=1, pady=5, sticky="w")

        tk.Label(tab_carga, text="Descripción / Nombre:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nom = tk.Entry(tab_carga, font=("Arial", 11), width=40)
        self.entry_nom.grid(row=1, column=1, pady=5, sticky="w")

        tk.Label(tab_carga, text="Cantidad Stock Inicial:").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_stk = tk.Entry(tab_carga, font=("Arial", 11), width=10)
        self.entry_stk.grid(row=2, column=1, pady=5, sticky="w")

        tk.Label(tab_carga, text="Precio Costo ($):").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_costo = tk.Entry(tab_carga, font=("Arial", 11), width=15)
        self.entry_costo.grid(row=3, column=1, pady=5, sticky="w")

        tk.Label(tab_carga, text="Precio Venta ($):").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_venta = tk.Entry(tab_carga, font=("Arial", 11), width=15)
        self.entry_venta.grid(row=4, column=1, pady=5, sticky="w")

        tk.Button(tab_carga, text="GUARDAR ARTÍCULO (F1)", bg="#28a745", fg="white", font=("Arial", 11, "bold"), command=self.guardar_producto).grid(row=5, column=0, columnspan=2, pady=20)

        self.cargar_productos_tabla()
        self.cargar_salidas_tabla()

    def limpiar_buscador(self):
        if hasattr(self, 'txt_buscar'):
            self.txt_buscar.delete(0, tk.END)

    def guardar_producto(self):
        if not hasattr(self, 'entry_cod'):
            return
        cod = self.entry_cod.get().strip()
        nom = self.entry_nom.get().strip()
        stk = self.entry_stk.get().strip()
        cos = self.entry_costo.get().strip()
        ven = self.entry_venta.get().strip()

        if not (cod and nom and stk and ven):
            messagebox.showwarning("Campos vacíos", "Por favor completa Código, Nombre, Stock y Precio Venta.")
            return

        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO productos (codigo, nombre, stock, precio_costo, precio_venta)
                VALUES (?, ?, ?, ?, ?)
            ''', (cod, nom, int(stk), float(cos) if cos else 0.0, float(ven)))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Producto registrado en base de datos.")
            
            self.entry_cod.delete(0, tk.END)
            self.entry_nom.delete(0, tk.END)
            self.entry_stk.delete(0, tk.END)
            self.entry_costo.delete(0, tk.END)
            self.entry_venta.delete(0, tk.END)
            
            self.cargar_productos_tabla()
        except Exception as e:
            print(f"Error al guardar: {e}")

    def lanzar_ventana_vuelto(self, nombre_prod, precio_total):
        """ Abre una pantalla interactiva para ingresar el billete y calcular el vuelto """
        ventana_vuelto = tk.Toplevel(self.root)
        ventana_vuelto.title("PAGO Y VUELTO EN EFECTIVO")
        ventana_vuelto.geometry("400x300")
        ventana_vuelto.resizable(False, False)
        ventana_vuelto.grab_set() # Bloquea la de atrás hasta terminar la cuenta
        
        # Centrar ventana flotante
        ventana_vuelto.transient(self.root)
        
        tk.Label(ventana_vuelto, text=f"Artículo: {nombre_prod}", font=("Arial", 11, "italic")).pack(pady=5)
        tk.Label(ventana_vuelto, text=f"TOTAL A PAGAR: ${precio_total:.2f}", font=("Arial", 14, "bold"), fg="#dc3545").pack(pady=10)
        
        tk.Label(ventana_vuelto, text="¿Con cuánto billete paga?", font=("Arial", 11, "bold")).pack(pady=2)
        entry_efectivo = tk.Entry(ventana_vuelto, font=("Arial", 14, "bold"), width=15, justify="center")
        entry_efectivo.pack(pady=5)
        entry_efectivo.focus()
        
        lbl_vuelto_resultado = tk.Label(ventana_vuelto, text="VUELTO: $0.00", font=("Arial", 16, "bold"), fg="#28a745")
        lbl_vuelto_resultado.pack(pady=15)
        
        self.resultado_pago = {"confirmado": False, "monto_abonado": 0.0}

        def calcular_al_escribir(event):
            try:
                abonado = float(entry_efectivo.get().strip())
                vuelto = abonado - precio_total
                if vuelto >= 0:
                    lbl_vuelto_resultado.config(text=f"VUELTO: ${vuelto:.2f}", fg="#28a745")
                else:
                    lbl_vuelto_resultado.config(text="Efectivo Insuficiente", fg="#dc3545")
            except ValueError:
                lbl_vuelto_resultado.config(text="VUELTO: $0.00", fg="gray")

        def finalizar_pago():
            try:
                abonado = float(entry_efectivo.get().strip())
                if abonado < precio_total:
                    messagebox.showwarning("Error de pago", "El dinero ingresado es menor al precio del producto.")
                    return
                self.resultado_pago["confirmado"] = True
                self.resultado_pago["monto_abonado"] = abonado
                ventana_vuelto.destroy()
            except ValueError:
                messagebox.showwarning("Error", "Ingrese un número válido para el billete.")

        # Evento dinámico: calcula el vuelto al vuelo mientras vas escribiendo
        entry_efectivo.bind("<KeyRelease>", calcular_al_escribir)
        # Al dar enter dentro del efectivo, cierra y confirma
        entry_efectivo.bind("<Return>", lambda e: finalizar_pago())
        
        tk.Button(ventana_vuelto, text="CONFIRMAR VENTA (Enter)", font=("Arial", 11, "bold"), bg="#2f8a745", fg="white", command=finalizar_pago).pack(padding=5)
        
        self.root.wait_window(ventana_vuelto)
        return self.resultado_pago

    def interstate_check(self):
        pass

    def procesar_venta_rapida(self):
        if not hasattr(self, 'txt_buscar'):
            return
            
        codigo_buscar = self.txt_buscar.get().strip()
        if not codigo_buscar:
            return

        self.cursor.execute("SELECT nombre, stock, precio_venta FROM productos WHERE codigo = ?", (codigo_buscar,))
        prod = self.cursor.fetchone()

        if prod:
            nombre, stock, precio = prod
            if stock > 0:
                # Lanzar la nueva interfaz de cálculo de vuelto en efectivofff
                pago = self.lanzar_ventana_vuelto(nombre, precio)
                
                if pago["confirmado"]:
                    cae, vto_cae = self.solicitar_cae_arca(precio)
                    
                    if cae:
                        nuevo_stock = stock - 1
                        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        
                        self.cursor.execute("UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo_buscar))
                        self.cursor.execute('''
                            INSERT INTO ventas (fecha_hora, codigo, nombre, cantidad, total, cae_arca, vencimiento_cae, estado) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVA')
                        ''', (ahora, codigo_buscar, nombre, 1, precio, cae, vto_cae))
                        self.conn.commit()
                        
                        vuelto_final = pago["monto_abonado"] - precio
                        messagebox.showinfo("Venta Guardada con Éxito", 
                                            f"Artículo: {nombre}\nTotal: ${precio}\nPagó con: ${pago['monto_abonado']}\n\n👉 ENTREGAR DE VUELTO: ${vuelto_final:.2f}\n\nCAE Legal: {cae}")
                        
                        self.txt_buscar.delete(0, tk.END)
                        self.cargar_productos_tabla()
                        self.cargar_salidas_tabla()
                    else:
                        messagebox.showerror("Error ARCA", "ARCA rechazó el comprobante. Venta cancelada.")
                else:
                    print("[VENTA] Cancelada por el usuario en la ventana de vuelto.")
            else:
                messagebox.showwarning("Sin Stock", f"El producto '{nombre}' no tiene stock disponible.")
        else:
            messagebox.showerror("No encontrado", "El código escaneado no existe.")
        
        self.txt_buscar.delete(0, tk.END)
        self.txt_buscar.focus()

    def anular_factura_por_id(self):
        factura_id = self.entry_anular_id.get().strip()
        if not factura_id:
            messagebox.showwarning("Falta ID", "Por favor, ingrese un número de factura válido.")
            return

        self.cursor.execute("SELECT codigo, nombre, cantidad, cae_arca, estado FROM ventas WHERE id = ?", (factura_id,))
        venta = self.cursor.fetchone()

        if not venta:
            messagebox.showerror("No encontrada", f"La factura N° {factura_id} no existe.")
            return

        codigo, nombre, cantidad, cae_original, estado_actual = venta

        if estado_actual == "ANULADA":
            messagebox.showwarning("Ya anulada", f"La factura N° {factura_id} ya está ANULADA.")
            return

        confirmar = messagebox.askyesno("Confirmar Anulación", f"¿Anular factura N° {factura_id}?\nSe devolverán {cantidad} unidad(es) al stock.")
        
        if confirmar:
            cae_nc = self.solicitar_anulacion_arca(cae_original)
            if cae_nc:
                self.cursor.execute("UPDATE ventas SET estado = 'ANULADA' WHERE id = ?", (factura_id,))
                self.cursor.execute("SELECT stock FROM productos WHERE codigo = ?", (codigo,))
                prod_stock = self.cursor.fetchone()
                if prod_stock:
                    nuevo_stock = prod_stock[0] + cantidad
                    self.cursor.execute("UPDATE productos SET stock = ? WHERE codigo = ?", (nuevo_stock, codigo))
                
                self.conn.commit()
                messagebox.showinfo("Anulación Exitosa", f"Factura N° {factura_id} anulada.\nMercadería reingresada.")
                self.entry_anular_id.delete(0, tk.END)
                self.cargar_productos_tabla()
                self.cargar_salidas_tabla()

    def cargar_productos_tabla(self):
        if not hasattr(self, 'tabla'):
            return
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            self.cursor.execute("SELECT id, codigo, nombre, stock, precio_venta FROM productos")
            for fila in self.cursor.fetchall():
                self.tabla.insert("", "end", values=fila)
        except Exception as e:
            print(f"Error al cargar almacén: {e}")

    def cargar_salidas_tabla(self):
        if not hasattr(self, 'tabla_salidas'):
            return
        for item in self.tabla_salidas.get_children():
            self.tabla_salidas.delete(item)
        try:
            self.cursor.execute("SELECT id, fecha_hora, codigo, nombre, cantidad, total, cae_arca, estado FROM ventas ORDER BY id DESC")
            for fila in self.cursor.fetchall():
                self.tabla_salidas.insert("", "end", values=fila)
        except Exception as e:
            print(f"Error al cargar historial: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServiWebPro(root)
    root.mainloop()