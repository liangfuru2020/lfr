import requests
import io,sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
r = requests.get("https://www.taobao.com/")

print(r.status_code)
r.encoding=None
print(r.encoding)
print(r.text)
