#!/usr/bin/env python

from argparse import ArgumentParser
import provdebug as pvd 

def run():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Prov.Json file to analyze")

    args = parser.parse_args() 

    browser = pvd.ProvBrowser(args.file)
    
    print("Welcome to the Multilingual Provenance Debugger, type help for more information")

    while(True):
        userInput = input(">")

        if(userInput == "help"):
            #TODO Expand this info
            print("This is a time-traveling language agnostic debugger. TODO for the developer, expand this info!")
            continue
        elif(userInput == "n" or userInput == "next"):
            browser.nextNode()
        elif(userInput == "b" or userInput == "back"):
            browser.previousNode()
        elif(userInput == "s" or userInput == "step"):
            browser.stepIn()
        elif(userInput == "o" or userInput == "out"):
            browser.stepOut()
        elif(userInput == "i" or userInput == "info"):
            print(browser.getCurrentNodeInfo())
            continue
        elif(userInput == "quit"):
            break

        print(browser.getCurrentNodeInfo())