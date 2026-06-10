# Ghost Local YouTube Scraper

Run YouTube transcript scraping from your Mac to avoid IP blocking.

## Quick Start

```bash
# 1. Install dependencies
pip install youtube-transcript-api google-api-python-client requests python-dotenv

# 2. Run once
python youtube_scraper.py

# 3. Or run continuously (every 30 minutes)
python youtube_scraper.py --daemon
```

## How It Works

1. Fetches recent videos from finance YouTube channels
2. Searches for finance-related content
3. Extracts **full transcripts** (not just titles/descriptions)
4. Sends data to your Ghost API or saves locally

## Why This Works

- **Your home IP** looks like a normal YouTube viewer
- **No cloud IP blocking** - YouTube blocks AWS/GCP/Azure, not home connections
- **Rate limiting** - Built-in delays to stay under YouTube's radar

## Configuration

The scraper uses your existing `.env` from the scraper folder:

```
YOUTUBE_API_KEY=your_key_here
```

## Running as a Background Service

### Option 1: Keep Terminal Open
```bash
python youtube_scraper.py --daemon
```

### Option 2: Use launchd (Mac)
Create `~/Library/LaunchAgents/com.ghost.youtube-scraper.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ghost.youtube-scraper</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/GH_ST/local-scraper/youtube_scraper.py</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.ghost.youtube-scraper.plist
```

## Output

Scraped content is:
1. Sent to Ghost API if running
2. Saved to `data/youtube_YYYYMMDD_HHMMSS.json` as backup

## Customization

Edit `youtube_scraper.py` to add/remove:
- YouTube channels to monitor
- Search terms
- Scraping frequency
