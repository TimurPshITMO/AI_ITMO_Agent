from gptReqManager import checkValid, firstTry, classify, outSearch
from yandex_cloud_ml_sdk import YCloudML
from config import FOLDER_ID, AUTH_KEY

def sendPrompt(prompt, log):
    log('-----STARTING PROCESSING PROMPT-----')
    
    sdk = YCloudML(
        folder_id=FOLDER_ID,
        auth=AUTH_KEY
    )

    valid = checkValid(sdk, prompt, log)
    if not valid['valid']:
        return {'answer' : None, 'reasoning' : valid['text'], 'sources':[]}
    
    ft = firstTry(sdk, prompt, log)
    if ft['valid']:
        return classify(sdk, prompt, ft, log)
    else:
        ds = outSearch(sdk, prompt, log)
        return classify(sdk, prompt, ds, log)