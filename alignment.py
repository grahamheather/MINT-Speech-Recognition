from math import inf
from itertools import groupby

# adapted from: 
# https://en.wikipedia.org/wiki/Levenshtein_distance 
def levenshtein(recognized_words, word_list_words, unknown):
	weighting = {
		'base': 1.0,
		'synonym': 0.8,
		'hypernym': 0.6

	}

	# len(recognized_words) rows x len(word_list_words) columns 
	distances = [[0 for y in range(len(word_list_words) + 1)] for x in range(len(recognized_words) + 1)] 
	choices = [[0 for y in range(len(word_list_words) + 1)] for x in range(len(recognized_words) + 1)] 
 
	for init in range(len(recognized_words)): 
		distances[init][0] = 0 
 
	for init in range(len(word_list_words)): 
		distances[0][init] = 0 
 
	for i in range(1, len(recognized_words) + 1): 
		for j in range(1, len(word_list_words) + 1):

			transcription = None
			subscore = 0
			if unknown in recognized_words[i-1][0]:
				transcription = unknown
				subscore = .5
			for possible_word in recognized_words[i-1][0]:
				if possible_word in word_list_words[j-1] and ((not unknown in recognized_words[i-1][0]) or (recognized_words[i-1][0].index(unknown) > recognized_words[i-1][0].index(possible_word))):
						if .5 + .5 * (weighting[word_list_words[j-1][possible_word]]) > subscore:
							transcription = possible_word
							subscore = .5 + .5 * (weighting[word_list_words[j-1][possible_word]])

			if transcription == None:
				distances[i][j], choices[i][j] = max(
								(distances[i-1][j], 'a_up'),
								(distances[i][j-1], 'z_back'))
			else :
				distances[i][j], choices[i][j] = max(
								(distances[i-1][j], 'a_up'),
								(distances[i][j-1], 'z_back'),
								(distances[i-1][j-1] + subscore, transcription)
						)

	return traceback(distances, choices, len(recognized_words), len(word_list_words), unknown) 
 
def traceback(distances, choices, m, n, default): 
	word_list_pairs = ['UNKNOWN' for y in range(n)] 
	i, j = m, n
	while i > 0 and j > 0: 
		if choices[i][j] == 'a_up':
			i -= 1 
		elif choices[i][j] == 'z_back':
			j -= 1 
		else: 
			word_list_pairs[j-1] = choices[i][j] 
			i -= 1 
			j -= 1 
	return word_list_pairs

def backshift(results, unknown):
	grouped = [(k, len(list(g))) for k, g in groupby(results)]
	if grouped[-1][0] == unknown and grouped[-2][0] == 'UNKNOWN':
		return results[:-grouped[-1][1]-grouped[-2][1]] + results[-grouped[-1][1]:] + results[-grouped[-1][1]-grouped[-2][1]:-grouped[-1][1]]
	else:
		return results