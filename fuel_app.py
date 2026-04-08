import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="⛽ Fuel Prices Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #f8f9fa; }
[data-testid="stSidebar"]          { background-color: #ffffff; }
h1, h2, h3                         { color: #1a1d29 !important; }
.stMetric                          { background:#f0f4ff; border-radius:12px;
                                     padding:16px; border:2px solid #e0e8ff; }
.stMetricLabel                     { color: #5a6470 !important; }
label, .stSelectbox label,
.stMultiSelect label               { color: #1a1d29 !important; }
.stTabs [role="tablist"]           { border-bottom: 2px solid #e0e8ff; }
.stTab                             { color: #5a6470 !important; }
</style>
""", unsafe_allow_html=True)

# ── Carregar dados — auto-update a cada 6 horas via Kaggle ─────────────────
@st.cache_data(ttl=21600)  # 6 horas
def load_all():
    import kagglehub

    try:
        # dataset_download() é a API correta — load_dataset() não existe
        path = kagglehub.dataset_download(
            "zkskhurram/world-vs-asia-fuel-prices",
            force_download=True,
        )
    except Exception as e:
        st.warning(f"⚠️ Kaggle indisponível ({e}). A usar CSVs locais.")
        path = "."  # fallback para ficheiros na mesma pasta

    def read(name, **kwargs):
        return pd.read_csv(os.path.join(path, name), **kwargs)

    trend   = read("price_trend_monthly.csv",       parse_dates=["date"])
    asia    = read("asia_fuel_prices_detailed.csv", parse_dates=["price_date"])
    subsidy = read("asia_subsidy_tracker.csv")
    crude   = read("crude_oil_annual.csv")
    tax     = read("fuel_tax_comparison.csv")
    global_ = read("global_fuel_prices.csv",        parse_dates=["price_date"])
    return trend, asia, subsidy, crude, tax, global_

trend, asia, subsidy, crude, tax, global_df = load_all()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⛽ Fuel Prices")
    st.markdown("**World vs Asia · 2015–2026**")
    st.markdown("---")
    st.markdown("### Filtros")

    all_countries = sorted(trend["country"].unique())
    sel_countries = st.multiselect(
        "🌍 Países (série temporal)", all_countries,
        default=["Pakistan","India","China","Germany","USA","Saudi Arabia"]
        if all(c in all_countries for c in ["Pakistan","India","China","Germany","USA","Saudi Arabia"])
        else all_countries[:6]
    )

    all_regions = sorted(trend["region"].unique())
    sel_regions = st.multiselect("📍 Região", all_regions, default=all_regions)

    years = sorted(trend["year"].unique())
    sel_years = st.slider("📅 Anos", int(min(years)), int(max(years)),
                          (int(min(years)), int(max(years))))

    fuel_type = st.radio("🛢️ Combustível", ["Gasoline", "Diesel"], horizontal=True)
    fuel_col  = "gasoline_usd_per_liter" if fuel_type == "Gasoline" else "diesel_usd_per_liter"

    st.markdown("---")
    st.caption(f"📊 {len(trend):,} obs · {len(global_df)} países · USD/litro")

# ── Filtrar série temporal ──────────────────────────────────────────────────
tf = trend[
    trend["country"].isin(sel_countries) &
    trend["region"].isin(sel_regions) &
    trend["year"].between(sel_years[0], sel_years[1])
].copy()

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("# ⛽ Global Fuel Prices Dashboard")
st.markdown("Preços de combustível · Asia vs Mundo · Subsídios · Petróleo bruto · Impostos")
st.markdown("---")

# ── TABS ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Tendências", "🌍 Preços Globais", "💰 Subsídios & Impostos", "🛢️ Petróleo Bruto"
])

# ─────────────────────────────────────────────────────────
# TAB 1 — Tendências mensais
# ─────────────────────────────────────────────────────────
with tab1:
    latest_year = trend["year"].max()
    prev_year   = latest_year - 1
    avg_now   = trend[trend["year"] == latest_year]["gasoline_usd_per_liter"].mean()
    avg_prev  = trend[trend["year"] == prev_year]["gasoline_usd_per_liter"].mean()
    delta_pct = ((avg_now - avg_prev) / avg_prev * 100) if avg_prev else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Preço Médio Global", f"${avg_now:.3f}/L", f"{delta_pct:+.1f}% vs ano anterior")
    c2.metric("🔺 Mais caro (hoje)",
              f"${global_df['gasoline_usd_per_liter'].max():.3f}",
              global_df.loc[global_df['gasoline_usd_per_liter'].idxmax(), 'country'])
    c3.metric("🔻 Mais barato (hoje)",
              f"${global_df['gasoline_usd_per_liter'].min():.3f}",
              global_df.loc[global_df['gasoline_usd_per_liter'].idxmin(), 'country'])
    c4.metric("🌏 Países analisados", len(global_df))

    st.markdown("---")

    st.subheader(f"📅 Evolução Mensal — {fuel_type} (USD/L)")
    if tf.empty:
        st.warning("Seleciona pelo menos um país nos filtros da sidebar.")
    else:
        fig_line = px.line(tf, x="date", y=fuel_col, color="country",
                           template="plotly",
                           labels={fuel_col: "USD/litro", "date": "", "country": "País"})
        for dt, label in [("2020-04-01","COVID-19"), ("2022-02-01","Guerra Ucrânia"), ("2023-06-01","Cortes OPEP+")]:
            fig_line.add_vline(x=dt, line_dash="dot", line_color="#999", opacity=0.6)
        fig_line.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                               margin=dict(l=0,r=0,t=10,b=0), height=400,
                               legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_line, width='stretch')

    st.subheader("📊 Variação Anual (%) por País")
    yoy_df = tf.dropna(subset=["yoy_change_pct"]).groupby(["country","year"])["yoy_change_pct"].mean().reset_index()
    if not yoy_df.empty:
        fig_yoy = px.bar(yoy_df, x="year", y="yoy_change_pct", color="country",
                         barmode="group", template="plotly",
                         labels={"yoy_change_pct": "Variação YoY (%)", "year": "Ano"})
        fig_yoy.add_hline(y=0, line_dash="dash", line_color="#e74c3c", opacity=0.8)
        fig_yoy.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_yoy, width='stretch')

# ─────────────────────────────────────────────────────────
# TAB 2 — Preços Globais
# ─────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader("🗺️ Mapa Global — Preços da Gasolina")
        fig_map = px.choropleth(
            global_df, locations="iso3", color="gasoline_usd_per_liter",
            hover_name="country",
            hover_data={"diesel_usd_per_liter": True, "region": True},
            color_continuous_scale="RdYlGn_r", template="plotly",
            labels={"gasoline_usd_per_liter": "USD/L"},
        )
        fig_map.update_layout(
            paper_bgcolor="#ffffff",
            geo=dict(bgcolor="#f0f4ff", showframe=False,
                     showcoastlines=True, coastlinecolor="#ccc"),
            margin=dict(l=0,r=0,t=10,b=0), height=370,
        )
        st.plotly_chart(fig_map, width='stretch')

    with col_b:
        st.subheader("🔀 Asia vs Mundo")
        box_df = global_df.copy()
        box_df["Grupo"] = box_df["is_asian"].map({1: "🌏 Asia", 0: "🌍 Mundo"})
        fig_box = px.box(box_df, x="Grupo", y="gasoline_usd_per_liter",
                         color="Grupo", points="all", template="plotly",
                         color_discrete_map={"🌏 Asia":"#e74c3c","🌍 Mundo":"#3498db"},
                         labels={"gasoline_usd_per_liter":"USD/litro"})
        fig_box.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False, height=370)
        st.plotly_chart(fig_box, width='stretch')

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("🏆 15 Mais Caros")
        top15 = global_df.nlargest(15, "gasoline_usd_per_liter").copy()
        top15["cor"] = top15["is_asian"].map({1:"#e74c3c", 0:"#3498db"})
        fig_top = px.bar(top15, x="gasoline_usd_per_liter", y="country", orientation="h",
                         color="cor", color_discrete_map="identity", template="plotly",
                         labels={"gasoline_usd_per_liter":"USD/L","country":""})
        fig_top.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top, width='stretch')

    with col_d:
        st.subheader("💸 15 Mais Baratos")
        bot15 = global_df.nsmallest(15, "gasoline_usd_per_liter").copy()
        bot15["cor"] = bot15["is_asian"].map({1:"#e74c3c", 0:"#3498db"})
        fig_bot = px.bar(bot15, x="gasoline_usd_per_liter", y="country", orientation="h",
                         color="cor", color_discrete_map="identity", template="plotly",
                         labels={"gasoline_usd_per_liter":"USD/L","country":""})
        fig_bot.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bot, width='stretch')

    st.subheader("🌏 Acessibilidade na Ásia — % do Salário Diário gasto em Gasolina")
    asia_s = asia.sort_values("gasoline_pct_daily_wage", ascending=False)
    fig_af = px.bar(asia_s, x="gasoline_pct_daily_wage", y="country", orientation="h",
                    color="gasoline_pct_daily_wage", color_continuous_scale="Reds",
                    template="plotly",
                    hover_data=["avg_monthly_income_usd","gasoline_usd_per_liter","sub_region"],
                    labels={"gasoline_pct_daily_wage":"% salário diário","country":""})
    fig_af.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                         margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_af, width='stretch')

# ─────────────────────────────────────────────────────────
# TAB 3 — Subsídios & Impostos
# ─────────────────────────────────────────────────────────
with tab3:
    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader("💸 Custo Anual dos Subsídios (Ásia)")
        sub_s = subsidy.sort_values("annual_subsidy_cost_bn_usd", ascending=True)
        fig_sub = px.bar(sub_s, x="annual_subsidy_cost_bn_usd", y="country",
                         orientation="h", color="subsidy_type", template="plotly",
                         hover_data=["subsidy_pct_gdp","pricing_mechanism"],
                         labels={"annual_subsidy_cost_bn_usd":"USD Bilhões/ano","country":""})
        fig_sub.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0),
                              yaxis=dict(autorange="reversed"),
                              legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_sub, width='stretch')

    with col_f:
        st.subheader("📊 Subsídio como % do PIB")
        fig_gdp = px.bar(sub_s, x="subsidy_pct_gdp", y="country", orientation="h",
                         color="subsidy_pct_gdp", color_continuous_scale="Oranges",
                         template="plotly",
                         labels={"subsidy_pct_gdp":"% do PIB","country":""})
        fig_gdp.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_gdp, width='stretch')

    st.subheader("🏛️ Impostos sobre Combustível por País")
    tax_s = tax.sort_values("gasoline_tax_pct", ascending=False)
    fig_tax = px.bar(tax_s, x="country", y=["gasoline_tax_pct","diesel_tax_pct"],
                     barmode="group", template="plotly",
                     color_discrete_sequence=["#e74c3c","#3498db"],
                     labels={"value":"Taxa (%)","variable":"Tipo","country":""},
                     hover_data={"vat_pct":True,"excise_usd_per_liter":True})
    fig_tax.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                          margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(tickangle=45),
                          legend=dict(orientation="h", y=1.05), height=420)
    st.plotly_chart(fig_tax, width='stretch')

    st.subheader("📋 Detalhes dos Subsídios — Ásia")
    st.dataframe(
        subsidy[["country","subsidy_type","annual_subsidy_cost_bn_usd",
                 "subsidy_pct_gdp","pricing_mechanism","regulator","subsidy_description"]]
        .rename(columns={"annual_subsidy_cost_bn_usd":"Custo (Bn USD)",
                         "subsidy_pct_gdp":"% PIB","pricing_mechanism":"Mecanismo",
                         "subsidy_type":"Tipo","regulator":"Regulador",
                         "subsidy_description":"Descrição"}),
        width='stretch', height=300,
    )

# ─────────────────────────────────────────────────────────
# TAB 4 — Petróleo Bruto
# ─────────────────────────────────────────────────────────
with tab4:
    col_g, col_h = st.columns([2, 1])

    with col_g:
        st.subheader("🛢️ Brent & WTI — Preço Anual (USD/barril)")
        fig_crude = go.Figure()
        fig_crude.add_trace(go.Bar(x=crude["year"], y=crude["brent_avg_usd_bbl"],
                                   name="Brent", marker_color="#e74c3c"))
        fig_crude.add_trace(go.Bar(x=crude["year"], y=crude["wti_avg_usd_bbl"],
                                   name="WTI",   marker_color="#3498db"))
        fig_crude.update_layout(barmode="group", template="plotly",
                                paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                                margin=dict(l=0,r=0,t=20,b=0), height=380,
                                yaxis_title="USD/barril",
                                legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_crude, width='stretch')

    with col_h:
        st.subheader("📈 Variação YoY Brent (%)")
        yoy_c  = crude.dropna(subset=["brent_yoy_change_pct"])
        colors = ["#ff7b72" if v < 0 else "#3fb950" for v in yoy_c["brent_yoy_change_pct"]]
        fig_yc = go.Figure(go.Bar(
            x=yoy_c["year"], y=yoy_c["brent_yoy_change_pct"],
            marker_color=colors,
            text=yoy_c["brent_yoy_change_pct"].map("{:.1f}%".format),
            textposition="outside",
        ))
        fig_yc.add_hline(y=0, line_dash="dash", line_color="#8b949e")
        fig_yc.update_layout(template="plotly",
                             paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                             margin=dict(l=0,r=0,t=10,b=0), height=380,
                             yaxis_title="YoY (%)")
        st.plotly_chart(fig_yc, width='stretch')

    st.subheader("🔗 Correlação: Preço do Brent vs Gasolina nos Países")
    corr_df = trend.merge(crude[["year","brent_avg_usd_bbl"]], on="year", how="left")
    corr_df = corr_df[corr_df["country"].isin(sel_countries)]
    if not corr_df.empty:
        fig_corr = px.scatter(corr_df, x="brent_avg_usd_bbl", y="gasoline_usd_per_liter",
                              color="country", trendline="ols", template="plotly",
                              labels={"brent_avg_usd_bbl":"Brent (USD/bbl)",
                                      "gasoline_usd_per_liter":"Gasolina (USD/L)"})
        fig_corr.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                               margin=dict(l=0,r=0,t=10,b=0),
                               legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_corr, width='stretch')

    st.subheader("📋 Dados Anuais — Petróleo Bruto")
    st.dataframe(crude.rename(columns={
        "year":"Ano","brent_avg_usd_bbl":"Brent (USD/bbl)","wti_avg_usd_bbl":"WTI (USD/bbl)",
        "brent_yoy_change_pct":"Brent YoY %","wti_yoy_change_pct":"WTI YoY %","key_event":"Evento",
    })[["Ano","Brent (USD/bbl)","WTI (USD/bbl)","Brent YoY %","WTI YoY %","Evento"]],
    width='stretch')

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("⛽ Fuel Prices Dashboard · Kaggle: zkskhurram/world-vs-asia-fuel-prices · Streamlit + Plotly")
