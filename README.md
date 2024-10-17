# CPS v2.1 (Command Prompt Saver)

## Coming soon
- Variable manipulation.
- Profiles.

## Why?
The last version of CPS ([See here](https://github.com/POLA-LCS/CPS)) it's OK, but the main problem was it's scalability.  
I am open to future implementations and the way CPS v1 was coded it's a little too _bad_.

## New implementations
- **Console REPL**:  
The CPS v2 has a Read-Eval-Print-Loop, so you can setup your CPS easily.  
Try it by typing `cps.py --repl`

- **Indexation**
NOW you can modify your macro code lines by index :O

- **Multi-line operations**:  
The line: `macro + 'echo Hello' 'echo Goodbye'`  
executes `macro + 'echo Hello'` and `macro + 'echo Goodbye'`.

- **Disable output messages**:  
Each time you type an instruction there's an output message. Output message of:  
`goodbye = 'rmdir C:\Windows\system32'` is `[CPS] Created: goodbye`  
  
Starting the line with "." makes the output messages to disable for that instruction.  
`. message = 'echo The output message must not display'`
