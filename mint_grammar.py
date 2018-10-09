import os
from shutil import rmtree
from re import split
import argparse

import subprocess


def createMintGrammar(wordlist, grammar_name, unknown_value, print_errors):
	grammar_header = '''#JSGF V1.0;
	grammar transcription;

	public <transcription> = '''

	weighting = {
		'base': 1.0,
		'synonym': 0.000001,
		'hypernym': 0.000001
  	}

	# weight wordlist based on estimated phonetic qualities
	new_wordlist = ['/' + '%.6f' %weighting[wordlist[word]] + '/ ' + word for word in wordlist]
	
	# write JSGF grammar
	name = grammar_name
	new_grammar = open(name + '.jsgf', 'w')
	new_grammar.write(grammar_header)
	rule = '( ' + " | ".join(new_wordlist) + ' | /1.0/ ' + unknown_value + ' );'
	new_grammar.write(rule)
	new_grammar.close()
	
	# convert to FSG grammar
	if print_errors:
		compile_result = subprocess.run(["sphinx_jsgf2fsg", "-jsgf", name + '.jsgf', "-fsg", name + '.fsg'])
	else:
		compile_result = subprocess.run(["sphinx_jsgf2fsg", "-jsgf", name + '.jsgf', "-fsg", name + '.fsg'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	# delete old JSGF grammar
	os.remove(name + '.jsgf')

	if not compile_result.returncode == 0:
		return("Invalid wordlist.")
	return True


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Create grammars for the MINT task.")
	parser.add_argument('wordlist_file', help='a file containing the words, multiple possibilities on a single line separated by commas, each new object on a new line')
	parser.add_argument('grammar_name', help='the name of the grammar to create')
	parser.add_argument('--unknown', nargs='?', default='don\'t know', help='default possibility for all objects')
	parser.add_argument('-v', '--verbose', action='store_true', help='print all Sphinx output')
	args = parser.parse_args()
	
	# read the wordlist file
	try:
		wordlist = open(os.path.join(os.getcwd(), args.wordlist_file), 'r')
		words = wordlist.read()
		wordlist.close()
	except IOError:
		sys.exit("Could not read " + wordlist_file)

	result = createMintGrammar({word: "base" for word in split('[(\r\n)\n,]', words)}, os.path.join(os.getcwd(), args.grammar_name), args.unknown, args.verbose)
	if not result == True:
		print(result)
	else:
		print("Grammar successfully created.")