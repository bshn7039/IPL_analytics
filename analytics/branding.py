"""
Franchise Branding & Visual Identity Palette
Maps official IPL team brand colors, stadiums, aliases, and visual badges.
"""

FRANCHISE_METADATA = {
    "MI": {
        "full_name": "Mumbai Indians",
        "primary_color": "#004BA0",
        "secondary_color": "#D1AB3E",
        "accent": "#0078FF",
        "home_ground": "Wankhede Stadium, Mumbai",
        "titles": 5,
        "emoji": "🔵",
        "tagline": "Duniya Hila Denge Hum"
    },
    "CSK": {
        "full_name": "Chennai Super Kings",
        "primary_color": "#F9CD05",
        "secondary_color": "#0081E9",
        "accent": "#FACC15",
        "home_ground": "M. A. Chidambaram Stadium (Chepauk)",
        "titles": 5,
        "emoji": "🟡",
        "tagline": "Whistle Podu"
    },
    "RCB": {
        "full_name": "Royal Challengers Bengaluru",
        "primary_color": "#EC1C24",
        "secondary_color": "#000000",
        "accent": "#EF4444",
        "home_ground": "M. Chinnaswamy Stadium, Bengaluru",
        "titles": 0,
        "emoji": "🔴",
        "tagline": "Ee Sala Cup Namde"
    },
    "KKR": {
        "full_name": "Kolkata Knight Riders",
        "primary_color": "#3A225D",
        "secondary_color": "#B3995D",
        "accent": "#8B5CF6",
        "home_ground": "Eden Gardens, Kolkata",
        "titles": 3,
        "emoji": "🟣",
        "tagline": "Korbo Lorbo Jeetbo"
    },
    "RR": {
        "full_name": "Rajasthan Royals",
        "primary_color": "#EA1A85",
        "secondary_color": "#254AA5",
        "accent": "#EC4899",
        "home_ground": "Sawai Mansingh Stadium, Jaipur",
        "titles": 1,
        "emoji": "🌸",
        "tagline": "Halla Bol"
    },
    "SRH": {
        "full_name": "Sunrisers Hyderabad",
        "primary_color": "#F26522",
        "secondary_color": "#000000",
        "accent": "#F97316",
        "home_ground": "Rajiv Gandhi Stadium, Hyderabad",
        "titles": 1,
        "emoji": "🟠",
        "tagline": "Orange Army"
    },
    "DC": {
        "full_name": "Delhi Capitals",
        "primary_color": "#004C93",
        "secondary_color": "#D71920",
        "accent": "#38BDF8",
        "home_ground": "Arun Jaitley Stadium, Delhi",
        "titles": 0,
        "emoji": "🔷",
        "tagline": "Roar Macha"
    },
    "PBKS": {
        "full_name": "Punjab Kings",
        "primary_color": "#ED1B24",
        "secondary_color": "#D7A22A",
        "accent": "#F87171",
        "home_ground": "Maharaja Yadavindra Singh Stadium",
        "titles": 0,
        "emoji": "🦁",
        "tagline": "Sadda Punjab"
    },
    "GT": {
        "full_name": "Gujarat Titans",
        "primary_color": "#1C2841",
        "secondary_color": "#CBB279",
        "accent": "#38BDF8",
        "home_ground": "Narendra Modi Stadium, Ahmedabad",
        "titles": 1,
        "emoji": "⚡",
        "tagline": "Aava De"
    },
    "LSG": {
        "full_name": "Lucknow Super Giants",
        "primary_color": "#0057B8",
        "secondary_color": "#E31837",
        "accent": "#60A5FA",
        "home_ground": "BRSABV Ekana Stadium, Lucknow",
        "titles": 0,
        "emoji": "🦅",
        "tagline": "Adab Se Harayenge"
    }
}

def get_franchise_meta(team_code):
    """Retrieves branded styling, colors, and titles for a given franchise short code."""
    return FRANCHISE_METADATA.get(team_code, {
        "full_name": team_code,
        "primary_color": "#1E293B",
        "secondary_color": "#3B82F6",
        "accent": "#38BDF8",
        "home_ground": "Neutral Ground",
        "titles": 0,
        "emoji": "🏏",
        "tagline": "IPL Franchise"
    })
