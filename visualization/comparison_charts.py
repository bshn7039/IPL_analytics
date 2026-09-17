"""
Comparison Visualizations Module
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
        line=dict(color="#3B82F6", width=2),
        fillcolor="rgba(59, 130, 246, 0.25)"
    ))

    fig.add_trace(go.Scatterpolar(
        r=vals_b,
        theta=cat_loop,
        fill="toself",
        name=team_b,
        line=dict(color="#F97316", width=2),
        fillcolor="rgba(249, 115, 22, 0.25)"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
            bgcolor="#11151F"
        ),
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor="#11151F",
        margin=dict(l=40, r=40, t=40, b=40),
        title=f"Head-to-Head Tactical Radar: {team_a} vs {team_b}"
    )
    return fig

def plot_comparison_grouped_bars(stats_a, stats_b, team_a, team_b):
    """Side-by-side grouped bar chart comparing raw totals and rates."""
    metrics = ["Avg Score", "Strike Rate", "Economy", "Win %"]
    vals_a = [stats_a.get("avg_score", 0), stats_a.get("batting_sr", 0), stats_a.get("economy", 0), stats_a.get("win_rate", 0)]
    vals_b = [stats_b.get("avg_score", 0), stats_b.get("batting_sr", 0), stats_b.get("economy", 0), stats_b.get("win_rate", 0)]

    fig = go.Figure(data=[
        go.Bar(name=team_a, x=metrics, y=vals_a, marker_color="#3B82F6"),
        go.Bar(name=team_b, x=metrics, y=vals_b, marker_color="#F97316")
    ])
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        title="Direct Metric Comparison",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_player_comparison_bars(bat_a, bat_b, name_a, name_b):
    """Visualizes comparative batting stats for two players."""
    metrics = ["Runs", "Average", "Strike Rate", "Sixes"]
    va = [bat_a.get("runs", 0), bat_a.get("average", 0), bat_a.get("strike_rate", 0), bat_a.get("sixes", 0)] if bat_a else [0, 0, 0, 0]
    vb = [bat_b.get("runs", 0), bat_b.get("average", 0), bat_b.get("strike_rate", 0), bat_b.get("sixes", 0)] if bat_b else [0, 0, 0, 0]

    fig = go.Figure(data=[
        go.Bar(name=name_a, x=metrics, y=va, marker_color="#10B981"),
        go.Bar(name=name_b, x=metrics, y=vb, marker_color="#6366F1")
    ])
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        plot_bgcolor="#11151F",
        paper_bgcolor="#11151F",
        title="Player Batting Profile Comparison",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
