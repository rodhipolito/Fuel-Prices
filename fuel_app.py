import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime

st.set_page_config(
    page_title="⛽ Fuel Prices Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Traduções ────────────────────────────────────────────────────────────────
LANG = {
    "PT": {
        "app_title": "⛽ Global Fuel Prices Dashboard",
        "app_subtitle": "Preços de combustível · Asia vs Mundo · Subsídios · Petróleo bruto · Impostos",
        "sidebar_title": "⛽ Fuel Prices",
        "sidebar_subtitle": "**Mundo vs Asia · 2015–2026**",
        "filters": "Filtros",
        "countries": "🌍 Países (série temporal)",
        "region": "📍 Região",
        "years": "📅 Anos",
        "fuel_type": "🛢️ Combustível",
        "tab1": "📅 Tendências",
        "tab2": "🌍 Preços Globais",
        "tab3": "💰 Subsídios & Impostos",
        "tab4": "🛢️ Petróleo Bruto",
        "metric_avg": "💰 Preço Médio Global",
        "metric_expensive": "🔺 Mais caro (hoje)",
        "metric_cheap": "🔻 Mais barato (hoje)",
        "metric_countries": "🌏 Países analisados",
        "vs_prev_year": "vs ano anterior",
        "monthly_trend": "📅 Evolução Mensal",
        "yoy_variation": "📊 Variação Anual (%) por País",
        "global_map": "🗺️ Mapa Global — Preços da Gasolina",
        "asia_vs_world": "🔀 Asia vs Mundo",
        "top15": "🏆 15 Mais Caros",
        "bot15": "💸 15 Mais Baratos",
        "accessibility": "🌏 Acessibilidade na Ásia — % do Salário Diário gasto em Gasolina",
        "subsidy_cost": "💸 Custo Anual dos Subsídios (Ásia)",
        "subsidy_gdp": "📊 Subsídio como % do PIB",
        "fuel_tax": "🏛️ Impostos sobre Combustível por País",
        "subsidy_details": "📋 Detalhes dos Subsídios — Ásia",
        "crude_title": "🛢️ Brent & WTI — Preço Anual (USD/barril)",
        "crude_yoy": "📈 Variação YoY Brent (%)",
        "crude_corr": "🔗 Correlação: Preço do Brent vs Gasolina nos Países",
        "crude_table": "📋 Dados Anuais — Petróleo Bruto",
        "data_from": "🕒 Dados de",
        "loaded_at": "🔄 Carregado às",
        "next_refresh": "🔄 Próxima atualização: ~",
        "select_country_warn": "Seleciona pelo menos um país nos filtros da sidebar.",
        "footer": "⛽ Fuel Prices Dashboard · Kaggle: zkskhurram/world-vs-asia-fuel-prices · Streamlit + Plotly",
        "usd_liter": "USD/litro",
        "year": "Ano",
        "country": "País",
        "region_lbl": "Região",
        "yoy_pct": "Variação YoY (%)",
        "daily_wage_pct": "% salário diário",
        "subsidy_bn": "USD Bilhões/ano",
        "pct_gdp": "% do PIB",
        "mechanism": "Mecanismo",
        "type": "Tipo",
        "regulator": "Regulador",
        "description": "Descrição",
        "asia_grp": "🌏 Asia",
        "world_grp": "🌍 Mundo",
        "group": "Grupo",
        "event": "Evento",
        "brent_bbl": "Brent (USD/bbl)",
        "wti_bbl": "WTI (USD/bbl)",
        "brent_yoy": "Brent YoY %",
        "wti_yoy": "WTI YoY %",
        "gasoline": "Gasolina",
        "diesel": "Diesel",
        "obs": "obs",
        "countries_lbl": "países",
        "covid_lbl": "COVID-19",
        "ukraine_lbl": "Guerra Ucrânia",
        "opec_lbl": "Cortes OPEP+",
    },
    "EN": {
        "app_title": "⛽ Global Fuel Prices Dashboard",
        "app_subtitle": "Fuel prices · Asia vs World · Subsidies · Crude oil · Taxes",
        "sidebar_title": "⛽ Fuel Prices",
        "sidebar_subtitle": "**World vs Asia · 2015–2026**",
        "filters": "Filters",
        "countries": "🌍 Countries (time series)",
        "region": "📍 Region",
        "years": "📅 Years",
        "fuel_type": "🛢️ Fuel type",
        "tab1": "📅 Trends",
        "tab2": "🌍 Global Prices",
        "tab3": "💰 Subsidies & Taxes",
        "tab4": "🛢️ Crude Oil",
        "metric_avg": "💰 Global Average Price",
        "metric_expensive": "🔺 Most expensive (today)",
        "metric_cheap": "🔻 Cheapest (today)",
        "metric_countries": "🌏 Countries analysed",
        "vs_prev_year": "vs previous year",
        "monthly_trend": "📅 Monthly Trend",
        "yoy_variation": "📊 Year-on-Year Change (%) by Country",
        "global_map": "🗺️ Global Map — Gasoline Prices",
        "asia_vs_world": "🔀 Asia vs World",
        "top15": "🏆 Top 15 Most Expensive",
        "bot15": "💸 Top 15 Cheapest",
        "accessibility": "🌏 Affordability in Asia — % of Daily Wage spent on Gasoline",
        "subsidy_cost": "💸 Annual Subsidy Cost (Asia)",
        "subsidy_gdp": "📊 Subsidy as % of GDP",
        "fuel_tax": "🏛️ Fuel Taxes by Country",
        "subsidy_details": "📋 Subsidy Details — Asia",
        "crude_title": "🛢️ Brent & WTI — Annual Price (USD/barrel)",
        "crude_yoy": "📈 Brent YoY Change (%)",
        "crude_corr": "🔗 Correlation: Brent Price vs Gasoline across Countries",
        "crude_table": "📋 Annual Data — Crude Oil",
        "data_from": "🕒 Data as of",
        "loaded_at": "🔄 Loaded at",
        "next_refresh": "🔄 Next refresh: ~",
        "select_country_warn": "Please select at least one country in the sidebar filters.",
        "footer": "⛽ Fuel Prices Dashboard · Kaggle: zkskhurram/world-vs-asia-fuel-prices · Streamlit + Plotly",
        "usd_liter": "USD/litre",
        "year": "Year",
        "country": "Country",
        "region_lbl": "Region",
        "yoy_pct": "YoY Change (%)",
        "daily_wage_pct": "% of daily wage",
        "subsidy_bn": "USD Billion/year",
        "pct_gdp": "% of GDP",
        "mechanism": "Mechanism",
        "type": "Type",
        "regulator": "Regulator",
        "description": "Description",
        "asia_grp": "🌏 Asia",
        "world_grp": "🌍 World",
        "group": "Group",
        "event": "Event",
        "brent_bbl": "Brent (USD/bbl)",
        "wti_bbl": "WTI (USD/bbl)",
        "brent_yoy": "Brent YoY %",
        "wti_yoy": "WTI YoY %",
        "gasoline": "Gasoline",
        "diesel": "Diesel",
        "obs": "obs",
        "countries_lbl": "countries",
        "covid_lbl": "COVID-19",
        "ukraine_lbl": "Ukraine War",
        "opec_lbl": "OPEC+ Cuts",
    },
}

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

# ── Seleção de idioma (topo da sidebar) ─────────────────────────────────────
with st.sidebar:
    lang_choice = st.radio("🌐 Language / Idioma", ["PT", "EN"], horizontal=True)

T = LANG[lang_choice]

# ── Carregar dados — auto-update a cada 6 horas via Kaggle ──────────────────
@st.cache_data(ttl=21600)
def load_all():
    import kagglehub
    try:
        path = kagglehub.dataset_download(
            "zkskhurram/world-vs-asia-fuel-prices",
            force_download=True,
        )
    except Exception as e:
        st.warning(f"⚠️ Kaggle unavailable ({e}). Using local CSVs.")
        path = "."

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

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## {T['sidebar_title']}")
    st.markdown(T["sidebar_subtitle"])
    st.markdown("---")
    st.markdown(f"### {T['filters']}")

    all_countries = sorted(trend["country"].unique())
    default_countries = ["Pakistan","India","China","Germany","USA","Saudi Arabia"]
    sel_countries = st.multiselect(
        T["countries"], all_countries,
        default=default_countries
        if all(c in all_countries for c in default_countries)
        else all_countries[:6]
    )

    all_regions = sorted(trend["region"].unique())
    sel_regions = st.multiselect(T["region"], all_regions, default=all_regions)

    years = sorted(trend["year"].unique())
    sel_years = st.slider(T["years"], int(min(years)), int(max(years)),
                          (int(min(years)), int(max(years))))

    fuel_type = st.radio(T["fuel_type"], [T["gasoline"], T["diesel"]], horizontal=True)
    fuel_col  = "gasoline_usd_per_liter" if fuel_type == T["gasoline"] else "diesel_usd_per_liter"

    st.markdown("---")
    st.caption(f"📊 {len(trend):,} {T['obs']} · {len(global_df)} {T['countries_lbl']} · USD/L")

    last_data_date = pd.to_datetime(global_df["price_date"]).max()
    st.caption(f"{T['data_from']}: {last_data_date.strftime('%d/%m/%Y')}")
    next_refresh = datetime.datetime.now() + datetime.timedelta(hours=6)
    st.caption(f"{T['next_refresh']}{next_refresh.strftime('%H:%M')}")

# ── Filtrar série temporal ───────────────────────────────────────────────────
tf = trend[
    trend["country"].isin(sel_countries) &
    trend["region"].isin(sel_regions) &
    trend["year"].between(sel_years[0], sel_years[1])
].copy()

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown(f"# {T['app_title']}")

last_loaded = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M" if lang_choice == "PT" else "%d/%m/%Y at %H:%M")
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(T["app_subtitle"])
with col_badge:
    st.info(f"{T['data_from']} {last_data_date.strftime('%d/%m/%Y')}\n\n{T['loaded_at']} {last_loaded}")

st.markdown("---")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"]])

# ─────────────────────────────────────────────────────────
# TAB 1 — Tendências / Trends
# ─────────────────────────────────────────────────────────
with tab1:
    latest_year = trend["year"].max()
    prev_year   = latest_year - 1
    avg_now   = trend[trend["year"] == latest_year]["gasoline_usd_per_liter"].mean()
    avg_prev  = trend[trend["year"] == prev_year]["gasoline_usd_per_liter"].mean()
    delta_pct = ((avg_now - avg_prev) / avg_prev * 100) if avg_prev else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T["metric_avg"], f"${avg_now:.3f}/L", f"{delta_pct:+.1f}% {T['vs_prev_year']}")
    c2.metric(T["metric_expensive"],
              f"${global_df['gasoline_usd_per_liter'].max():.3f}",
              global_df.loc[global_df['gasoline_usd_per_liter'].idxmax(), 'country'])
    c3.metric(T["metric_cheap"],
              f"${global_df['gasoline_usd_per_liter'].min():.3f}",
              global_df.loc[global_df['gasoline_usd_per_liter'].idxmin(), 'country'])
    c4.metric(T["metric_countries"], len(global_df))

    st.markdown("---")

    st.subheader(f"{T['monthly_trend']} — {fuel_type} (USD/L)")
    if tf.empty:
        st.warning(T["select_country_warn"])
    else:
        fig_line = px.line(tf, x="date", y=fuel_col, color="country",
                           template="plotly",
                           labels={fuel_col: T["usd_liter"], "date": "", "country": T["country"]})
        for dt, label in [
            ("2020-04-01", T["covid_lbl"]),
            ("2022-02-01", T["ukraine_lbl"]),
            ("2023-06-01", T["opec_lbl"]),
        ]:
            fig_line.add_vline(x=dt, line_dash="dot", line_color="#999", opacity=0.6)
            fig_line.add_annotation(x=dt, y=1, yref="paper", text=label,
                                    showarrow=False, xanchor="left",
                                    font=dict(size=10, color="#999"),
                                    bgcolor="rgba(255,255,255,0.7)")
        fig_line.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                               margin=dict(l=0,r=0,t=10,b=0), height=400,
                               legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_line, width='stretch')

    st.subheader(T["yoy_variation"])
    yoy_df = tf.dropna(subset=["yoy_change_pct"]).groupby(["country","year"])["yoy_change_pct"].mean().reset_index()
    if not yoy_df.empty:
        fig_yoy = px.bar(yoy_df, x="year", y="yoy_change_pct", color="country",
                         barmode="group", template="plotly",
                         labels={"yoy_change_pct": T["yoy_pct"], "year": T["year"]})
        fig_yoy.add_hline(y=0, line_dash="dash", line_color="#e74c3c", opacity=0.8)
        fig_yoy.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig_yoy, width='stretch')

# ─────────────────────────────────────────────────────────
# TAB 2 — Preços Globais / Global Prices
# ─────────────────────────────────────────────────────────
with tab2:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.subheader(T["global_map"])
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
        st.subheader(T["asia_vs_world"])
        box_df = global_df.copy()
        box_df[T["group"]] = box_df["is_asian"].map({1: T["asia_grp"], 0: T["world_grp"]})
        fig_box = px.box(box_df, x=T["group"], y="gasoline_usd_per_liter",
                         color=T["group"], points="all", template="plotly",
                         color_discrete_map={T["asia_grp"]: "#e74c3c", T["world_grp"]: "#3498db"},
                         labels={"gasoline_usd_per_liter": T["usd_liter"]})
        fig_box.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False, height=370)
        st.plotly_chart(fig_box, width='stretch')

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader(T["top15"])
        top15 = global_df.nlargest(15, "gasoline_usd_per_liter").copy()
        top15["cor"] = top15["is_asian"].map({1: "#e74c3c", 0: "#3498db"})
        fig_top = px.bar(top15, x="gasoline_usd_per_liter", y="country", orientation="h",
                         color="cor", color_discrete_map="identity", template="plotly",
                         labels={"gasoline_usd_per_liter": "USD/L", "country": ""})
        fig_top.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top, width='stretch')

    with col_d:
        st.subheader(T["bot15"])
        bot15 = global_df.nsmallest(15, "gasoline_usd_per_liter").copy()
        bot15["cor"] = bot15["is_asian"].map({1: "#e74c3c", 0: "#3498db"})
        fig_bot = px.bar(bot15, x="gasoline_usd_per_liter", y="country", orientation="h",
                         color="cor", color_discrete_map="identity", template="plotly",
                         labels={"gasoline_usd_per_liter": "USD/L", "country": ""})
        fig_bot.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), showlegend=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_bot, width='stretch')

    st.subheader(T["accessibility"])
    asia_s = asia.sort_values("gasoline_pct_daily_wage", ascending=False)
    fig_af = px.bar(asia_s, x="gasoline_pct_daily_wage", y="country", orientation="h",
                    color="gasoline_pct_daily_wage", color_continuous_scale="Reds",
                    template="plotly",
                    hover_data=["avg_monthly_income_usd", "gasoline_usd_per_liter", "sub_region"],
                    labels={"gasoline_pct_daily_wage": T["daily_wage_pct"], "country": ""})
    fig_af.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                         margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False,
                         yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_af, width='stretch')

# ─────────────────────────────────────────────────────────
# TAB 3 — Subsídios & Impostos / Subsidies & Taxes
# ─────────────────────────────────────────────────────────
with tab3:
    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader(T["subsidy_cost"])
        sub_s = subsidy.sort_values("annual_subsidy_cost_bn_usd", ascending=True)
        fig_sub = px.bar(sub_s, x="annual_subsidy_cost_bn_usd", y="country",
                         orientation="h", color="subsidy_type", template="plotly",
                         hover_data=["subsidy_pct_gdp", "pricing_mechanism"],
                         labels={"annual_subsidy_cost_bn_usd": T["subsidy_bn"], "country": ""})
        fig_sub.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0),
                              yaxis=dict(autorange="reversed"),
                              legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_sub, width='stretch')

    with col_f:
        st.subheader(T["subsidy_gdp"])
        fig_gdp = px.bar(sub_s, x="subsidy_pct_gdp", y="country", orientation="h",
                         color="subsidy_pct_gdp", color_continuous_scale="Oranges",
                         template="plotly",
                         labels={"subsidy_pct_gdp": T["pct_gdp"], "country": ""})
        fig_gdp.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                              margin=dict(l=0,r=0,t=10,b=0), coloraxis_showscale=False,
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_gdp, width='stretch')

    st.subheader(T["fuel_tax"])
    tax_s = tax.sort_values("gasoline_tax_pct", ascending=False)
    fig_tax = px.bar(tax_s, x="country", y=["gasoline_tax_pct", "diesel_tax_pct"],
                     barmode="group", template="plotly",
                     color_discrete_sequence=["#e74c3c", "#3498db"],
                     labels={"value": "(%)", "variable": T["type"], "country": ""},
                     hover_data={"vat_pct": True, "excise_usd_per_liter": True})
    fig_tax.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                          margin=dict(l=0,r=0,t=10,b=0), xaxis=dict(tickangle=45),
                          legend=dict(orientation="h", y=1.05), height=420)
    st.plotly_chart(fig_tax, width='stretch')

    st.subheader(T["subsidy_details"])
    st.dataframe(
        subsidy[["country", "subsidy_type", "annual_subsidy_cost_bn_usd",
                 "subsidy_pct_gdp", "pricing_mechanism", "regulator", "subsidy_description"]]
        .rename(columns={
            "annual_subsidy_cost_bn_usd": T["subsidy_bn"],
            "subsidy_pct_gdp": T["pct_gdp"],
            "pricing_mechanism": T["mechanism"],
            "subsidy_type": T["type"],
            "regulator": T["regulator"],
            "subsidy_description": T["description"],
            "country": T["country"],
        }),
        width='stretch', height=300,
    )

# ─────────────────────────────────────────────────────────
# TAB 4 — Petróleo Bruto / Crude Oil
# ─────────────────────────────────────────────────────────
with tab4:
    col_g, col_h = st.columns([2, 1])

    with col_g:
        st.subheader(T["crude_title"])
        fig_crude = go.Figure()
        fig_crude.add_trace(go.Bar(x=crude["year"], y=crude["brent_avg_usd_bbl"],
                                   name="Brent", marker_color="#e74c3c"))
        fig_crude.add_trace(go.Bar(x=crude["year"], y=crude["wti_avg_usd_bbl"],
                                   name="WTI",   marker_color="#3498db"))
        fig_crude.update_layout(barmode="group", template="plotly",
                                paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                                margin=dict(l=0,r=0,t=20,b=0), height=380,
                                yaxis_title="USD/barrel" if lang_choice == "EN" else "USD/barril",
                                legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_crude, width='stretch')

    with col_h:
        st.subheader(T["crude_yoy"])
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

    st.subheader(T["crude_corr"])
    corr_df = trend.merge(crude[["year", "brent_avg_usd_bbl"]], on="year", how="left")
    corr_df = corr_df[corr_df["country"].isin(sel_countries)]
    if not corr_df.empty:
        fig_corr = px.scatter(corr_df, x="brent_avg_usd_bbl", y="gasoline_usd_per_liter",
                              color="country", trendline="ols", template="plotly",
                              labels={
                                  "brent_avg_usd_bbl": T["brent_bbl"],
                                  "gasoline_usd_per_liter": f"{T['gasoline']} (USD/L)",
                                  "country": T["country"],
                              })
        fig_corr.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#fafafa",
                               margin=dict(l=0,r=0,t=10,b=0),
                               legend=dict(orientation="h", y=1.05))
        st.plotly_chart(fig_corr, width='stretch')

    st.subheader(T["crude_table"])
    st.dataframe(crude.rename(columns={
        "year": T["year"],
        "brent_avg_usd_bbl": T["brent_bbl"],
        "wti_avg_usd_bbl": T["wti_bbl"],
        "brent_yoy_change_pct": T["brent_yoy"],
        "wti_yoy_change_pct": T["wti_yoy"],
        "key_event": T["event"],
    })[[T["year"], T["brent_bbl"], T["wti_bbl"], T["brent_yoy"], T["wti_yoy"], T["event"]]],
    width='stretch')

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(T["footer"])
