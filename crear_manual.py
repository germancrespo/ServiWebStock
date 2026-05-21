import os

contenido_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Manual de Usuario - ServiWeb Stock Pro</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 40px 20px; background-color: #f9f9f9; }
        .container { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        .header { text-align: center; border-bottom: 3px solid #0056b3; padding-bottom: 20px; margin-bottom: 30px; }
        .logo { font-size: 28px; font-weight: bold; color: #0056b3; letter-spacing: 1px; }
        .subtitle { font-size: 14px; color: #666; font-style: italic; margin-top: 5px; }
        h1, h2, h3 { color: #0056b3; }
        h2 { border-left: 5px solid #0056b3; padding-left: 10px; margin-top: 30px; }
        .credenciales { background: #eef7ff; padding: 15px; border-radius: 6px; border-left: 5px solid #007bff; margin: 15px 0; }
        .consejo { background: #fff3cd; padding: 15px; border-radius: 6px; border-left: 5px solid #ffc107; margin: 15px 0; }
        ol, ul { padding-left: 20px; }
        li { margin-bottom: 8px; }
        .btn-print { display: block; width: 220px; margin: 30px auto 0; padding: 12px; background: #28a745; color: white; text-align: center; font-weight: bold; text-decoration: none; border-radius: 5px; cursor: pointer; border: none; font-size: 16px; }
        @media print { .btn-print { display: none; } body { padding: 0; } .container { box-shadow: none; padding: 0; } }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <div class="logo">🌐 SERVIWEB STOCK PRO</div>
        <div class="subtitle">Manual Oficial de Usuario para Gestión Comercial</div>
        <p><strong>Desarrollado por:</strong> Germán Crespo / ServiWeb</p>
    </div>

    <h2>1. Credenciales de Acceso (Login)</h2>
    <p>Al iniciar el sistema, se desplegará una pantalla de protección para restringir modificaciones no autorizadas en el stock.</p>
    <div class="credenciales">
        <strong>Perfil Administrador (Dueño de negocio):</strong><br>
        • Usuario: <code>admin</code> | • Contraseña: <code>admin123</code><br><br>
        <strong>Perfil Empleado (Cajero / Operador):</strong><br>
        • Usuario: <code>empleado1</code> | • Contraseña: <code>venta123</code>
    </div>

    <h2>2. Buscador Inteligente y Modo Lector</h2>
    <p>El campo principal <strong>"Buscador / Escáner de Venta Rápida"</strong> está optimizado para su uso continuo:</p>
    <ul>
        <li><strong>Lector de barras:</strong> Al pasar un artículo por el lector físico, el sistema extraerá y autocompletará sus campos de forma inmediata en la pantalla.</li>
        <li><strong>Búsqueda manual:</strong> Escriba el nombre del producto; la base de datos SQLite filtrará las existencias en milisegundos, ideal para catálogos con más de 1,000 referencias.</li>
    </ul>

    <h2>3. Registro de Entrada de Mercancía</h2>
    <p>Procedimiento estricto para alta o reabastecimiento de stock de proveedores:</p>
    <ol>
        <li>Posiciónese en el <strong>Buscador</strong> o en el campo de <strong>Código de Barras</strong> y use la pistola lectora.</li>
        <li>Si el producto es de primera inserción, capture su <strong>Nombre</strong>, <strong>Precio Costo</strong> e indique el <strong>Precio Venta</strong> sugerido.</li>
        <li>En el control <strong>Cantidad Actuar</strong>, introduzca el número de unidades entrantes.</li>
        <li>Haga clic en <strong>📥 Registrar Entrada</strong>.</li>
    </ol>

    <h2>4. Registro de Salidas (Ventas)</h2>
    <p>Flujo operativo ágil para atención al cliente:</p>
    <ol>
        <li>Escanee el código de barras del producto directamente desde la barra superior de búsqueda rápida.</li>
        <li>El sistema importará el registro y posicionará automáticamente el foco en la casilla de cantidad.</li>
        <li>Defina el volumen de piezas solicitadas por el comprador.</li>
        <li>Presione el botón <strong>📤 Registrar Venta</strong>. Las métricas de utilidades y stock se actualizarán instantáneamente.</li>
    </ol>

    <h2>5. Eliminación Definitiva de Registros</h2>
    <p>Para depurar productos obsoletos que no volverán a comercializarse:</p>
    <ol>
        <li>Seleccione el producto objetivo mediante un clic izquierdo en la tabla general.</li>
        <li>Presione el botón <strong>🗑️ Eliminar</strong>.</li>
        <li>Valide la ventana emergente de confirmación de baja para concluir la operación de forma segura.</li>
    </ol>

    <h2>6. Exportación de Reportes Financieros</h2>
    <p>Herramienta analítica de administración interna exclusiva para el dueño del negocio:</p>
    <ol>
        <li>Haga clic en <strong>📊 Generar Reporte</strong>.</li>
        <li>Se generará de forma local un libro automatizado con extensión <code>.csv</code> estructurado para compatibilidad directa con Microsoft Excel.</li>
        <li>El informe detallará de forma desglosada el valor monetario de la mercancía retenida, el ingreso bruto total recaudado en caja y el margen de ganancia real líquida del comercio.</li>
    </ol>

    <div class="consejo">
        <strong>💡 RECOMENDACIONES DE SEGURIDAD:</strong><br>
        Siempre utilice el botón <strong>🚪 Cerrar Sesión</strong> al abandonar el puesto de control. Adicionalmente, ejecute un respaldo preventivo manual del archivo <code>inventario_pro.db</code> de manera semanal en una unidad de almacenamiento externa (Pendrive).
    </div>

    <button class="btn-print" onclick="window.print()">🖨️ Guardar como PDF</button>
</div>

</body>
</html>
"""

# Guarda el manual directamente dentro de tu carpeta activa
with open("Manual_Usuario_ServiWeb.html", "w", encoding="utf-8") as f:
    f.write(contenido_html)

print("\n========================================================")
print("¡ÉXITO GERMÁN! El archivo del manual ha sido fabricado.")
print("========================================================")