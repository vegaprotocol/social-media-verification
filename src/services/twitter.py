from typing import Iterator, List, Optional
import os
import json
from twython import Twython
from twython.exceptions import TwythonError

from .secret import get_json_secret_from_gcp


class Tweet(object):
    def __init__(
        self,
        tweet_id: int,
        user_id: int,
        user_screen_name: int,
        full_text: str,
    ) -> None:
        self.tweet_id = tweet_id
        self.user_id = user_id
        self.user_screen_name = user_screen_name
        self.full_text = full_text

    def __repr__(self) -> str:
        return (
            f"Tweet(tweet_id={self.tweet_id!r}, user_id={self.user_id!r}, "
            f"user_screen_name={self.user_screen_name!r}, "
            f"full_text={self.full_text!r})"
        )

    def __eq__(self, other):
        if isinstance(other, Tweet):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        return hash(self.tweet_id)

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )


class TwitterClient(object):
    def __init__(
        self,
        *,
        gcp_secret_name: str,
    ) -> None:
        """Twitter Client connects to Twitter API
        using credentials read from GCP Secret Manager
        or Environment variable

        Args:
            gcp_secret_name (str): A secret name in GCP Secret Manager
            OR environment variable containing that secret name.

            Note: GCP secret name has format: projects/*/secrets/*/versions/*

        Raises:
            json.JSONDecodeError: If the secret value is not valid json.

        """
        if not gcp_secret_name.startswith("projects/"):
            if gcp_secret_name not in os.environ:
                raise ValueError(
                    "Failed to connect to Twitter API: missing environment "
                    f'variable "{gcp_secret_name}" containing Twitter API '
                    "credentials."
                )
            gcp_secret_name = os.environ[gcp_secret_name]

        if gcp_secret_name.startswith("projects/"):
            twitter_secret = get_json_secret_from_gcp(gcp_secret_name)
        else:
            twitter_secret = json.loads(gcp_secret_name)

        self.account_name = twitter_secret["ACCOUNT_NAME"]
        self._consumer_key = twitter_secret["CONSUMER_KEY"]
        self._consumer_secret = twitter_secret["CONSUMER_SECRET"]
        self._access_token = twitter_secret["ACCESS_TOKEN"]
        self._access_secret = twitter_secret["ACCESS_SECRET"]

        self.twapi = Twython(
            self._consumer_key,
            self._consumer_secret,
            self._access_token,
            self._access_secret,
        )

    def get_by_id(self, tweet_id: int) -> Optional[Tweet]:
        """Returns one tweet specified by id.

        Args:
            tweet_id (int): The id of the tweet to return

        Returns:
            Tweet or None
        """

        try:
            result = self.twapi.show_status(
                id = tweet_id,
                include_entities = True,
                tweet_mode = "extended",
            )

            return Tweet(
                tweet_id=result["id"],
                user_id=result["user"]["id"],
                user_screen_name=result["user"]["screen_name"],
                full_text=result["full_text"],
            )
        except TwythonError:
            pass

        return None

    def search(
        self,
        search_text: str,
        since_tweet_id: int = None,
    ) -> Iterator[Tweet]:
        """Searches for recent tweets contining specified text.

        Args:
            search_text (str): A text that tweet needs to contain
            since_tweet_id (int): Return only tweets newer than

        Returns:
            Iterator with Tweet
        """

        query = {
            "q": search_text,
            "count": 100,
            "include_entities": True,
            "tweet_mode": "extended",
        }

        if since_tweet_id:
            query["since_id"] = since_tweet_id

        while True:
            result = self.twapi.search(**query)
            for tweet_data in result["statuses"]:
                yield Tweet(
                    tweet_id=tweet_data["id"],
                    user_id=tweet_data["user"]["id"],
                    user_screen_name=tweet_data["user"]["screen_name"],
                    full_text=tweet_data["full_text"],
                )

            if "next_results" not in result["search_metadata"]:
                break

            query["max_id"] = tweet_data["id"] - 1

    def mentions(
        self,
        since_tweet_id: int = None,
    ) -> Iterator[Tweet]:
        """Get Tweet timelines

        Args:
            since_tweet_id (int): Return only tweets newer than

        Returns:
            Iterator with Tweet
        """

        query = {
            "count": 100,
            "include_entities": True,
            "tweet_mode": "extended",
        }

        if since_tweet_id:
            query["since_id"] = since_tweet_id

        while True:
            result = self.twapi.get_mentions_timeline(**query)

            if len(result) == 0:
                break

            for tweet_data in result:
                yield Tweet(
                    tweet_id=tweet_data["id"],
                    user_id=tweet_data["user"]["id"],
                    user_screen_name=tweet_data["user"]["screen_name"],
                    full_text=tweet_data["full_text"],
                )

            query["max_id"] = tweet_data["id"] - 1

    def get_tweets(
        self,
        search_text: str,
        since_tweet_id: int = None,
    ) -> List[Tweet]:
        """Gathers all Tweets from:
        - using 'search' call with search_text,
        - user's timeline

        Args:
            search_text (str): A text that tweet needs to contain
            since_tweet_id (int): Return only tweets newer than

        Returns:
            Ordered list of Tweets
        """
        result = list(
            self.search(search_text, since_tweet_id=since_tweet_id)
        ) + list(self.mentions(since_tweet_id=since_tweet_id))
        # remove duplicates
        result = list(set(result))
        # order ascending
        result = sorted(result, key=lambda t: t.tweet_id)

        return result

    def reply(self, msg: str, tweet: Tweet):
        msg = f"@{tweet.user_screen_name} {msg}"
        print(
            json.dumps(
                {
                    "twitter_reply": {
                        "text": msg,
                        "tweet": tweet.toJSON(),
                        "from": self.account_name,
                    }
                }
            )
        )
        self.twapi.update_status(
            status=msg,
            in_reply_to_status_id=tweet.tweet_id,
        )
