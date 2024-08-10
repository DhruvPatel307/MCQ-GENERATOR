# import os
# import json
# import traceback
# import pandas as pd
# from dotenv import load_dotenv
# from src.mcqgenerator.utils import read_file,get_table_data
# from src.mcqgenerator.logger import logging
# from langchain.prompts import PromptTemplate

# #imporing necessary packages packages from langchain

# from langchain.chat_models import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# from langchain.chains import SequentialChain


# # Load environment variables from the .env file
# load_dotenv()

# # Access the environment variables just like you would with os.environ
# key=os.getenv("OPENAI_API_KEY")


# llm = ChatOpenAI(openai_api_key=key,model_name="gpt-3.5-turbo", temperature=0.7)

# template="""
# Text:{text}
# You are an expert MCQ maker. Given the above text, it is your job to \
# create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
# Make sure the questions are not repeated and check all the questions to be conforming the text as well.
# Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
# Ensure to make {number} MCQs
# ### RESPONSE_JSON
# {response_json}

# """

# quiz_generation_prompt = PromptTemplate(
#     input_variables=["text", "number", "subject", "tone", "response_json"],
#     template=template)


# quiz_chain=LLMChain(llm=llm,prompts=quiz_generation_prompt,output_key="quiz",verbose=True)


# template2="""
# You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
# You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
# if the quiz is not at per with the cognitive and analytical abilities of the students,\
# update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
# Quiz_MCQs:
# {quiz}

# Check from an expert English Writer of the above quiz:
# """


# quiz_evaluation_prompt=PromptTemplate(input_variables=["subject", "quiz"], template=template2)

# review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


# # This is an Overall Chain where we run the two chains in Sequence
# generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text", "number", "subject", "tone", "response_json"],
#                                         output_variables=["quiz", "review"], verbose=True,)


import os
from dotenv import load_dotenv
#from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain


load_dotenv()
# key=os.getenv("OPENAI_API_KEY")
key=os.getenv("Groq_Key")

# llm = ChatOpenAI(openai_api_key=key, model_name="gpt-3.5-turbo", temperature=0.7)
llm = ChatGroq(groq_api_key=key, model_name="mixtral-8x7b-32768", temperature=0.7)

template = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming to the text as well.
Make sure to format your response like RESPONSE_JSON below and use it as a guide. \
Ensure to make {number} MCQs.
### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=template
)

quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

template2 = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,\
you need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
If the quiz is not at par with the cognitive and analytical abilities of the students,\
update the quiz questions which need to be changed and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}
Check from an expert English Writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(input_variables=["subject", "quiz"], template=template2)

review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)

generate_evaluate_chain = SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"],
    verbose=True,
)