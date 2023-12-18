#!/bin/bash

echo "<html><head><title>Model Notes</title>" > table.html
echo "<style>table,th,td { border: 1px solid black;
border-collapse: collapse;
}
</style>" >> table.html
echo "</head>" >> table.html
echo "<h1>The following are question and responses to all models contained on my system.</h1>" >> table.html
echo "<p>$(date)</p>" >> table.html
echo "<p>On the image recognition question the image is</p> <img src='./classic.jpg' >.<h2>Click below to view results</h2>" >> table.html

echo "</ul><hr>" >> table.html
echo "<table style='max-width:80%'><tr><th>Model</th><th>Query</th><th style='width:70% max-width:400px'>Response</th></tr>" >> table.html


for item in $(ollama list | awk '{print $1}'); do
    if [ "$item" == "NAME" ]; then
        continue
    fi
    echo "Working on " "$item"
    ./CreateTableOfModel.sh "$item"
done

echo "</table></body></html>" >> table.html

