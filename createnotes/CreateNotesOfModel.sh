#!/bin/bash

if [ -z "$1" ]; then
  echo "Error: Parameter $1 is not set."
  exit 1
fi

model_id=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

echo "<div class='model-section'>" >> notes.html
echo "<button class='collapsible'>$1</button>" >> notes.html
echo "<div class='content'>" >> notes.html
start=$(date +%s)
cat bye.txt | ollama run $1 
end=$(date +%s)
elapsed=$((end-start))
echo "<p><strong>Elapsed Loading Time:</strong> $elapsed seconds</p>" >> notes.html

questionNum=0
for file in q*txt; do
    questionstart=$(date +%s)
    (( questionNum++ ))
    echo "<h4>Question $questionNum</h4>" >> notes.html
    echo "<pre>" >> notes.html
    cat $file >> notes.html
    echo "</pre>" >> notes.html
    echo "<h4>Answer $questionNum</h4>" >> notes.html
    echo "<pre>" >> notes.html
    timeout 500s sh -c "cat $file | ollama run $1" >> notes.html
    echo "</pre>" >> notes.html
    end=$(date +%s)
    elapsed=$((end-questionstart))
    echo "<p><strong>Elapsed Time:</strong> $elapsed seconds</p>" >> notes.html
done
    end=$(date +%s)
    elapsed=$((end-start))
    echo "<p><strong>Total elapsed Time:</strong> $elapsed seconds</p>" >> notes.html

echo "</div>" >> notes.html
echo "</div>" >> notes.html

