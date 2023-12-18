#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: Parameter \$1 is not set."
    exit 1
fi

model_id=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')

start=$(date +%s)
cat bye.txt | ollama run $1 
end=$(date +%s)
elapsed=$((end-start))
echo "<tr><td colspan='3'><h3>" >> table.html
echo $1 >> table.html
echo "</h3></td><td>Loading Time:$elapsed seconds</td></tr>" >> table.html

questionNum=0
for file in q*txt; do
    echo "<tr>" >> table.html
    questionstart=$(date +%s)
    (( questionNum++ ))
    echo "<td>$questionNum</td>" >> table.html
    echo "<td>" >> table.html
    cat $file >> table.html
    echo "<td>" >> table.html
    timeout 500s sh -c "cat $file | ollama run $1" > temp.html
    
    # Use awk to process ``` pairs with flag initialized
    awk 'BEGIN { flag=0 } 
         /```/ { 
             if (flag == 0) {
                 sub(/```/, "<pre>```"); 
                 flag=1;
             } else {
                 sub(/```/, "```</pre>"); 
                 flag=0;
             }
         } 
         { print }' temp.html > temp2.html

    cat temp2.html >> table.html 
    rm temp.html temp2.html

    echo "</td>" >> table.html
    end=$(date +%s)
    elapsed=$((end-questionstart))
    echo "<td>Time:$elapsed seconds</td>" >> table.html
    echo "</tr>" >> table.html
done
end=$(date +%s)
elapsed=$((end-start))
echo "<tr><td>" >> table.html
echo $1 >> table.html
echo "</td><td></td><td></td><td>Loading Time:$elapsed seconds</td></tr>" >> table.html

