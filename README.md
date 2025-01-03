# CPS v2.3 (Command Prompt Saver)

## Coming soon
- Variable manipulation.
- Profiles.

## Why?
The last version of CPS ([See here](https://github.com/POLA-LCS/CPS)) it's OK, but the main problem was it's scalability.  
I am open to future implementations and the way CPS v1 was coded it's a little too _bad_.

## New implementations
- **Console REPL:**  
The CPS v2 has a **Read-Eval-Print-Loop**, so you can setup your **CPS** easily.  
Try it by typing `cps.py --repl`

- **Indexation:**  
`cps macro 0 = 'echo Hello'` set the first instruction of `macro` (if exists) to `echo Hello`.  
`cps macro 0 + ', World!'` appends `, World!` to the first instruction of `macro`.

- **Disable output messages**:  
Each time you type an instruction there's an output message. Output message of:  
`cps goodbye = 'rmdir C:\Windows\system32'` is `[CPS] Created: goodbye`  
Starting the line with "." makes the output message disabled for that instruction.  
`cps . message = 'echo The output message must not display'`

- **Parameters usage**:
Macros can have parameters, this paramters need a default value.  
Creating a parameter for the macro is this easy:  
`cps speak !! name 'Pola'` This sets the parameter `name` to a default value of `Pola` 

Now let's make it useful.  
`cps speak = 'echo !!name is speaking...'` the `!!` is the parameter template, this will be replaced with the value of the parameter when executing the macro.  
`cps speak` runs and displays this message `Pola is speaking...` due to the default value of `name` parameter.  
`cps speak ! Jonh` displays `Jonh is speaking...`.  
extra arguments as in `cps speak ! Jonh Maria Dave` do not causes a problem.  

- **Multi-line operations**:
If you want to do multiple operations on a single macro you can try using the multi-line "operator".  
Using a comma after a macro name and before each operation runs it using the macro name as the first argument of cps.  
example: `cps new_macro , = 'cls' , + 'echo Hello!'` this literally runs as:  
`cps new_macro = 'cls'`  
`cps new_macro + 'echo Hello!'`