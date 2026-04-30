"""
Run from project root: python scripts/seed_mock_data.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, MONGO_DB

SIGNALS = [
    {
        "topic": "Electricity Bills",
        "summary": "Maharashtra residents are furious after MSEDCL increased electricity tariffs by 18% without prior notice. Social media is flooded with screenshots of bills double the amount from last month, with many users in Pune and Mumbai reporting bills of ₹4,000–₹8,000 for single-room flats.",
        "sentiment": "neg",
        "score": -74,
        "region": "Mumbai",
        "signal_type": "spike",
        "post_count": 342,
        "duration_hours": 8,
        "spike_rate": 284.5,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.91,
            "bot_risk": 0.09,
            "account_diversity": 0.87,
            "language_mix": 0.52,
            "spread_pattern": 0.74,
        },
        "breakdown": [
            {"aspect": "Tariff hike without notice", "score": -88},
            {"aspect": "Billing errors", "score": -71},
            {"aspect": "No grievance redressal", "score": -65},
            {"aspect": "Summer demand surge", "score": -40},
            {"aspect": "Smart meter issues", "score": -35},
        ],
        "entities": [
            {"name": "MSEDCL", "type": "organization", "score": -82},
            {"name": "Devendra Fadnavis", "type": "person", "score": -45},
            {"name": "Mumbai", "type": "location", "score": -30},
        ],
        "trend": [10, 12, 8, 15, 18, 20, 25, 30, 28, 35, 42, 55, 68, 80, 90, 95, 100, 98, 92, 85, 78, 70, 65, 60],
        "posts": [
            {
                "source": "r/mumbai",
                "text": "Bijli ka bill dekha toh dil dukh gaya yaar. ₹6,200 aaya hai is mahine. Ek BHK flat mein sirf 2 log rehte hain. Kya ho raha hai MSEDCL waalon ko?",
                "sentiment": "neg", "score": -85, "upvotes": 1243, "comments": 287, "time_ago": "3h ago",
            },
            {
                "source": "r/india",
                "text": "Maharashtra electricity bill hike is absolutely criminal. No notification, no public hearing, just a 18% increase quietly slipped in. This is how they loot the middle class.",
                "sentiment": "neg", "score": -79, "upvotes": 3421, "comments": 512, "time_ago": "5h ago",
            },
            {
                "source": "r/pune",
                "text": "Got my bill today. Same usage as last month but paying ₹1,800 extra. When I called MSEDCL helpline it just rings and disconnects. Pathetic service.",
                "sentiment": "neg", "score": -72, "upvotes": 892, "comments": 143, "time_ago": "6h ago",
            },
            {
                "source": "r/unitedstatesofindia",
                "text": "The electricity tariff hike protest in Pune gathered 2000 people but not a single mainstream news channel covered it. We are invisible to the media.",
                "sentiment": "neg", "score": -68, "upvotes": 2100, "comments": 334, "time_ago": "7h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=8),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Cricket / IPL",
        "summary": "IPL 2025 is dominating Indian Reddit with overwhelmingly positive energy. CSK's dramatic last-over win against MI has sent fans into a frenzy, with 'Dhoni Magic' trending nationally. Even non-cricket users are engaging with memes and match highlights.",
        "sentiment": "pos",
        "score": 81,
        "region": "National",
        "signal_type": "sustained",
        "post_count": 876,
        "duration_hours": 36,
        "spike_rate": 45.2,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.96,
            "bot_risk": 0.04,
            "account_diversity": 0.93,
            "language_mix": 0.61,
            "spread_pattern": 0.88,
        },
        "breakdown": [
            {"aspect": "Dhoni finishing again", "score": 95},
            {"aspect": "CSK vs MI rivalry", "score": 88},
            {"aspect": "RCB not winning still", "score": -20},
            {"aspect": "Ticket prices too high", "score": -35},
            {"aspect": "Broadcast quality excellent", "score": 72},
        ],
        "entities": [
            {"name": "MS Dhoni", "type": "person", "score": 97},
            {"name": "CSK", "type": "organization", "score": 89},
            {"name": "Mumbai Indians", "type": "organization", "score": 45},
            {"name": "Virat Kohli", "type": "person", "score": 78},
        ],
        "trend": [60, 55, 50, 45, 48, 52, 58, 65, 70, 72, 68, 64, 75, 82, 88, 92, 95, 100, 98, 94, 90, 85, 80, 78],
        "posts": [
            {
                "source": "r/cricket",
                "text": "DHONI FINISHES IT OFF IN STYLE AGAIN. 14 off 3 balls at age 43 and this man just does it. Unreal. GOAT confirmed forever.",
                "sentiment": "pos", "score": 98, "upvotes": 15420, "comments": 2341, "time_ago": "12h ago",
            },
            {
                "source": "r/IPL",
                "text": "Can we talk about how insane the CSK vs MI match was? Every over was a thriller. This is why IPL is the best cricket tournament in the world.",
                "sentiment": "pos", "score": 88, "upvotes": 8932, "comments": 1102, "time_ago": "14h ago",
            },
            {
                "source": "r/india",
                "text": "Entire office stopped working to watch the last 3 overs. Boss bhi dekh raha tha secretly. Dhoni ne woh shot maara toh literally screamed. Neighbours must think I'm crazy.",
                "sentiment": "pos", "score": 91, "upvotes": 6721, "comments": 872, "time_ago": "13h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=36),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Petrol Prices",
        "summary": "Petrol prices breaching ₹110/litre in metro cities is triggering widespread frustration. Users are calculating monthly fuel expenses and comparing to salary percentages. The conversation has an undertone of economic anxiety beyond just fuel costs.",
        "sentiment": "neg",
        "score": -61,
        "region": "National",
        "signal_type": "trending",
        "post_count": 198,
        "duration_hours": 18,
        "spike_rate": 78.3,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.85,
            "bot_risk": 0.15,
            "account_diversity": 0.76,
            "language_mix": 0.44,
            "spread_pattern": 0.69,
        },
        "breakdown": [
            {"aspect": "Fuel price crossing ₹110", "score": -78},
            {"aspect": "CNG vehicles demand", "score": -55},
            {"aspect": "Government inaction", "score": -70},
            {"aspect": "Commute cost burden", "score": -65},
        ],
        "entities": [
            {"name": "IOCL", "type": "organization", "score": -55},
            {"name": "Hardeep Puri", "type": "person", "score": -48},
        ],
        "trend": [20, 22, 25, 28, 30, 32, 35, 38, 42, 45, 48, 52, 55, 58, 60, 63, 65, 68, 70, 72, 74, 76, 78, 80],
        "posts": [
            {
                "source": "r/india",
                "text": "Petrol at ₹112 in Hyderabad today. I earn ₹35,000/month and spend ₹6,000 on fuel alone. That's 17% of my salary just to go to work. This is not sustainable.",
                "sentiment": "neg", "score": -75, "upvotes": 4521, "comments": 634, "time_ago": "4h ago",
            },
            {
                "source": "r/hyderabad",
                "text": "Switched to cycle for short distances. Petrol prices have made me healthier involuntarily. Thanks Modi ji for the fitness initiative.",
                "sentiment": "neg", "score": -45, "upvotes": 2134, "comments": 312, "time_ago": "6h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=18),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Metro",
        "summary": "Delhi Metro's proposed fare hike for Phase 4 corridors is causing anxiety among daily commuters. Users are sharing calculations showing how a ₹20 fare increase translates to ₹800+ monthly for average workers, threatening the metro's promise of affordable urban mobility.",
        "sentiment": "neg",
        "score": -55,
        "region": "Delhi",
        "signal_type": "trending",
        "post_count": 156,
        "duration_hours": 24,
        "spike_rate": 62.1,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.88,
            "bot_risk": 0.12,
            "account_diversity": 0.81,
            "language_mix": 0.38,
            "spread_pattern": 0.72,
        },
        "breakdown": [
            {"aspect": "Fare hike proposal", "score": -72},
            {"aspect": "Phase 4 delays", "score": -60},
            {"aspect": "Overcrowding in peak hours", "score": -50},
            {"aspect": "New stations opening", "score": 45},
        ],
        "entities": [
            {"name": "DMRC", "type": "organization", "score": -48},
            {"name": "Delhi Metro Phase 4", "type": "project", "score": -35},
            {"name": "Arvind Kejriwal", "type": "person", "score": -20},
        ],
        "trend": [30, 32, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 62, 65, 68, 70, 72, 74, 76, 78, 80, 82, 84, 85],
        "posts": [
            {
                "source": "r/delhi",
                "text": "DMRC is planning to increase fares again? This is the third time in 5 years. Delhi Metro was supposed to be public transport, not a premium service only office workers can afford.",
                "sentiment": "neg", "score": -68, "upvotes": 3210, "comments": 445, "time_ago": "8h ago",
            },
            {
                "source": "r/india",
                "text": "Good news: Janakpuri West to RK Ashram corridor finally opening next month. Bad news: fares going up by ₹20 on new stretches. Give and take I suppose.",
                "sentiment": "neu", "score": -10, "upvotes": 1543, "comments": 198, "time_ago": "10h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=24),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Unemployment",
        "summary": "A viral LinkedIn post about a 26-year-old with an MBA unable to find work for 14 months has reignited the youth unemployment debate. Engineering graduates in the comments are sharing similar stories, with the thread accumulating 800+ comments and getting cross-posted across multiple subreddits.",
        "sentiment": "neg",
        "score": -68,
        "region": "National",
        "signal_type": "spike",
        "post_count": 423,
        "duration_hours": 12,
        "spike_rate": 198.7,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.93,
            "bot_risk": 0.07,
            "account_diversity": 0.89,
            "language_mix": 0.35,
            "spread_pattern": 0.82,
        },
        "breakdown": [
            {"aspect": "MBA/engineering jobs scarce", "score": -80},
            {"aspect": "Skill mismatch", "score": -65},
            {"aspect": "Startup layoffs", "score": -72},
            {"aspect": "Government job delays", "score": -75},
            {"aspect": "Mental health impact", "score": -85},
        ],
        "entities": [
            {"name": "IIT/IIM graduates", "type": "group", "score": -60},
            {"name": "IT sector", "type": "industry", "score": -55},
        ],
        "trend": [15, 18, 22, 28, 35, 45, 58, 72, 85, 92, 95, 100, 98, 94, 90, 86, 82, 78, 74, 70, 65, 60, 55, 50],
        "posts": [
            {
                "source": "r/india",
                "text": "I have a B.Tech from NIT and 2 years of work ex. Been applying for 8 months. 400+ applications. 12 interviews. 0 offers. I don't know what I'm doing wrong anymore.",
                "sentiment": "neg", "score": -90, "upvotes": 12400, "comments": 1832, "time_ago": "6h ago",
            },
            {
                "source": "r/indiaspeaks",
                "text": "Youth unemployment in India is at 16.5% officially. Unofficially everyone knows it's much higher. We're creating graduates faster than jobs. This is a ticking time bomb.",
                "sentiment": "neg", "score": -72, "upvotes": 5621, "comments": 782, "time_ago": "8h ago",
            },
            {
                "source": "r/unitedstatesofindia",
                "text": "Ek baar sochna chahiye hum sab ko — hum apne bacchon ko engineer banate hain because it's safe, but the market doesn't need 15 lakh engineers every year.",
                "sentiment": "neg", "score": -65, "upvotes": 3421, "comments": 567, "time_ago": "10h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Budget Session",
        "summary": "Parliament's monsoon budget session is generating mixed reactions. The middle class is cautiously optimistic about tax relief under the new regime, while farmers and MSME owners feel left out. The opposition walkout is generating political commentary across subreddits.",
        "sentiment": "neu",
        "score": 12,
        "region": "National",
        "signal_type": "sustained",
        "post_count": 287,
        "duration_hours": 48,
        "spike_rate": 32.4,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.79,
            "bot_risk": 0.21,
            "account_diversity": 0.71,
            "language_mix": 0.42,
            "spread_pattern": 0.65,
        },
        "breakdown": [
            {"aspect": "Income tax changes", "score": 55},
            {"aspect": "Agriculture allocation", "score": -40},
            {"aspect": "MSME support", "score": -25},
            {"aspect": "Infrastructure spend", "score": 60},
            {"aspect": "Opposition walkout", "score": -30},
        ],
        "entities": [
            {"name": "Nirmala Sitharaman", "type": "person", "score": 15},
            {"name": "Narendra Modi", "type": "person", "score": 20},
            {"name": "Rahul Gandhi", "type": "person", "score": -35},
        ],
        "trend": [55, 52, 50, 48, 52, 55, 58, 60, 58, 55, 52, 50, 55, 58, 62, 65, 60, 55, 50, 48, 52, 55, 58, 60],
        "posts": [
            {
                "source": "r/india",
                "text": "Budget is classic: give with one hand (tax relief), take with the other (cess increases). Middle class always ends up in the same place. At least the new tax regime is simpler to understand.",
                "sentiment": "neu", "score": 10, "upvotes": 4321, "comments": 623, "time_ago": "1d ago",
            },
            {
                "source": "r/IndianStockMarket",
                "text": "Markets up 1.2% post budget. Capital gains tax unchanged, infra push is real, MSME credit guarantee scheme doubled. Overall positive for mid/small caps.",
                "sentiment": "pos", "score": 65, "upvotes": 2134, "comments": 287, "time_ago": "1d ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=48),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Railway Delays",
        "summary": "Monsoon season has triggered a cascade of train delays across North and Central India, with Rajdhani and Shatabdi services running 4-8 hours late. Passengers stranded at stations are sharing real-time updates on Reddit, and the IRCTC complaint hashtag has been trending.",
        "sentiment": "neg",
        "score": -58,
        "region": "National",
        "signal_type": "sustained",
        "post_count": 234,
        "duration_hours": 72,
        "spike_rate": 25.8,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.94,
            "bot_risk": 0.06,
            "account_diversity": 0.91,
            "language_mix": 0.48,
            "spread_pattern": 0.85,
        },
        "breakdown": [
            {"aspect": "Monsoon track flooding", "score": -55},
            {"aspect": "No real-time information", "score": -78},
            {"aspect": "IRCTC refund delays", "score": -72},
            {"aspect": "Staff communication poor", "score": -65},
        ],
        "entities": [
            {"name": "Indian Railways", "type": "organization", "score": -62},
            {"name": "IRCTC", "type": "organization", "score": -58},
            {"name": "Ashwini Vaishnaw", "type": "person", "score": -30},
        ],
        "trend": [70, 68, 65, 62, 60, 58, 55, 52, 50, 55, 58, 62, 65, 68, 70, 72, 68, 65, 62, 60, 58, 55, 52, 50],
        "posts": [
            {
                "source": "r/india",
                "text": "Rajdhani Express to Patna is 6 hours late and there's no announcement at New Delhi station. Hundreds of people just sitting and guessing. This is how Indian Railways treats passengers.",
                "sentiment": "neg", "score": -75, "upvotes": 5432, "comments": 743, "time_ago": "5h ago",
            },
            {
                "source": "r/delhi",
                "text": "IRCTC website shows train on time, national train enquiry shows 4 hours late, the station display shows nothing. Three systems, three different answers. Incredible.",
                "sentiment": "neg", "score": -68, "upvotes": 3210, "comments": 445, "time_ago": "7h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=72),
        "updated_at": datetime.now(timezone.utc),
    },
    {
        "topic": "Stock Market",
        "summary": "Nifty crossing 25,000 for the first time is generating genuine excitement in r/IndianStockMarket. First-time retail investors are sharing their gains, while veteran users are cautioning about valuations. The SIP culture boom is visible with many users celebrating milestone portfolios.",
        "sentiment": "pos",
        "score": 67,
        "region": "National",
        "signal_type": "spike",
        "post_count": 312,
        "duration_hours": 6,
        "spike_rate": 312.5,
        "fact_check": {
            "verdict": "organic",
            "confidence": 0.87,
            "bot_risk": 0.13,
            "account_diversity": 0.82,
            "language_mix": 0.28,
            "spread_pattern": 0.76,
        },
        "breakdown": [
            {"aspect": "Nifty 25k milestone", "score": 88},
            {"aspect": "Retail investor participation", "score": 75},
            {"aspect": "FII inflows", "score": 65},
            {"aspect": "Overvaluation concerns", "score": -40},
            {"aspect": "SIP portfolio gains", "score": 82},
        ],
        "entities": [
            {"name": "Nifty 50", "type": "index", "score": 85},
            {"name": "Sensex", "type": "index", "score": 80},
            {"name": "SEBI", "type": "organization", "score": 30},
            {"name": "Zerodha", "type": "organization", "score": 55},
        ],
        "trend": [20, 25, 30, 35, 42, 50, 60, 72, 82, 90, 95, 100, 98, 95, 92, 88, 85, 82, 80, 78, 75, 72, 70, 68],
        "posts": [
            {
                "source": "r/IndianStockMarket",
                "text": "Nifty 25,000. Started my SIP 4 years ago with ₹5,000/month. Portfolio crossed ₹4 lakhs today for the first time. Small number for most here but massive for a ₹40k/month earning person.",
                "sentiment": "pos", "score": 92, "upvotes": 8923, "comments": 1243, "time_ago": "2h ago",
            },
            {
                "source": "r/india",
                "text": "Everyone celebrating Nifty 25k but P/E ratio is at 24. Historical average is 20. Either earnings need to catch up or we're in for a correction. Be careful out there.",
                "sentiment": "neu", "score": -15, "upvotes": 3421, "comments": 567, "time_ago": "3h ago",
            },
            {
                "source": "r/IndianStockMarket",
                "text": "FII bought ₹8,200 crore worth of Indian equities today. Global funds are finally coming back after 6 months of selling. This could sustain the rally.",
                "sentiment": "pos", "score": 75, "upvotes": 4521, "comments": 432, "time_ago": "4h ago",
            },
        ],
        "created_at": datetime.now(timezone.utc) - timedelta(hours=6),
        "updated_at": datetime.now(timezone.utc),
    },
]


async def seed():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db["signals"]

    await col.drop()
    result = await col.insert_many(SIGNALS)
    print(f"Seeded {len(result.inserted_ids)} signals into MongoDB.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
