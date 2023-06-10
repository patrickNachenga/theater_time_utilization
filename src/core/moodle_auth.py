from src.core.moodle_api import MoodleApi
from src.core.redis import get_redis

MOODLE_EXPIRE_TIME = 60 * 30


class MoodleAuth:
    """
    Class representing Moodle authentication mechanism
    """

    def __init__(self, username):
        self.username = username
        self.moodle = MoodleApi()
        self.user_key = 'moodle-' + username
        self.redis = await get_redis()

    async def get_moodle_auth_url(self) -> str | None:
        try:
            # check if key exists otherwise get it and store to redis
            auth_url = await self.redis.get(self.user_key)
            if not auth_url:
                auth_url = self.moodle.get_login_url_auth(self.username)
                if auth_url:
                    await self.redis.set(self.user_key, auth_url, MOODLE_EXPIRE_TIME)
                else:
                    return None
            return auth_url
        except Exception as e:
            print(e)
            return None

