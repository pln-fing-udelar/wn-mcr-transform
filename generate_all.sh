#!/usr/bin/env bash

echoerr() { echo "$@" 1>&2; }

if [ "$#" -lt 2 -o "$#" -gt 3 ]; then
	echoerr "Incorrect number of parameters. Syntax should be:"
	echoerr "    $ $0 root_mcr root_eng [foreign_glosses_path]"
else
	ROOT_MCR=${1%%/}
	ROOT_ENG=${2%%/}
	ROOT_RESULT=aux
	FOREIGN_GLOSSES_PATH=${3%%/}
	mkdir $ROOT_RESULT
	if [ ! -d $ROOT_RESULT -o "$(ls -A $ROOT_RESULT)" ]; then
	    echoerr "\"$ROOT_RESULT\" directory does not exists or is not empty"
	else
		for LANG in `find $ROOT_MCR -iregex '.*WN' -printf '%f ' | sed -e "s/\(\w\)WN/\1/g"`; do
			echo "-------------------"
			echo "Processing $LANG..."
			echo "-------------------"
			TAR_FILE=wordnet_$LANG.tar
			LZMA_FILE=$TAR_FILE.lzma
			tar -xf $LZMA_FILE -C $ROOT_RESULT
			rm $LZMA_FILE
			./transform.py "$ROOT_MCR" "$ROOT_ENG" "$LANG" "$ROOT_RESULT" "$FOREIGN_GLOSSES_PATH"
			tar -cf $TAR_FILE -C $ROOT_RESULT .
			rm $ROOT_RESULT/*
			echo "Compressing..."
			lzma -9 $TAR_FILE
		done
		echo "Done"
	fi
	rmdir $ROOT_RESULT
fi
