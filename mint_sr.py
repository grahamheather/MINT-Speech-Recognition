import sys
import os
from shutil import rmtree
from re import split
import argparse

from read_wordlist import readWordlist
from wordnet_nltk_interface import relatedFromWordlist
from mint_grammar import createMintGrammar
from create_dictionary import createDictionary
import speech_recognition as sr
from audio_split import AudioSettingsContainer, splitAudio
import alignment

# https://stackoverflow.com/a/5103455
def redirect_stderr():
	sys.stderr.flush()
	newstderr = os.dup(2)
	devnull = os.open(os.devnull, os.O_WRONLY)
	os.dup2(devnull, 2)
	os.close(devnull)
	sys.stderr = os.fdopen(newstderr, 'w')


def transcribeMINT(audio_name, grammar_name, dictionary_name, word_list, unknown, audio_settings, language, print_errors):
	# set language paths
	if language == "English":
		language_path = (os.path.join(os.path.dirname(__file__), "en_model", "en-us"), os.path.join(os.path.dirname(__file__), "en_model", "en-us.lm.bin"), dictionary_name)
	elif language == "Spanish":
		language_path = (os.path.join(os.path.dirname(__file__), "es_model", "voxforge_es_sphinx.cd_ptm_4000"), os.path.join(os.path.dirname(__file__), "es_model", "es-20k.lm.gz"), dictionary_name)
	elif language == "Chinese":
		language_path = (os.path.join(os.path.dirname(__file__), "zh_model", "zh_broadcastnews_ptm256_8000"), os.path.join(os.path.dirname(__file__), "zh_model", "zh_broadcastnews_64000_utf8.DMP"), dictionary_name)

	# split audio into individual words
	count = splitAudio(audio_name, audio_settings)
	if not isinstance(count, int):
		return (False, count)
	(file, extension) = os.path.splitext(audio_name)
	base_name = os.path.basename(file)

	num_digits_audio = len(str(count))
	N_bests = [None for i in range(0, count)]

	if not print_errors:
		redirect_stderr()

	# for each audio file
	for i in range(1, count + 1):
		# read the audio file
		r = sr.Recognizer()
		with sr.AudioFile(file + '/' + base_name + "_" + str(i).zfill(num_digits_audio) + ".wav") as source:
			audio = r.record(source)

		# recognize word
		try:
			decoder = r.recognize_sphinx(audio, grammar=grammar_name, show_all=True, language=language_path)
			result = ([best.hypstr for best in decoder.nbest()], [best.score for best in decoder.nbest()])
		except sr.UnknownValueError:	
			result = []
		except sr.RequestError as e:
			print("Error in transcription (1).")
			rmtree(file)
			return (False, e)
		except RuntimeError as e:
			print("Error in transcription (2).")
			rmtree(file)
			if e.args[0] == "Decoder_set_fsg returned -1":
				return (False, e.args[0] + "\nAn invalid word was detected in the wordlist.")
			else:
				return (False, e)

		# record results
		N_bests[i-1] = result

	rmtree(file)

	return (True, '\n'.join(alignment.backshift(alignment.levenshtein(N_bests, word_list, unknown), unknown)))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Create a transcription of a MINT task audio file.")
	parser.add_argument('audio_file', help='the audio file to transcribe')
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

	# AUDIO FILE
	audio_file = os.path.join(os.getcwd(), args.audio_file)

	# WORDLIST
	if args.default:
		if args.language == "English":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "englishWordlist.txt")
		if args.language == "Spanish":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "spanishWordlist.txt")
		if args.language == "Chinese":
			wordlist = os.path.join(os.path.dirname(__file__), "default", "chineseWordlist.txt")
	else:
		wordlist = os.path.join(os.getcwd(), args.wordlist)
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
	
	# transcribe audio
	success, result = transcribeMINT(audio_file, grammar_name, dictionary_name, hierarchy_wordlist, unknown, AudioSettingsContainer(args.min_silence_len, args.silence_thresh, args.keep_silence), args.language, args.verbose)
	
	if not args.cache and not args.default:
		if not args.grammar:
			os.remove(grammar_name)
		if not args.dictionary:
			os.remove(dictionary_name)

	print(result)