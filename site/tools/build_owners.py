import json, urllib.request, time
RPC="https://rpc.mainnet.chain.robinhood.com"; C="0xebeea5e9b5483d53df59da10dd753ee5a33baa19"
own={}
for s in range(1,1301,10):
    batch=[{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":C,"data":"0x6352211e"+hex(i)[2:].rjust(64,"0")},"latest"]} for i in range(s,min(s+10,1301))]
    for t in range(6):
        try:
            r=json.load(urllib.request.urlopen(urllib.request.Request(RPC,json.dumps(batch).encode(),{"Content-Type":"application/json","User-Agent":"Mozilla/5.0"}),timeout=30));break
        except Exception as e: time.sleep(2+t*2)
    for x in r: own[x["id"]]="0x"+x["result"][-40:]
    time.sleep(0.4)
w={}
for i,a in sorted(own.items()): w.setdefault(a.lower(),[]).append(i)
json.dump(w,open("site/world/owners.json","w"),separators=(",",":"))
print(len(own),len(w),len(w.get("0xe7d8a2c008a24c9877447df0876af436ab217041",[])))
