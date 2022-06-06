# telq-interface
A command line interface for sending SMS test notifications to TelQ.

Please note that this repo and the quick start process described below are intended for advanced users.

It is intended that CloudOps personnel will follow https://path.***********.com/display/NO/How+to+use+the+CLI+SMS+Testing+Tool+-+TelQ which documents how to use an already installed version of this tool on the CloudOps utility server.

## Requirements
- Python 3.6 or greater.
- Some extra python libraries:
  - pycountry
  - requests
- An appId and appKey from TelQ: https://app.telqtele.com/#/user/account/api
- The TelQ Test Org's API key.


## Quick Start
 1. Clone this repository.
 2. Edit the "telq.py" file and replace "yourkeyhere" with the various API keys for the TelQ Test orgs in prod US, EU and stage.
 3. Login to TelQ and generate an "appID" and "appKey" and save this somewhere safe. You'll need this to use the script and it will associate any tests using this key to your user. https://app.telqtele.com/#/user/account/api
    1. Consider editing the script to hard code these in as well. Should be obvious where.
 4. Run the script: `python3 telq.py'
 5. Follow the prompts on screen.
 6. Check TelQ for test results.

## Troubleshooting
>My country is not found

A. TelQ doesn't have every country in the world technically. Verify it's on the list in the TelQ tool. If it is and the script cannot find it, please report this.

>"Permission Denied"

A. It's likely the file doesn't have execute permissions. Try `chmod 755 telq.py`

>I'm getting an invalid credential error even though I know I entered it correctly

A. You probably forgot to actually save the key in TelQ. Moving the toggle is not enough, you must also hit the save button to apply your key.

## Possible feature enhancements/updates
- Enable looping or multiple runs, i.e. I need to test something 10x, I need to test each country in EU, etc 
- Service account user for API calls (so each person doesn't need their own API key) 
- Email feature to send results to share or as proof 
- Specify 'timeout' for test to mark the test failed after X seconds
- Go back and delete the contact after we are done?
