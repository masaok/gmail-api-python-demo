## Quickstart

1. Create a `credentials.json` file in this directory via this URL:

   https://developers.google.com/gmail/api/quickstart/python

1. Install Python libraries via pip (also on the quickstart page)

   https://developers.google.com/gmail/api/quickstart/python#step_2_install_the_google_client_library

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


