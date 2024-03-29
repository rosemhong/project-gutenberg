import collections
import heapq
import random
import re
import string

from trie import *

class ProjectGutenberg:
	def __init__(self, book_fname='Pride-and-Prejudice.txt', common_words_fname='1-1000.txt'):
		self.book_fname = book_fname
		self.common_words_fname = common_words_fname
		self.book_parsed = ''
		self.book_parsed_with_apostrophes_only = ''
		self.book_parsed_with_punctuation = ''
		self.book_parsed_without_quotes = ''
		self.common_words_parsed = ''
		self.chapters = 1
		self.chapter_numbers_list = []
		self.freqs = {}

		self.parse_book_txt_file()
		self.parse_common_words_txt_file(300) # filter out the 300 most common English words
		self.populate_freqs()

	"""
	parse_book_txt_file()
	Description: Parses the book's .txt file into a string, excluding
	the Project Gutenberg front-matter and back-matter sections. 
	"""
	def parse_book_txt_file(self):
		with open(self.book_fname, 'r') as f:
			# start reading at 'Chapter 1\n'
			line = f.readline()
			while (line != 'Chapter 1\n'):
				line = f.readline()

			# stop reading immediately before 'End of the Project Gutenberg EBook'
			for line in f:
				if 'End of the Project Gutenberg EBook' in line:
					break

				if 'Chapter ' in line:
					self.chapters += 1

				self.book_parsed += line.replace('\n', ' ')

		self.book_parsed_with_punctuation = self.book_parsed.replace('_', '')

		# strip string of '_', '“', '”', "'", '(', ')', '[', and ']'
		self.book_parsed_without_matching = self.book_parsed.replace('_', '').replace('“', '').replace('”', '').replace("' ", ' ').replace('(', '').replace(')', '').replace('[', '').replace(']', '')

		# strip string of all punctuation
		exclude = set(string.punctuation)
		exclude.add('“') # double quotation symbols specific to the 'Pride-and-Prejudice.txt' file
		exclude.add('”')
		exclude.remove('-') # hyphenated words should remain that way
		
		self.book_parsed = self.book_parsed.replace('--', ' ')

		exclude.remove("'")
		self.book_parsed_with_apostrophes_only = ''.join(ch for ch in self.book_parsed if ch not in exclude)
		exclude.add("'")

		self.book_parsed = ''.join(ch for ch in self.book_parsed if ch not in exclude)

		self.chapter_numbers_list = [str(i) for i in range(1, self.chapters)]

	"""
	parse_common_words_txt_file(n)
	Description: Parses a .txt file of the 1,000 most common English words
	into a list containing the first n words.
	Credit for '1-1000.txt', which contains a list of the 1,000 most common
	English words, goes to https://gist.github.com/deekayen.
	"""
	def parse_common_words_txt_file(self, n):
		if not(n >= 0 and n <= 1000):
			print('Error: The number of common words to be parsed must be between 0 and 1000 inclusive.')
			print()
			return

		with open(self.common_words_fname, 'r') as f:
			self.common_words_parsed = [next(f).replace('\n', '') for i in range(n)]

	"""
	get_total_number_of_chapters()
	Description: Returns the number of chapters in the text.
	"""
	def get_total_number_of_chapters(self):
		return self.chapters

	"""
	get_total_number_of_words()
	Description: Returns the number of words in the text using
	regular expressions, which handles cases of punctuation marks or
	special characters in the string.
	"""
	def get_total_number_of_words(self):
		total_number_of_words = len(re.findall(r'\w+', self.book_parsed_with_apostrophes_only))
		return total_number_of_words

	"""
	get_total_unique_words()
	Description: Returns the number of unique words in the text.
	"""
	def get_total_unique_words(self):
		book_parsed_lower = self.book_parsed_with_apostrophes_only.lower()
		return len(set(book_parsed_lower.split()))

	"""
	populate_freqs(self)
	Description: Populates a dictionary containing the frequencies of
	each word in the text.
	"""
	def populate_freqs(self):
		book_parsed = self.book_parsed_with_apostrophes_only
		self.freqs = dict(collections.Counter(book_parsed.split()))

		# adjust count for common nouns that are occasionally capitalized
		# at the beginning of sentences and counted as 2 distinct words
		# for example: 'the' and 'The' should be recombined as 1 entry 'the'
		# in freqs
		for word in list(self.freqs):
			if word[0].islower():
				capitalized_word = word[0].upper() + word[1:]
			else:
				capitalized_word = word
				word = word[0].lower() + word[1:]

			if word in self.freqs and capitalized_word in self.freqs: # not a proper noun
				self.freqs[word] += self.freqs.pop(capitalized_word)

		# adjust count for words that appear in all caps, as necessary
		for word in list(self.freqs):
			if len(word) == 1:
				continue

			all_caps = True
			for c in word:
				if c.islower():
					all_caps = False

			if all_caps:
				all_lower_word = ''
				for c in word:
					all_lower_word += c.lower()
				capitalized_word = all_lower_word[0].upper() + all_lower_word[1:]

				# proper noun, since double-counted common nouns were already deleted
				if capitalized_word in self.freqs:
					self.freqs[capitalized_word] += self.freqs.pop(word)
				elif all_lower_word in self.freqs: # not a proper noun
					self.freqs[all_lower_word] += self.freqs.pop(word)

	"""
	get_20_most_frequent_words()
	Description: Returns a list of the 20 most frequent words in the text.
	including the number of times each word was used.
	"""
	def get_20_most_frequent_words(self):
		# use a max heap
		heap = [(-freq, word) for word, freq in self.freqs.items()]
		heapq.heapify(heap)

		most_frequent_20_words = []
		for i in range(20):
			if not heap:
				break
			popped = heapq.heappop(heap)
			most_frequent_20_words.append([popped[1], -popped[0]])

		for i in range(len(most_frequent_20_words)):
			if 'Mrs' in most_frequent_20_words[i][0] or 'Mr' in most_frequent_20_words[i][0] or 'Esq' in most_frequent_20_words[i][0]:
				most_frequent_20_words[i][0] += '.'

		return most_frequent_20_words

	"""
	get_20_most_interesting_frequent_words()
	Description: Returns a list of the 20 most frequent words in the text
	after filtering out the n most common English words, where n is a
	parameter of the method parse_common_words_txt_file(n).
	Credit for '1-1000.txt', which contains a list of the 1,000 most common
	English words, goes to https://gist.github.com/deekayen.
	"""
	def get_20_most_interesting_frequent_words(self):
		# use a max heap
		heap = [(-freq, word) for word, freq in self.freqs.items()]
		heapq.heapify(heap)

		most_frequent_20_interesting_words = []
		while (heap and (len(most_frequent_20_interesting_words) < 20)):
			popped = heapq.heappop(heap)
			if popped[1] not in self.common_words_parsed and popped[1].upper() not in self.common_words_parsed:
				most_frequent_20_interesting_words.append([popped[1], -popped[0]])

		for i in range(len(most_frequent_20_interesting_words)):
			if 'Mrs' in most_frequent_20_interesting_words[i][0] or 'Mr' in most_frequent_20_interesting_words[i][0] or 'Esq' in most_frequent_20_interesting_words[i][0]:
				most_frequent_20_interesting_words[i][0] += '.'

		return most_frequent_20_interesting_words

	"""
	get_20_least_frequent_words()
	Description: Returns a list of the 20 least frequent words in the text.
	If multiple words are seen the same number of times, then the first 20
	are chosen in lexical order. Chapter numbers are excluded from the list.
	"""
	def get_20_least_frequent_words(self):
		# use a min heap
		heap = [(freq, word) for word, freq in self.freqs.items()]
		heapq.heapify(heap)

		least_frequent_20_words = []
		while len(least_frequent_20_words) < 20:
			if not heap:
				break
			popped = heapq.heappop(heap)
			if popped[1] not in self.chapter_numbers_list:
				least_frequent_20_words.append([popped[1], popped[0]])

		for i in range(len(least_frequent_20_words)):
			if 'Mrs' in least_frequent_20_words[i][0] or 'Mr' in least_frequent_20_words[i][0] or 'Esq' in least_frequent_20_words[i][0]:
				least_frequent_20_words[i][0] += '.'

		return least_frequent_20_words

	"""
	get_frequency_of_word(word)
	Description: Returns a list of the number of times a word was used
	in each chapter (61 chapters for Pride and Prejudice).
	Capitalization-sensitive (ie 'the' is counted separate from 'The').
	"""
	def get_frequency_of_word(self, word):
		chapter_frequency_of_word = []
		for i in range(1, self.chapters + 1):
			chapter_start = 'Chapter ' + str(i)
			if i == self.chapters:
				chapter_stop = 'End of the Project Gutenberg EBook'
			else:
				chapter_stop = 'Chapter ' + str(i + 1)

			chapter_start_index = self.book_parsed_with_apostrophes_only.find(chapter_start)
			chapter_stop_index = self.book_parsed_with_apostrophes_only.find(chapter_stop)
			chapter_parsed = self.book_parsed_with_apostrophes_only[chapter_start_index:chapter_stop_index]
				
			chapter_parsed_list = chapter_parsed.split()
			chapter_frequency_of_word.append(chapter_parsed_list.count(word))

		return chapter_frequency_of_word

	"""
	get_chapter_quote_appears(quote)
	Description: Returns the chapter in which the quote appears.
	Capitalization-sensitive.
	"""
	def get_chapter_quote_appears(self, quote):
		for i in range(1, self.chapters + 1):
			chapter_start = 'Chapter ' + str(i)
			chapter_start_index = self.book_parsed_with_punctuation.find(chapter_start)

			if i == self.chapters: # last chapter
				chapter_parsed = self.book_parsed_with_punctuation[chapter_start_index:]
			else:
				chapter_stop = 'Chapter ' + str(i + 1)
				chapter_stop_index = self.book_parsed_with_punctuation.find(chapter_stop)
				chapter_parsed = self.book_parsed_with_punctuation[chapter_start_index:chapter_stop_index]

			if quote in chapter_parsed:
				return i

		return -1

	"""
	generate_sentence()
	Description: Generates a 20-word sentence in the author's style, word by word.
	All sentences generated start with 'The'.
	"""
	def generate_sentence(self):
		sentence_list = ['The']

		while len(sentence_list) < 20:
			sentence_list.append(self.generate_sentence_helper(sentence_list[-1]))

		punctuation = set(string.punctuation)
		punctuation.add('“') # double quotation symbols specific to the 'Pride-and-Prejudice.txt' file
		punctuation.add('”')

		# delete punctuation located at last index of the sentence
		sentence = ' '.join(sentence_list)
		if sentence[-1] in punctuation:
			sentence = sentence[:len(sentence) - 1]
		sentence += '.'

		return sentence

	"""
	generate_sentence_helper()
	Description: Generates the next word for generate_sentence(). Searches for words
	that occur immediately after all instances of the word passed in. Randomly selects
	and returns 1 of these words. More frequently-occurring words are selected more often.
	Capitalization-sensitive.
	"""
	def generate_sentence_helper(self, word):
		book_parsed_list = self.book_parsed_without_matching.split()
		next_words = []

		done = False
		while not done:
			try:
				word_index = book_parsed_list.index(word)
				if word_index < len(book_parsed_list) - 1:
					next_words.append(book_parsed_list[word_index + 1])
					book_parsed_list = book_parsed_list[word_index + 1:]
			except ValueError: # not found
				done = True

		random_index = random.randint(0, len(next_words) - 1)
		return next_words[random_index]

	"""
	get_autocomplete_sentences(start_of_sentence)
	Description: Takes in word(s) that occur at the start of some sentence
	in the text and returns a list of all sentences that start with those word(s).
	Capitalization-sensitive.
	"""
	def get_autocomplete_sentences(self, start_of_sentence):
		# 'Mrs.', 'Mr.', and 'Esq.' should not be parsed into their own sentences
		book_parsed_with_punctuation = self.book_parsed_with_punctuation.replace('Mrs.', '$MRS$').replace('Mr.', '$MR$').replace('Esq.', '$ESQ$')
		
		# split at '.', '?', or '!', but preserve the punctuation after the split
		book_parsed_sentences_list = re.split('(?<=[.!?]).', book_parsed_with_punctuation)
		
		trie = Trie()
		# insert every sentence of the text into the trie
		for sentence in book_parsed_sentences_list:
			trie.insert(sentence)
			pass

		# capitalize the start of the sentence
		start_of_sentence = start_of_sentence[0].upper() + start_of_sentence[1:]
		if 'Mrs.' in start_of_sentence:
			start_of_sentence = start_of_sentence.replace('Mrs.', '$MRS$')
		if 'Mr.' in start_of_sentence:
			start_of_sentence = start_of_sentence.replace('Mr.', '$MR$')
		if 'Esq.' in start_of_sentence:
			start_of_sentence = start_of_sentence.replace('Mr.', '$MR$')

		autocomplete_sentences = trie.get_autocomplete_sentences_helper(start_of_sentence)

		# re-render 'Mrs.', 'Mr.', and 'Esq.' in the autocomplete sentences
		for i in range(len(autocomplete_sentences)):
			if '$MRS$' in autocomplete_sentences[i]:
				autocomplete_sentences[i] = autocomplete_sentences[i].replace('$MRS$', 'Mrs.')
			if '$MR$' in autocomplete_sentences[i]:
				autocomplete_sentences[i] = autocomplete_sentences[i].replace('$MR$', 'Mr.')
			if '$ESQ$' in autocomplete_sentences[i]:
				autocomplete_sentences[i] = autocomplete_sentences[i].replace('$ESQ$', 'Esq.')

		return autocomplete_sentences