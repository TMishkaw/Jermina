import asyncio
import logging
import sys

from jemini.analytics.youtube_ingestor import YouTubeChannelIngestor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

async def main():
    ingestor = YouTubeChannelIngestor(
        token_path="config/youtube_token.json",
        output_dir="data/youtube_dump",
    )
    res = await ingestor.ingest_channel(
        channel_id="UC1ol6l3KL3sgmLPiwQy2QTA", # @Jermina_AI
        include_comments=True,
    )
    print("\n" + "=" * 80)
    print("  YOUTUBE ARCHIVE INGESTION COMPLETED")
    print("=" * 80)
    print(f"  Channel:          {res['channel']} ({res['channel_id']})")
    print(f"  Videos Ingested:  {res['videos_synced']}")
    print(f"  Comments Ingested:{res['comments_synced']}")
    print(f"  Local JSON Dump:  {res['dump_path']}")
    print("  LLM Tokens Used:  0 (Pure YouTube Data API v3)")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
