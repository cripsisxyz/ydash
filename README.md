# Yuh Portfolio Analyzer 📊

Aplicación Streamlit para analizar tu portfolio de inversiones de Yuh y calcular beneficios netos.

## 🚀 Características

- ✅ Carga de archivos CSV de Yuh
- 💰 Cálculo de fees totales pagadas
- 📈 Análisis de rendimiento del portfolio
- 💵 Cálculo de beneficio/pérdida neto (después de fees)
- 📊 Visualizaciones interactivas (composición, rendimiento por activo)
- 📜 Historial detallado de transacciones por activo
- 🎯 Soporte para ETFs, acciones y crypto

## 📦 Instalación

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## 🎮 Uso

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📝 Cómo usar

1. **Descarga tu CSV**: Exporta tus transacciones desde Yuh
2. **Carga el archivo**: Usa el botón de carga en la aplicación
3. **Revisa el resumen**: Visualiza tus fees y transacciones
4. **Ingresa precios actuales**: Actualiza los precios de mercado de tus activos
5. **Calcula beneficios**: Haz clic en "Calcular Beneficios" para ver tu rendimiento

## 📋 Formato del CSV

El CSV debe contener las siguientes columnas:

- `ACTIVITY TYPE`: Tipo de actividad (INVEST_ORDER_EXECUTED, etc.)
- `ACTIVITY NAME`: Nombre de la actividad
- `DEBIT`: Monto debitado
- `DEBIT CURRENCY`: Moneda del débito
- `CREDIT`: Monto acreditado
- `CREDIT CURRENCY`: Moneda del crédito
- `CARD NUMBER`: Número de tarjeta (si aplica)
- `LOCALITY`: Localidad
- `RECIPIENT`: Destinatario
- `SENDER`: Remitente
- `FEES/COMMISSION`: Fees o comisiones
- `BUY/SELL`: Tipo de operación (compra/venta)
- `QUANTITY`: Cantidad de activos
- `ASSET`: Nombre del activo
- `PRICE PER UNIT`: Precio por unidad

## 🎯 Tipos de Actividad Soportados

- `INVEST_ORDER_EXECUTED`: Orden de inversión ejecutada
- `INVEST_RECURRING_ORDER_EXECUTED`: Orden recurrente ejecutada
- Y más...

## 📊 Métricas Calculadas

- **Total Invertido**: Suma de todas tus compras
- **Valor Actual**: Valor de mercado de tu portfolio
- **Beneficio/Pérdida Bruto**: Diferencia entre valor actual y costo
- **Beneficio/Pérdida NETO**: Después de deducir fees
- **ROI Neto**: Retorno de inversión porcentual
- **Composición del Portfolio**: Distribución por activo

## 🛠️ Tecnologías

- Python 3.8+
- Streamlit
- Pandas
- Plotly

## 📄 Licencia

MIT
