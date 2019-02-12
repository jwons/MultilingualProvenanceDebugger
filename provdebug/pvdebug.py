#!/usr/bin/env python

from argparse import ArgumentParser
import provdebug as pvd 

def run():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="file", required=True,
                        help="Prov.Json file to analyze")

    args = parser.parse_args() 

    p_debugger = pvd.ProvDebug(args.file)
    
    print(p_debugger.typeCheck("foo"))