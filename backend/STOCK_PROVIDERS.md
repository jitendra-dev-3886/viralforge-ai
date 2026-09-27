# Stock media fallbacks

Scene search tries Pexels and Pixabay first for each search phrase. Optional
fallbacks add photo and video coverage without changing the generation workflow:

| Media | Extra provider | Backend environment setting |
| --- | --- | --- |
| Photos | Openverse, CC0 results only | `OPENVERSE_ENABLED=true` |
| Videos | Coverr | `COVERR_API_KEY=your-key` |

Set these in `backend/.env` and restart the backend. Both are disabled until
configured. Use **Find new stock media** on a failed scene to retry.

Create a Coverr application at https://coverr.co/developers. API access and
commercial usage depend on the account and plan; use a plan that permits your
intended use. The adapter uses the tracked download URL, and media previews show
Coverr source credit. Documentation: https://api.coverr.co/docs/start/ and
https://api.coverr.co/docs/videos/.

Openverse uses public, rate-limited search. It is an index, so source images may
have moved. The adapter accepts only results marked CC0, excludes mature results,
and downloads from known image hosts (Flickr, Wikimedia, StockSnap and Rawpixel).
Missing dimensions or insufficient relevance cause a result to be skipped.
Source credit appears in the media views. See https://docs.openverse.org/.

Both providers retain the existing orientation and duplicate-asset checks.
No result is guaranteed for a particular topic. These additions do not repair
invalid Pexels or Pixabay credentials. New integrations have mocked regression
coverage; live account access must be verified with your configuration.
