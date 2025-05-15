import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import bs4
from langchain.document_loaders import PDFPlumberLoader, TextLoader
import requests
# import validators

API = st.secrets["API"]

st.set_page_config(page_title="Waraq Bot", page_icon='images/icon.png')

if "messages" not in st.session_state:
    st.session_state.messages = [
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


if "chat" not in st.session_state:
    st.session_state.chat = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=API, temprature=0)

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

def summarize(m, type="message"):
    st.session_state.messages.append(HumanMessage(content=m))
    answer = st.session_state.chat(st.session_state.messages)
    if type !="message":
        del st.session_state.messages[-1]
    st.session_state.messages.append(answer)
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

st.columns([1,1,1])[1].image("images/chatbot.png")
st.columns([1,1,1])[1].image("images/horizontal2.png")


st.info("Easy Summarize your text documents, Web contents, LinkedIn posts, pdf, and text files...")
st.write("---")

HORIZONTAL_RED = "images/horizontal.png"
ICON_RED = "images/icon.png"

st.logo("images/horizontal2.png", icon_image="images/icon.png")


# st.sidebar.info("Octobot")
st.sidebar.write("Summarize from:")
link = st.sidebar.text_input("Link")
bt = st.sidebar.button("Summarize")
st.sidebar.write("---")
file = st.sidebar.file_uploader("Browse Files...", type=["pdf", "txt"])
bt_file = st.sidebar.button("Summarize ")

for m in st.session_state.messages:
    if m.type == "system":
        continue
    if m.type == "human":
        st.chat_message("user").markdown(m.content)
    else:
        st.chat_message("assistant").markdown(m.content)
    # st.write("---")

if len(st.session_state.messages)==1:
    st.chat_message("assistant").markdown('أهلا, اقدر اساعدك ازاي؟')

message = st.chat_input("Say something")

if message is None:
    pass
else:
    st.chat_message("user").markdown(message)
    answer = chatting(message=message)
    st.chat_message("assistant").markdown(answer)

if bt_file:
    if file is not None:
        with open(file.name, 'wb') as f:
            f.write(file.getbuffer())
        answer = chatting(type='file', path=file.name)
        st.chat_message("assistant").markdown(answer)
        del file

if bt:
    if link is not "":
        # is_valid = validators.url(link)
        # if is_valid:
        answer = chatting(type="link", link=link)
        st.chat_message("assistant").markdown(answer)
