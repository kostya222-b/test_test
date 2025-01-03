import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        'name': 'SEARCH ANSWERS',
        'description': 'API для поиска правильных ответов.',
    }
]

origin_endpoint = [
    'https://iomqt-vo.edu.rosminzdrav.ru',
    'https://iomqt-spo.edu.rosminzdrav.ru',
    'https://iomqt-nmd.edu.rosminzdrav.ru'
]

app = FastAPI(
    root_path="/api",
    title='API for SEARCH ANSWERS',
    description='API для поиска правильных ответов',
    version='0.1.0',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_endpoint,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_answers(text, quest, original_text):
    true_answers_list = []
    beg_beg = 0
    for _ in range(text.count(quest)):
        begin = text.find(quest, beg_beg)
        if begin == -1:
            break
        beg_beg = begin + len(quest)
        num_quest = original_text[original_text.rfind('\n', 0, begin):begin - 2].strip().replace('.', '')
        end1 = original_text.find('\n\n', begin + len(quest))
        end2 = original_text.find(f'{int(num_quest) + 1}. ', begin + len(quest))
        end = min(filter(lambda val: val > 0, [end1, end2]))
        answers = original_text[begin + len(quest):end].strip()
        answers_list = answers.split('\n')
        for i in answers_list:
            if i[0] == '~' or i[-1] == '+':
                if i[-1] == '+':
                    cleaned_i = i[:-1].rstrip(';.').lstrip('~').strip()
                    true_answers_list.append(cleaned_i)
    return true_answers_list

@app.get('/test')
async def test(quest: str = None):
    if not quest:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    quest += '\n'
    this_folder = os.getcwd()
    with open(f'{this_folder}/src/myans.txt', 'r', encoding="utf-8") as f:
        text = f.read()

    # Первый поиск как есть
    true_answers_list = find_answers(text, quest, text)

    if not true_answers_list:
        # Преобразование в нижний регистр и повторный поиск
        quest_lower = quest.lower()
        text_lower = text.lower()
        true_answers_list = find_answers(text_lower, quest_lower, text)

    if not true_answers_list:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

    new_true_answers_list = []
    for i in true_answers_list:
        new_true_answers_list.append(i.replace('а', 'a').replace('о', 'o'))
        new_true_answers_list.append(i.replace('a', 'а').replace('o', 'о'))

    return true_answers_list + new_true_answers_list

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
