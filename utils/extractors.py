import re
def sqlExtractor(message):
    matchCodeblock = re.findall(r"```sql\n(.*)```", message, re.DOTALL)
    if(matchCodeblock):
        return matchCodeblock[-1]
    
    matchCodeblock = re.findall(r"```(.*)```", message, re.DOTALL)
    if(matchCodeblock):
        return matchCodeblock[-1]
    
    return message

def jsonExtractor(message):
    matchCodeblock = re.findall(r"```json\n(.*?)```", message, re.DOTALL)
    if(matchCodeblock):
        return matchCodeblock
    
    matchCodeblock = re.findall(r"```(.*?)```", message, re.DOTALL)
    if(matchCodeblock):
        return matchCodeblock
    
    return message
