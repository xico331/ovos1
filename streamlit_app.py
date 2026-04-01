# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:44:26 2026

@author: Francisco
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da página no telemóvel
st.set_page_config(page_title="Gestão de Ovos", page_icon="🥚")

# --- FUNÇÕES DE BASE DE DADOS ---
def criar_tabela():
    conn = sqlite3.connect('ovos_web.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vendas 
                 (data TEXT, duzias INTEGER, preco REAL, alim REAL, novas REAL, faturacao REAL, lucro REAL)''')
    conn.commit()
    conn.close()

def guardar_dados(d, q, p, a, n, f, l):
    conn = sqlite3.connect('ovos_web.db')
    c = conn.cursor()
    c.execute("INSERT INTO vendas VALUES (?,?,?,?,?,?,?)", (d, q, p, a, n, f, l))
    conn.commit()
    conn.close()

# --- INTERFACE ---
st.title("🥚 Gestão Avícola - Portugal")
criar_tabela()

# Menu lateral para entradas
st.sidebar.header("Novo Registo")
with st.sidebar.form("formulario_venda"):
    data_venda = st.date_input("Data", datetime.now())
    qtd = st.number_input("Dúzias Vendidas", min_value=1, step=1)
    preco = st.number_input("Preço por Dúzia (€)", min_value=0.0, format="%.2f")
    gasto_alim = st.number_input("Gasto Alimentação (€)", min_value=0.0, format="%.2f")
    gasto_novas = st.number_input("Gasto Galinhas Novas (€)", min_value=0.0, format="%.2f")
    
    submetido = st.form_submit_button("Guardar Registo")

if submetido:
    faturacao = qtd * preco
    lucro = faturacao - (gasto_alim + gasto_novas)
    guardar_dados(data_venda.strftime("%d/%m/%Y"), qtd, preco, gasto_alim, gasto_novas, faturacao, lucro)
    st.sidebar.success("Dados guardados!")

# --- EXIBIÇÃO DOS DADOS ---
conn = sqlite3.connect('ovos_web.db')
df = pd.read_sql_query("SELECT * FROM vendas", conn)
conn.close()

if not df.empty:
    st.subheader("📊 Histórico de Vendas")
    st.dataframe(df.style.format(subset=['preco', 'alim', 'novas', 'faturacao', 'lucro'], formatter="{:.2f}€"))

    # Linha de Totais em destaque
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Dúzias", int(df['duzias'].sum()))
    col2.metric("Faturação Total", f"{df['faturacao'].sum():.2f} €")
    col3.metric("Lucro Acumulado", f"{df['lucro'].sum():.2f} €", delta=f"{df['lucro'].sum():.2f} €")
else:
    st.info("Ainda não existem registos. Usa o menu lateral para começar!")