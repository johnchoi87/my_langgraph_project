import streamlit as st
from streamlit_js_eval import get_geolocation
from my_langgraph_project.utils.graph import create_workflow
from langchain_core.messages import ChatMessage

st.set_page_config(page_title="나만의 알프레드", page_icon="🧑‍⚖️")
st.title('🧑안녕하세요 알프레드입니다! ')
location_data = get_geolocation()
print(location_data)

# 대화 내용을 저장할 세션 상태를 초기화합니다.
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# 사용자와 AI의 대화 내용을 출력합니다.
def print_history():
    for msg in st.session_state["messages"]:
        st.chat_message(msg.role).write(msg.content)


# 사용자와 AI의 대화 내용을 추가합니다.
def add_history(role, content):
    st.session_state["messages"].append(ChatMessage(role=role, content=content))


# 사용자와 AI의 대화 내용을 출력합니다.
print_history()

if "graph" not in st.session_state:
    st.session_state["graph"] = create_workflow()

if chat_input := st.chat_input('지역 정보나 날씨 관련된 질문을 남겨주세요'):
    add_history("user", chat_input)
    st.chat_message("user").write(chat_input)

    final_message = ""  # 마지막 메시지를 저장할 변수

    print(str(location_data["coords"]))
    for chunk in st.session_state["graph"].stream(
            {
                "messages": [
                    ("human", f'{chat_input} coordinates: {str(location_data["coords"])}')
                ],
            },
            stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
        final_message = chunk["messages"][-1].content

    with st.chat_message("ai"):
        st.write(chunk["messages"][-1].content)

    add_history("ai", final_message)
