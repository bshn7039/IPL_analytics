"""
Bowling Visualizations Module
Renders interactive Plotly charts and static Matplotlib figures for bowling analytics.
"""
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_wickets_by_bowler(top_bowlers_df):
    """Horizontal bar chart showing leading wicket-takers."""
    if top_bowlers_df.empty:
        return go.Figure()

    df_sorted = top_bowlers_df.sort_values(by="wickets", ascending=True)
    fig = px.bar(
        df_sorted,
        x="wickets",
        y="player",
        orientation="h",
        text="wickets",
        color="economy",
        color_continuous_scale="Reds_r",  # Lower economy is darker
        title="Top Wicket Takers (Colored by Economy)"
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        xaxis_title="Wickets Taken",
        yaxis_title="Bowler",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig.update_traces(textposition="outside")
    return fig

def plot_economy_vs_wickets(bowling_df):
    """Scatter plot: Economy Rate vs Wickets Taken."""
    if bowling_df.empty:
        return go.Figure()

    fig = px.scatter(
        bowling_df,
        x="wickets",
        y="economy",
        size="overs" if "overs" in bowling_df.columns else None,
        hover_name="player",
        color="economy",
        color_continuous_scale="Tealrose_r",
        title="Economy Rate vs Wickets Matrix",
        labels={"wickets": "Total Wickets", "economy": "Economy Rate (RPO)"}
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_bowling_economy_bars_mpl(bowlers_df):
    """Matplotlib bar chart illustrating economy comparison across bowlers."""
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#11151F")
    ax.set_facecolor("#11151F")

    if bowlers_df.empty:
        return fig

    sub = bowlers_df.head(6)
    bars = ax.bar(sub["player"], sub["economy"], color="#EF4444", edgecolor="#F87171", width=0.55)

    ax.axhline(8.5, color="#F59E0B", linestyle="--", linewidth=1.2, label="IPL Avg (8.5 RPO)")
    ax.set_ylabel("Economy (RPO)", color="white", fontsize=10)
    ax.set_title("Bowler Economy Rates", color="white", fontsize=12, pad=12)
    ax.tick_params(colors="white", labelsize=9)
    plt.xticks(rotation=20, ha="right")
    ax.legend(facecolor="#1E293B", edgecolor="none", labelcolor="white")
    plt.tight_layout()
    return fig
