import config
import time
from mastodon import Mastodon
from pywikibot.comms.eventstreams import EventStreams


def main():
    """Interate through the filtered stream and post edits to Mastodon"""
    stream = EventStreams(streams=["recentchange", "revision-create"])
    stream.register_filter(server_name="en.wikipedia.org", type="edit")
    just_stop = 100

    while stream:
        # No way I'm ever let this run indefinitely
        print(just_stop)
        if just_stop == 0:
            break
        just_stop -= 1

        # Get the next change from the stream
        change = next(iter(stream))

        # We don't want bot edits
        if change["bot"]:
            continue
        user = change["user"]
        type = change["type"]
        title = change["title"]
        new_rev = change["revision"]["new"]
        status = f"'User:{user}' made [an {type}](https://en.wikipedia.org/wiki/Special:Diff/{new_rev}) to '{title}'"

        # Post to Mastodon
        post_mastodon(status)
        print(status)

        # Prevent immediate rate limiting
        time.sleep(3)


def post_mastodon(status):
    """Post a status to Mastodon"""
    mastodon = Mastodon(access_token=config.ACCESS_TOKEN, api_base_url=config.API_URL)
    mastodon.toot(status)


if __name__ == "__main__":
    main()
