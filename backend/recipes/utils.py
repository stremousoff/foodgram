import random
import string

from recipes.constants import Config


def generate_short_url():
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits, k=Config.MAX_URL_LENGTH
        )
    )
