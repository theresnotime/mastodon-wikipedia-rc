import config
import time
from mastodon import Mastodon
from pywikibot.comms.eventstreams import EventStreams
from typing import Union


def main() -> None:
    """Interate through the filtered stream and post edits to Mastodon"""
    streams = ["recentchange", "revision-create", "page-create"]
    stream = EventStreams(streams=streams)
    stream.register_filter(server_name=config.WIKI_SITE, type=config.ENABLED_EVENTS)

    print("Listening for events...")
    while stream:
        # Get the next change from the stream
        change = next(iter(stream))

        # Filter out changes we don't want
        if filter_change(change):
            status = get_status(change)
            if status is not None:
                post_mastodon(status)

            # EventStream sleep
            time.sleep(0.5)


def filter_change(change) -> bool:
    """Filter out changes we don't want"""
    # Filter bots if enabled
    if config.FILTER_BOTS and change["bot"] is True:
        if config.VERBOSE:
            print("Bot edit by", change["user"])
        return False
    # Filter disallowed namespaces
    elif change["namespace"] and change["namespace"] not in config.ENABLED_NS:
        if config.VERBOSE:
            print("Not an enabled namespace — NS =", change["namespace"])
        return False
    # Filter disallowed events
    elif change["type"] not in config.ENABLED_EVENTS:
        if config.VERBOSE:
            print("Not an enabled event — type =", change["type"])
        return False
    else:
        return True


def get_status(change) -> Union[str, None]:
    """Get the status to post to Mastodon"""
    # Handle new pages
    if change["type"] == "new":
        user = change["user"]
        title = change["title"]
        uri = change["meta"]["uri"]
        status = f"'User:{user}' created a new page called '{title}' — {uri}"
        return status
    else:
        return None


def post_mastodon(status) -> None:
    """Post a status to Mastodon"""
    if config.DRY is False:
        mastodon = Mastodon(
            access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL
        )
        mastodon.toot(status)
        print("Posted:", status)
        # Always sleep after posting to Mastodon
        time.sleep(4)
    else:
        print("Dry run, did not post:", status)


if __name__ == "__main__":
    print("Dry run:", config.DRY)
    print("Verbose:", config.VERBOSE)
    print("Wiki:", config.WIKI_SITE)
    print("Filter bots:", config.FILTER_BOTS)
    print("Enabled namespaces:", config.ENABLED_NS)
    print("Enabled events:", config.ENABLED_EVENTS)
    main()
