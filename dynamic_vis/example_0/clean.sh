file_pattern=( -name '*.dot' -o -name '*.yaml' -o -name '*.data' -o -name '*.ll' -o -name '*.json') 
find . -maxdepth 1 -type f \( "${file_pattern[@]}" \) -exec rm {} \;
rm -r work