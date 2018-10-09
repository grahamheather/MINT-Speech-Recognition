import argparse

from nltk.corpus import wordnet

def cleanWord(word):
	replacements = {
		"_" : " ",
		"-" : " ",
		"." : "",
		"1" : "one ",
		"2" : "two ",
		"3" : "three ",
		"4" : "four ",
		"5" : "five ",
		"6" : "six ",
		"7" : "seven ",
		"8" : "eight ",
		"9" : "nine ",
		"0" : "zero "
	}
	for original_segment in replacements:
		word = word.replace(original_segment, replacements[original_segment])
	return word.lower().strip()

def relatedWords(word, language):
	#translate language name to language code
	if language == "English":
		lang = 'eng'
	elif language == "Chinese":
		lang = 'cmn'
	elif language == "Spanish":
		lang = 'spa'

	# search for word in WordNet
	synsets = wordnet.synsets(word, pos=wordnet.NOUN, lang=lang)

	# check if word in WordNet
	if synsets == []:
		# try removing whitespace
		synsets = wordnet.synsets(word.replace(" ", ""), pos=wordnet.NOUN, lang=lang)

	# if the word still isn't in WordNet
	if synsets == []:
		#try replacing whitespace with _
		synsets = wordnet.synsets(word.replace(" ","_"), pos=wordnet.NOUN, lang=lang)

	# if the word is not in WordNet in any possible form
	if synsets == []:
		return [(word, 'base')]

	synonyms = [(str(cleanWord(lemma.name())), 'synonym') for lemma in synsets[0].lemmas(lang=lang)]
	direct_hypernyms = [(str(cleanWord(lemma.name())), 'hypernym') for hypernym in synsets[0].hypernyms() for lemma in hypernym.lemmas(lang=lang)]

	return [(word, 'base')] + synonyms + direct_hypernyms

def relatedFromWordlist(wordlist, language):
	new_wordlist = []
	for entry in wordlist:
		new_set = []
		for synonym in entry:
			new_set += relatedWords(synonym, language)
		new_wordlist.append(dict(new_set))
		for synonym in entry:
			new_wordlist[-1][synonym] = 'base' # make sure that this hasn't been overwritten
	return new_wordlist

if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Create grammars for the MINT task.")
	parser.add_argument('word', help='the word to find synonyms/hypernyms/etc. for')
	parser.add_argument('language', help='the language, currently supported: English, Chinese, Spanish')
	args = parser.parse_args()

	print(relatedWords(args.word, args.language))