# CPS v2.1 (Command Prompt Saver)

## Work in progress

**TODO** list:
- Add variable manipulation.
- Profiles.

## Why?
The last version of CPS ([See here](https://github.com/POLA-LCS/CPS))  
it's OK, but the main problem is it's scalability. I am open to future implementations
and the way CPS v1 is writed it is a little too bad.


## New implementations
- **Multi-line operations**:  
The line: `macro + 'echo Hello' 'echo Goodbye'`  
executes `macro + 'echo Hello'` and `macro + 'echo Goodbye'`.

- **Disable output messages**:  
Each time you type a instruction there's an output message. Output message of:  
`macro = 'del C:\Windows\system32'` is `[CPS] Created: macro`  
Starting the line with "." makes the output messages to disable for that instruction.  
`. macro = 'echo The output message must not display'`

- **Console interpreter**:  
The CPS v2.1 has a console interpreter, so you can setup your CPS testing.

- **Indexation**
Can acess macro code lines by index.