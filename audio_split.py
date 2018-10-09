import os
import argparse

from pydub import AudioSegment
from pydub.silence import split_on_silence

class AudioSettingsContainer:
	def __init__(self, min_silence_len, silence_thresh, keep_silence):
		self.min_silence_len = min_silence_len
		self.silence_thresh = silence_thresh
		self.keep_silence = keep_silence


def splitAudio(audio_file, audioSettings):
	# read audio
	pydub_audio = AudioSegment.from_wav(audio_file)

	# split on silence
	split_audio = split_on_silence(pydub_audio, min_silence_len=audioSettings.min_silence_len, silence_thresh=audioSettings.silence_thresh, keep_silence=audioSettings.keep_silence)

	# calculate how many digits to zfill
	num_digits = len(str(len(split_audio))) # or do int(math.log10(len(words))) + 1

	# create folder for the audio files
	(file, extension) = os.path.splitext(audio_file)
	base_name = os.path.basename(file)
	if not os.path.exists(file):
		os.makedirs(file)
	else:
		return "The directory specified for the audio files (" + base_name + ") already exists."

	# save output
	count = 0
	for single_word in split_audio:
		count = count + 1
		single_word.export(os.path.join(file, base_name + "_" + str(count).zfill(num_digits) + ".wav"), format="wav")

	return count

if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Split an audio file on silence.")
	parser.add_argument('audio_file', help='the audio file to split')
	parser.add_argument('--min_silence_len', default=400)
	parser.add_argument('--silence_thresh', default=-36)
	parser.add_argument('--keep_silence', default=400)
	args = parser.parse_args()

	result = splitAudio(os.path.join(os.getcwd(), args.audio_file), AudioSettingsContainer(args.min_silence_len, args.silence_thresh, args.keep_silence))
	if not isinstance(result, int):
		print(result)
	else:
		print(str(result) + " audio file(s) successfully created.")