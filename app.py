import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="World Happiness Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f7f8fc; }
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e8eaf0;
}
.sidebar-title { font-size:22px; font-weight:700; color:#1a1d2e; margin-bottom:24px; }
.kpi-strip {
    display:flex; border:1px solid #e2e5f0; border-radius:12px;
    overflow:hidden; background:#ffffff; margin-bottom:28px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
}
.kpi-cell { flex:1; padding:18px 20px; border-right:1px solid #e2e5f0; }
.kpi-cell:last-child { border-right:none; }
.kpi-label {
    font-size:10px; font-weight:600; letter-spacing:0.1em;
    text-transform:uppercase; color:#9098b1; margin-bottom:8px;
}
.kpi-value { font-size:28px; font-weight:700; color:#1a1d2e; line-height:1; margin-bottom:6px; }
.kpi-up   { font-size:12px; color:#27ae60; font-weight:500; }
.kpi-down { font-size:12px; color:#e74c3c; font-weight:500; }
.chart-card {
    background:#ffffff; border:1px solid #e2e5f0; border-radius:12px;
    padding:20px 22px; margin-bottom:20px;
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.chart-title { font-size:13px; font-weight:600; color:#1a1d2e; margin-bottom:2px; }
.chart-sub   { font-size:12px; color:#9098b1; margin-bottom:14px; }
.insight {
    background:#fff8f0; border-left:3px solid #e05a2b;
    border-radius:0 8px 8px 0; padding:10px 14px;
    font-size:12.5px; color:#555; margin-top:10px; line-height:1.6;
}
.insight b { color:#e05a2b; }
.stMultiSelect [data-baseweb="tag"] {
    background-color:#e05a2b !important; border-radius:4px !important;
}
.stMultiSelect [data-baseweb="tag"] span { color:white !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color:#e05a2b !important;
    border-bottom-color:#e05a2b !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
CONTINENT_MAP = {
    "Finland":"Europe","Denmark":"Europe","Iceland":"Europe","Switzerland":"Europe",
    "Netherlands":"Europe","Luxembourg":"Europe","Sweden":"Europe","Norway":"Europe",
    "New Zealand":"Oceania","Austria":"Europe","Australia":"Oceania",
    "Canada":"North America","Ireland":"Europe","United States":"North America",
    "Germany":"Europe","Belgium":"Europe","Czech Republic":"Europe",
    "United Kingdom":"Europe","Lithuania":"Europe","France":"Europe",
    "Slovenia":"Europe","Costa Rica":"North America","Romania":"Europe",
    "Estonia":"Europe","Poland":"Europe","Spain":"Europe","Serbia":"Europe",
    "Malta":"Europe","Latvia":"Europe","Chile":"South America",
    "Slovakia":"Europe","Hungary":"Europe","Portugal":"Europe","Cyprus":"Europe",
    "Croatia":"Europe","Greece":"Europe","Italy":"Europe",
    "El Salvador":"North America","Nicaragua":"North America",
    "Brazil":"South America","Uruguay":"South America","Singapore":"Asia",
    "Kosovo":"Europe","Montenegro":"Europe","Japan":"Asia",
    "South Korea":"Asia","Taiwan Province of China":"Asia","Taiwan":"Asia",
    "Philippines":"Asia","Vietnam":"Asia","Mexico":"North America",
    "Argentina":"South America","Colombia":"South America","Peru":"South America",
    "Bolivia":"South America","Ecuador":"South America","Paraguay":"South America",
    "Venezuela":"South America","Panama":"North America","Honduras":"North America",
    "Guatemala":"North America","Dominican Republic":"North America",
    "Jamaica":"North America","Trinidad and Tobago":"North America",
    "Trinidad & Tobago":"North America","Haiti":"North America","Cuba":"North America",
    "Belize":"North America","China":"Asia","Indonesia":"Asia","India":"Asia",
    "Bangladesh":"Asia","Pakistan":"Asia","Thailand":"Asia","Myanmar":"Asia",
    "Malaysia":"Asia","Sri Lanka":"Asia","Cambodia":"Asia","Laos":"Asia",
    "Mongolia":"Asia","Nepal":"Asia","Bhutan":"Asia","Kazakhstan":"Asia",
    "Uzbekistan":"Asia","Tajikistan":"Asia","Kyrgyzstan":"Asia",
    "Turkmenistan":"Asia","Azerbaijan":"Asia","Armenia":"Asia","Georgia":"Asia",
    "Jordan":"Asia","Lebanon":"Asia","Turkey":"Asia","Iran":"Asia",
    "Iraq":"Asia","Afghanistan":"Asia","Yemen":"Asia","Saudi Arabia":"Asia",
    "United Arab Emirates":"Asia","Kuwait":"Asia","Bahrain":"Asia","Qatar":"Asia",
    "Oman":"Asia","Palestinian Territories":"Asia","Palestine":"Asia",
    "Russia":"Europe","Ukraine":"Europe","Belarus":"Europe","Moldova":"Europe",
    "Albania":"Europe","Bosnia and Herzegovina":"Europe","Bulgaria":"Europe",
    "North Macedonia":"Europe","Macedonia":"Europe","Israel":"Asia",
    "Hong Kong S.A.R., China":"Asia","Hong Kong":"Asia",
    "South Africa":"Africa","Nigeria":"Africa","Kenya":"Africa","Ethiopia":"Africa",
    "Ghana":"Africa","Tanzania":"Africa","Uganda":"Africa","Cameroon":"Africa",
    "Ivory Coast":"Africa","Senegal":"Africa","Mali":"Africa",
    "Burkina Faso":"Africa","Niger":"Africa","Chad":"Africa","Sudan":"Africa",
    "Egypt":"Africa","Morocco":"Africa","Algeria":"Africa","Tunisia":"Africa",
    "Libya":"Africa","Angola":"Africa","Mozambique":"Africa","Zambia":"Africa",
    "Zimbabwe":"Africa","Madagascar":"Africa","Malawi":"Africa","Rwanda":"Africa",
    "Burundi":"Africa","Somalia":"Africa","Sierra Leone":"Africa",
    "Liberia":"Africa","Guinea":"Africa","Benin":"Africa","Togo":"Africa",
    "Congo (Brazzaville)":"Africa","Congo (Kinshasa)":"Africa",
    "Central African Republic":"Africa","Botswana":"Africa","Namibia":"Africa",
    "Lesotho":"Africa","Swaziland":"Africa","Eswatini":"Africa",
    "Mauritius":"Africa","Gabon":"Africa","Equatorial Guinea":"Africa",
    "Papua New Guinea":"Oceania","Fiji":"Oceania",
}

CONTINENT_COLORS = {
    "Africa":        "#e05a2b",
    "Asia":          "#1f77b4",
    "Europe":        "#2ca02c",
    "North America": "#ff7f0e",
    "Oceania":       "#e377c2",
    "South America": "#9467bd",
    "Other":         "#8c8c8c",
}

# ── Shared base layout (NO xaxis/yaxis — those go in each chart directly) ──
def base_layout(height=400, extra_margin=None):
    m = dict(l=10, r=10, t=10, b=40)
    if extra_margin:
        m.update(extra_margin)
    return dict(
        plot_bgcolor  = "white",
        paper_bgcolor = "white",
        font          = dict(family="Inter", size=12, color="#444"),
        margin        = m,
        height        = height,
    )

XGRID = dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False,
             linecolor="#e0e0e0", linewidth=1)
YGRID = dict(showgrid=True, gridcolor="#f0f0f0", zeroline=False,
             linecolor="#e0e0e0", linewidth=1)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    files = {
        2015: "2015_cleaned.csv",
        2016: "2016_cleaned.csv",
        2017: "2017_cleaned.csv",
        2018: "2018_cleaned.csv",
        2019: "2019_cleaned.csv",
    }
    RENAME = {
        "Country":"Country",
        "Happiness Score":"Score","Happiness Rank":"Rank",
        "Economy (GDP per Capita)":"GDP","Family":"Social_Support",
        "Health (Life Expectancy)":"Life_Expectancy",
        "Freedom":"Freedom","Trust (Government Corruption)":"Corruption",
        "Generosity":"Generosity",
        "Happiness.Score":"Score","Happiness.Rank":"Rank",
        "Economy..GDP.per.Capita.":"GDP","Health..Life.Expectancy.":"Life_Expectancy",
        "Trust..Government.Corruption.":"Corruption",
        "Country or region":"Country","Score":"Score","Overall rank":"Rank",
        "GDP per capita":"GDP","Social support":"Social_Support",
        "Healthy life expectancy":"Life_Expectancy",
        "Freedom to make life choices":"Freedom",
        "Perceptions of corruption":"Corruption",
    }
    KEEP = ["Country","Rank","Score","GDP","Social_Support",
            "Life_Expectancy","Freedom","Generosity","Corruption"]
    frames = []
    for year, fname in files.items():
        if os.path.exists(fname):
            df = pd.read_csv(fname).rename(columns=RENAME)
            df["Year"] = year
            cols = [c for c in KEEP if c in df.columns] + ["Year"]
            frames.append(df[cols])
    if not frames:
        st.error("❌ CSV files not found. Place 2015_cleaned.csv … 2019_cleaned.csv beside app.py")
        st.stop()
    df = pd.concat(frames, ignore_index=True)
    df["Continent"] = df["Country"].map(CONTINENT_MAP).fillna("Other")
    for col in ["Score","GDP","Social_Support","Life_Expectancy",
                "Freedom","Generosity","Corruption"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


df_all  = load_data()
YEARS   = sorted(df_all["Year"].unique())
CONTS   = sorted(df_all["Continent"].unique())
BASE_YR = YEARS[0]

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-title'>Filters</div>", unsafe_allow_html=True)

    select_all = st.checkbox("Select All Years", value=True)
    sel_years  = YEARS if select_all else st.multiselect(
        "Years", YEARS, default=YEARS)

    st.markdown("**Select Continents**")
    sel_conts = st.multiselect(
        "", CONTS, default=CONTS, label_visibility="collapsed")

    st.markdown("---")
    top_n = st.slider("Top N Countries (Bar Chart)", 5, 20, 10)

    st.markdown("---")
    st.markdown("**Country Comparison (Line Chart)**")
    all_c    = sorted(df_all["Country"].unique())
    defaults = [c for c in ["Finland","Denmark","Norway","India",
                             "Nigeria","United States","Brazil","China"]
                if c in all_c]
    sel_c = st.multiselect("Select countries:", all_c, default=defaults)

    st.markdown("---")
    st.markdown("**Scatter Plot X-axis**")
    fac_opts = [c for c in ["GDP","Social_Support","Life_Expectancy",
                             "Freedom","Generosity","Corruption"]
                if c in df_all.columns]
    sel_fac = st.selectbox("Factor:", fac_opts, index=0)

# ─────────────────────────────────────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────────────────────────────────────
if not sel_years: sel_years = YEARS
if not sel_conts: sel_conts = CONTS

df = df_all[
    df_all["Year"].isin(sel_years) &
    df_all["Continent"].isin(sel_conts)
].copy()

latest   = max(sel_years)
df_snap  = (df[df["Year"] == latest]
            .sort_values("Score", ascending=False)
            .reset_index(drop=True))
df_base  = df_all[df_all["Year"] == BASE_YR]
yr_label = (f"{min(sel_years)} to {max(sel_years)}"
            if len(sel_years) > 1 else str(latest))

# ─────────────────────────────────────────────────────────────────────────────
# KPI STRIP
# ─────────────────────────────────────────────────────────────────────────────
def delta_html(curr, base, fmt=".2f", invert=False):
    if pd.isna(curr) or pd.isna(base):
        return ""
    d   = curr - base
    up  = (d > 0) if not invert else (d < 0)
    cls = "kpi-up" if up else "kpi-down"
    arr = "▲" if d > 0 else "▼"
    return f"<span class='{cls}'>{arr} {abs(d):{fmt}} from {BASE_YR}</span>"

def safe_mean(df_in, col):
    return float(df_in[col].mean()) if col in df_in.columns else float("nan")

avg_score = safe_mean(df_snap, "Score")
avg_gdp   = safe_mean(df_snap, "GDP")
avg_free  = safe_mean(df_snap, "Freedom")
avg_soc   = safe_mean(df_snap, "Social_Support")
avg_corr  = safe_mean(df_snap, "Corruption")

b_score = safe_mean(df_base, "Score")
b_gdp   = safe_mean(df_base, "GDP")
b_free  = safe_mean(df_base, "Freedom")
b_soc   = safe_mean(df_base, "Social_Support")
b_corr  = safe_mean(df_base, "Corruption")

st.markdown(f"""
<div class="kpi-strip">
  <div class="kpi-cell">
    <div class="kpi-label">Happiness Score</div>
    <div class="kpi-value">{avg_score:.2f}</div>
    {delta_html(avg_score, b_score)}
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">GDP / Capita</div>
    <div class="kpi-value">{avg_gdp:.3f}</div>
    {delta_html(avg_gdp, b_gdp, fmt=".3f")}
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">Freedom</div>
    <div class="kpi-value">{avg_free:.3f}</div>
    {delta_html(avg_free, b_free, fmt=".3f")}
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">Social Support</div>
    <div class="kpi-value">{avg_soc:.3f}</div>
    {delta_html(avg_soc, b_soc, fmt=".3f")}
  </div>
  <div class="kpi-cell">
    <div class="kpi-label">Trust / Corruption</div>
    <div class="kpi-value">{avg_corr:.3f}</div>
    {delta_html(avg_corr, b_corr, fmt=".3f", invert=True)}
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB
# ─────────────────────────────────────────────────────────────────────────────
(tab,) = st.tabs(["📊 Exploratory Analysis (EDA)"])

with tab:

    # =========================================================================
    # CHART 1 — GEO PLOT  (full width)
    # =========================================================================
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='chart-title'>Global Happiness Map ({yr_label})</div>"
        f"<div class='chart-sub'>Choropleth — average happiness score per country</div>",
        unsafe_allow_html=True)

    map_df  = df.groupby("Country")["Score"].mean().reset_index()
    fig_map = px.choropleth(
        map_df,
        locations              = "Country",
        locationmode           = "country names",
        color                  = "Score",
        hover_name             = "Country",
        color_continuous_scale = "Viridis",
        range_color            = [df_all["Score"].min(), df_all["Score"].max()],
        labels                 = {"Score": "Happiness Score"},
    )
    fig_map.update_layout(
        geo=dict(
            showframe       = False,
            showcoastlines  = True,
            projection_type = "natural earth",
            bgcolor         = "white",
            landcolor       = "#e8ecf0",
            showocean       = True,
            oceancolor      = "white",
            coastlinecolor  = "#b0b8c4",
            showlakes       = True,
            lakecolor       = "white",
        ),
        paper_bgcolor      = "white",
        height             = 480,
        coloraxis_colorbar = dict(title="Score", thickness=14, len=0.55),
        margin             = dict(l=0, r=0, t=0, b=0),
        font               = dict(family="Inter", size=12, color="#444"),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown(
        "<div class='insight'><b>💡 Insight:</b> Northern Europe shows the highest scores. "
        "Sub-Saharan Africa and parts of South Asia remain the lowest. "
        "Geographic clusters reflect shared cultural, economic, and governance patterns.</div>",
        unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # CHARTS 2 & 3 — TIME SERIES  +  BAR CHART  (2 columns)
    # =========================================================================
    c1, c2 = st.columns(2)

    # ── CHART 2 · Time Series ─────────────────────────────────────────────
    with c1:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='chart-title'>Happiness Trend by Continent ({yr_label})</div>"
            f"<div class='chart-sub'>Average score per continent across selected years</div>",
            unsafe_allow_html=True)

        trend  = df.groupby(["Year","Continent"])["Score"].mean().reset_index()
        fig_ts = px.line(
            trend, x="Year", y="Score",
            color="Continent", color_discrete_map=CONTINENT_COLORS,
            markers=True,
            labels={"Score":"Avg Happiness Score","Year":"Year"},
        )
        fig_ts.update_traces(line_width=2.2, marker_size=7)
        fig_ts.update_layout(
            **base_layout(400),
            xaxis  = dict(title="Year", tickmode="linear", dtick=1,
                          **XGRID),
            yaxis  = dict(title="Avg Happiness Score", **YGRID),
            legend = dict(orientation="h", y=-0.22, x=0,
                          bgcolor="white", borderwidth=0),
        )
        st.plotly_chart(fig_ts, use_container_width=True)
        st.markdown(
            "<div class='insight'><b>💡 Insight:</b> Europe leads at ~6.8–7.0 throughout. "
            "Africa shows the steepest upward slope. "
            "North America dips slightly after 2017.</div>",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── CHART 3 · Bar Chart ───────────────────────────────────────────────
    with c2:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='chart-title'>Top {top_n} Countries by Happiness Score ({yr_label})</div>"
            f"<div class='chart-sub'>Ranked lowest → highest · color = continent</div>",
            unsafe_allow_html=True)

        top_df  = df_snap.nlargest(top_n, "Score").sort_values("Score")
        fig_bar = px.bar(
            top_df, x="Score", y="Country", orientation="h",
            color="Continent", color_discrete_map=CONTINENT_COLORS,
            text="Score",
            labels={"Score":"Happiness Score","Country":""},
        )
        fig_bar.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            marker_line_width=0,
        )
        fig_bar.update_layout(
            **base_layout(400),
            xaxis  = dict(title="Happiness Score",
                          range=[top_df["Score"].min()-0.3,
                                 top_df["Score"].max()+0.5],
                          **XGRID),
            yaxis  = dict(showgrid=False, zeroline=False,
                          linecolor="#e0e0e0", linewidth=1),
            legend = dict(orientation="h", y=-0.22, x=0, borderwidth=0),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown(
            "<div class='insight'><b>💡 Insight:</b> Nordic nations dominate — "
            "high social trust, strong freedom, and universal healthcare, "
            "not just high GDP.</div>",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # CHARTS 4 & 5 — LINE CHART  +  HISTOGRAM  (2 columns)
    # =========================================================================
    c3, c4 = st.columns(2)

    # ── CHART 4 · Line Chart ──────────────────────────────────────────────
    with c3:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown(
            "<div class='chart-title'>Country-Level Happiness Score (2015–2019)</div>"
            "<div class='chart-sub'>Track individual countries — select in sidebar</div>",
            unsafe_allow_html=True)

        if sel_c:
            cdf      = df_all[df_all["Country"].isin(sel_c)].sort_values("Year")
            fig_line = px.line(
                cdf, x="Year", y="Score", color="Country",
                markers=True,
                labels={"Score":"Happiness Score","Year":"Year"},
            )
            fig_line.update_traces(line_width=2.2, marker_size=8)
            fig_line.update_layout(
                **base_layout(400),
                xaxis  = dict(title="Year", tickmode="linear", dtick=1,
                              **XGRID),
                yaxis  = dict(title="Happiness Score", **YGRID),
                legend = dict(orientation="h", y=-0.22, x=0, borderwidth=0),
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown(
                "<div class='insight'><b>💡 Insight:</b> Finland overtook Denmark and Norway "
                "in 2018 and has held #1 since. Developing nations show more volatility "
                "due to political and economic instability.</div>",
                unsafe_allow_html=True)
        else:
            st.info("👈 Select countries in the sidebar to display this chart.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── CHART 5 · Histogram ───────────────────────────────────────────────
    with c4:
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='chart-title'>Distribution of Happiness Scores ({yr_label})</div>"
            f"<div class='chart-sub'>Orange dashed = mean · Yellow dashed = median · Blue band = ±1σ</div>",
            unsafe_allow_html=True)

        scores   = df_snap["Score"].dropna()
        fig_hist = go.Figure()

        # faint background — all years
        for yr in YEARS:
            fig_hist.add_trace(go.Histogram(
                x=df_all[df_all["Year"] == yr]["Score"].dropna(),
                nbinsx=20, opacity=0.10,
                marker_color="#1f77b4", showlegend=False,
            ))
        # foreground — latest selected year
        fig_hist.add_trace(go.Histogram(
            x=scores, nbinsx=20,
            marker_color="#1f77b4", opacity=0.82,
            marker_line=dict(color="white", width=0.6),
            name=str(latest),
        ))

        mean_s = float(scores.mean())
        med_s  = float(scores.median())
        std_s  = float(scores.std())

        fig_hist.add_vline(
            x=mean_s, line_dash="dash", line_color="#e05a2b", line_width=2,
            annotation_text=f"Mean: {mean_s:.2f}",
            annotation_font=dict(color="#e05a2b", size=11),
            annotation_position="top right",
        )
        fig_hist.add_vline(
            x=med_s, line_dash="dash", line_color="#f4a500", line_width=2,
            annotation_text=f"Median: {med_s:.2f}",
            annotation_font=dict(color="#b8860b", size=11),
            annotation_position="top left",
        )
        fig_hist.add_vrect(
            x0=mean_s - std_s, x1=mean_s + std_s,
            fillcolor="#1f77b4", opacity=0.07,
            layer="below", line_width=0,
            annotation_text="±1σ",
            annotation_font=dict(color="#1f77b4", size=10),
            annotation_position="bottom right",
        )
        fig_hist.update_layout(
            **base_layout(400),
            barmode    = "overlay",
            showlegend = False,
            xaxis      = dict(title="Happiness Score", **XGRID),
            yaxis      = dict(title="Number of Countries", **YGRID),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Mean",    f"{mean_s:.3f}")
        s2.metric("Median",  f"{med_s:.3f}")
        s3.metric("Std Dev", f"{std_s:.3f}")
        s4.metric("Range",   f"{float(scores.min()):.2f}–{float(scores.max()):.2f}")

        st.markdown(
            "<div class='insight'><b>💡 Insight:</b> Distribution is roughly normal. "
            "The mean–median gap reveals a few very low-scoring countries pulling the "
            "average down. 68% of countries fall within the ±1σ band.</div>",
            unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================================
    # CHART 6 — SCATTER PLOT  (full width)
    # =========================================================================
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='chart-title'>"
        f"{sel_fac.replace('_',' ')} vs Happiness Score with Trendline ({yr_label})"
        f"</div>"
        f"<div class='chart-sub'>"
        f"Each dot = one country · Color = continent · "
        f"Dashed lines = per-continent LOWESS trendline"
        f"</div>",
        unsafe_allow_html=True)

    scat_df  = df.dropna(subset=[sel_fac, "Score"])
    use_logx = (sel_fac == "GDP")

    fig_scat = px.scatter(
        scat_df,
        x                  = sel_fac,
        y                  = "Score",
        color              = "Continent",
        color_discrete_map = CONTINENT_COLORS,
        hover_data         = ["Country","Year"],
        trendline_scope    = "trace",
        log_x              = use_logx,
        labels             = {
            sel_fac: sel_fac.replace("_"," ") + (" (Log)" if use_logx else ""),
            "Score": "Happiness Score",
        },
    )
    fig_scat.update_traces(
        selector=dict(mode="markers"),
        marker=dict(size=7, opacity=0.72,
                    line=dict(width=0.4, color="white")),
    )
    fig_scat.update_traces(
        selector=dict(mode="lines"),
        line=dict(dash="dot", width=1.8),
    )
    fig_scat.update_layout(
        **base_layout(480, extra_margin=dict(r=150)),
        xaxis  = dict(title=sel_fac.replace("_"," ") + (" (Log)" if use_logx else ""),
                      **XGRID),
        yaxis  = dict(title="Happiness Score", **YGRID),
        legend = dict(title="Continent", orientation="v",
                      x=1.01, y=1, bgcolor="white", borderwidth=1),
    )

    corr_val = scat_df[[sel_fac, "Score"]].corr().iloc[0, 1]
    st.plotly_chart(fig_scat, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Pearson r", f"{corr_val:.3f}")
    m2.metric("R²",        f"{corr_val**2:.3f}")
    m3.metric("Countries", str(scat_df["Country"].nunique()))

    strength  = ("very strong" if abs(corr_val) > 0.7 else
                 "strong"      if abs(corr_val) > 0.5 else
                 "moderate"    if abs(corr_val) > 0.3 else "weak")
    direction = "positive" if corr_val > 0 else "negative"
    st.markdown(
        f"<div class='insight'><b>💡 Insight:</b> "
        f"<b>{sel_fac.replace('_',' ')}</b> has a <b>{strength} {direction}</b> "
        f"relationship with happiness (r = {corr_val:.3f}). "
        f"Europe (green) clusters top-right; Africa (orange) bottom-left.</div>",
        unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#c0c4d0;font-size:12px;'>"
    "World Happiness Report · Streamlit + Plotly · "
    "Data: <a href='https://www.kaggle.com/datasets/unsdsn/world-happiness' "
    "style='color:#c0c4d0;'>Kaggle / UNSDSN</a>"
    "</p>",
    unsafe_allow_html=True,
)
