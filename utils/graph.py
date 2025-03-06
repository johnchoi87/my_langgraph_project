import os

from langchain_google_community import GooglePlacesTool
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langchain_community.utilities import OpenWeatherMapAPIWrapper

from utils.state import ServiceState
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from langgraph.prebuilt import ToolNode
import streamlit as st
import googlemaps

load_dotenv()
# Google Maps API 키 설정
key = os.getenv("GMAPS_API_KEY")
gmaps = googlemaps.Client(key=key)


# LangChain Tool 정의
@tool("get_city_from_coordinates")
def get_city_from_coordinates(coordinates: str) -> str:
    """
    주어진 위도와 경도 좌표 (latitude, longitude)로부터 도시 이름을 반환합니다.
    입력 형식: "latitude,longitude" (예: "37.5665,126.9780")
    """
    try:
        # 입력 좌표 파싱
        lat, lng = map(float, coordinates.split(','))

        # Reverse Geocoding 요청
        reverse_geocode_result = gmaps.reverse_geocode((lat, lng), language='ko')
        print(reverse_geocode_result)
        # 도시 이름 추출
        if reverse_geocode_result:
            for component in reverse_geocode_result[0]['address_components']:
                if 'locality' in component['types'] or 'sublocality_level_1' in component['types']:
                    return f"도시 이름: {component['long_name']}"
            return "도시 정보를 찾을 수 없습니다."
        else:
            return "결과를 찾을 수 없습니다."
    except Exception as e:
        return f"오류 발생: {e}"


@tool
def get_weather(location: str):
    """Call to get the current weather."""
    with st.spinner("날씨 정보를 가져오는 중입니다."):
        weather = OpenWeatherMapAPIWrapper()
        weather_data = weather.run(location)
        print(weather_data)
    return weather_data


@tool
# def get_places(location: str, category: str):
def get_places(query: str):
    """Get a list of places"""
    with st.spinner("장소 정보를 가져오는 중입니다."):
        places = GooglePlacesTool()
        places_data = places.run(query)
        print(places_data)
    return places_data


tools = [get_city_from_coordinates, get_weather, get_places]

tool_node = ToolNode(tools)
model_with_tools = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def call_model(state: MessagesState):
    print(state)
    messages = state["messages"]
    # 프롬프트에 이모지를 추가하여 더 친근하고 생동감 있게 만듦 🎨✨
    messages.append({
        "role": "system",
        "content": "당신은 친절하고 유쾌한 AI입니다! 🤖💡답변에 이모지를 적극 활용하고, 명확하고 간결한 방식으로 설명해주세요! 한글로 대답해주세요!🚀🔥"
                   "사용자가 특정 도시의 날씨를 요청하면, 해당 도시 이름을 영어로 변환하여 get_weather 도구를 호출하세요. "
                   "예: '서울 날씨를 알려줘' -> get_weather(location='seoul')"
                   "입력 프롬프트에 도시에 대한 정보가 없으면 get_city_from_coordinates 도구를 사용하여 도시 이름을 찾아주세요. "
    })
    with st.spinner("AI가 답변을 준비하고 있습니다."):
        response = model_with_tools.invoke(messages)
    return {"messages": [response]}


def create_workflow():
    workflow = StateGraph(MessagesState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    app = workflow.compile()
    return app


'''
for chunk in app.stream(
        # {"messages": [("human", "분당 날씨는?")]}, stream_mode="values"
        # {"messages": [("human", "동대문구 장안1동 근처 아파트?")]},
        # {"messages": [("human", "오늘 서울에서 운동하기 날씨가 어때?")]},
        # {"messages": [("human", "여의도에서 따뜻한 국물 요리 맛집을 소개해줘")]},
        {"messages": [("human", "현재 서울에 연날리기 하기에 어떄?")]},
        stream_mode="values"
):
    chunk["messages"][-1].pretty_print()
    '''
