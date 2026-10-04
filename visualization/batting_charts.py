"""
Batting Visualizations Module — IPL Telemetry Pro Theme
Renders interactive Plotly charts and static figures for batting analytics.
"""
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_runs_by_player(top_batsmen_df):
    """Horizontal bar chart showing top run scorers with Stitch broadcast polish."""
    if top_batsmen_df.empty:
        return go.Figure()
    
    df_sorted = top_batsmen_df.sort_values(by="runs", ascending=True)
    fig = px.bar(
        df_sorted,
        x="runs",
        y="player",
        orientation="h",
        text="runs",
        color="runs",
        color_continuous_scale=[[0, "#083344"], [0.5, "#0891B2"], [1, "#06B6D4"]],
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        xaxis=dict(
            title=dict(text="Total Runs Scored", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        yaxis=dict(
            title="",
            tickfont=dict(family="Outfit, sans-serif", size=13, color="#FFFFFF"),
            showgrid=False
        ),
        coloraxis_showscale=False,
        margin=dict(l=20, r=30, t=20, b=20)
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(family="Space Mono, monospace", size=12, color="#4CD7F6"),
        marker=dict(line=dict(width=1, color="rgba(6, 182, 212, 0.4)"))
    )
    return fig

def plot_runs_vs_strike_rate(batting_df):
    """Scatter plot: Runs vs Strike Rate with efficiency quadrant benchmarks."""
    if batting_df.empty:
        return go.Figure()
    
    fig = px.scatter(
        batting_df,
        x="runs",
        y="strike_rate",
        size="innings" if "innings" in batting_df.columns else None,
        hover_name="player",
        color="strike_rate",
        color_continuous_scale=[[0, "#38BDF8"], [0.5, "#10B981"], [1, "#F59E0B"]],
        labels={"runs": "Total Runs Scored", "strike_rate": "Batting Strike Rate"}
    )

    # Crosshair benchmark lines
    fig.add_hline(y=135.0, line_dash="dash", line_color="rgba(255, 255, 255, 0.25)",
                  annotation_text="League Median SR (135.0)",
                  annotation_font=dict(family="Space Mono", size=10, color="#64748B"))
    fig.add_vline(x=200.0, line_dash="dash", line_color="rgba(255, 255, 255, 0.25)",
                  annotation_text="High Volume Benchmark (200 Runs)",
                  annotation_font=dict(family="Space Mono", size=10, color="#64748B"))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        xaxis=dict(
            title=dict(text="Total Runs Scored", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        yaxis=dict(
            title=dict(text="Strike Rate (%)", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    fig.update_traces(marker=dict(line=dict(width=1.5, color="#080D1A")))
    return fig

def plot_boundary_distribution_mpl(fours, sixes, total_runs):
    """Renders Matplotlib boundary distribution with dark luxury theme."""
    boundary_runs = (fours * 4) + (sixes * 6)
    non_boundary_runs = max(0, total_runs - boundary_runs)
    
    labels = ['Running (1s, 2s, 3s)', 'Fours (4s)', 'Sixes (6s)']
    sizes = [non_boundary_runs, fours * 4, sixes * 6]
    colors = ['#1E293B', '#06B6D4', '#F59E0B']

    fig, ax = plt.subplots(figsize=(5, 4.2), facecolor='#0B1220')
    ax.set_facecolor('#0B1220')

    if total_runs > 0:
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            textprops=dict(color='#DAE2FD', fontfamily='sans-serif', fontsize=9),
            wedgeprops=dict(width=0.45, edgecolor='#080D1A', linewidth=2)
        )
        for autotext in autotexts:
            autotext.set_color('#FFFFFF')
            autotext.set_weight('bold')
            autotext.set_fontsize(10)
    else:
        ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', color='#64748B')

    ax.axis('equal')
    plt.tight_layout()
    return fig
