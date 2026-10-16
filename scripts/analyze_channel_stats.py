"""Statistical and Semantic Analysis of YouTube channel videos."""

import asyncio
from sqlalchemy import text
from jemini.storage.database import AsyncSessionLocal


async def main():
    async with AsyncSessionLocal() as session:
        # 1. Total summary
        res = await session.execute(text("""
            SELECT 
                count(*) as total,
                count(*) FILTER (WHERE is_short = true) as shorts_count,
                count(*) FILTER (WHERE is_short = false) as wide_count,
                round(avg(view_count)::numeric, 1) as avg_views,
                max(view_count) as max_views,
                round(avg(like_count)::numeric, 1) as avg_likes,
                round(avg(comment_count)::numeric, 1) as avg_comments
            FROM youtube_videos;
        """))
        summary = dict(res.mappings().one())
        print("=== OVERALL CHANNEL METRICS ===")
        for k, v in summary.items():
            print(f"  {k}: {v}")

        # 2. Compare Shorts vs Widescreen
        res_comp = await session.execute(text("""
            SELECT 
                is_short,
                count(*) as count,
                round(avg(view_count)::numeric, 1) as avg_views,
                round(avg(like_count)::numeric, 1) as avg_likes,
                round(avg(comment_count)::numeric, 1) as avg_comments,
                max(view_count) as max_views,
                min(view_count) as min_views
            FROM youtube_videos
            GROUP BY is_short;
        """))
        print("\n=== FORMAT COMPARISON (SHORTS vs WIDESCREEN) ===")
        for r in res_comp.mappings().all():
            label = "Shorts (9:16)" if r["is_short"] else "Longform (16:9)"
            print(f"  [{label}] Count: {r['count']} | Avg Views: {r['avg_views']} | Max Views: {r['max_views']} | Avg Likes: {r['avg_likes']} | Avg Comm: {r['avg_comments']}")

        # 3. Top 20 Videos by Views
        res_top = await session.execute(text("""
            SELECT video_id, title, view_count, like_count, comment_count, duration_seconds, is_short, published_at
            FROM youtube_videos
            ORDER BY view_count DESC
            LIMIT 20;
        """))
        print("\n=== TOP 20 BEST PERFORMING VIDEOS ===")
        for idx, r in enumerate(res_top.mappings().all(), 1):
            views = r["view_count"]
            likes = r["like_count"]
            comms = r["comment_count"]
            eng = round(((likes + comms) / (views or 1)) * 100, 2)
            fmt = "Short" if r["is_short"] else "Wide"
            dur = f"{r['duration_seconds']:.0f}s"
            date = str(r["published_at"])[:10]
            print(f"[{idx:02d}] {views:>6} views | {likes:>4} L | {comms:>3} C | {eng:>5.1f}% Eng | {fmt:<5} ({dur:>4}) | {date} | {r['title']}")

        # 4. Bottom 20 Videos by Views
        res_bot = await session.execute(text("""
            SELECT video_id, title, view_count, like_count, comment_count, duration_seconds, is_short, published_at
            FROM youtube_videos
            ORDER BY view_count ASC
            LIMIT 20;
        """))
        print("\n=== BOTTOM 20 WORST PERFORMING VIDEOS ===")
        for idx, r in enumerate(res_bot.mappings().all(), 1):
            views = r["view_count"]
            likes = r["like_count"]
            comms = r["comment_count"]
            fmt = "Short" if r["is_short"] else "Wide"
            dur = f"{r['duration_seconds']:.0f}s"
            date = str(r["published_at"])[:10]
            print(f"[{idx:02d}] {views:>6} views | {likes:>4} L | {comms:>3} C | {fmt:<5} ({dur:>4}) | {date} | {r['title']}")

        # 5. Engagement Leaders (most comments & likes)
        res_eng = await session.execute(text("""
            SELECT video_id, title, view_count, like_count, comment_count, is_short
            FROM youtube_videos
            WHERE view_count > 100
            ORDER BY comment_count DESC
            LIMIT 10;
        """))
        print("\n=== TOP 10 MOST DISCUSSED VIDEOS (HIGHEST COMMENTS) ===")
        for idx, r in enumerate(res_eng.mappings().all(), 1):
            print(f"[{idx:02d}] {r['comment_count']:>3} Comm | {r['like_count']:>4} Likes | {r['view_count']:>6} Views | {r['title']}")

        # 6. Real Viewer Voice
        res_comm = await session.execute(text("""
            SELECT author_name, sentiment, audience_topic, text, like_count
            FROM youtube_comments
            WHERE author_name NOT IN ('@Jermina_AI', 'Jermina AI Studio')
              AND length(text) > 8
            ORDER BY like_count DESC, published_at DESC
            LIMIT 15;
        """))
        print("\n=== REAL VIEWER COMMENTS & PAIN POINTS ===")
        for idx, r in enumerate(res_comm.mappings().all(), 1):
            sent = r['sentiment'] or '?'
            print(f"[{idx:02d}] [{sent.upper():<8}] ({r['author_name']}): {r['text'][:120]}")


if __name__ == "__main__":
    asyncio.run(main())

