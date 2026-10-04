"""
Bowling Visualizations Module — IPL Telemetry Pro Theme
Renders interactive Plotly charts and static Matplotlib figures for bowling analytics.
"""
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def plot_wickets_by_bowler(top_bowlers_df):
    """Horizontal bar chart showing leading wicket-takers with crimson broadcast glow."""
    if top_bowlers_df.empty:
        return go.Figure()

    df_sorted = top_bowlers_df.sort_values(by="wickets", ascending=True)
    fig = px.bar(
        df_sorted,
        x="wickets",
        y="player",
        orientation="h",
        text="wickets",
        color="wickets",
        color_continuous_scale=[[0, "#4C0519"], [0.5, "#BE123C"], [1, "#EF4444"]],
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        xaxis=dict(
            title=dict(text="Total Wickets Taken", font=dict(family="Space Mono", size=11, color="#64748B")),
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
        textfont=dict(family="Space Mono, monospace", size=12, color="#F87171"),
        marker=dict(line=dict(width=1, color="rgba(239, 68, 68, 0.4)"))
    )
    return fig

def plot_economy_vs_wickets(bowling_df):
    """Scatter plot: Economy Rate vs Wickets Taken with efficiency quadrants."""
    if bowling_df.empty:
        return go.Figure()

    fig = px.scatter(
        bowling_df,
        x="wickets",
        y="economy",
        size="overs" if "overs" in bowling_df.columns else None,
        hover_name="player",
        color="economy",
        color_continuous_scale=[[0, "#10B981"], [0.5, "#F59E0B"], [1, "#EF4444"]],
        labels={"wickets": "Total Wickets", "economy": "Economy Rate (RPO)"}
    )

    # Inverted interpretation benchmark lines
    fig.add_hline(y=8.60, line_dash="dash", line_color="rgba(255, 255, 255, 0.25)",
                  annotation_text="Tournament Par Econ (8.60 RPO)",
                  annotation_font=dict(family="Space Mono", size=10, color="#64748B"))
    fig.add_vline(x=10.0, line_dash="dash", line_color="rgba(255, 255, 255, 0.25)",
                  annotation_text="Strike Threshold (10 Wkts)",
                  annotation_font=dict(family="Space Mono", size=10, color="#64748B"))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        xaxis=dict(
            title=dict(text="Wickets Taken", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        yaxis=dict(
            title=dict(text="Economy Rate (RPO)", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    fig.update_traces(marker=dict(line=dict(width=1.5, color="#080D1A")))
    return fig

def plot_bowling_economy_bars_mpl(bowlers_df):
    """Matplotlib bar chart comparing bowler economies against par line (8.60)."""
    fig, ax = plt.subplots(figsize=(6, 4.2), facecolor='#0B1220')
    ax.set_facecolor('#0B1220')

    if not bowlers_df.empty:
        top_n = bowlers_df.head(8).sort_values("economy", ascending=True)
        colors = ['#10B981' if e < 8.0 else '#F59E0B' if e < 9.5 else '#EF4444' for e in top_n['economy']]
        bars = ax.barh(top_n['player'], top_n['economy'], color=colors, height=0.6, edgecolor='#080D1A')
        
        # Par line
        ax.axvline(8.60, color='#64748B', linestyle='--', linewidth=1.5, label='Tournament Par (8.60)')
        
        ax.set_xlabel('Economy Rate (RPO)', color='#94A3B8', fontsize=10, fontfamily='monospace')
        ax.tick_params(colors='#DAE2FD', labelsize=9)
        ax.grid(axis='x', color='rgba(255,255,255,0.06)', linestyle=':')
        ax.legend(facecolor='#131B2E', edgecolor='rgba(255,255,255,0.1)', labelcolor='#DAE2FD', fontsize=8)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.2f}',
                    ha='left', va='center', color='#FFFFFF', fontsize=9, fontweight='bold', fontfamily='monospace')
    else:
        ax.text(0.5, 0.5, 'No Bowling Records', horizontalalignment='center', color='#64748B')

    plt.tight_layout()
    return fig
