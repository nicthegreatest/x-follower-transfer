import tweepy
import csv
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OLD_API_KEY = os.getenv("OLD_API_KEY")
OLD_API_SECRET = os.getenv("OLD_API_SECRET")
OLD_ACCESS_TOKEN = os.getenv("OLD_ACCESS_TOKEN")
OLD_ACCESS_TOKEN_SECRET = os.getenv("OLD_ACCESS_TOKEN_SECRET")

client = tweepy.Client(
    consumer_key=OLD_API_KEY,
    consumer_secret=OLD_API_SECRET,
    access_token=OLD_ACCESS_TOKEN,
    access_token_secret=OLD_ACCESS_TOKEN_SECRET
)

# Replace with your list of usernames from manual export
usernames = ["elonmusk", "XDevelopers"]  # e.g., ["elonmusk", "XDevelopers"]
following = []
try:
    users = client.get_users(usernames=usernames, user_fields=["username"])
    if users.data:
        for user in users.data:
            following.append({"username": user.username, "id": user.id})
            logger.info(f"Fetched {user.username} (ID: {user.id})")
    else:
        logger.warning("No users found.")
except tweepy.TweepyException as e:
    logger.error(f"Error fetching users: {e}")
    raise

with open("following.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["username", "id"])
    writer.writeheader()
    writer.writerows(following)
logger.info("Saved to following.csv")
