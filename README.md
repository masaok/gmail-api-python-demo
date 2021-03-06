## Quickstart

1. Setup Python virtual environment

   ```
   python3 -m venv env
   source env/bin/activate
   source env/Scripts/Activate       # Windows
   pip3 install -r requirements.txt  # install from requirements
   pip3 freeze > requirements.txt    # save requirements
   deactivate
   ```

1. Create a `credentials.json` file in the repo redirectory via the Google Cloud Console:

   https://console.cloud.google.com/apis/credentials
   
   ...as instructed by the quickstart:

   https://developers.google.com/gmail/api/quickstart/python

1. Install Python libraries via pip (also on the quickstart page)

   https://developers.google.com/gmail/api/quickstart/python#step_2_install_the_google_client_library
   
   ```
   pip install mysql-connector-python
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

1. Run the script

   ```
   % ./quickstart.py
   ```

## List Messages and Insert into Database for Analysis

1. Copy and edit `env.sample.sh` with MySQL credentials

   ```
   cp env.samples.sh env.sh
   vim env.sh
   source env.sh
   ```

1. Run the script

   ```
   % ./list_emails.py
   ```
   
## Delete Old Emails

1. Create credentials above.
1. Run the script

   ```
   % ./delete_old_emails.py
   ```

## How to Change Email Addresses

Remove the `token.pickle` and rerun the script

## References

### Gmail API Reference

- https://developers.google.com/gmail/api/v1/reference/users/messages/list
