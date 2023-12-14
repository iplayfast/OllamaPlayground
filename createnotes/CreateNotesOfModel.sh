#!/bin/bash
if [ -z "$1" ]; then
  echo "Error: Parameter $1 is not set."
  exit 1
fi

echo "-------------------- $1 --------------------" 
echo "## $1 " >> notes.md
start=$(date +%s)
echo "Loading time" >> notes.md
cat bye.txt | ollama run $1 
end=$(date +%s)
elapsed=$((end-start))
echo "### Elapsed Time: $elapsed seconds" >> notes.md
questionNum=0
for file in q*txt; do
	questionstart=$(date +%s)
	(( questionNum++ ))
	echo "### Question " $questionNum >> notes.md
	cat $file >> notes.md
	echo "### Answer " $questionNum >> notes.md
	echo '``````' >> notes.md
#	cat $file | ollama run $1 >> notes.md
	timeout 500s sh -c 'cat $file | ollama run $1' >> notes.md
	echo '``````' >> notes.md
	end=$(date +%s)
	elapsed=$((end-questionstart))
	echo "### Elapsed Time: $elapsed seconds" >> notes.md
done
cat bye.txt | ollama run $1 >> notes.md
end=$(date +%s)
elapsed=$((end-start))
echo "Elapsed Time: $elapsed seconds" >> notes.md

