# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 21:44:26 2026

@author: Francisco
"""

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Gestão de Ovos", page_icon="🥚")

# --- PASSWORD ---
def check_password():
    if "password" not in st.secrets:
        st.error("⚠️ Password não configurada!")
        st.stop()

    def password_entered():
        if st.session_state.get("password") == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("🔐 Acesso Restrito")
    st.text_input(
        "Palavra-passe",
        type="password",
        on_change=password_entered,
        key="password"
    )

    if "password_correct" in st.session_state:
        st.error("❌ Palavra-passe incorreta")

    return False


if not check_password():
    st.stop()

# --- GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🥚 Gestão Avícola")

# --- FORMULÁRIO (CORRIGIDO) ---
st.sidebar.header("Novo Registo")

with st.sidebar.form("formulario"):
    data_venda = st.date_input("Data", datetime.now())
    qtd = st.number_input("Dúzias", min_value=1, step=1)
    preco = st.number_input("Preço (€)", min_value=0.0, format="%.2f")
    alim = st.number_input("Alimentação (€)", min_value=0.0, format="%.2f")
    novas = st.number_input("Galinhas (€)", min_value=0.0, format="%.2f")

    submit = st.form_submit_button("Guardar")  # ✅ AGORA ESTÁ NO SÍTIO CERTO

# --- GUARDAR ---
if submit:
    ffaturacao = qtd * preco
    lucro = faturacao - (gasto_alim + gasto_novas)
    nova_linha = {
        "Data": data_venda.strftime("%d/%m/%Y"),
        "Duzias": int(qtd),
        "Preco": float(preco),
        "Alim": float(gasto_alim),
        "Novas": float(gasto_novas),
        "Faturacao": float(faturacao),
        "Lucro": float(lucro)
    }
    try:
        # CORREÇÃO: ttl=0 obriga a app a ler os dados frescos do Google Sheets
        df_atual = conn.read(spreadsheet=URL_DA_FOLHA, ttl=0)
        df = conn.read(spreadsheet=URL_DA_FOLHA, ttl=0)
        if not df.empty:
        # Junta a nova linha aos dados que já lá estão
        df_final = pd.concat([df_atual, pd.DataFrame([nova_linha])], ignore_index=True)
        
        # Atualiza a folha de cálculo
        conn.update(spreadsheet=URL_DA_FOLHA, data=df_final)
        
        # Limpa a memória da app para o histórico atualizar na hora
        st.cache_data.clear() 
        
        st.sidebar.success("✅ Dados guardados!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Erro: {e}")

# --- MOSTRAR DADOS ---
try:
    df = conn.read()

    if df is not None and not df.empty:
        st.subheader("📊 Histórico")

        st.dataframe(
            df.style.format({
                "Preco": "{:.2f}€",
                "Alim": "{:.2f}€",
                "Novas": "{:.2f}€",
                "Faturacao": "{:.2f}€",
                "Lucro": "{:.2f}€"
            })
        )

        st.divider()

        c1, c2, c3 = st.columns(3)

        c1.metric("Dúzias", int(df["Duzias"].sum()))
        c2.metric("Faturação", f"{df['Faturacao'].sum():.2f} €")
        c3.metric("Lucro", f"{df['Lucro'].sum():.2f} €")

    else:
        st.info("Sem dados ainda.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
