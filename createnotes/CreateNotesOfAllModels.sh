#!/bin/bash
echo "# The following are question and responses to all models contained on my system." > notes.md
echo $(date ) >> notes.md
echo "## Contents" >> notes.md
for item in $(ollama list | awk '{print $1}'); do
	if [ "$item" == "NAME" ]; then
		continue
	fi
	echo "- [" "$item" "](#$item)" >> notes.md
done

echo "The image used in all the following tests is ![](./classic.jpg)" >> notes.md
for item in $(ollama list | awk '{print $1}'); do
	if [ "$item" == "NAME" ]; then
		continue
	fi
    # This will update a model's question and answers
	./CreateNotesOfModel.sh "$item"
	echo "- [Contents](#Contents)" >> notes.md
    #break
done


