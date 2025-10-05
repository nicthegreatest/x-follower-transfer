# x-follower-transfer
A python script to transfer followed accounts from one X account to another. Exports list of accounts the old account is following to a CSV called following.csv - and uses the same CSV to upload to the new account.

NOTE: The API is prohibitively expensive. You'll need to fork out $200 a month for this to run properly - the free tier API will run in to issues. Probably due to spam/bot protection.

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
