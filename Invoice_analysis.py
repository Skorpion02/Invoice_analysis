# -*- coding: utf-8 -*-
"""
Created on Sat Dec 21 22:38:00 2024

@author: Roberto De Gouveia
"""

import pandas as pd
from unidecode import unidecode
import re
import unicodedata

# =============================================================================
# 1. Initial Data Exploration and Transformation
# 
# • Load the dataset: How do we load the CSV file containing
# invoices into a Pandas DataFrame?
# • Explore the data: How do we visualize the first few rows
# of the dataset to better understand the data?
# • Data types: What command is used to check the
# data types of each column in the DataFrame?
# • Conversion of the 'Monto' (Amount) column: How can we
# remove commas from the 'Monto' column (if any) and
# convert it to float type?
# • Date conversion: Why is it important to convert the
# 'Fecha de factura' (Invoice Date) column to datetime type? Explain how you would do it.
# =============================================================================

data = pd.read_csv("C:/Users/degou/Documents/IMMUNE/Bloque_3/Trabajo grupal/ventas-por-factura.csv")

data.columns = [unidecode(col) for col in data.columns]

data.columns
data.dtypes

lista_texto = data.select_dtypes(include=[object]).columns

for i in lista_texto:
    data[i] = data[i].apply(
        lambda texto: re.sub(r'[\u0300-\u036f]',"",unicodedata.normalize('NFD',texto)))
    
    
data.columns = data.columns.str.lower().str.strip()   
  
data.columns = data.columns.str.replace(" ","_")

data["fecha_de_factura"] = pd.to_datetime(data.fecha_de_factura)

data.monto = data.monto.str.replace(",",".")

data["monto"] = data.monto.astype(float)

# =============================================================================
# 2. Creation of New Synthetic Columns
# =============================================================================
# 2.1 Year, month, and day of the week: How do we create new
# columns for the year, month, and day of the week from
# 'Fecha de factura' (Invoice Date)?
# =============================================================================

data["mes"] = data.fecha_de_factura.dt.month
data["day"] = data.fecha_de_factura.dt.day
data["año"] = data.fecha_de_factura.dt.year


# =============================================================================
# 2.2 Purchase hour: How do we extract the purchase hour
# from the 'Fecha de factura' (Invoice Date) column?
# =============================================================================

data["hora_compra"] = data.fecha_de_factura.dt.hour

# =============================================================================
# 2.3 Time slot: Create a new column called 'Franja Horaria'
# (Time Slot) using conditionals that classify hours into
# Morning, Afternoon, Evening, and Dawn. Which Pandas function
# would you use for this classification?
# =============================================================================

data["Franja_horaria"] = pd.cut(data.hora_compra,bins=[0,6,12,18,23],
                        labels=["Madrugada","Mañana","Tarde","Noche"])

# =============================================================================
# 3. Analysis by Customer and Country

# 3.1 Grouping by customer: Group data by 'ID Cliente' (Customer ID) and calculate:
# • Total products purchased.
# • Total amount spent by each customer.
# • Number of invoices.
# • Which customer has spent the most?
# =============================================================================

df_country = data.groupby(['pais', 'id_cliente']).agg({'monto': 'sum', 'cantidad': 'sum'}).reset_index()


# Total por cliente
df_cliente = data.groupby('id_cliente').agg(
    total_productos=('cantidad','sum'),
    total_gasto=('monto','sum'),
    num_facturas=('ndeg_de_factura','count')
).reset_index()


# =============================================================================
# 3.2 Grouping by country: How do we group sales by 'País' (Country) to
# analyze the total amount sold and the number of invoices in each country?
# =============================================================================

df_pais = data.groupby('pais').agg(
    monto_total=('monto','sum'),
    num_facturas=('ndeg_de_factura','count')
).reset_index()

# =============================================================================
# 3.3 Who are the customers who have spent more than 5000 and, therefore,
# can be considered VIP clients?
# • Note: Create a new column named VIP in the DataFrame
# that contains True if the customer has spent more than 5000 and
# False if they have spent less. Make sure to show only the
# customers considered VIP in the final result.
# =============================================================================

data_vip = data 

data_vip_2 = data_vip.groupby('id_cliente').agg(
    total_gasto=('monto','sum')
).reset_index()


data_vip_3 = data_vip_2.loc[data_vip_2.total_gasto > 5000,:]

# =============================================================================
# 4. Temporal Analysis
# =============================================================================
# =============================================================================
# 4.1 Sales by semester: Divide sales into two semesters and create
# a new column called 'Semestre' (Semester). Which semester has more
# sales?
# =============================================================================

data["semestre"] = pd.cut(data.mes, bins=[0, 6, 12], labels=[1,2])

data.semestre.value_counts()

# =============================================================================
# 4.2 Sales by time slot and country: Group data by 'País' (Country) and
# 'Franja Horaria' (Time Slot) to analyze sales. Which country sells more in
# the morning? And at night?
# =============================================================================

agrupados = data.groupby(['pais', 'franja_horaria'])['monto'].sum().reset_index()

ventas_manana = agrupados[agrupados['franja_horaria'] == 'Mañana']
pais_venta_manana = ventas_manana[ventas_manana['monto'] == ventas_manana['monto'].max()]

ventas_noches = agrupados[agrupados['franja_horaria'] == 'Noche']
pais_venta_noche = ventas_noches[ventas_noches['monto'] == ventas_noches['monto'].max()]

# =============================================================================
# 5. Filtering Weekend Data:
# =============================================================================
# =============================================================================
# 5.A Analysis of the 20 most important customers:
# =============================================================================

# =============================================================================
# Which are the 20 customers who have purchased the most products and
# generated the most sales during the weekend?
# =============================================================================

top_clientes = data.loc[(data.dia_semana.between(5,6)),:]\
        .sort_values("cantidad",ascending=0).head(20)[["id_cliente","cantidad"]]

# =============================================================================
# How many invoices have these 20 customers generated during the weekend?
# =============================================================================
         
top_clientes_facturas = data.loc[(data.dia_semana.between(5,6)),:]\
        .sort_values("cantidad",ascending=0).head(20)\
        .groupby("id_cliente")["ndeg_de_factura"].count().reset_index()

# =============================================================================
# •5.B Grouping by semester:
#
# • How are total sales, the quantity of products
#   sold, and the number of invoices issued distributed in each semester of the year?
# =============================================================================

por_semestre = data.loc[:,["semestre","cantidad"]]\
    .groupby("semestre",as_index=False).sum()

# =============================================================================
# • What is the sales trend throughout the semesters?
# =============================================================================

tendencia_por_semestre = data.loc[:,["semestre","cantidad"]]\
    .groupby("semestre",as_index=False).mean()

# =============================================================================
# 6. Comprehensive Billing Analysis by Country, Customer, and Products
# Perform the following:
# =============================================================================
# =============================================================================
# 6.1 Group data by country and customer, and calculate the total
# quantity and amount invoiced by each customer in each country.
# =============================================================================

por_cliente_pais = data.groupby(["pais", "id_cliente"]).agg(
    cantidad_total=("cantidad", "sum"),
    monto_total=("monto", "sum")).reset_index()

# =============================================================================
# 6.2 Which are the five customers with the highest invoiced amount in each country?
# =============================================================================

top_5_clientes_por_pais = (data.groupby(['id_cliente', 'pais'])['monto'].sum().reset_index()
    .sort_values(['pais', 'monto'], ascending=[1,0]).groupby('pais').head(5))

# =============================================================================
# 6.3 Identify the country with the highest total invoiced amount across all customers,
# and calculate the average invoiced amount per customer in that country.
# ==============================================================================

top_pais_monto = (data.groupby('pais')['monto'].sum().reset_index().head(1))

top_Australia_monto = data.loc[data.pais.isin(["Australia"])]\
    .groupby(['id_cliente'], as_index=False)['monto'].mean()
    
'''  
Contrasto cuantos clientes hay en Australia
'''

clientes = data.loc[data.pais.isin(["Australia"])].nunique()

# =============================================================================
# 6.4 Order customers in each country by the total invoiced quantity
# and show the 3 customers with the highest quantities per country.

# Additionally, calculate the correlation
# between the quantity and the invoiced amount for each country
# and display these values.
# =============================================================================

cl_pais_cantidad = data.groupby(["pais","id_cliente"], as_index=False)['cantidad'].sum()\
    .sort_values(["pais","cantidad"], ascending=[1,0]).groupby('pais').head(3)

# =============================================================================
# 6.5 For each country, divide the total invoiced amount per
# customer into four groups using the pd.cut function
# to segment them into quartiles.
# How many customers belong to each group in each country?
# =============================================================================

clt_monto = data.groupby(["pais", "id_cliente"]).agg(
    monto_total=("monto", "sum")).reset_index()

clt_monto["monto_total_cuartiles"] = pd.qcut(clt_monto["monto_total"]\
                                ,q=4, labels=["Q1","Q2","Q3","Q4"])
    
clt_monto_pais = clt_monto.groupby(['pais','monto_total_cuartiles'], as_index=False)['id_cliente'].count()

# =============================================================================
# 6.6 Create a new column that indicates the total amount invoiced
# by each customer across all their purchases and replace
# any negative values in the 'Monto' (Amount) column with the
# average value of the amount for the entire database.
# =============================================================================

total_facturado= data.groupby("id_cliente")["monto"].sum().reset_index()

data.loc[data['monto'] < 0, 'monto'] = data['monto'].mean()

# =============================================================================
# 7. Customer Segmentation and Purchase Behavior Analysis:
# Now perform the following analysis:

# 7.1 Calculate the total amount invoiced by each customer in each
# country and create a new column 'Total Facturado' (Total Invoiced) that
# aggregates this information. Then, perform a
# transformation using the transform function to calculate
# the total invoiced per customer and add this new column
# to the original DataFrame.
# =============================================================================

data33 = data
data33 = data33.dropna()
data33.isnull().any()

data33['total_facturado'] = data33.groupby(['id_cliente', 'pais'])['monto'].transform('sum')

# =============================================================================
# 7.2 Use pd.cut to classify customers based on the total
# invoiced amount into 4 segments: low, medium-low, medium-
# high, and high. How many customers exist in each segment for each country?
# =============================================================================

data33["Segmento"] = pd.qcut(data33.monto, q=4, labels= ["bajo","medio-bajo","medio-alto","alto"])

clientes_por_segmento = data.groupby(['pais','Segmento'])['id_cliente'].nunique()

# =============================================================================
# 7.3 Create a contingency table using crosstab that
# shows the relationship between the customer segment (based on their
# total invoiced amount) and the country they are in.
# Which country has the most customers in the high segment?
# =============================================================================

contingencia = pd.crosstab(data33['Segmento'], data33['pais'])
suma_columnas = contingencia.sum(axis=0)


clientes_segmento_alto = data[data['Segmento'] == 'alto']
clientes_alto_por_pais = clientes_segmento_alto.groupby('pais')['id_cliente'].nlargest(5,"id_cliente").nunique()

# =============================================================================
# 7.4 Calculate the correlation between the quantity purchased
# ('Cantidad' - Quantity) and the invoiced amount ('Monto' - Amount) for each country.
# Are there differences in correlation between countries?
# =============================================================================

correlacion_por_pais = data.groupby('pais')[['cantidad', 'monto']].corr().iloc[1::2, 0]  

# =============================================================================
# 7.5 Which are the 5 customers with the highest invoicing in the
# dataset? Use nlargest to get these
# customers and show the corresponding invoice and country for
# each of them.
# =============================================================================

top_5_clientes = data.groupby('id_cliente').agg({'total_facturado': 'max'}).nlargest(5, 'total_facturado')

top_5_clientes_info = data[data['id_cliente'].isin(top_5_clientes.index)][['id_cliente', 'total_facturado', 'ndeg_de_factura', 'pais']]

# =============================================================================
# 7.6 Use the unstack function to transform the DataFrame and
# view the total amount invoiced per month for each customer.
# Make sure to add a new column for the month of
# each invoice.
# =============================================================================

data['Mes'] = data['fecha_de_factura'].dt.to_period('M')

data_mes_cliente = data.drop_duplicates(subset=['id_cliente', 'Mes'])

facturado_por_mes = data_mes_cliente.pivot_table(index='id_cliente', columns='Mes', values='total_facturado', aggfunc='sum')

# =============================================================================
# 8. Comprehensive Invoicing Analysis and Data Transformation:
# =============================================================================

# =============================================================================
# 8.1 Create a new column that indicates the total amount invoiced
# per customer across all invoices. Use the transform command
# so that this column is added to each corresponding row
# for each customer.
# =============================================================================

data['Total_Facturado'] = data.groupby('id_cliente')['monto'].transform('sum')

# =============================================================================
# 8.2 Order the DataFrame by country and invoicing amount in
# descending order. Show the first 5 records.
# =============================================================================

df8_ordenado = data.sort_values(["pais", "monto"], ascending = False).head(5)

# =============================================================================
# 8.3 For customers who have a total invoicing amount
# greater than the average total amount per country,
# replace negative values in the 'Monto' (Amount) column
# with the average value of the 'Monto' column.
# =============================================================================

data.loc[(data['Total_Facturado'] > data['Total_pais']) & (data['monto'] < 0), 'monto'] = data['monto'].mean()

# =============================================================================
# 8.4 Use the stack function to reorganize the DataFrame into
# a stacked form that allows you to see the relationships between
# the customer and the invoice amount. Then, use unstack
# to display the same information but with customers
# as columns.
# =============================================================================

data = data.set_index('id_cliente')

data = data[~data.index.duplicated(keep='first')]

stacked_data = data.stack()

unstacked_data = stacked_data.unstack(level=0)

# =============================================================================
# 8.5 Perform a comparison of total sales by country and
# by customer using groupby and then calculate the average
# sales per country. Next, perform a correlation analysis
# between the invoice amount and the quantity
# purchased by country.
# =============================================================================

ventas_totales = data.groupby(['pais', 'id_cliente'])['monto'].sum().reset_index()

media_ventas_pais = data.groupby('pais')['monto'].mean().reset_index()

correlacion_pais = data.groupby('pais')[['monto', 'cantidad']].corr().iloc[0::2,-1].reset_index()
correlacion_pais = correlacion_pais.drop(columns=['level_1'])

# =============================================================================
# 8.6 What is the invoicing percentage of each country
# relative to the total invoiced? Use aggregation methods
# and transform the result into a percentage.
# =============================================================================

total_facturado_por_pais = data.groupby('pais')['monto'].sum()

total_facturado_global = data['monto'].sum()

porcentaje_facturacion_por_pais = (total_facturado_por_pais / total_facturado_global) * 100

# =============================================================================
# 8.7 Identify the 3 invoices with the highest amounts and
# show the country they belong to. Is there any pattern in
# the countries with higher invoices?
# =============================================================================

top_3_facturas = data.nlargest(3, 'monto')

top_3_paises = top_3_facturas[['pais', 'monto']]