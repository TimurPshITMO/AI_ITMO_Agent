from gptReqManager import checkValid, firstTry, classify, outSearch

from yandex_cloud_ml_sdk import YCloudML

# (Волшебные переменные, дающие доступ ко всем моим кровным)
# Не разобрался с этим вашим .env, сделал конфигом, все равно
# не на инфобезе учусь (надеюсь, не забыл в гитигнор кинуть)
from conf import FOLDER_ID, AUTH_KEY

def sendPrompt(prompt, log):

    """
    Роутер:

    Координирует задействование агентов и порядок их использования
    """

    log('-----STARTING PROCESSING PROMPT-----')
    
    sdk = YCloudML(
        folder_id=FOLDER_ID,
        auth=AUTH_KEY
    )

    # Запрос пользователя валиден и по адресу?
    valid = checkValid(sdk, prompt, log)

    if not valid['valid']:
        
        # Нет!? Ну и зачем он тогда? Меняй 
        return {'answer' : None, 'reasoning' : valid['text'], 'sources':[]}
    
    # Приятно... А яндекс уже знает ответ?
    ft = firstTry(sdk, prompt, log)

    if ft['valid']:

        # Джиназес, тогда лови ответ, друг
        return classify(sdk, prompt, ft['text'], log)
    
    else:

        # Неприятно... Ладно, сами найдем, не страшно
        ds = outSearch(sdk, prompt, log)

        # Ну тут уже без вариантов
        return classify(sdk, prompt, ds, log)