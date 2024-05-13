from api.main import app
from fastapi.testclient import TestClient
from api.schemas.schemas import Difficulty, WordInfo

client = TestClient(app)
TEST_OBJECTS = [
    ("Harry Potter", Difficulty.Easy),
    ("Harry Potter", Difficulty.Medium),
    ("Harry Potter", Difficulty.Hard),
    ("Star Wars", Difficulty.Easy),
    ("Star Wars", Difficulty.Medium),
    ("Star Wars", Difficulty.Hard)
]


def test_get_games():
    success_rate = []

    for topic, difficulty in TEST_OBJECTS:
        response = client.post("/games/?topic=" + topic +
                               "&difficulty=" + difficulty.value)
        print(response.json())

        # Assert that the response status code is 200
        assert response.status_code == 200

        # Assert that the response contains a list of words
        assert len(response.json()) > 0

        success_count = 0

        # Assert that the return objects are of type WordInfo
        for word in response.json():
            assert word.get("word") is not None
            assert word.get("definition") is not None
            # Count the number of successful words within the difficulty range
            if Difficulty.Easy == difficulty:
                if 1 <= len(word.get("word")) <= 4:
                    success_count += 1
            elif Difficulty.Medium == difficulty:
                if 4 <= len(word.get("word")) <= 7:
                    success_count += 1
            else:
                if 7 <= len(word.get("word")):
                    success_count += 1

            # Append the success rate for the current test object
            success_rate.append(success_count / len(response.json()))
    print(sum(success_rate) / len(success_rate) * 100)
