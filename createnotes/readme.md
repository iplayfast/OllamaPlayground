# CreateNotes Find about the models in your Ollama system

This directory contains two shell scripts. 

The first one finds the list of ollama models, and for each one calls the second script.

The second script runs the model through a series of questions and finds the time for each question. The questions are any text files that start with q. 

     For example q3whatlanguage.txt contains the following text:

        **can you create code and if so what are your best languages.**

The notes are collected in notes.html (markdown couldn't hide things and the notes get lengthy) You can see a preview here [GitHub &amp; BitBucket HTML Preview](https://htmlpreview.github.io/?https://github.com/iplayfast/OllamaPlayground/blob/main/createnotes/notes.html)



On a linux system this can be run from the command line 

```
./CreateNotesOfAllModels.sh
```

and then you can browse to your local file system and watch your notes.html be created as the questions are answered.

New questions can be added as much as you like. The only stipulation is the filename  starts with 'q' for question. They are answered in alphabetical order.


