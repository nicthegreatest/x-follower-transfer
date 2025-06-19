# Limits of the Free-Tier API

The free API limits are very prohibitive, especially for tasks like transferring followers that used to be relatively straightforward.

Here's some issues I ran in to...

Old Account (GET /2/users/me): Hit a 24-hour limit of 25 requests for certain user-specific endpoints. Each time you run the script and it tries to authenticate the old account, it consumes one of these.
New Account (POST /2/users/:id/following): An extremely strict limit of just 1 follow per roughly 15-minute window. To follow even a small list of 5 accounts, that would take over an hour, and for a larger list, it becomes impractical (e.g., 100 followers would take 25 hours of continuous script running).
These limits effectively make automated mass following/transferring of accounts unfeasible for most users without upgrading to a paid API tier. The $200/month "Basic" tier is likely what's needed for reasonable access... extortion.

## Is it worth it?

Using the API under these free tier restrictions is likely not worth the effort or the potential frustration.

**Time:** The time required to wait for rate limits to reset, constantly monitoring the script, and re-running it, will far outweigh any benefit of automation.
**Risk:** Even with time.sleep, attempting to follow hundreds or thousands of accounts on a new profile via the API (even when successful within limits) could still trigger X's internal spam detection, potentially leading to temporary account restrictions or even suspension of your new account. X wants to curb automated, high-volume activity without payment.
**Simplicity:** For the small number of follows you're managing to achieve per 15 minutes, manually following accounts directly on the X website might actually be faster and simpler, even if tedious.

Unless you're willing to pay for a higher API tier, pursuing this via the X API is likely to be a continuous battle against highly restrictive rate limits.

### x-follower-transfer
A python script to transfer followed accounts from one X account to another. Exports list of accounts the old account is following to a CSV called following.csv - and uses the same CSV to upload to the new account.

### Dependencies
tweepy for this to work & tqdm for a progress bar.

> pip3 install tweepy tqdm --user

### Create an API key @ https://developer.x.com/
- Create a new project on both your old acc (to transfer FROM) and new acc (to transfer TO).
- Generate the Client ID, API key and Access Token and their secrets.
- For Callback URI / Redirect URL Requirements, you can use the URL http://127.0.0.1:port/callback with an open port of your choice.
- Lines 12 to 22 in transfer_following.py will be where you need to put in your API keys and Access Token Secrets etc.

### Run
> python3 transfer_following.py

### Notes
- Examine the define for export_following and follow_accounts (the meat in this sandwich).
- There's a confirmation prompt - maybe check the CSV and make any changes or omittances before you commit.
