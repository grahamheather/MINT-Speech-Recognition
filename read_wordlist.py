from re import split

def readWordlist(filename):
	# read the wordlist file
	try:
		wordlist = open(filename, 'r')
		words = wordlist.readlines()
		wordlist.close()
	except IOError:
		return("Could not read " + filename)

	possible_words = []
	for word in words:
		possible_words += [list(filter(None, map(str.strip, split('[(\r\n)\n,]', word))))]
	
	return possible_words