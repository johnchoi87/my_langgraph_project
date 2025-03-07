import streamlit as st
from streamlit_js_eval import get_geolocation
from my_langgraph_project.utils.graph import create_workflow
from langchain_core.messages import ChatMessage
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import googlemaps
import os

load_dotenv()
# Google Maps API 키 설정
key = os.getenv("GMAPS_API_KEY")
gmaps = googlemaps.Client(key=key)


def get_city_from_coordinates(lat: float, lng: float) -> str:
    try:
        # Reverse Geocoding 요청
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng), language='ko')
        print(reverse_geocode_result)
        # 도시 이름 추출
        if reverse_geocode_result:
            result_address = ""
            locality = ""
            administrative_area_level_1 = ""
            sublocality_level_1 = ""
            sublocality_level_2 = ""
            for geocode_result in reverse_geocode_result:
                for component in geocode_result['address_components']:
                    if 'locality' in component['types']:
                        locality = component['long_name']
                    if 'administrative_area_level_1' in component['types']:
                        administrative_area_level_1 = component['long_name']
                    if 'sublocality_level_1' in component['types']:
                        sublocality_level_1 = component['long_name']
                    if 'sublocality_level_2' in component['types']:
                        sublocality_level_2 = component['long_name']

            if sublocality_level_1 is None or sublocality_level_1 == "":
                sublocality_level_1 = locality
            #result_address = f"도시 이름: {locality}, {administrative_area_level_1}, {sublocality_level_1}, {sublocality_level_2}"
            result_address = f"{administrative_area_level_1} {sublocality_level_1} {sublocality_level_2}"
            #print(result_address)
            return result_address
        else:
            return "결과를 찾을 수 없습니다."
    except Exception as e:
        return f"오류 발생: {e}"


st.set_page_config(page_title="나만의 알프레드", page_icon="🧑‍⚖️")
st.title('나만의 알프레드 🧑‍⚖️')


if "my_location" not in st.session_state:
    location_data = get_geolocation()
    if location_data is not None and "coords" in location_data:
        my_coords = location_data["coords"]
        latitude = my_coords["latitude"]
        longitude = my_coords["longitude"]
        #latitude = 38.182081
        #longitude = 128.549606
        my_address = get_city_from_coordinates(latitude, longitude)
        st.session_state["my_location"] = my_address
        print(my_address)
    else:
        print("No location data")

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

    template = PromptTemplate(
        input_variables=["user_input", "my_location"],
        template= """
        당신은 친절하고 유쾌한 AI입니다! 주어진 메시지 입력에 대한 🤖💡답변에 이모지를 적극 활용하고, 명확하고 간결한 방식으로 설명해주세요! 한글로 대답해주세요!🚀🔥
        질문에 대상 장소에 대한 정보가 없다면 사용자의 현재 위치 정보를 참고하여 답변을 해주세요.
        사용자가 특정 도시의 날씨를 요청하면, 해당 도시 이름을 영어로 변환하여 get_weather 도구를 호출하세요. "
        예: '서울 날씨를 알려줘' -> get_weather(location='seoul')"
        사용자가 특정 도시의 근처 장소를 요청하면, 해당 도시 이름을 영어로 변환하여 get_places 도구를 호출하세요. "
        
        질문: {user_input}
        현재 위치: {my_location}
        """
    )

    final_message = ""  # 마지막 메시지를 저장할 변수
    prompt_text = template.format(user_input=chat_input, my_location=st.session_state["my_location"])
    #print(str(location_data["coords"]))
    for chunk in st.session_state["graph"].stream(
            {
                "messages": [
                    ("human", prompt_text),
                    #("human", f'{chat_input} coordinates: {str(location_data["coords"])}')
                ],
            },
            stream_mode="values"
    ):
        chunk["messages"][-1].pretty_print()
        final_message = chunk["messages"][-1].content

    with st.chat_message("ai"):
        st.write(chunk["messages"][-1].content)

    add_history("ai", final_message)
