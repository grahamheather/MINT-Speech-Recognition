import os
import sys
from shutil import rmtree
import argparse

from read_wordlist import readWordlist
from wordnet_nltk_interface import relatedFromWordlist
from mint_grammar import createMintGrammar
from create_dictionary import createDictionary
from audio_split import AudioSettingsContainer
from mint_sr import transcribeMINT

if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Create a transcription of a MINT task audio file.")
	parser.add_argument('audio_directory', help='the directory of audio files to transcribe')
	parser.add_argument('language', help='the language the speech is in', choices=['English', 'Spanish', 'Chinese'])
	parser.add_argument('-d', '--default', action='store_true', help='use the default wordlist for this language')
	parser.add_argument('--unknown', help='default possibility for all objects')
	parser.add_argument('--min_silence_len', help='minimum length of silence for audio splitting', default=400)
	parser.add_argument('--silence_thresh', help='threshold of silence for audio splitting', default=-36)
	parser.add_argument('--keep_silence', help='milliseconds of presumed silence to keep on either end of split audio file', default=400)
	parser.add_argument('--wordlist', help='a file containing the words, multiple possibilities on a single line separated by commas, each new object on a new line (this or default must be set)')
	parser.add_argument('--dictionary', help='specify an already created dictionary')
	parser.add_argument('--grammar',  help='specify an already created grammar')
	parser.add_argument('-c', '--cache', action='store_true', help='save dictionary and grammar for reuse')
	parser.add_argument('-v', '--verbose', action='store_true', help='print all Sphinx output')
	args = parser.parse_args()

	if not args.default and not args.wordlist:
		sys.exit("Please specify either a wordlist or indicate --default to use the default wordlist.")

	if not args.unknown:
		if args.language == "English":
			unknown = "don't know"
		if args.language == "Spanish":
			unknown = "no sé"
		if args.language == "Chinese":
			unknown = "不知道"
	else:
		unknown = args.unknown

	# WORDLIST
	if args.default:
		if args.language == "English":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "englishWordlist.txt")
		if args.language == "Spanish":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "spanishWordlist.txt")
		if args.language == "Chinese":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "chineseWordlist.txt")
	else:
		wordlist = os.path.join(os.getcwd(), args.list)
	# read wordlist
	wordlist = readWordlist(wordlist)
	if not isinstance(wordlist, list):
		print("Error reading wordlist.")
		sys.exit(wordlist)
	# find related words
	source_hierarchy = ['base', 'synonym', 'hypernym']
	hierarchy_wordlist = relatedFromWordlist(wordlist, args.language) # a dictionary for each object, key: word, value: source (word from original list ('base'), synonym,  hypernym)
	flat_wordlist = {}
	for dictionary in hierarchy_wordlist:
		for word in dictionary:
			if word not in flat_wordlist:
				flat_wordlist[word] = dictionary[word]
			elif source_hierarchy.index(flat_wordlist[word]) > source_hierarchy.index(dictionary[word]):
					flat_wordlist[word] = dictionary[word]
	separated_wordlist = sum([word.split() for word in flat_wordlist.keys()], []) # all individual words

	# GRAMMAR
	if not args.grammar:
		if args.default:
			if args.language == "English":
				grammar_name = os.path.join(os.path.dirname(__file__), "default", "englishGrammar.fsg")
			if args.language == "Spanish":
				grammar_name = os.path.join(os.path.dirname(__file__), "default", "spanishGrammar.fsg")
			if args.language == "Chinese":
				grammar_name = os.path.join(os.path.dirname(__file__), "default", "chineseGrammar.fsg")
		else:
			# create grammar
			grammar_name = "temp_grammar"
			result = createMintGrammar(flat_wordlist, grammar_name, unknown, args.verbose)
			grammar_name = grammar_name + ".fsg"
			if not result == True:
				print("Error creating grammar.")
				sys.exit(result)
	else:
		grammar_name = os.path.join(os.getcwd(), args.grammar)

	# DICTIONARY
	if not args.dictionary:
		if args.default:
			if args.language == "English":
				dictionary_name = os.path.join(os.path.dirname(__file__), "default", "englishDictionary.dic")
			if args.language == "Spanish":
				dictionary_name = os.path.join(os.path.dirname(__file__), "default", "spanishDictionary.dic")
			if args.language == "Chinese":
				dictionary_name = os.path.join(os.path.dirname(__file__), "default", "chineseDictionary.dic")
		else:
			# create dictionary
			dictionary_name = "temp_dictionary"
			result = createDictionary(separated_wordlist, unknown, dictionary_name, args.language, args.verbose)
			dictionary_name = dictionary_name + ".dic"
			if not result == True:
				if not args.cache and not args.grammar:
					os.remove(grammar_name)
				print("Error creating dictionary.")
				sys.exit(result)
	else:
		dictionary_name = os.path.join(os.getcwd(), args.dictionary)
	
	# AUDIO FILES
	files = os.listdir(os.path.join(os.getcwd(), args.audio_directory))
	for filename in files:
		# transcribe audio
		if os.path.isfile(os.path.join(os.getcwd(), args.audio_directory,  filename)):
			success, result = transcribeMINT(os.path.join(os.getcwd(), args.audio_directory,  filename), grammar_name, dictionary_name, hierarchy_wordlist, unknown, AudioSettingsContainer(args.min_silence_len, args.silence_thresh, args.keep_silence), args.language, args.verbose)
			if success:
				try:
					(basename, extension) = os.path.splitext(filename)
					result_file = open(os.path.join(os.getcwd(), args.audio_directory, basename + '.txt'), 'w')
					result_file.write(result)
					result_file.close()
				except IOError:
					print('Could not write results for', filename)
			else:
				print(result)

	if not args.cache and not args.default:
		if not args.grammar:
			os.remove(grammar_name)
		if not args.dictionary:
			os.remove(dictionary_name)