"""
Comparison Visualizations Module — IPL Telemetry Pro Theme
Renders multi-axis radar/spider charts and comparative grouped bar charts.
"""
import plotly.graph_objects as go

def plot_team_radar(stats_a, stats_b, team_a, team_b):
    """
    Renders radar / spider chart across 5 normalized cricket performance axes:
    Batting Avg, Strike Rate, Bowling Control, Win Rate, Boundary Power.
    """
    categories = ["Batting Avg", "Strike Rate", "Bowling Control", "Win Rate", "Boundary Rate"]

    # Normalize metrics to 0-100 scale
    def get_norm_profile(s):
        bat_avg_norm = min(100.0, max(20.0, (s.get("avg_score", 160) - 130) / (210 - 130) * 100))
        sr_norm = min(100.0, max(20.0, (s.get("batting_sr", 130) - 110) / (180 - 110) * 100))
        # Economy: 7.0 is best (100), 11.0 is worst (20)
        econ = s.get("economy", 8.5)
        bowl_ctrl_norm = min(100.0, max(20.0, (11.0 - econ) / (11.0 - 7.0) * 100))
        win_norm = s.get("win_rate", 50.0)
        # Sixes per match norm
        sixes_per_m = s.get("total_sixes", 0) / max(1, s.get("matches", 1))
        six_norm = min(100.0, max(20.0, (sixes_per_m - 4) / (14 - 4) * 100))

        return [round(bat_avg_norm, 1), round(sr_norm, 1), round(bowl_ctrl_norm, 1), round(win_norm, 1), round(six_norm, 1)]

    vals_a = get_norm_profile(stats_a)
    vals_b = get_norm_profile(stats_b)

    # Complete the radar loop
    vals_a.append(vals_a[0])
    vals_b.append(vals_b[0])
    cat_loop = categories + [categories[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=vals_a,
        theta=cat_loop,
        fill="toself",
        name=team_a,
        line=dict(color="#06B6D4", width=2.5),
        fillcolor="rgba(6, 182, 212, 0.22)"
    ))

    fig.add_trace(go.Scatterpolar(
        r=vals_b,
        theta=cat_loop,
        fill="toself",
        name=team_b,
        line=dict(color="#F59E0B", width=2.5),
        fillcolor="rgba(245, 158, 11, 0.22)"
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit, sans-serif", color="#DAE2FD"),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color="#64748B",
                gridcolor="rgba(255,255,255,0.08)",
                tickfont=dict(family="Space Mono", size=9)
            ),
            angularaxis=dict(
                color="#CBD5E1",
                gridcolor="rgba(255,255,255,0.08)",
                tickfont=dict(family="Space Mono", size=10, color="#FFFFFF")
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(family="Space Mono", size=11, color="#DAE2FD")
        ),
        margin=dict(l=30, r=30, t=20, b=30)
    )
    return fig

def plot_comparison_grouped_bars(stats_a, stats_b, team_a, team_b):
    """Grouped bar chart for direct team comparison."""
    metrics = ["Win %", "Avg Score", "Strike Rate", "Economy"]
    val_a = [stats_a.get("win_rate", 0), stats_a.get("avg_score", 0), stats_a.get("batting_sr", 0), stats_a.get("economy", 0) * 10]
    val_b = [stats_b.get("win_rate", 0), stats_b.get("avg_score", 0), stats_b.get("batting_sr", 0), stats_b.get("economy", 0) * 10]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics, y=val_a, name=team_a,
        marker=dict(color="#06B6D4", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v:.1f}" if m != "Economy" else f"{v/10:.2f}" for v, m in zip(val_a, metrics)],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))
    fig.add_trace(go.Bar(
        x=metrics, y=val_b, name=team_b,
        marker=dict(color="#F59E0B", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v:.1f}" if m != "Economy" else f"{v/10:.2f}" for v, m in zip(val_b, metrics)],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        barmode="group",
        xaxis=dict(
            tickfont=dict(family="Outfit, sans-serif", size=11, color="#FFFFFF"),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            title=dict(text="Normalized Value Index", font=dict(family="Space Mono", size=10, color="#64748B"))
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Space Mono", size=11, color="#DAE2FD")
        ),
        margin=dict(l=20, r=20, t=20, b=30)
    )
    return fig

def plot_player_comparison_bars(stats_a, stats_b, player_a, player_b):
    """Bar chart comparing two players on key batting stats."""
    stats_a = stats_a or {}
    stats_b = stats_b or {}
    metrics = ["Total Runs", "Strike Rate", "Average", "Boundary 4s", "Boundary 6s"]
    val_a = [stats_a.get("runs", 0), stats_a.get("strike_rate", 0), stats_a.get("average", 0), stats_a.get("fours", 0), stats_a.get("sixes", 0)]
    val_b = [stats_b.get("runs", 0), stats_b.get("strike_rate", 0), stats_b.get("average", 0), stats_b.get("fours", 0), stats_b.get("sixes", 0)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics, y=val_a, name=player_a,
        marker=dict(color="#818CF8", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in val_a],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))
    fig.add_trace(go.Bar(
        x=metrics, y=val_b, name=player_b,
        marker=dict(color="#06B6D4", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v:.1f}" if isinstance(v, float) else str(v) for v in val_b],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        barmode="group",
        xaxis=dict(
            tickfont=dict(family="Outfit, sans-serif", size=11, color="#FFFFFF"),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Space Mono", size=11, color="#DAE2FD")
        ),
        margin=dict(l=20, r=20, t=20, b=30)
    )
    return fig

def plot_player_bowling_comparison_bars(stats_a, stats_b, player_a, player_b):
    """Bar chart comparing two players on key bowling metrics."""
    stats_a = stats_a or {}
    stats_b = stats_b or {}
    metrics = ["Wickets", "Economy (x10)", "Bowling Avg", "Strike Rate", "Maidens"]
    val_a = [
        stats_a.get("wickets", 0) or 0,
        round((stats_a.get("economy", 0) or 0) * 10, 1),
        stats_a.get("bowling_avg", 0) or 0,
        stats_a.get("bowling_sr", 0) or 0,
        stats_a.get("maidens", 0) or 0
    ]
    val_b = [
        stats_b.get("wickets", 0) or 0,
        round((stats_b.get("economy", 0) or 0) * 10, 1),
        stats_b.get("bowling_avg", 0) or 0,
        stats_b.get("bowling_sr", 0) or 0,
        stats_b.get("maidens", 0) or 0
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics, y=val_a, name=player_a,
        marker=dict(color="#EF4444", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v/10:.2f}" if m == "Economy (x10)" else (f"{v:.1f}" if isinstance(v, float) else str(v)) for v, m in zip(val_a, metrics)],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))
    fig.add_trace(go.Bar(
        x=metrics, y=val_b, name=player_b,
        marker=dict(color="#F59E0B", line=dict(color="rgba(255,255,255,0.1)", width=1)),
        text=[f"{v/10:.2f}" if m == "Economy (x10)" else (f"{v:.1f}" if isinstance(v, float) else str(v)) for v, m in zip(val_b, metrics)],
        textposition="outside",
        textfont=dict(family="Space Mono", size=10)
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        barmode="group",
        xaxis=dict(
            tickfont=dict(family="Outfit, sans-serif", size=11, color="#FFFFFF"),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Space Mono", size=11, color="#DAE2FD")
        ),
        margin=dict(l=20, r=20, t=20, b=30)
    )
    return fig
