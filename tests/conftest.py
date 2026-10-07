import os

# Settings are not needed by unit tests, but importing config loads .env;
# make sure tests never depend on real secrets.
os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", "test")
os.environ.setdefault("YOUTUBE_TRANSCRIPT_API_KEY", "test")
