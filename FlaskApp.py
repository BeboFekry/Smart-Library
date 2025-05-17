from flask import Flask, request, redirect, render_template, jsonify
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import bs4
from langchain.document_loaders import PDFPlumberLoader, TextLoader
import requests

API = "AIzaSyCaPzDUJujNjXa8r2wQ5P0RCHlTMXJc5zE"

messages = [
        SystemMessage(content="""you are a helpfull AI assistant with main tasks:
                      1. Summarizing books and documents" (read long texts and summarize them briefly for user, focusing on the most important points and topics),
                      2. Answering questions: (answer questions about the texts you have on hand),
                      3. Suggesting books: (suggest books based on users interests),
                      4. Translating texts: (translate texts from one language to another),
                      5. and Writing texts: (write various texts, such as articles, reports, or research).
                      
    your name is Octobot.
    you are a smart chatbot a part of Smart Library website system.
    you are developed by 'Waraq team' or "فريق ورق".
    you will take a text and summarize it to focus on the important topics. Summarize the book, add summary at the end, then add Question and Asnwers on it.
    you may get questions on the summarized topice you need you answer all of them.
    if you asked by Arabic answer by Egyptian Arabic if you asked by English answer by English.
    You can help the users that can't attach the book for you ask them to press into the sidebar, upload the file then press Summarize button.
    You can help the users that can't attach the web link for you ask them to press into the sidebar, paste the web link then press Summarize button.
    you can recommend a books according to the user's needs, you can ask him to recommend the books. Recommend the book name, edition, and description.
    text:{quesion}"""),
    ]

chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API, temprature=0)

def web_scrap(url):
  response = requests.get(url)
  soup = bs4.BeautifulSoup(response.content, "html.parser")
  paragraphs = soup.find_all("p")
  doc = ""
  for p in paragraphs:
      doc += p.text
  return doc

def file_scrap(path):
  if path.split('.')[1] == "pdf":
    loader = PDFPlumberLoader(path)
  else:
    loader = TextLoader(path)
  doc = loader.load()
  d = ""
  for i in doc:
    d += i.page_content
  return d

def summarize(message_list, type="message"):
    if type=='message':
        for m in message_list:
            if m['type']=='HumanMessage':
                messages.append(HumanMessage(content = m['content']))
            elif m['type']=='AIMessage':
                messages.append(AIMessage(content = m['content']))
    else:
       messages.append(HumanMessage(content = message_list))
    # print(messages)
    answer = chat(messages)
    # print(answer.content)
    # if type !="message":
    #     del messages[-1]
    # messages.append(answer)
    return answer.content

def chatting(type="message", link="", path="", message=""):
    if type == 'link':
      doc = web_scrap(link)
      answer = summarize(doc, type=type)
    elif type =="file":
      doc = file_scrap(path)
      answer = summarize(doc, type=type)
    elif type =="message":
      answer = summarize(message, type=type)
    return answer


# ______________________________________________________

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'  # فولدر حفظ الملفات
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # الحد الأقصى لحجم الملف (مثلاً 16MB)

# تأكد إن الفولدر موجود
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # return render_template('upload.html')  # صفحة فيها form للرفع
    return "<p>Waraq Chatbot</p>"

@app.route('/upload', methods=['POST'])
def upload_file():
    print('**************************')
    if 'pdf_file' not in request.files:
        return 'No file part'

    file = request.files['pdf_file']
    
    if file.filename == '':
        return 'No selected file'

    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'myfile.pdf')
        file.save(filepath)
        # file_content = file_scrap(filepath)
        output = chatting(type='file',path=filepath)
        return jsonify({'response':output})

        # return f'File uploaded successfully: {file.filename}'

    else:
        return 'Only PDF files are allowed.'

@app.route('/link', methods=['POST'])
def search_link():
    textjson = request.json
    link_value = textjson['link']
    output = chatting(type='link',link=link_value)
    return jsonify({'response':output})


@app.route('/predict',methods=['POST'])
def predict():
    
    """
    # *** input shape ***
    {
    'messages': [
                    {'content':'text text text text','type':'HumanMessage'}
                    {'content':'text text text text','type':'AIMessage'}
                ]
    }
    """
    data = request.get_json()
    # message = data.get('messages',[])
    # print(type(data))
    output = chatting(message=data, type='message')
    return jsonify({'response':output})

if __name__ == '_main_':
    app.run(debug=True)

