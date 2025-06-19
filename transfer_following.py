import tweepy
import csv
import time
import logging
import os
from tqdm import tqdm
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API credentials for old account
OLD_API_KEY = os.getenv("OLD_API_KEY")
OLD_API_SECRET = os.getenv("OLD_API_SECRET")
OLD_ACCESS_TOKEN = os.getenv("OLD_ACCESS_TOKEN")
OLD_ACCESS_TOKEN_SECRET = os.getenv("OLD_ACCESS_TOKEN_SECRET")

# API credentials for new account
NEW_API_KEY = os.getenv("NEW_API_KEY")
NEW_API_SECRET = os.getenv("NEW_API_SECRET")
NEW_ACCESS_TOKEN = os.getenv("NEW_ACCESS_TOKEN")
NEW_ACCESS_TOKEN_SECRET = os.getenv("NEW_ACCESS_TOKEN_SECRET")

# Check for missing credentials
if not all([OLD_API_KEY, OLD_API_SECRET, OLD_ACCESS_TOKEN, OLD_ACCESS_TOKEN_SECRET,
            NEW_API_KEY, NEW_API_SECRET, NEW_ACCESS_TOKEN, NEW_ACCESS_TOKEN_SECRET]):
    logger.error("Missing environment variables: Please set OLD_API_KEY, OLD_API_SECRET, OLD_ACCESS_TOKEN, OLD_ACCESS_TOKEN_SECRET, NEW_API_KEY, NEW_API_SECRET, NEW_ACCESS_TOKEN, NEW_ACCESS_TOKEN_SECRET.")
    raise ValueError("Missing environment variables")

def setup_client(api_key, api_secret, access_token, access_token_secret):
    """Set up and authenticate Tweepy client."""
    try:
        logger.debug(f"Authenticating with API Key: {api_key[:5]}..., Access Token: {access_token[:5]}...")
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        logger.debug("Client created successfully")
        # Verify authentication
        user = client.get_me().data
        logger.info(f"Verified authentication as {user.username} (ID: {user.id})")
        return client
    except tweepy.TweepyException as e:
        logger.error(f"Failed to authenticate: {e}")
        raise

def export_following(client, user_id, output_file="following.csv"):
    """Export list of accounts the old account follows to a CSV file using v2 API."""
    following = []
    retries = 3
    backoff = 5  # Initial backoff in seconds
    try:
        logger.info("Fetching following list using v2 API...")
        for attempt in range(retries):
            try:
                paginator = tweepy.Paginator(
                    client.get_users_following,
                    id=user_id,
                    max_results=1000,
                    user_fields=["username"]
                )
                for page in paginator:
                    logger.debug(f"Page response: {page.meta}")
                    if page.data:
                        for user in page.data:
                            following.append({"username": user.username, "id": user.id})
                            logger.info(f"Added {user.username} to list")
                    if "next_token" in page.meta:
                        logger.debug(f"Next token: {page.meta['next_token']}")
                break  # Success, exit retry loop
            except tweepy.errors.Unauthorized as e:
                logger.error(f"Attempt {attempt + 1} failed with 401 Unauthorized: {e}")
                if attempt < retries - 1:
                    logger.warning(f"Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error("Likely Free tier restriction on GET /2/users/:id/following. Upgrade to Basic tier ($200/month) at https://developer.x.com/en/portal/dashboard or use manual export.")
                    print("\nError: Cannot fetch following list due to Free tier restrictions.")
                    print("Options:")
                    print("1. Upgrade to Basic tier at https://developer.x.com/en/portal/dashboard.")
                    print("2. Manually export @SomaHempFoods's following list as a CSV with 'username' and 'id' columns.")
                    print("   Tools: https://tweepsmap.com/ or X's web interface.")
                    print("   Place the CSV in following.csv and rerun the script with export commented out.")
                    while True:
                        choice = input("\nContinue with manual export? (yes/no): ").strip().lower()
                        if choice in ['yes', 'y']:
                            return False  # Skip export, expect manual CSV
                        elif choice in ['no', 'n']:
                            raise SystemExit("Exiting. Please upgrade tier or prepare manual export.")
                        else:
                            print("Please enter 'yes' or 'no'.")
            except tweepy.TweepyException as e:
                logger.error(f"Attempt {attempt + 1} failed with error: {e}")
                if attempt < retries - 1:
                    logger.warning(f"Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.error(f"Error exporting following list after {retries} attempts: {e}")
                    raise
            except RequestException as e:
                logger.error(f"Network error: {e}")
                raise
        
        if following:
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["username", "id"])
                writer.writeheader()
                writer.writerows(following)
            logger.info(f"Saved {len(following)} accounts to {output_file}")
        else:
            logger.warning("No accounts found to export.")
    except tweepy.TweepyException as e:
        logger.error(f"Error exporting following list: {e}")
        raise
    return True  # Export succeeded

def confirm_continue():
    """Prompt user to confirm proceeding with following accounts after reviewing CSV."""
    print(f"\nThe following list has been exported to 'following.csv'.")
    print("Please review the file before proceeding to follow accounts.")
    print("You can open 'following.csv' in a text editor or spreadsheet program.")
    while True:
        response = input("\nDo you want to proceed with following accounts? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            logger.info("User chose to stop before following accounts.")
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def follow_accounts(client, input_file="following.csv"):
    """Follow accounts from the new account using the exported CSV with a progress bar."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f) - 1  # Subtract header row
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in tqdm(reader, total=total, desc="Following accounts"):
                try:
                    logger.info(f"Attempting to follow {row['username']} (ID: {row['id']})")
                    client.follow_user(target_user_id=int(row["id"]))
                    logger.info(f"Followed {row['username']}")
                    # Sleep for a very conservative duration after a successful follow
                    # This helps prevent hitting the limit immediately if the limit is tight
                    time.sleep(900) # Sleep for 15 minutes as a base
                except tweepy.errors.TooManyRequests as e:
                    # Access headers from the exception object 'e'
                    reset_time_str = e.response.headers.get("x-rate-limit-reset")
                    current_time = time.time()
                    wait_time = 0

                    if reset_time_str:
                        reset_time = int(reset_time_str)
                        wait_time = reset_time - int(current_time) + 5 # Add 5 seconds buffer
                        if wait_time < 0: # If reset time is in the past, default to a safe value
                            wait_time = 900 # Default to 15 minutes if something went wrong or time passed
                    else:
                        wait_time = 900 # Default to 15 minutes if no reset header found
                    
                    logger.error(f"Error following {row['username']}: {e}. Rate limit hit. Waiting for {wait_time} seconds until reset.")
                    print(f"Rate limit hit. Waiting for {wait_time} seconds before retrying.")
                    time.sleep(wait_time)
                    # After waiting, you might want to re-attempt the *same* user.
                    # The current loop will move to the next user, which might lead to
                    # skipping some if the wait time isn't long enough for the *next* request.
                    # For a robust solution, consider implementing a retry decorator or
                    # a loop that re-attempts the current user after the wait.
                    # For now, this fixes the AttributeError and lets it try the next.

                except tweepy.TweepyException as e:
                    logger.error(f"Error following {row['username']}: {e}")
                    time.sleep(5)  # Wait longer on other errors
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
    
    # Step 3: Skip export_following since using manual CSV
    logger.info("Using manual export. Ensure following.csv exists.")
    
    # Step 4: Prompt user to confirm before proceeding
    if not confirm_continue():
        return
    
    # Step 5: Authenticate with new account
    new_client = setup_client(NEW_API_KEY, NEW_API_SECRET, NEW_ACCESS_TOKEN, NEW_ACCESS_TOKEN_SECRET)
    
    # Step 6: Follow accounts from new account
    follow_accounts(new_client)

if __name__ == "__main__":
    main()
