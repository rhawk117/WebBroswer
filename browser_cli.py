import webbrowser as web
import sys
import requests as req
import logging as log
import json
import os
import traceback
import re as regex 



@staticmethod
def GetInput(prompt: str, choices : list) -> str: # recursive input validation
    log.info('Attempting to recieve input from user..')
    option ='\nOptions -> ' + ' , '.join(choices)
    user_input = input('[?] ' + prompt + option + '\nEnter: ')
    if user_input not in choices: 
        log.warning('Invalid user input detected, making recursive call to function.')
        print('\n[*] User Input Invalid [*]\n')
        return GetInput(prompt, choices) # recursive call 
    else: 
        return user_input # user input passes input validation

# --divider--
@staticmethod
def OpenBrowser(url: str) -> bool:
    '''
    Opens the users windows default browser
    and returns 1 for successful URLs opened 
    or 0 for failed GET requests 
    '''
    try:
        log.info(f'Sending GET Request to -> ({url})')
        response = req.get(url)
        log.info('Raising get request response for status..')
        response.raise_for_status() 
        if response.status_code == 200: # Check if the URL is reachable before browser query 
            log.info('GET Request successful')
            web.open(url)
            log.info('Returned 1, request was successful')
            return True # will use later to track no. of successful requests
        else:
            log.warning(f'GET Request Failed (Status Code Not 200) and returned a {response.status_code} status code')
            return False
    except req.exceptions.RequestException as error:
        log.critical(f'HTTP Error occurred, failed to reach URL: {error}')
        return False
    except Exception as error:
        log.critical(f'An unexpected error occurred: {error}')
        return False

# --divider--
@staticmethod
def AnalyzeLib(json_lib: dict, isAll: bool) -> None: # parses dictionary parameter for URLS and keys
    # check for the user mode 
    successes = 0
    if not isAll: # if user picked select mode 
        log.info('User picked select mode, starting select mode')
        running = True # while loop flag
        msg = 'Type in the name of the Website you\'d like to open, type "esc" any time to end the loop\n[!] WARNING Input is case sensitive'
         # iterables used for logging purposes
        json_keys = list(json_lib.keys())  # list of keys from .json or dict
        json_keys.append('esc')
        while running:
            key = GetInput(msg, json_keys) # recieve key from user
            if key == 'esc':
                log.info('User entered -> "esc" -> Closing program')
                sys.exit()
            else:
                tmp = json_lib[key]
                try:
                    attempt = OpenBrowser(json_lib[key]) # adds one 1 each time request was succesful
                    log.info('GET Request sent')
                    if attempt:
                        log.info('URL (' + tmp + ') was successfully open in the browser')
                        successes += 1
                    else:
                        log.info('The URL (' + tmp + ')failed to open...')
                except Exception as error:
                    log.critical('[!] Request Failed ')
                    raise Exception('An Exception occured')
    else:
        log.info('User picked all mode, trying to reach all URLs in either the dictionary or .JSON File.')
        for url in list(json_lib.values()):
            try:
                log.info(f'Attempting to reach -> {url} ')
                attempt = OpenBrowser(url)
                if attempt:
                    successes += 1
                    log.info('URL was successfully open in the browser')
                else:
                    log.warning('URL could not be opened and method returned false')
            except Exception as error:
                raise Exception('An error occured while proccessing the dictionary to URLs')
        log.info('Number of successful URL opens in browser -> ' + str(successes))
        input('[*] All of the URLs in the data set have been attempted to be opened [*] \nPress Enter to quit: ')
        sys.exit()

# --divider--
@staticmethod
def LoadPreset(json_file:str) -> dict:
    '''
    if the user uses a .json preset, we need to convert it to a dictionary
    in order to extract the URL values 
    '''
    path = 'presets\\' + json_file
    try:
        log.info(f'Trying to open the JSON File -> ({json_file})', )
        with open(file=path , mode='r') as json_lib:
            preset = json.load(json_lib)
        if not preset: # checks if dictionary loaded was empty
            log.critical('The JSON preset was empty! Terminating program')
            print('The JSON file you tried to use was empty, cannot process data.')
            sys.exit()
        return preset
    except IOError as error:
        log.critical(f'IO Exception occured -> {error}')
        print('[!] An IO Exception was raised likely due to an error with the programs home directory file structure')
        traceback.print_exc()
        sys.exit()
    except Exception as error:
        log.critical(f'An Exception occured -> {error}\n\n')
        print('[! An unknown exception was raised while trying to load a JSON preset')
        traceback.print_exc()
        sys.exit()

# --divider--
@staticmethod
def DetermineMode(mode:str) -> bool:
    # simple boolean to determine the users mode
    return (mode == 'all')

# --divider--
@staticmethod
def CheckFileName(file_name:str) -> bool:
    '''
    a series of if statements that determines whether or not a file name is invalid
    this method only allows filenames that are less than 25 chars.
    '''
    if file_name == ' ':
        log.info('An empty string was given as a parameter likely due to input validation process starting')
        return False
    prefix = '[*] Invalid File Name [*]\n'
    if not regex.match(f"^[A-Za-z0-9_.-]*$", file_name):
        print(prefix + 'Cannot create a file with invalid characters')
        return False

    # Check for valid extension
    if not file_name.endswith('.json'):
        print(prefix +'Files must end with the .json extension')
        return False

    # Check for maximum length
    if len(file_name) > 25:
        print(prefix + 'File names should be less than 25 characters')
        return False

    # Check for reserved names
    reserved_names = ["con", "prn", "nul"]
    if file_name.lower() in reserved_names:
        print(prefix + 'Files names cannot be reserved')
        return False
    
    # Check in Presets folder if file with same name exists
    if os.path.isfile('presets\\' + file_name):
        print(prefix + 'A file with the same name already exist!')
        return False 
    
    return True # file name passes all checks, return true 

# --divider--
@staticmethod
def Header() -> None:
    print('**Automated Browser URL Opener***')
    print('***Developed by rhawk117***')
    print('GitHub: https://github.com/rhawk117')

# --divider
@staticmethod
def main() -> None:
    os.chdir(os.path.dirname(sys.argv[0]))
    app_logs = 'logs\\' # path to the 'logs directory'
    app_logs += 'app_data.log' # put the name of the log file here
    log.basicConfig(level=log.DEBUG, format=' %(asctime)s – %(levelname)s -%(message)s', filename=app_logs)
    if not os.path.exists('logs'):
        print('[*] No logging directory was found making one..')
        os.mkdir('logs')
    if not os.path.exists('presets'):
        print('[*] No Preset directory was found making one...')
        os.mkdir('presets')
    try:
        with open(file=app_logs, mode='w'):
            pass # overwrites previous log file or creates, modify if you'd like to save all program logs
    except Exception:
        log.warning('**Failed to overwrite previous program instance log**')
        print('Failed to overwrite previous program instance log, logs will be appended to the previous')

    '''
    NOTE:
    change the dictionary below before runtime to the desired key and values 
    for personal use if you intend to use dict mode or want to easily create a custom json preset.
    the key should be something descriptive and easy to type, the value should be the URL of the 
    resource you want to open.
    '''

    data_set = {   
       "D2L" :"https://lms.augusta.edu/d2l/home",
       "Outlook" :"https://outlook.office365.com/mail/",
       "YouTube" :"https://www.youtube.com/",
        "ChatGPT":"https://chat.openai.com/",
        "Website":"https://rhawk117.github.io/ryan_web/views/index.html"
    }

    Header()
    msg = 'Are you loading a .JSON File Preset or using the programs dictionary'
    choice = GetInput(prompt=msg, choices=['json', 'dict'])
    prefix = '.JSON file'
    msg = f'Would you like to open all of the URLs in the {prefix} or select them individually?'
    if choice == 'json': # for presets
        print('[*] Searching for presets in the preset directory')
        for _, __, files in os.walk("presets"):
            choices = [file for file in files if file.endswith('.json')] # find all json files in preset directory

        if not choices: # no json files were found 
            log.critical('The user tried to use .JSON mode with no .json files in the presets folder. Aborting program')
            print('[!] No .JSON files were found in the presets, directory\n[!] Cannot support .JSON compatibility, try again')
            return

        file_n = GetInput(f'Pick one of the following {prefix} found in your preset directory ', choices)
        preset = LoadPreset(file_n) # save .json ile data to a dictionary to work w/ the keys and values
        mode = GetInput(msg, choices=['all', 'select'])
        toggle = DetermineMode(mode)
        AnalyzeLib(preset, toggle)  # perform programs core logic

    else: # for dictionaries / hard coded values 
        if not data_set: # the prorgrams dictionary was empty
            log.critical('[!] User tried to use an empty dictionary in dictionary mode! Aborting program')
            print('[!] The programs dictionary you tried to use was empty, cannot use an empty data set. Please try again.')
            return 
        
        msg = 'Would you like to save this dictionary as a preset to use again?'
        prefix = 'dictionary' 
        log.info('Using hard-coded dictionary value...')
        choice = GetInput(msg, choices=['y','n'])
        if choice == 'y': # if user wants to create a JSON preset from the programs dictionary
            log.info('User picked yes, attempting to save the built-in dictionary to a JSON file')
            preset_name = ' '
            msg = '[?] What is the desired name for the JSON preset?\n[!] MUST provide a valid file name ending with .json extension [!]\n[*] Enter:'
            while not CheckFileName(preset_name):
                preset_name = input(msg)
            print(f'[*] Attempting to creating a JSON File titled "{preset_name}" that matches the programs dictionary key-value pairs..')
            try:
                with open(file='presets\\' + preset_name, mode='w') as file:
                    json.dump(data_set, file)
            except Exception:
                log.warning('Could not create a JSON file from programs dictionary..')
                raise Exception('Failed to create the .JSON file likely due to an invalid dictionary...')
        else:
            log.info('User opted to NOT save the dictionary as a preset')
            print('[*] Not saving dictionary as preset')
        msg = f'Would you like to open all of the URLs in the {prefix} or select them individually?'
        mode = GetInput(msg, ['all', 'select'])
        toggle = DetermineMode(mode)
        if toggle:
            log.info('User picked all mode')
        else:
            log.info('User picked select mode')

        AnalyzeLib(data_set, toggle) # perform programs core logic 
    
if __name__ == '__main__':
    main() # call to main to start program
    sys.exit() # for clean exits 