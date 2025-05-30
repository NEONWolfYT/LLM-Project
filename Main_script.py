from functions import QwenChatbot,get_reqs,create_excel
from rouge import Rouge
import json
import evaluate

if __name__ == "__main__":
    chatbot = QwenChatbot()
    with open("/kaggle/input/llm-testing-5/references-10.csv", "r", encoding="utf-8") as f:
        references = [line.strip() for line in f.readlines()]

    predictions = []
    arr = []
    for req in get_reqs('/kaggle/input/llm-testing-5/test-10.csv'):
        user_input = req
        response = chatbot.generate_response(user_input)
        answer = response.rsplit('\n\n', 1)[-1].strip()
        predictions.append(answer)
        if answer != ("Попробуйте другой товар"):
            data = {
                key.strip(): value.strip()
                for key, value in (item.split(":", 1) for item in answer.split(";") if item.strip())
            }
            # Преобразование словаря в JSON-строку
            json_string = json.dumps(data, ensure_ascii=False)
            arr.append(json_string)

    # Оценка с помощью ROUGE

    rouge = evaluate.load('rouge')

    results = rouge.compute(predictions=predictions, references=references)
    print(results)

create_excel(json_string,'Example.csv','Лист 1')
