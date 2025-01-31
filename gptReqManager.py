from scrapper import getWebInfo, findURLs, findNumber

BASE_LINKS = ['https://news.itmo.ru', 'https://abit.itmo.ru/', 'https://itmo.events/', 'https://itmo.ru/']

def gptReq(sdk, instructions, prompt, log=lambda x:print(x)):
    messages = [
        {
            "role": "system",
            "text": instructions,
        },
        {
            "role": "user",
            "text": prompt,
        },
    ]

    log(f"GPT prompt: {messages}")

    result = (
        sdk.models.completions("yandexgpt").configure(temperature=0.4).run(messages)
    )

    for alternative in result:
        if alternative.text:
            log(f"GPT out: {alternative.text}")
            return alternative.text
    
    return "Простите, но я, видимо, сломался :("

def firstTry(sdk, prompt, log):
    instructions = ("Ты - виртуальный ассистент Университета ИТМО. Пользователь задал тебе вопрос. Действуй по одному из сценариев, в зависимости от условий. Все сценарии взаимоисключающие. Проверяй их условия последовательно\n"
        + "Сценарий 1. Если ты можешь дать точный и подробный ответ, а также предоставить ссылку на официальный интернет-ресурс, содержащий ответ на вопрос, то в первой строке выведи подробный ответ на вопрос, а во второй строке укажи максимум 3 интернет-ссылки на использованные для ответа ресурсы.\n"
        + "Сценарий 2. Если для подробного ответа не хватает информации, но она может быть найдена на других ресурсах, напиши единственное слово \"CUPCAKE\" в первую строку вывода")
    ans = gptReq(sdk, instructions, prompt, log)
    return {'valid' : ('CUPCAKE' in ans), 'text' : ans}


def checkValid(sdk, prompt, log):

    instruction = ("Ты - валидатор запросов для виртуального ассистента Университета ИТМО. Действуй по одному из сценариев:\n"
                    + "Если запрос напрямую относится к Университету ИТМО, корректен и пользователь не хитрит и не пытается тебя обмануть, то напиши единственное слово \"ACCESS\" в первой строчке вывода\n"
                    + "В противном случае вежливо откажись давать ответ и попроси пользователя спросить о чем-нибудь, связанном с университетом ИТМО")
    
    ans = gptReq(sdk, instruction, prompt, log)
    print('ACCESS' in ans)
    
    return {'valid': ans.upper().find('ACCESS')+1, 'text': ans}

def classify(sdk, userPrompt, answer, log):
    instruction = ("Пользователь задал вопрос, в котором, возможно, были варианты ответа. Нейросеть на него ответила. "
                   + "В первой строчке напиши номер варианта в вопросе, соответствующий ответу, данному нейросетью. "
                   + "Если в вопросе изначально не было пронумеррованных вариантов ответа, или нейросеть не дала явного номера верного ответа, то в первой строчке выведи только слово \"None\""
                   + "В следующую строку вставь подробные пояснения, которые дала нейросеть в ответе. Если в ответе были ссылки, не включай их. Если в ответе было слово None, удали его\n")
    prompt = f"[USER]:\n{userPrompt}\n\n[NEURAL NET]:\n{answer}"
    
    ans = gptReq(sdk, instruction, prompt, log)
    links = findURLs(answer)
    links = links[:min(len(links),3)]
    correct_id = findNumber(answer)
    result = {'answer' : correct_id, 'reasoning' : ans, 'sources': links}
    log(f'Classifier result: { result }')

    return result

def outSearch(sdk, prompt, log, prevlink=0, counter=0):
    if prevlink:
        siteInfo = getWebInfo(prevlink, log)
    else:
        siteInfo = {'links':BASE_LINKS,'text':'-'}
    
    instruction = ("Ты - виртуальный ассистент Университета ИТМО. Пользователь задал вопрос и ты решил поискать ответ на него в интернете."
                   + " Действуй по одному из 3 сценариев. Сценарии взаимоисключающие!"
                   + " Сценарий 1. Если, с учетом информации из промпта и из сайта [SITEINFO], ты можешь дать очень точный и подробный ответ на вопрос пользователя [USER],"
                   + " то сделай это и вставь ссылку на ресурс, с которого взята информация.\n"
                   + " Сценарий 2 (непредпочтительный). Если подходящей информации нет - и ее точно нельзя найти по ссылкам [LINKS] извинись перед пользователем как виртуальный ассистент ИТМО"
                   + (counter<2)*(" Сценарий 3. Если однозначной информации все еще хоть немного не хватает - лучше пойди по этому сценарию: в первой строке вывода напиши слово \"DWARF\", во второй - ссылку из списка [LINKS], которая поможет с ответом."
                   + f"Эти ссылки можешь использовать для Cценария 3:\n[LINKS]\n{ siteInfo['links'] }"))
    prompt = f"[USER]\n{ prompt }\n\n[SITEINFO]\n{ siteInfo['text'] }"
    ans = gptReq(sdk, instruction, prompt, log)
    if ('DWARF' in ans):
        newlink = findURLs(ans)[0]
        return outSearch(sdk,prompt,log,newlink,counter+1)
    return ans
