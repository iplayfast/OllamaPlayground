# CreateNotes: Find Out About the Models in Your Ollama System

**Introduction**

This project interrogates all models in your system and evaluates how they respond to a series of questions.

There are two Python modules: `CreateNotes.py` for querying all the models in your system, and `ViewResults.py` for displaying the results.

`CreateNotes.py` generates a file called `results.json`.

`ViewResults.py` uses `results.json` to display a graph and heat map, followed by a webpage showing the results in graph form. This webpage also provides hints about the questions, answers, and timing of the results.

`CreateNotes.py` retrieves a list of Ollama models currently on your system. For each model, it queries a range of questions and categories. The module expects the Mistral model to be installed on your system, as Mistral critiques the answers given by other models.

Questions are stored in `questions.json` in the following format:

```
[
    {
        "question": "hello",
        "answer": "hello",
        "special_instructions": ""
    },
    {
        "question": "what areas of knowledge do you have?",
        "answer": "",
        "special_instructions": ""
    },
    {
        "question": "what is the answer to 10 + 2 * 5 - 1",
        "answer": "the correct answer is 19",
        "special_instructions": "check that the answer is 19"
    },
    {
        "question": "Create a python program to capture a wave file when sound is happening, when done print the name of the wave file",
        "answer": "",
        "special_instructions": "evaluate code for errors"
    },
...
```

If an answer is provided, it is checked for correctness against the model's response, then 'You believe the best answer is ...' is added to the critique prompt.

If special instructions are provided, they are included in the critique prompt.

Each answer is critiqued by Mistral in regards to categories such as Humor, Sincerity, Logic, and Code Correctness, and given a rating from 0 to 100, with 100 being the best. A category that does not match the answer at all is given a 0 rating. Each rating is accompanied by an explanation and the time taken to generate the answer.

**Getting Started**

To run, set up a new Conda environment (e.g., `conda create -n notes python==3.11`):

bashCopy code

`conda create -n modelnotes python==3.11 conda activate modelnotes pip install -r requirements.txt python CreateNotes.py`

While `CreateNotes.py` is running, the `results.json` can be viewed:

bashCopy code

`python ViewResults.py`

New questions can be added to the `questions.json` file as desired.
