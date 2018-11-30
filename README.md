# Multilingual Provenance Debugger

A langugage - agnostic version of [provDebugR.](https://github.com/ProvTools/provDebugR/wiki)

This debugger uses provenance information to reconstruct past-executions and allow users to explore them at their will. This tool will work with any program so long as it has provenance collected that follows [this format](https://github.com/End-to-end-provenance/ExtendedProvJson).

## Current Features

**Lineage:**
A function that finds connections that variables have with each other and will return a variable's forward or backward connections.

**Error Tracing:** 
Error trace can be used to trace the lineage of an error message (if an error exists), returning the lines that led up to a script's stopping. It can also query Stack Overflow for similar errors and provide the user the option to open one of the similar questions in the browser.

**Type Checking:**
A function that can be used to examine how or whether or not a variable's type changes throughout the execution of a script.

**By Line Information:**
A function that can be used to examine the variables that exist in a script on a line-by-line basis. This function can be used in two ways, can either display all the variables and their values on a single line, or all variables that existed in the program's environment at a certain line number.

## Future Features

**Command-Line Debugging:**
This will function similarly to standard command-line debuggers. A user will be able to step through a past execution as if it was currently being debugged. However, this will also have the added benefit of letting the user step backwards or forwards. 
