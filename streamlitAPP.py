

# import os
# import json
# import traceback
# import pandas as pd
# from dotenv import load_dotenv
# from src.mcqgenerator.utils import read_file, get_table_data
# import streamlit as st

# from langchain.callbacks import get_openai_callback
# from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
# from src.mcqgenerator.logger import logging

# # Load environment variables from the .env file
# load_dotenv()

# # Access the environment variables just like you would with os.environ
# # key = os.getenv("OPENAI_API_KEY")
# key=os.getenv("Groq_Key")

# # Load the JSON file
# with open('Response.json', 'r') as file:
#     RESPONSE_JSON = json.load(file)

# # Creating a title for the app
# st.title("MCQ Generator Application with LangChain ")

# with st.form("user input"):
#     uploaded_file = st.file_uploader("Upload PDF or text")
#     mcq_count = st.number_input("No. of MCQs", min_value=3, max_value=50)
#     subject = st.text_input("Insert Subject", max_chars=20)
#     tone = st.text_input("Complexity level of questions", max_chars=20, placeholder="simple")
#     button = st.form_submit_button("Create MCQ")

#     if button and uploaded_file is not None and mcq_count and subject and tone:
#         with st.spinner("Loading..."):
#             try:
#                 text = read_file(uploaded_file)
#                 # How to setup Token Usage Tracking in LangChain
#                 with get_openai_callback() as cb:
#                     response = generate_evaluate_chain(
#                         {
#                             "text": text,
#                             "number": mcq_count,
#                             "subject": subject,
#                             "tone": tone,
#                             "response_json": json.dumps(RESPONSE_JSON)
#                         }
#                     )
#             except Exception as e:
#                 traceback.print_exception(type(e), e, e.__traceback__)
#                 st.error("Error")
#             else:
#                 print(f"Total Tokens: {cb.total_tokens}")
#                 print(f"Prompt Tokens: {cb.prompt_tokens}")
#                 print(f"Completion Tokens: {cb.completion_tokens}")
#                 print(f"Total Cost: {cb.total_cost}")
#                 if isinstance(response, dict):
#                     # Extract the quiz data from the response
#                     quiz = response.get("quiz", None)
#                     if quiz is not None:
#                         table_data = get_table_data(quiz)
#                         if table_data is not None:
#                             df = pd.DataFrame(table_data)
#                             df.index = df.index + 1
#                             st.table(df)
#                             # Display the review in a text box as well
#                             st.text_area(label="Review", value=response["review"])
#                         else:
#                             st.error("Error in the table data")
#                 else:
#                     st.write(response)


import os
import json
import traceback
import pandas as pd
import fitz  # PyMuPDF for reading PDFs
from dotenv import load_dotenv
import streamlit as st
from io import BytesIO  # For creating downloadable files
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.utils import get_table_data
from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# Load environment variables
load_dotenv()
key = os.getenv("Groq_Key")

# Load the JSON response file
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Set Streamlit page config with dark mode
st.set_page_config(page_title="MCQ Generator", page_icon="📝", layout="wide")

# Apply custom dark mode CSS
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
        color: #ffffff;
    }
    .stTextInput, .stNumberInput, .stFileUploader {
        color: #ffffff;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton button {
        background-color: #ff7f0e;
        color: white;
        font-weight: bold;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        border: 1px solid white;
    }
    th, td {
        border: 1px solid white;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #333333;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to extract text from a PDF file
def read_pdf(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")  # Open PDF from stream
        text = "\n".join([page.get_text() for page in doc])  # Extract text from all pages
        return text
    except Exception as e:
        st.error("Error reading PDF file: " + str(e))
        return None

# Function to extract text from a text file
def read_text(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8")  # Decode as UTF-8
    except Exception as e:
        st.error("Error reading text file: " + str(e))
        return None

# Function to create a downloadable PDF file
def create_pdf(dataframe):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setFont("Helvetica", 12)

    y_position = 750  # Starting position for text

    pdf.drawString(200, 800, "Generated MCQs")  # Title

    for index, row in dataframe.iterrows():
        question_text = f"{index}. {row['Question']}"
        options = f"A) {row['Option A']}  B) {row['Option B']}  C) {row['Option C']}  D) {row['Option D']}"
        answer = f"Answer: {row['Answer']}"

        pdf.drawString(50, y_position, question_text)
        y_position -= 20
        pdf.drawString(50, y_position, options)
        y_position -= 20
        pdf.drawString(50, y_position, answer)
        y_position -= 30  # Space between questions

        if y_position < 50:  # New page if needed
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y_position = 750

    pdf.save()
    output.seek(0)
    return output

# Creating a title for the app
st.title("📝 MCQ Generator Application")

# Initialize session state to store MCQ data for download
if "mcq_dataframe" not in st.session_state:
    st.session_state.mcq_dataframe = None

with st.form("user_input"):
    uploaded_file = st.file_uploader("📂 Upload PDF or Text File", type=["pdf", "txt"])
    mcq_count = st.number_input("🔢 Number of MCQs", min_value=3, max_value=50)
    subject = st.text_input("📖 Subject", max_chars=20)
    tone = st.text_input("⚡ Complexity Level (e.g., simple, medium, hard)", max_chars=20, placeholder="simple")
    button = st.form_submit_button("🚀 Generate MCQs")

if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("⚙️ Processing file..."):
        try:
            # Read file content based on its type
            if uploaded_file.type == "application/pdf":
                text = read_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                text = read_text(uploaded_file)
            else:
                st.error("⚠️ Unsupported file format. Please upload a PDF or TXT file.")
                text = None

            if not text:
                st.error("❌ No text extracted from the file. Please check the document.")
            else:
                # Track token usage with LangChain
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain({
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error("❌ Error processing the file")
        else:
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost: {cb.total_cost}")

            if isinstance(response, dict):
                quiz = response.get("quiz", None)
                
                # ✅ Fix: Convert JSON string to dictionary if necessary
                if isinstance(quiz, str):
                    quiz = json.loads(quiz)

                if quiz:
                    table_data = []

                    for key, value in quiz.items():
                        mcq = value.get("mcq", "")
                        options = value.get("options", {})
                        correct = value.get("correct", "")

                        table_data.append({
                            "Question": mcq,
                            "Option A": options.get("a", ""),
                            "Option B": options.get("b", ""),
                            "Option C": options.get("c", ""),
                            "Option D": options.get("d", ""),
                            "Answer": correct
                        })

                    if table_data:
                        df = pd.DataFrame(table_data)
                        df.index += 1
                        st.session_state.mcq_dataframe = df  # Store data for download
                        
                        # Display in tabular format
                        st.write("### 📊 Preview of Generated MCQs")
                        st.dataframe(df.style.set_properties(**{
                            # 'background-color': '#333333',
                            # 'color': 'white',
                            # 'border-color': 'white'
                        }))
                        
                        #st.text_area(label="💬 Review", value=response.get("review", "No review available."))
                    else:
                        st.error("⚠️ Error in the table data")
            else:
                st.write(response)

# Show the download button **outside** the form after response generation
if st.session_state.mcq_dataframe is not None:
    pdf_file = create_pdf(st.session_state.mcq_dataframe)
    st.download_button(
        label="📥 Download MCQs as PDF",
        data=pdf_file,
        file_name="mcqs.pdf",
        mime="application/pdf"
    )

