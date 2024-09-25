#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importing packages
import requests 
import urllib.request
import time
from bs4 import BeautifulSoup
import numpy as np
import nltk  #NLTK stands for Natural Language Toolkit
import zipfile
import os
import pandas as pd
# Ensure NLTK data directory exists
nltk.data.path.append('.')

# Download the WordNet corpus
nltk.download('wordnet')

# Path to the downloaded WordNet zip file
wordnet_zip_path = os.path.join(nltk.data.find('corpora'), 'wordnet.zip')

# Extract the contents of the downloaded zip file
with zipfile.ZipFile(wordnet_zip_path, 'r') as zip_ref:
    zip_ref.extractall(nltk.data.find('corpora'))


# # # Table of Contents
# 
# 1	Cleaning using Stop Words Lists
# 
# 2	Creating dictionary of Positive and Negative words
# 
# 3	Analysis of Readability
# 
# 4	Average Number of Words Per Sentence
# 
# 5	Complex Word Count
# 
# 6	Word Count
# 
# 7	Syllable Count Per Word
# 
# 8	Personal Pronouns
# 
# 9	Average Word Length	
# 
# 

# # Use of Different packages and libraries imported
# **requests**: This library is used to send HTTP requests and retrieve responses from web pages.
# 
# **urllib.request:** This module provides a high-level interface for fetching data across the World Wide Web. Although it's imported here, it's not explicitly used in the provided code snippet.
# 
# **time**: This module provides various time-related functions, and it might be used for adding delays between web requests to avoid overloading servers or to pace the scraping process.
# 
# **BeautifulSoup from bs4:** BeautifulSoup is a Python library for pulling data out of HTML and XML files. It allows for easy navigation and extraction of information from web pages. Here, BeautifulSoup is imported specifically for parsing HTML content fetched from web pages during the scraping process.

# **numpy as np**: NumPy is a popular library in Python used for numerical computing. It provides support for large, multi-dimensional arrays and matrices, along with a collection of mathematical functions to operate on these arrays efficiently. It is commonly abbreviated as np for convenience.
# 
# **nltk**: As mentioned, NLTK stands for Natural Language Toolkit. It is a comprehensive library for working with human language data in Python. It provides a wide range of tools and resources for tasks such as tokenization, stemming, tagging, parsing, and more, making it a popular choice for natural language processing (NLP) tasks.
# 
# **zipfile**: This module in Python provides classes for reading and writing ZIP files. It is used here to handle the extraction of files from a ZIP archive.
# 
# **os**: The os module in Python provides a way of interacting with the operating system. It is used here to perform various operating system-related tasks such as path manipulation.
# 
# **pandas as pd:** Pandas is a powerful data manipulation and analysis library in Python. It provides data structures like DataFrames and Series, along with functions to manipulate and analyze tabular data effectively. It is widely used for tasks such as data cleaning, exploration, and transformation. It is commonly imported under the alias pd for brevity and convenience.

# 

# In[2]:


# this is to install syllapy which is used in counting the syllables per word
get_ipython().system('pip install syllapy   ')


# In[ ]:





# In[3]:


import syllapy# importing syllapy for counting the syllables per word
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import string
import re

# Download NLTK data (if not already downloaded)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


# In[4]:


# @Use of Different packages and libraries imported
# @sent_tokenize: This function is used to tokenize text into sentences.

# word_tokenize: This function is used to tokenize text into words.

# stopwords: This module provides access to a list of common stopwords in various languages. Stopwords are words that are commonly used in a language but do not convey significant meaning, such as "the", "and", "is", etc. They are often filtered out during text processing to focus on more meaningful words.

# WordNetLemmatizer: This class is used for lemmatization, which is the process of reducing words to their base or root form. Lemmatization helps in standardizing words so that different forms of the same word are treated as the same token.

# Counter: This is a built-in Python class that is used to count the occurrences of elements in a list or iterable. It is often used for frequency analysis in text processing.

# string: This module provides constants and classes for working with strings. It includes sets of ASCII and Unicode characters, as well as functions for string manipulation and formatting. However, in this context, it's likely used for accessing punctuation characters for text processing tasks.


# # **WEB SCRAPING OF GIVEN URLS FROM INPUT FILE**

# In[5]:


# Function to extract main content from HTML 
def extract_main_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the first div element with class "td-post-content tagdiv-type"
    main_content_div_1 = soup.find('div', class_='td-post-content tagdiv-type')
    
    # Find the second div element with class "tdb-block-inner td-fix-index"
    main_content_div_2 = soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
    
    # If the main content div is found, extract text content from it
    if main_content_div_1:
        main_content = main_content_div_1.get_text()
        # If the alternative main content div is found, extract text content from it
        
    else:
        # If neither div is found, return an empty string
        main_content = main_content_div_2.get_text()
    
    return main_content


# This code defines a function named extract_main_content which takes html_content as input and returns the main content extracted from HTML.
# 
# Here's a breakdown of what the function does:
# 
# It uses BeautifulSoup to parse the HTML content provided as input.
# 
# It attempts to find the main content div by searching for specific div elements with certain class attributes:
# > **all the urls has main content without ads with qany of the both below given div with class as html code**- if not we can use div with class "main content" to get conetent but with some text of ads . that is universal
# main_content_div_1 searches for a div with class "td-post-content tagdiv-type".
# main_content_div_2 searches for a div with class "td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type".
# If main_content_div_1 is found, it extracts the text content from it using .get_text().
# 
# If main_content_div_1 is not found, it attempts to extract text from main_content_div_2.
# If neither div is found, it returns an empty string.
# Finally, it returns the extracted main content.
# 
# This function is useful for web scraping applications where you want to extract the main textual content from HTML pages, typically found within specific div elements with particular class attributes.

# # **1 Cleaning using Stop Words Lists**

# In[6]:


#we are combining the stopwords of nltk library of english basic words,given custom words as it necessary for analysis text 
# Function to remove stopwords and perform text cleaning
def preprocess_text(text, custom_stopwords_folder):
    
    # Load NLTK English stopwords# 
    english_stopwords = set(stopwords.words('english'))
    # Combine NLTK English stopwords with custom stopwords from each file in the folder
    all_stopwords = english_stopwords
    #using for loop and if conditions and file handling techinques to open stopwords file and load data from it by checking the filepath and filename ,if matched opens it and asiigns the words to cutsom stopwords
    for filename in os.listdir(custom_stopwords_folder):
        filepath = os.path.join(custom_stopwords_folder, filename)
        if os.path.isfile(filepath) and filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                custom_stopwords = f.read().splitlines()
                all_stopwords = all_stopwords.union(set(custom_stopwords))# combining custom stopwords with english stopwords of nltk with uinion keyword
    
    # Tokenize the text
    tokens = word_tokenize(text)
    # Remove stopwords and perform lemmatization
    lemmatizer = WordNetLemmatizer()
    cleaned_tokens = [lemmatizer.lemmatize(word.lower()) for word in tokens if word.lower() not in all_stopwords and word.isalnum()]
    cleaned= [lemmatizer.lemmatize(word) for word in cleaned_tokens if word not in all_stopwords ] 
    cleaned_tokens = {word for word in cleaned_tokens if not re.match(r'^\d+$', word)}## taking a set because it will store uniques values and in order which is mostuseful as there repeating  words and sets takes only unique instead of text cleaning the words more than once 
    # Join the tokens back into a single string
    cleaned_text = ' '.join(cleaned)# this is used to convert tokens of words into normal text like paragraghs again but it is easy for checking the tokens form positive and negative dictinary words so iam just returning cleaned_tokens
    return cleaned_tokens,all_stopwords# returning stopwords to be used in master dictinary filtering.


# > This function, preprocess_text, preprocesses the input text by performing several text processing tasks. Here's what each part of the function does:
# 
# # Loading Stopwords:
# 
# **It loads the English stopwords from the NLTK library.
# It iterates over each file in the specified custom stopwords folder, reads the stopwords from each file, and combines them with the NLTK English stopwords.
# This step is essential for filtering out common words that do not carry much meaning, such as "the," "and," "is," etc.
# # Tokenization and Lemmatization:**
# 
# **It tokenizes the input text using the word_tokenize function from NLTK.
# It removes stopwords and performs lemmatization on the tokens.
# Lemmatization reduces words to their base or root form, which helps in standardizing words and reducing their dimensionality.**
# # Cleaning Tokens:
# 
# **It filters out tokens that are numeric or consist only of digits.
# This step helps in removing numerical values or digits that might not contribute much to the analysis.**
# # Returning Results:
# 
# **It returns the cleaned tokens along with the combined set of all stopwords.
# The cleaned tokens represent the processed text in tokenized form, while the combined stopwords set contains all stopwords used for filtering.
# Overall, this function provides a comprehensive preprocessing pipeline for text data, making it suitable for various natural language processing tasks such as sentiment analysis, text classification, and information retrieval.**

# In[7]:


# Load Excel file form input file given
df = pd.read_excel(r"C:\Users\NISHITHA SAI\OneDrive\Desktop\BC\Input.xlsx")

# Path to the folder containing custom stopwords files
custom_stopwords_folder = r"C:\Users\NISHITHA SAI\OneDrive\Desktop\BC\StopWords-20240822T102228Z-001\StopWords"


# # 2 Creating dictionary of Positive and Negative words

# In[8]:


def load_words_from_files(folder_path):
    words_dict = {}
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath) and filename.lower() in ['positive-words.txt', 'negative-words.txt']:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                words_dict[filename.lower().split('.')[0]] = [word.strip() for word in f.readlines()]
                #print(type(words_dict))
    return words_dict
#the function receives master dictinary file as  parameter and open and reading the folder and assigning the postive and negative words to word_dict and returning it
# Path to the Master Dictionary folder given by Black coffer Team
master_dict_folder = r"C:\Users\NISHITHA SAI\OneDrive\Desktop\BC\MasterDictionary-20240822T102226Z-001\MasterDictionary"

# Load positive and negative words
positive_negative_words = load_words_from_files(master_dict_folder)#calling the function load_words_from_files
Positive_words=positive_negative_words.get('positive-words', {})
Negative_words=positive_negative_words.get('negative-words',{})


# # 3 Analysis of Readability**
# # 4 Average Number of Words Per Sentence**
# # 
# # 5 Complex Word Count**
# 

# In[9]:


# * ***3 **Analysis of Readability is calculated using the Gunning Fox index formula described below. 
# * * **Average Sentence Length = the number of words / the number of sentences 
# * * **Percentage of Complex words = the number of complex words / the number of words
# * * **Fog Index = 0.4 * (Average Sentence Length + Percentage of Complex words)**
# * * **


# In[10]:


# **4--Average Number of Words Per Sentence

# **The formula for calculating is:**

# **Average Number of Words Per Sentence = the total number of words / the total number of sentences**
# **


# In[11]:


# **# **5 	Complex Word Count**
# Complex words are words in the text that contain more than two syllables.


# In[12]:


def calculate_readability(text):
    # Tokenize text into sentences
    sentences = sent_tokenize(text)

    # Tokenize text into words
    words = word_tokenize(text)

    # Calculate average sentence length
    average_sentence_length = len(words) / len(sentences)

    # Count complex words using syllapy as Complex words are words in the text that contain more than two syllables.
    complex_words = {word for word in words if syllapy.count(word) > 2}# taking a set because it will store uniques values and in order which is mostuseful for instead of repeatition words
    complex_word_count = len(complex_words)# complex word count found by taking lenth of complex words
    percentage_complex_words = (len(complex_words) / len(words)) * 100# taking the percentage

    # Calculate Gunning Fox index
    FOG_INDEX = 0.4 * (average_sentence_length + percentage_complex_words)# also called FOG INDEX
    
    # Calculate average number of words per sentence
    average_words_per_sentence = len(words) / len(sentences)



    return average_sentence_length,percentage_complex_words,FOG_INDEX,average_words_per_sentence,complex_word_count ## 3,4,5 table of contents in one function check.


# # 6 Word Count****

# In[13]:


# **6	Word Count**

# We count the total cleaned words present in the text by 

# 1.	removing the stop words (using stopwords class of nltk package).

# 2.	removing any punctuations like ? ! , . from the word before counting.
# **


# In[14]:


def count_cleaned_words(text):
    # Tokenize text into words
    words = word_tokenize(text)

    # Get English stopwords
    stop_words = set(stopwords.words('english'))

    # Remove punctuations
    words = [word for word in words if word not in string.punctuation]

    # Remove stop words
    words = {word for word in words if word.lower() not in stop_words}# asigning a set gives as unique values
    # Count cleaned words
    cleaned_word_count = len(words)

    return cleaned_word_count


# # 7.Syllable Count Per Word

# In[15]:


# We count the number of Syllables in each word of the text by counting the vowels present in each word. 
# We also handle some exceptions like words ending with "es","ed" by not counting them as a syllable.


# In[16]:



def count_syllables_per_word(word):
    # Remove "es" and "ed" endings and count the remaining vowels as syllables
    exceptions = ["es", "ed"]
    for exception in exceptions:
        if word.endswith(exception):
            word = word[:-len(exception)]
    
    # Count vowels in the word
    vowels = 'aeiouy'
    syllable_count = 0
    prev_char_was_vowel = False
    for char in word:
        if char.lower() in vowels and not prev_char_was_vowel:
            syllable_count += 1
            prev_char_was_vowel = True
        elif char.lower() not in vowels:
            prev_char_was_vowel = False
    
    # Handle special cases like "e" at the end of the word
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    # Ensure that at least one syllable is counted for the word
    if syllable_count == 0:
        syllable_count = 1
    
    return syllable_count


# # 8	Personal Pronouns
# 

# In[17]:


# To calculate Personal Pronouns mentioned in the text,
# we use regex to find the counts of the words - “I,” “we,” “my,” “ours,” and “us”.
# Special care is taken so that the country name US is not included in the list.


# In[18]:


def count_personal_pronouns(text):
    # Define the list of personal pronouns
    personal_pronouns = ['I', 'we', 'my', 'ours', 'us']
    
    # Define a regex pattern to match the personal pronouns
    pattern = r'\b(?:{})\b'.format('|'.join(personal_pronouns))
    
    # Use regex to find all matches in the text
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    
    # Exclude instances of "US" as a separate word
    matches = [match for match in matches if match != 'us']
    
     # Count the occurrences of each personal pronoun
    total_count = len(matches)
    
    return total_count
    


# # 9	Average Word Length
# 
# 

# In[19]:


# Average Word Length is calculated by the formula:
# Sum of the total number of characters in each word/Total number of words


# In[20]:


def calculate_average_word_length(text):
    # Split the text into words
    words = text.split()
    
    # Calculate the total number of characters in all words
    total_characters = sum(len(word) for word in words)
    
    # Calculate the total number of words
    total_words = len(words)
    
    # Calculate the average word length
    if total_words > 0:
        average_word_length = total_characters / total_words
    else:
        average_word_length = 0  # Handle case when there are no words
    
    return average_word_length


# # We convert the text into a list of tokens using the nltk tokenize module and 
# # use these tokens to calculate the 4 variables described below:
# # Positive Score: This score is calculated by assigning the value of +1 for each word if found in the Positive Dictionary and then adding up all the values.
# # Negative Score: This score is calculated by assigning the value of -1 for each word if found in the Negative Dictionary and then adding up all the values. We multiply the score with -1 so that the score is a positive number.
# # Polarity Score: This is the score that determines if a given text is positive or negative in nature. It is calculated by using the formula: 
# # Polarity Score = (Positive Score – Negative Score)/ ((Positive Score + Negative Score) + 0.000001)
# # Range is from -1 to +1
# # Subjectivity Score: This is the score that determines if a given text is objective or subjective. It is calculated by using the formula: 
# # Subjectivity Score = (Positive Score + Negative Score)/ ((Total Words after cleaning) + 0.000001)
# # Range is from 0 to +1
# 

# In[21]:


cleaned_text_dict={}
# Create an empty DataFrame to store the information
data = []
# Iterate through URLs
for url, url_id in zip(df['URL'], df['URL_ID']):
    # Fetch web page
    response = requests.get(url)
    
    if response.status_code == 200:
        # Extract main content
        html_content = response.text
        main_content = extract_main_content(html_content)
        
        # Text preprocessing
        cleaned_text,all_stopwords= preprocess_text(main_content, custom_stopwords_folder)
        # Store cleaned text in dictionary
        cleaned_text_dict[url] = cleaned_text
        #Filter stopwords from positive and negative words FROM STOPWORDS 
        Filtered_Positive_words = {word.lower() for word in Positive_words if word not in all_stopwords}
        Filtered_Negative_words = {word.lower() for word in Negative_words if word not in all_stopwords}
        # 	Extracting Derived variables
        Positive_cleaned_text = {word  for word in cleaned_text if word in Filtered_Positive_words}
        Negative_cleaned_text = {word for word in cleaned_text if word in Filtered_Negative_words}
        
        Positive_score = sum(1 for word in cleaned_text if word in Filtered_Positive_words)# FOR EACH POSITIVE WORD +1 SCORE IS ADDED IF FOUND IN POSTIVE WORDS DICTINARY
        Negative_score = sum(1 for word in cleaned_text if word in Filtered_Negative_words)# FOR EACH NEGATIVE WORD  +1 IS COUNTED IF FOUND IN NEGATIVE WORDS DICTINARY
        
        Polarity_score = (Positive_score - Negative_score) / ((Positive_score + Negative_score) + 0.000001)
        
        total_words_after_cleaning = len(cleaned_text)
        
        subjectivity_score = (Positive_score + Negative_score) / (total_words_after_cleaning + 0.000001)
        # Calculate readabilityz
        AVG_SENTENCE_LENGTH,PERCENTAGE_OF_COMPLEX_WORDS,FOG_INDEX,AVG_WORDS_PER_SENTENCE,COMPLEX_WORD_COUNT= calculate_readability(main_content)
    
        # Count cleaned words
        Word_count = count_cleaned_words(main_content)
        # Count syllables per word
        syllables_per_word = {word: count_syllables_per_word(word) for word in cleaned_text}
        #print(syllables_per_word)
        pronoun_counts = count_personal_pronouns(main_content)
        #print(pronoun_counts)
        average_length = calculate_average_word_length(main_content)
        #print("Average Word Length:", average_length)
        data.append([url_id,url, Positive_score, Negative_score, Polarity_score, subjectivity_score,AVG_SENTENCE_LENGTH,PERCENTAGE_OF_COMPLEX_WORDS,FOG_INDEX,AVG_WORDS_PER_SENTENCE,COMPLEX_WORD_COUNT, Word_count,
                     syllables_per_word, pronoun_counts, average_length])
        #print(cleaned_text[0:100])
         # Example: print first 100 characters of cleaned text
    else:
        print(f"Failed to fetch URL: {url}")
        


# # CREATING OUTPUT FILE WITH ALL  COLUMNS AND INPUT VARIABLES AS PER OBJECTIVE DEFINED IN ASSIGNMENT
# *** 1.	All input variables in “Input.xlsx”
# * 2.	POSITIVE SCORE
# * 3.	NEGATIVE SCORE
# * 4.	POLARITY SCORE
# * 5.	SUBJECTIVITY SCORE
# * 6.	AVG SENTENCE LENGTH
# * 7.	PERCENTAGE OF COMPLEX WORDS
# * 8.	FOG INDEX
# * 9.	AVG NUMBER OF WORDS PER SENTENCE
# * 10.	COMPLEX WORD COUNT
# * 11.	WORD COUNT
# * 12.	SYLLABLE PER WORD
# * 13.	PERSONAL PRONOUNS
# * 14.	AVG WORD LENGTH
# **
# # STORING THE FILE AS  "Output Data Structure.xlsx" 

# In[22]:


# Create a DataFrame from the data list
columns = ['URL_ID','URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 'SUBJECTIVITY SCORE','AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS',
           'FOG_INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT',
           'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH']

df_output = pd.DataFrame(data, columns=columns)

# Write the DataFrame to an Excel file
Output_Data_Structure = "Output_Data_Structure.xlsx"
df_output.to_excel(Output_Data_Structure, index=False)
print(f"Data has been written to {Output_Data_Structure}.")
df_output


# In[ ]:





# In[ ]:




