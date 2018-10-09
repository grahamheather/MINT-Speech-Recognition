import os
from re import split
import argparse

import subprocess


def createDictionary(wordlist, other_words, dictionary_name, language, print_errors):

	if language == 'English':
		dictionary_path = os.path.join(os.path.dirname(__file__), "en_dict_model")
	elif language == 'Spanish':
		dictionary_path = os.path.join(os.path.dirname(__file__), "es_dict_model")
	elif language == 'Chinese':
		dictionary_path = os.path.join(os.path.dirname(__file__), "zh_dict_model")

	parsed_wordlist_file = open(dictionary_name + '.txt', 'w')
	parsed_wordlist_file.write('\n'.join(wordlist + other_words.split()))
	parsed_wordlist_file.close()

	new_dictionary = open(dictionary_name + ".dic", 'w')
	
	# create dictionary
	if print_errors:
		compile_result = subprocess.run(["g2p-seq2seq", "--decode", dictionary_name + '.txt', "--model", dictionary_path], stdout=new_dictionary)
	else:
		compile_result = subprocess.run(["g2p-seq2seq", "--decode", dictionary_name + '.txt', "--model", dictionary_path], stdout=new_dictionary, stderr=subprocess.PIPE)

	new_dictionary.close()
	
	# remove temporary parsed word list
	os.remove(dictionary_name + '.txt')

	if not compile_result.returncode == 0:
		return "Invalid wordlist."

	# remove extraneous output from file
	new_dictionary = open(dictionary_name + ".dic", 'r')
	lines = new_dictionary.readlines()
	new_dictionary.close()
	new_dictionary = open(dictionary_name + ".dic", 'w')
	new_dictionary.write(''.join(lines[3:]))
	new_dictionary.close()

	return True


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Create a dictionary from the given words.")
	parser.add_argument('wordlist_file', help='a file containing the words, multiple possibilities on a single line separated by commas, each new object on a new line')
	parser.add_argument('dictionary_name', help='the name of the dictionary to create')
	parser.add_argument('language', help='the language the word list is in', choices=['English', 'Spanish', 'Chinese'])
	parser.add_argument('--other', help='an extra word to add to the word list (for use by MINT task for "don\'t know")')
	parser.add_argument('-v', '--verbose', action='store_true', help='print all Sphinx output')
	args = parser.parse_args()

	if not args.other:
		if args.language == "English":
			other = "don't know"
		if args.language == "Spanish":
			other = "no sé"
		if args.language == "Chinese":
			other = "不知道"

	# read the wordlist file
	try:
		wordlist = open(os.path.join(os.getcwd(), args.wordlist_file), 'r')
		words = wordlist.read()
		wordlist.close()
	except IOError:
		sys.exit("Could not read " + args.wordlist_file)

	# parsed word list
	possible_words = split('[(\r\n)\n, ]', words)

	result = createDictionary(possible_words, other, os.path.join(os.getcwd(), args.dictionary_name), args.language, args.verbose)
	if not result == True:
		print(result)
	else:
		print("Dictionary successfully created.")