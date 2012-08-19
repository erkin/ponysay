mkdir -p quotes

for ponies in $(cat ponyquotes/ponies); do

    for pony in $(echo $ponies | sed -e 's/+/ /g'); do
	echo 'Generating quote files for '"$pony"

	for file in $(ls "ponyquotes/" | grep "$pony\\.*"); do

	    if [[ -f "ponyquotes/$file" ]]; then

		cp "ponyquotes/"$file "quotes/"$ponies'.'$(echo $file | cut -d '.' -f 2)
	    fi
	done
    done
done

