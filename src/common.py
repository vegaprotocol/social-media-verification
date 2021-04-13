class SMVConfig(object):
    def __init__(
        self,
        *,
        twitter_search_text: str,
        twitter_reply_message_success: str,
        twitter_reply_message_invalid_format: str,
        twitter_reply_message_invalid_signature: str,
        twitter_reply_delay: float,
    ) -> None:
        self.twitter_search_text = twitter_search_text
        self.twitter_reply_message_success = twitter_reply_message_success
        self.twitter_reply_message_invalid_format = (
            twitter_reply_message_invalid_format
        )
        self.twitter_reply_message_invalid_signature = (
            twitter_reply_message_invalid_signature
        )
        self.twitter_reply_delay = twitter_reply_delay
