import tweepy
import csv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API credentials for old X account (replace with your own)
OLD_API_KEY = "your_api_key"
OLD_API_SECRET = "your_api_secret"
OLD_ACCESS_TOKEN = "your_access_token"
OLD_ACCESS_TOKEN_SECRET = "your_access_token_secret"

# API credentials for new X account (replace with your own)
NEW_API_KEY = "your_api_key"  # Can be same as OLD_API_KEY
NEW_API_SECRET = "your_api_secret"  # Can be same as OLD_API_SECRET
NEW_ACCESS_TOKEN = "new_access_token"
NEW_ACCESS_TOKEN_SECRET = "new_access_token_secret"

def setup_client(api_key, api_secret, access_token, access_token_secret):
    """Set up and authenticate Tweepy client."""
    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        return client
    except tweepy.TweepyException as e:
        logger.error(f"Failed to authenticate: {e}")
        raise

def export_following(client, user_id, output_file="following.csv"):
    """Export list of accounts the old account follows to a CSV file."""
    following = []
    try:
        logger.info("Fetching following list...")
        for user in tweepy.Paginator(client.get_users_following, user_id, max_results=1000).flatten():
            following.append({"username": user.username, "id": user.id})
            logger.info(f"Added {user.username} to list")
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "id"])
            writer.writeheader()
            writer.writerows(following)
        logger.info(f"Saved {len(following)} accounts to {output_file}")
    except tweepy.TweepyException as e:
        logger.error(f"Error exporting following list: {e}")
        raise

def follow_accounts(client, input_file="following.csv"):
    """Follow accounts from the new account using the exported CSV."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    client.follow_user(target_user_id=int(row["id"]))
                    logger.info(f"Followed {row['username']}")
                    time.sleep(2)  # Avoid rate limits (50 follows/hour ~ 1 every 72 seconds)
                except tweepy.TweepyException as e:
                    logger.error(f"Error following {row['username']}: {e}")
                    time.sleep(5)  # Wait longer on error
    except FileNotFoundError:
        logger.error(f"Input file {input_file} not found")
        raise
    except tweepy.TweepyException as e:
        logger.error(f"Error during follow operation: {e}")
        raise

def main():
    # Step 1: Authenticate with old account
    old_client = setup_client(OLD_API_KEY, OLD_API_SECRET, OLD_ACCESS_TOKEN, OLD_ACCESS_TOKEN_SECRET)
    
    # Step 2: Get user ID of old account
    try:
        user = old_client.get_me().data
        user_id = user.id
        logger.info(f"Authenticated as {user.username} (ID: {user_id})")
    except tweepy.TweepyException as e:
        logger.error(f"Failed to get user ID: {e}")
        return
    
    # Step 3: Export following list
    export_following(old_client, user_id)
    
    # Step 4: Authenticate with new account
    new_client = setup_client(NEW_API_KEY, NEW_API_SECRET, NEW_ACCESS_TOKEN, NEW_ACCESS_TOKEN_SECRET)
    
    # Step 5: Follow accounts from new account
    follow_accounts(new_client)

if __name__ == "__main__":
    main()
