# INSTALLATION ON LINUX
Copy mint.zip to a convenient location and extract.
Open a command line terminal.
Run the following commands in this order (enter y to continue if prompted during installation procedures):
	sudo apt-get install python3
	sudo apt-get install python3-pip
	pip3 install SpeechRecognition
	sudo apt-get install swig
	sudo apt-get install build-essential
	sudo apt-get install libpulse-dev
	pip3 install pocketsphinx
	pip3 install nltk
	pip3 install pydub
	pip3 install tensorflow
	sudo apt-get install ffmpeg
In a web browser, go to:
	https://github.com/cmusphinx/g2p-seq2seq/archive/master.zip
This should download a file 'g2p-seq2seq-master.zip', extract this to create
	the folder g2p-seq2seq-master.  Close the current terminal and open a new
	one in g2p-seq2seq-master.  Run the following command:
		sudo python3 setup.py install
Run the following command:
	python3
This will open a python shell.  From there, run:
	import nltk
	nltk.download('wordnet')
	nltk.download('omw')
	quit()

# RUNNING THE PROGRAM
To run the program, open a command line in the folder that the mint folder is in and run:
	python3 mint/batch_mint.py <folder of audio files> <language> --default
So, for example, if the folder which contains the audio files is called 'audio_files' and the language is English:
	python3 mint/batch_mint.py audio_files English --default
This will create a text file transcript for each audio file.
	
The language options are English, Spanish, and Chinese.  For help:
	python3 mint/batch_mint.py -h
To transcribe a single file
	python3 mint/mint_sr.py <audio file> <language> --default
	
# TROUBLESHOOTING / CUSTOMIZATION
Some files have very poor recognition, and the transcription is mostly UNKNOWNs.  Other files have accurate transcriptions.
	- If the file is significantly quieter or louder than expected, then a custom silence threshold may be necessary.  Use the option --silence_thresh <new_threshold>.
		This option defaults to -36.  Values between -60 and -30 are appropriate for most files.  Use more negative numbers for quieter files.
	- Use the following command to test how the new parameters are splitting the audio file:
			python3 mint/audio_split.py <audio_file> --silence_thresh <new_threshold>
		Audio segments that only contain silence or background noise can be handled by the program, but each word needs to be alone in a single audio segment for proper transcription.
	- If varying the silence threshold is ineffective, try varying the --min_silence_len and --keep_silence parameters.  (This should not be necessary in almost all cases.)
To specify a non-default wordlist:
	- Use the option --wordlist <wordlist_name> with either batch_mint.py or mint_sr.py
	- Use the option --unknown to specify what to use for "don't know"
	- Note: if the new wordlist contains charaacters that are not in the pre-existing g2p model (unlikely for English and Spanish, likely for Chinese), the following error will occur:
		Decoder_set_fsg returned -1
		An invalid word was detected in the wordlist.
	In this case, use the --cache option to create a dictionary and add the missing word and its pronunciation.  Then, use the --dictionary option to specify the custom dictionary.
If the program is running too slowly:
	- The Chinese model runs extremely slowly.  (On the order of hours for a 3-5 minute audio file.)  This problem is currently being investigated.
	- If you are using a custom wordlist, the program must recalculate the dictionary and grammar each time.  Use the --cache option to save the dictionary and grammar, and use the --dictionary and --grammar options to specify them in future runs.
Other errors:
	Try the --verbose option for more details.
	
# OTHER NOTES
3RD-PARTY-LICENSES.txt contains the licenses of libraries used directly by this program.