import requests
import base64
import os


def extract_answer(structure):
    if not structure or not structure[0]:
        return None

    first_element = structure[0]

    if len(first_element) < 2:
        return None

    answer = first_element[1]
    return answer[-1]


def main():

    question = 'Please describe, what you see?'
    gradio_url = "http://127.0.0.1:7860/"

    # Iterate over jpg, png, jpeg files in the current directory
    for filename in os.listdir("."):
        if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
            with open(filename, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            print('\nUploading image:', filename)
            payload = {
                "data": [
                    f"data:image/jpeg;base64,{base64_image}",
                    "vision",
                    None
                ]
            }
            response = requests.post(gradio_url + "run/upload_image", json=payload)
            data = response.json()["data"]

            print('Sending question:', question)
            response = requests.post(gradio_url + "run/ask_question", json={
                "data": [
                    question,
                    [["Hi","Hello"],["1 + 1","2"]],
                    None,
                ]
            }).json()
            data = response["data"]

            print('Waiting for answer..')
            response = requests.post(gradio_url + "run/get_answer", json={
                "data": [
                    [["hi","Hello"],["1 + 1","2"]],
                    None,
                    None,
                    1,
                    1,
                    1000,
                ]
            }).json()
            data = response["data"]
            print('Answer:', extract_answer(data))


if __name__ == '__main__':
    main()
