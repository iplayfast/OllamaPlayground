#!/bin/bash
echo "<html><head><title>Model Notes</title>" > notes.html
echo "<style>.collapsible {background-color: #777; color: white; cursor: pointer; padding: 18px; width: 100%; border: none; text-align: left; outline: none; font-size: 15px;}.active, .collapsible:hover {background-color: #555;}.content {padding: 0 18px; display: none; overflow: hidden; background-color: #f1f1f1;}</style>" >> notes.html
echo "<script>function setupCollapsible() {var coll = document.getElementsByClassName('collapsible');var i;for (i = 0; i < coll.length; i++) {coll[i].addEventListener('click', function() {this.classList.toggle('active');var content = this.nextElementSibling;if
(content.style.display === 'block') {content.style.display = 'none';} else {content.style.display = 'block';}});}}</script>" >> notes.html
echo "</head><body onload='setupCollapsible()'>" >> notes.html
echo "<h1>The following are question and responses to all models contained on my system.</h1>" >> notes.html
echo "<p>$(date)</p>" >> notes.html
echo "<p>On the image recognition question the image is</p> <img src='./classic.jpg' >.<h2>Click below to view results</h2>" >> notes.html
#echo "<ul>" >> notes.html
#
#for item in $(ollama list | awk '{print $1}'); do
#    if [ "$item" == "NAME" ]; then
#        continue
#    fi
    
#    if [ "$item" == "MrT:latest" ]; then
#	    break;
#    fi
#    anchor=$(echo "$item" | tr '[:upper:]' '[:lower:]' | sed 's/ /-/g')
#    echo "<li><a href=\"#${anchor}\">$item</a></li>" >> notes.html
#done

echo "</ul><hr>" >> notes.html

for item in $(ollama list | awk '{print $1}'); do
    if [ "$item" == "NAME" ]; then
        continue
    fi
#    if [ "$item" == "MrT:latest" ]; then
#	    break;
#    fi
	echo "Working on " "$item"
    ./CreateNotesOfModel.sh "$item"
done

echo "</body></html>" >> notes.html

