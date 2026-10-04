"""
Trend Visualizations Module — IPL Telemetry Pro Theme
Renders win/loss donuts, match run trajectories, and multi-season performance lines.
"""
import plotly.express as px
import plotly.graph_objects as go

def plot_win_loss_donut(wins, losses):
    """Renders sleek broadcast-grade donut chart of team win-loss record."""
    total = wins + losses
    if total == 0:
        return go.Figure()

    labels = ["Wins", "Losses"]
    values = [wins, losses]
    colors = ["#10B981", "#EF4444"]

    win_rate = round(wins / total * 100, 1)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.68,
        marker=dict(colors=colors, line=dict(color="#080D1A", width=3)),
        textinfo="percent",
        textfont=dict(family="Space Mono, monospace", size=12, color="#FFFFFF"),
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(family="Space Mono, monospace", size=11, color="#94A3B8")
        ),
        margin=dict(l=15, r=15, t=20, b=30),
        annotations=[dict(
            text=f"<b style='font-size:24px; font-family:Outfit; color:#FFFFFF;'>{win_rate}%</b><br><span style='font-size:11px; font-family:Space Mono; color:#64748B;'>WIN RATE</span>",
            x=0.5, y=0.5,
            showarrow=False
        )]
    )
    return fig

def plot_match_run_trend(match_df, team):
    """Line chart tracking team run scores across matches with victory annotations."""
    if match_df.empty:
        return go.Figure()

    fig = go.Figure()
    
    # League benchmark reference line (172.0)
    fig.add_hline(
        y=172.0,
        line_dash="dot",
        line_color="rgba(255, 255, 255, 0.25)",
        annotation_text="League Benchmark Par (172.0)",
        annotation_font=dict(family="Space Mono, monospace", size=10, color="#64748B"),
        annotation_position="top left"
    )

    # Season Average reference
    avg_score = match_df["team_score"].mean()
    fig.add_hline(
        y=avg_score,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text=f"Season Avg ({round(avg_score, 1)})",
        annotation_font=dict(family="Space Mono, monospace", size=10, color="#F59E0B"),
        annotation_position="bottom right"
    )

    # Team scoring trajectory
    fig.add_trace(go.Scatter(
        x=match_df["match_num"],
        y=match_df["team_score"],
        mode="lines+markers",
        name="Team Score",
        line=dict(color="#06B6D4", width=3, shape="spline"),
        marker=dict(
            size=11,
            color=["#10B981" if r == "Won" else "#EF4444" for r in match_df["result"]],
            line=dict(width=2, color="#080D1A")
        ),
        text=[f"M{m}: {score} vs {opp} ({res})" for m, score, opp, res in zip(match_df["match_num"], match_df["team_score"], match_df["opponent"], match_df["result"])],
        hoverinfo="text"
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#DAE2FD"),
        xaxis=dict(
            title=dict(text="Match Number", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)",
            tickmode="linear",
            dtick=1
        ),
        yaxis=dict(
            title=dict(text="Runs Scored", font=dict(family="Space Mono", size=11, color="#64748B")),
            showgrid=True,
            gridcolor="rgba(255,255,255,0.06)"
        ),
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    return fig
