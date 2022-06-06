#!/usr/bin/python3
################################################################################
##### Change these values to the correct API keys for the TelQ Test orgs!! #####
## This data is in lastpass under "TelQ API Keys" in the EBNOC shared folder. ##

Prod_US_***_API_Key = "yourkeyhere"
Stage_US_***_API_Key = "yourkeyhere"
Prod_EU_***_API_Key = "yourkeyhere"

################################################################################
### Set your TelQ appId and appKeys here. This is OPTIONAL
### If you leave these unset, you will simply be asked for them at runtime.
### Otherwise, if you set them now you wont have to enter your keys every time.
### Better not share this script with anyone then!

appId = "youridhere"
appKey = "yourkeyhere"

################################################################################
############ That's it! Stop here. No further changes are needed!! #############
################################################################################

# Enforce python3
import os
import time
if os.sys.version_info.major != 3:
    print("Sorry, you must run this script using python3.")
    print("I have detected you are using version " + os.sys.version + ".")
    raise SystemExit(0)

import requests
import pycountry
from getpass import getpass

if Prod_US_***_API_Key == "yourkeyhere":
    print("You appear not to have configured the *** API keys in the script settings.")
    print("It is almost certain that this attempt will fail.")
    print("You should consider exiting and editing the script settings before you continue.")
    print("Script will continue in 3 seconds...")
    time.sleep(3)


def obtain_bearer_token(app_id:str, app_key:str) -> dict:
    """Takes an app_id and appKey value input. Obtained from TelQ UI on a per-user level. Outputs a bearer token which is required for all future API calls"""
    url = 'https://api.telqtele.com/v2/client/token'
    payload = {'appId': app_id, 'appKey': app_key}
    response = requests.post(url, json=payload)
    output = response.json()
    return output

def set_env_vars(env:str) -> dict:
    """Set various environment variables depending on the selected *** environment we want to test from"""
    if env == "ProdUS":
        envVars = {"name" : "Prod US", "apiKey": Prod_US_***_API_Key, "orgId": "******************", "recordTypeId": "******************", "accountId": "******************", "deliveryId": "******************", "endpoint": "https://api.***********.net"}
    elif env == "ProdEU":
        envVars = {"name" : "Prod EU", "apiKey": Prod_EU_***_API_Key, "orgId": "******************", "recordTypeId": "******************", "accountId": "******************", "deliveryId": "******************", "endpoint": "https://api.***********.eu"}
    elif env == "Stage":
        envVars = {"name" : "Stage", "apiKey": Stage_US_***_API_Key, "orgId": "******************", "recordTypeId": "******************", "accountId": "******************", "deliveryId": "******************", "endpoint": "https://api-stage.***********.net"}
    return envVars

def get_networks() -> dict:
    """Downloads entire list of available networks"""
    auth_header = {'authorization': bearer_token}
    url = 'https://api.telqtele.com/v2/client/networks'
    response = requests.get(url, headers=auth_header)
    return response.json()

def get_country_networks(country_name:str) -> list:
    """Return a list of non-ported network/test targets for a specific country. We do not currently test to ported numbers."""
    result_list = []
    for net in networks:
        if net['countryName'] == country_name:
            if net['portedFromMnc'] is None:
                result_list.append(net)
    return result_list

def contains_number(value:str) -> bool:
    """Obvious. Dunno why I did this. Am noob."""
    for character in value:
        if character.isdigit():
            return True
    return False

def set_country(c_code:str) -> dict:
    """Using the pycountry library to translate 2 letter country code into a country name. Return False if we find nothing."""
    country_data = pycountry.countries.get(alpha_2=c_code)
    if hasattr(country_data, 'name'):
        return country_data
    return False

def show_networks(network_list:list) -> None:
    """Outputs a list of carrier names and corresponding number"""
    count = 1
    print("\n")
    for net in network_list:
        print("[" + str(count) + "] " + net['providerName'])
        count += 1
    return

def create_test(token:str, mcc:str, mnc:str) -> dict:
    """Tells the TelQ system that we'd like to test a specific network, outputs the first value in the response which contains the test id, 'testIdText' and destination phoneNumber.  Do error handling here since we might call this function repeatedly."""
    auth_header = {'authorization': token}
    data = {'destinationNetworks':[{'mcc': mcc, 'mnc': mnc}]}
    response = requests.post('https://api.telqtele.com/v2/client/tests', headers=auth_header, json=data)
    output = response.json()
    try:
        output = output[0]
    except:
        print("We seem to have received an unexpected response from TelQ. Here is what we received:")
        print(response.json())
        print("\nI am exiting now.")
        raise SystemExit(1)
    return output

def create_contact() -> str:
    """Create a contact in the TelQ org in *** with the information provided from telq. In accordance with how this was configured in ReadyAPI, we do not currently go back and delete this contact. I do not know why yet."""
    contact_data = {"organizationId" : environment['orgId'], "lastName" : phone_number, "status" : "A", "country" : country_code.upper(), "recordTypeId" : environment['recordTypeId'], "accountId" : "0", "externalId" : phone_number, "paths" : [{"waitTime" : "0", "pathId" : "******************", "countryCode" : country_code.upper(), "value" : phone_number, "skipValidation" : "false"}],"firstName" : "TelQ Test", "timezoneId" : "America/New_York"}
    header_data = {"Authorization" : environment['apiKey']}
    api_endpoint = str(environment['endpoint']) + "/rest/contacts/" + environment['orgId']
    response = requests.post(api_endpoint, headers=header_data, json=contact_data)
    create_contact_response = response.json()
    try:
        contact_id = create_contact_response['id']
    except:
        print("We seem to have received an unexpected response from ***. Here is what we received:")
        print(response.json())
        print("\nI am exiting now.")
        raise SystemExit(1)
    return contact_id

def build_notification(test_id:str, message_body:str, cont_id:str, title:str, confirm:str, language:str, polling:bool) -> str:
    """Here we put together and send the notification. Outputs the notification ID response from *** API"""
    # Polling messages in *** require additional details
    if polling is False:
        notification_data = {"status": "A", "organizationId": environment['orgId'], "priority": "NonPriority", "type": "Standard", "message": { "contentType": "Text", "title": title, "textMessage": test_id + message_body}, "broadcastContacts": { "contactIds": [ cont_id ] }, "broadcastSettings": {  "language": language, "confirm": confirm, "deliverPaths": [{"accountId": environment['accountId'], "pathId": "******************", "organizationId": environment['orgId'], "id": environment['deliveryId'], "status": "A", "seq": 1, "prompt": "SMS", "extRequired": "false", "displayFlag": "false", "default": "false"}]}, "launchtype": "SendNow" }
    else:
        notification_data = {"status": "A", "organizationId": environment['orgId'], "priority": "NonPriority", "type": "Polling", "message": { "contentType": "Text", "title": title, "textMessage": test_id + message_body, "questionaire": {"inputOptionAllowable": "false", "multipleSelected": "false", "answers": [{"quotaNum": 0, "name": "Hello"}, {"quotaNum": 0, "name": "Goodbye"}], "required": "false"}}, "broadcastContacts": { "contactIds": [ cont_id ] }, "broadcastSettings": {  "language": language, "confirm": confirm, "deliverPaths": [{"accountId": environment['accountId'], "pathId": "******************", "organizationId": environment['orgId'], "id": environment['deliveryId'], "status": "A", "seq": 1, "prompt": "SMS", "extRequired": "false", "displayFlag": "false", "default": "false"}]}, "launchtype": "SendNow" }
    header_data = {"Authorization" : environment['apiKey']}
    api_endpoint = str(environment['endpoint']) + "/rest/notifications/" + environment['orgId']
    response = requests.post(api_endpoint, headers=header_data, json=notification_data)
    notification_response = response.json()
    try:
        notifi_id = notification_response['id']
    except:
        print("We seem to have received an unexpected response from ***. Here is what we received:")
        print(notification_response)
        print("\nI am exiting now.")
        raise SystemExit(1)
    return notifi_id

def send_notification(test_type:str) -> str:
    """# Triggers the build/send of a notification based on selected notification test_type."""
    if test_type == "short":
        # Body must start with a space
        message_body = " You may have to leave your home quickly to stay safe."
        title = country_code + " Short Auto Message"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "long":
        message_body = " You may have to leave your home quickly to stay safe. Be familiar with your emergency route, and have a few different ways to get out of your immediate area. You never know what roads might be closed, damaged, or blocked."
        title = country_code + " Long Auto Message"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "five_part":
        message_body = " You need to know what path you'll take to get where you're going. It won't do you any good to be scrambling to figure out directions when you're scared and pressed for time. Be familiar with your emergency route, and have a few different ways to get out of your immediate area. You never know what roads might be closed"
        title = country_code + " Long Auto Message"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "outside_url_http":
        message_body = " If you need assistance, please go to this Website https://www.redcross.org/"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "outside_url_sans_http":
        message_body = " If you need assistance, please go to this Website www.redcross.org"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "internal_url_us":
        message_body = " If this is an emergency, please visit ******************"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "internal_url_eu":
        message_body = " If this is an emergency, please visit ******************"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "internal_url_us_extention":
        message_body = " If this is an emergency, please visit ******************AbC123"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "internal_url_eu_extention":
        message_body = " If this is an emergency, please visit ******************AbC123"
        title = country_code + " URL AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "special_char":
        message_body = " Message with special characters Françoise Å-Ring ßeta or Beta? Öh löök, umlauts! | | | ENCYCLOPÆDIA ça va! mon élève mi niña? Ðe lónlí blú bojs Françoise"
        title = country_code + " Special Char AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "gsm":
        message_body = " Message with GSM special characters.  Blueberry jam in Norwegian is Blåbærsyltetøy."
        title = country_code + " GSM Char AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "short_confirmation":
        message_body = " This is a confirmation message, This is the body."
        title = country_code + " Short Confirmation Message"
        confirm = "true"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "short_polling":
        message_body = " Polling Question:"
        title = country_code + " Polling AutoMessage"
        confirm = "false"
        language = "en_US"
        polling = True
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "short_polling_international":
        message_body = " Polling Question:"
        title = country_code + " Polling AutoMessage"
        confirm = "false"
        language = "ar_SA"
        polling = True
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id
    elif test_type == "custom":
        message_body = " Custom Text: " + globalCustomText
        title = country_code + " Custom Test Message"
        confirm = "false"
        language = "en_US"
        polling = False
        notification_id = build_notification(test_id_text, message_body, contact_id, title, confirm, language, polling)
        return notification_id

def clear_screen() -> None:
    """Clears the screen"""
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

## Start
# Welcome Message
clear_screen()
print("Welcome to the SMS CLI testing tool!")
print("Basic instructions for this process are documented here: https://path.******************/display/NO/How+to+use+the+CLI+SMS+Testing+Tool+-+TelQ")
print("Technical details are available in the gitlab repo: https://gitlab.******************/engineering/platform/noc/telq-interface")
print("This tool can always use improvement. Please report any issues to the issue tracker: https://gitlab.******************/engineering/platform/noc/telq-interface/-/issues")
time.sleep(1)

while True:
    # Print list of *** environments
    print("\nPlease select the *** environment you wish to test from:")
    print("[1] Prod US")
    print("[2] Prod EU")
    print("[3] Stage")
    print("\n")
    # Ask user what environment to use
    envChoice = input("Enter the number that corresponds to your choice above, or type 'exit' to exit: ")
    if envChoice == "exit":
        raise SystemExit(0)
    # Check if user input is 'int' and within the range of 1-3. If not, start the loop over
    try:
        envChoice = int(envChoice)
    except ValueError:
        print("\nPlease enter '1', '2', '3' or 'exit' only")
        time.sleep(1)
        print("\n")
        continue
    if envChoice not in [1,2,3]:
        print("\nPlease enter '1', '2', '3' or 'exit' only")
        time.sleep(1)
        print("\n")
        continue
    # User input is valid so set our environment variables accordingly, and break the loop
    elif envChoice == 1:
        environment = set_env_vars("ProdUS")
        break
    elif envChoice == 2:
        environment = set_env_vars("ProdEU")
        break
    elif envChoice == 3:
        environment = set_env_vars("Stage")
        break


# Obtain an auth/bearer token for use with subsequent API calls to TelQ
while True:
    print("\n")
    # If not entered custom appID/Keys in config section above, prompt user for this data, and set "coded_key" to True so we don't loop forever if a bad key was entered
    if appId == "youridhere":
        appId = input("Enter TelQ appId (4 or 5 Digits): ")
        coded_key = True
    if appKey == "yourkeyhere":
        appKey = getpass("Enter TelQ appKey (Long Secret String): ")
        coded_key = True

    print("\n")
    print("Obtaining Auth Token...")
    # Initialize "tokenRequest" because VSCode is mad if we don't
    tokenRequest = ""

    # Here we actually do the API call to telq
    try:
        tokenRequest = obtain_bearer_token(appId, appKey)
        bearer_token = tokenRequest['value']
    # Below code handles errors from telq like wrong key etc...
    # If the key was typed as input by the user instead of hard coded, we start the loop over. Otherwise exit.
    except:
        if coded_key is False:
            print("There was an error obtaining an auth token. Did you enter the correct appID and appKey?\n")
            print("Here is the response received from TelQ:\n")
            print(tokenRequest)
            print("\n")
            print("Please try again!\n")
            continue
        else:
            print("There was an error obtaining an auth token. Did you enter the correct appID and appKey in the script config?\n")
            print("Here is the response received from TelQ:\n")
            print(tokenRequest)
            print("\n")
            print("Since you've hard coded credentails, I am forced to exit. Please verify the data you've entered in the config section of the script.")
            raise SystemExit(1)
    else:
        print("Successfully Obtained Auth Token")
        print("\n")
        break

# Download every possible network/test point from TelQ
# Might want to add error handling here or inside the function above in the future
print("Downloading list of available test networks...\n")
networks = get_networks()
print("Updated list of networks successfully downloaded.\n")

# Next loop takes 2 letter country code from user and translates that using pycountry to try and match what's in TelQ
while True:
    while True:
        time.sleep(1)
        country_code = input("Enter two letter country code to test to (Ex 'US'), or type 'exit' to exit: ")
        if country_code.casefold() == "exit":
            raise SystemExit(0)
        if len(country_code) != 2:
            print("\nSorry, you must enter exactly 2 letters\n")
            continue
        elif contains_number(country_code) is True:
            print("\nSorry, you may enter only letters, not numbers\n")
            continue
        else:
            break
    country = set_country(country_code)

    # Make sure the code matches at least SOMETHING
    if country is False:
        print("\nNo country found with country code '" + country_code + "'")
        print("Please try again...\n")
        continue

    # One second delay keeps readability for the user
    time.sleep(1)
    print("\nIdentified country code '" + country_code + "' as '" + country.name + "'")
    print("\nSearching for networks using '" + country.name + "'\n")
    time.sleep(1)

    # Check our list of networks using what pycountry gave us for a match, using the "name" value from pycountry
    # Sometimes we get two names from pycountry, a "name" and an "official_name". Sometimes one matches TelQ but not the other,
    # like name = "United States" (does not match telq) but official_name = "United States of America" (matches telq).
    # Some countries work if we take the first word from official_name, like "Iran, the republic of"
    # The net effect of the below code block is that if there is an official_name, we will check name, then official_name, then the first word of name
    # Otherwise, we skip official_name and just check name then first_word.
    # Finally as a last ditch effort, we ask the user to manually enter what it shows in TelQ. Assuming they do this correctly, it should work.
    # The possible downside here is that if the 2 letter country code the user entered doesn't match the country, *** might throw a fit because it requires
    # That the phone number be formatted according to this country code. We don't have a great way to handle this currently.
    country_networks = get_country_networks(country.name)

    if hasattr(country, 'official_name'):
        # If no results using name, then check official_name
        if len(country_networks) == 0:
            print("No results found using '" + country.name + "'.\n")
            time.sleep(1)
            print("Trying a second search using '" + country.official_name + "'.\n")
            country_networks = get_country_networks(country.official_name)
        # Still no results. Some countries work if we take the first word from pycountry, like "Iran, the republic of"
        if len(country_networks) == 0:
            first_word = country.name
            first_word = str(first_word)
            first_word = first_word.split()[0]
            first_word = first_word.rstrip("!,. ")
            print("Third try, this time with just '" + first_word + "'")
            country_networks = get_country_networks(first_word)
            time.sleep(1)
        # Still nothing, try the last ditch effort
        if len(country_networks) == 0:
            print("Sorry, no results found using any available auto detected country name...\nPlease enter the full and complete name of the target country as it shows in the TelQ tool:\n")
            lastDitchName = input("Full country name to search for: ")
            country_networks = get_country_networks(lastDitchName)
        # Even manually entering failed... Start the loop over.
        if len(country_networks) == 0:
            print("Sorry friend, still no results found. Giving up... Your country seems to exist, but TelQ doesn't seem to have any networks there. Try another 2 letter country code.\n")
            continue
        else:
            break
    # This code only runs if there's no "official_name" but is otherwise the same as above
    else:
        if len(country_networks) == 0:
            first_word = country.name
            first_word = str(first_word)
            first_word = first_word.split()[0]
            first_word = first_word.rstrip("!,. ")
            print("Second try, this time with just '" + first_word + "'")
            country_networks = get_country_networks(first_word)
            time.sleep(1)
        if len(country_networks) == 0:
            print("Sorry, no results found using any available auto detected country name...\nPlease enter the full and complete name of the target country as it shows in the TelQ tool:\n")
            lastDitchName = input("Full country name to search for: ")
            country_networks = get_country_networks(lastDitchName)
        if len(country_networks) == 0:
            print("Sorry friend, still no results found. Giving up... Your country seems to exist, but TelQ doesn't seem to have any networks there. Try another 2 letter country code or CTRL + C to quit.\n")
            continue
        else:
            break


print("Done.\n")
clear_screen()
print("Available list of networks for " + country.name + ":")
show_networks(country_networks)

# At this point we are showing the list of all the networks/carriers we found to the user and here they will select which to choose.
while True:
    network = input("\nEnter the number corresponding to the network above that you wish to test to (Or type 'exit' to exit): ")
    if network == "exit":
        raise SystemExit(0)
    elif network.isnumeric() is not True:
        print("That's not a number. Try again!")
        continue
    elif int(network) == 0:
        print("Sorry, you must choose a number that corresponds to an option above.")
        continue
    else:
        network = int(network) -1
        try:
            testNetwork = country_networks[network]
        except IndexError:
            print("Sorry, you must choose a number that corresponds to an option above.")
            continue
        else:
            break


# User has chosen a target network. Now ask which test type to run
while True:
    clear_screen()
    print("\nWhich type of test would you like to run?")
    print("Please see the documentation for an explanation on what each of these do.")
    print("[1] Short")
    print("[2] Long")
    print("[3] 5 Part")
    print("[4] External URL w/ http")
    print("[5] External URL NO http")
    print("[6] Internal URL US")
    print("[7] Internal URL EU")
    print("[8] Internal URL US")
    print("[9] Internal URL EU w/ extention")
    print("[10] Special Character")
    print("[11] GSM")
    print("[12] Confirmation")
    print("[13] Polling")
    print("[14] Polling (international)")
    print("[15] Custom message - Enter a custom message to include in the message body (experimental)")
    print("[16] All Message Types - Send all message types [1-14] at once (experimental)")
    while True:
        test_type_input = input("\nEnter the number that corresponds to the test type you'd like to run, or 'exit' to exit: ")
        if test_type_input == "exit":
            raise SystemExit(0)
        elif test_type_input.isnumeric() is not True:
            print("Sorry, you must enter a number between 1 and 16, or 'exit'")
            continue
        elif int(test_type_input) > 16 or int(test_type_input) < 1:
            print("Sorry, you must enter a number between 1 and 16, or 'exit'")
            continue
        else:
            test_type_input = int(test_type_input)
            break
    if test_type_input == 1:
        test_type = "short"
        break
    elif test_type_input == 2:
        test_type = "long"
        break
    elif test_type_input == 3:
        test_type = "five_part"
        break
    elif test_type_input == 4:
        test_type = "outside_url_http"
        break
    elif test_type_input == 5:
        test_type = "outside_url_sans_http"
        break
    elif test_type_input == 6:
        test_type = "internal_url_us"
        break
    elif test_type_input == 7:
        test_type = "internal_url_eu"
        break
    elif test_type_input == 8:
        test_type = "internal_url_us_extention"
        break
    elif test_type_input == 9:
        test_type = "internal_url_eu_extention"
        break
    elif test_type_input == 10:
        test_type = "special_char"
        break
    elif test_type_input == 11:
        test_type = "gsm"
        break
    elif test_type_input == 12:
        test_type = "short_confirmation"
        break
    elif test_type_input == 13:
        test_type = "short_polling"
        break
    elif test_type_input == 14:
        test_type = "short_polling_international"
        break
    elif test_type_input == 15:
        # Custom input. Warn user not to include the "test" string and also do some checking to make sure it's not entered anyways just in case
        test_type = "custom"
        print("\n**Warning** TelQ has requested that we do not use the word 'test' in our message subject or body.")
        while True:
            globalCustomText = input("\nEnter your custom text to include in the test message: ")
            if "TEST" in globalCustomText.upper():
                print("\nSorry, you may not include the word 'test' in your custom message.")
                time.sleep(1)
                continue
            else:
                break
        break
    elif test_type_input == 16:
        # User wants to fire off every kind of test. Warn and then make sure.
        test_type = "all"
        print("\n**Warning!** You are about to send >>14<< tests at once!!")
        time.sleep(2)
        print("\nPlease Confirm that this is intentional by typing 'YES' below.")
        time.sleep(1)
        confirmTest = input("\nEnter 'YES' to continue: ")
        if confirmTest != "YES":
            print("\nSorry, you may only continue by typing 'YES' (in all caps). Starting over...")
            time.sleep(2)
            continue
        else:
            break
    else:
        print("\nYou have somehow entered an invalid option. Please try again (and consider reporting that you were able to do this)")
        continue

# End of user input. Do the thing.
clear_screen()
print("\nGot it... Kicking off the following test in the TelQ system:")
print("Target Country: " + country.name)
print("Target Network: " + testNetwork['providerName'])
print("Test Environment: " + environment['name'])
print("Test Type: " + test_type + "\n")
# Pause for readability.
time.sleep(2)

if test_type == "all": # If selected all test types, loop through them.
    typeList = ["short","long","five_part","outside_url_http","outside_url_sans_http","internal_url_us","internal_url_eu","internal_url_us_extention","internal_url_eu_extention","special_char","gsm","short_confirmation","short_polling","short_polling_international"]
    # Initialize empty lists to contain the test results
    notification_list = []
    contact_id_list = []
    testId_list = []
    test_id_text_list = []
    phone_number_list = []
    # Begin looping through each type of test, create the test in TelQ, send the SMS from ***, save results, continue.
    for t in typeList:
        print("Creating '" + t + "' type test in TelQ")
        test = create_test(bearer_token, testNetwork['mcc'], testNetwork['mnc'])
        id_num = str(test['id'])
        test_id_text = str(test['testIdText'])
        phone_number = str(test['phoneNumber'])

        print("Successfully created TelQ Test...")

        print("creating contact in ***...\n")
        contact_id = create_contact()
        print("Successfully created contact in ***.\n")

        print("Sending a '" + t + "' type Notification to the TelQ test number\n")
        notification_id = send_notification(t)

        #Collect notification stats
        notification_list.append(notification_id)
        contact_id_list.append(contact_id)
        testId_list.append(id_num)
        test_id_text_list.append(test_id_text)
        phone_number_list.append(phone_number)

        print("Notification successfully sent. Moving on.\n")

        # Delay keeps things from getting out of control
        time.sleep(1)
    time.sleep(2)
    print("\nDone. Here's some data for each test:")
    # Now show the data for each test
    notification_count = 1
    type_count = 0
    for n in notification_list:
        print("[" + str(notification_count) + "] " + typeList[type_count] + " | Notification ID: " + str(notification_list[type_count]) + " | Contact ID: " + str(contact_id_list[type_count]) + " | TelQ Test ID: " + testId_list[type_count] + " | ID Text: " + test_id_text_list[type_count] + " | Phone Number: " + phone_number_list[type_count])
        notification_count += 1
        type_count += 1
    print("\n*** Environment we sent the tests from: " + environment['name'])
    print("\nAll tests sent successfully...\n")
    time.sleep(2)
    print("\n\n")
    print(">>Please check the TelQ Tool for test results<<\n")
    time.sleep(2)
else: # If we only need to send one test, no loops needed.
    test = create_test(bearer_token, testNetwork['mcc'], testNetwork['mnc'])
    id_num = str(test['id'])
    test_id_text = str(test['testIdText'])
    phone_number = str(test['phoneNumber'])

    print("Successfully created TelQ Test...")

    print("creating contact in ***...\n")
    contact_id = create_contact()

    print("Sending a '" + test_type + "' type Notification to the TelQ test number\n")
    notification_id = send_notification(test_type)

    print("Notification successfully sent. Here's some stats for your enjoyment:")
    print("Notification ID: " + str(notification_id))
    print("Contact ID created: " + str(contact_id))
    print("*** Test Environment: " + environment['name'])
    print("TelQ Test ID: " + id_num)
    print("test_id_text: " + test_id_text)
    print("phoneNumber: " + phone_number)
    print("Country Code: " + country_code)
    time.sleep(2)
    print("\n")
    print(">> Please check the TelQ Tool for test results <<")
    print("https://app.telqtele.com/#/manual-testing")
    time.sleep(2)
