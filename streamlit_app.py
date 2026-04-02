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
    st.text_input("Palavra-passe", type="password", on_change=password_entered, key="password")

    if "password_correct" in st.session_state:
        st.error("❌ Palavra-passe incorreta")

    return False


if not check_password():
    st.stop()

# --- GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🥚 Gestão Avícola")

# --- FORMULÁRIO ---
st.sidebar.header("Novo Registo")

with st.sidebar.form("formulario"):
    data_venda = st.date_input("Data", datetime.now())
    qtd = st.number_input("Dúzias", min_value=1, step=1)
    preco = st.number_input("Preço (€)", min_value=0.0, format="%.2f")
    alim = st.number_input("Alimentação (€)", min_value=0.0, format="%.2f")
    novas = st.number_input("Galinhas (€)", min_value=0.0, format="%.2f")

    submit = st.form_submit_button("Guardar")

# --- GUARDAR ---
if submit:
    faturacao = qtd * preco
    lucro = faturacao - (alim + novas)

    nova_linha = pd.DataFrame([{
        "Data": data_venda.strftime("%d/%m/%Y"),
        "Duzias": int(qtd),
        "Preco": float(preco),
        "Alim": float(alim),
        "Novas": float(novas),
        "Faturacao": float(faturacao),
        "Lucro": float(lucro)
    }])

    try:
        df = conn.read(ttl=0)

        if df is None or df.empty:
            df_final = nova_linha
        else:
            df_final = pd.concat([df, nova_linha], ignore_index=True)

        conn.update(data=df_final)  # ✅ CORRIGIDO

        st.sidebar.success("✅ Guardado!")
        st.rerun()

    except Exception as e:
        st.sidebar.error(f"Erro: {e}")

# --- LER DADOS ---
try:
    df = conn.read(ttl=0)

    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()

except Exception:
    df = pd.DataFrame()

if df.empty:
    df = pd.DataFrame(columns=[
        "Data", "Duzias", "Preco", "Alim", "Novas", "Faturacao", "Lucro"
    ])

# --- MOSTRAR ---
if not df.empty:
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

    # --- LUCRO MENSAL ---
    st.subheader("📈 Lucro Mensal")

    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
    df["Mes"] = df["Data"].dt.to_period("M").astype(str)

    lucro_mensal = df.groupby("Mes")["Lucro"].sum()

    st.line_chart(lucro_mensal)

    # --- APAGAR DADOS ---
    st.divider()
    if st.button("🗑️ Apagar TODOS os dados"):
        conn.update(data=pd.DataFrame(columns=df.columns))  # ✅ CORRIGIDO
        st.success("Dados apagados!")
        st.rerun()

else:
    st.info("Sem dados ainda.")
