"""Offline installation check. Never requests platform data or reads secrets."""

from importlib.metadata import version

from google_play_scraper import Sort, reviews
import praw


def main() -> None:
    assert callable(reviews)
    assert Sort.NEWEST is not None
    assert callable(praw.Reddit)
    print(
        {
            "google-play-scraper": version("google-play-scraper"),
            "praw": version("praw"),
            "network_requests": 0,
            "reddit_auth_checked": False,
        }
    )


if __name__ == "__main__":
    main()
