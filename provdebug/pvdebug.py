#!/usr/bin/env python

import textwrap
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import provdebug as pvd 

def run():
    parser = ArgumentParser(description="provdb starts a provenance-based time traveling debugging interface.",
    formatter_class=RawDescriptionHelpFormatter,
    epilog=textwrap.dedent('''\
        Once the interface has started, type help for more information.

        Otherwise, the interactive controls are as follows:
            - n or next: step forward in execution
            - b or back: step backward in execution
            - s or step: step into code block
            - o or out: step out of code block
            - i or info: get current script, line number, and code block
            - v or vars: prints all variables that exist at current location
            - q or quit: quit the debugger
        '''))
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Prov.Json file to analyze")

    args = parser.parse_args() 

    browser = pvd.ProvBrowser(args.file)
    
    print("Welcome to the Multilingual Provenance Debugger, type help for more information")

    while(True):
        userInput = input(">")

        if(userInput == "help"):
            helpText = textwrap.dedent('''\        
                The interactive controls are as follows:
                    - n or next: step forward in execution
                    - b or back: step backward in execution
                    - s or step: step into code block
                    - o or out: step out of code block
                    - i or info: get current script, line number, and code block
                    - v or vars: prints all variables that exist at current location
                    - q or quit: quit the debugger
                ''')
            print(helpText)
            continue
        elif(userInput == "n" or userInput == "next"):
            browser.nextNode()
        elif(userInput == "b" or userInput == "back"):
            browser.previousNode()
        elif(userInput == "s" or userInput == "step"):
            browser.stepIn()
        elif(userInput == "o" or userInput == "out"):
            browser.stepOut()
        elif(userInput == "v" or userInput == "vars"):
            print(browser.getVarsFromCurrentLocation())
            continue
        elif(userInput == "i" or userInput == "info"):
            print(browser.getCurrentNodeInfo())
            continue
        elif(userInput == "q" or userInput == "quit"):
            break

        print(browser.getCurrentNodeInfo())