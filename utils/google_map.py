from langchain.tools import tool
from dotenv import load_dotenv
import googlemaps

# Google Maps API 키 설정
load_dotenv()
key = "AIzaSyB0eR19fETo1_qodLhComhcBlte-y7ny6o"
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


# 테스트 실행
if __name__ == "__main__":
    coordinates = "37.5665,126.9780"  # 서울 좌표 예제
    coordinates = "37.566705, 127.073439"
    coordinates = "37.749844, 128.902967"
    result = get_city_from_coordinates(coordinates)
    print(result)
