# Anton Brottare

import requests, json, struct, binascii, hashlib, time
from datetime import datetime
from decode_block import decodeBlock, decodeHeader

RPC_USER = 'anton'
RPC_PASS = 'brottare'
ux = binascii.unhexlify

BEST_BLOCK_FILE = 'bestblock.bin'

def writeblock(blockbin):
    print('Writing binary block data to:',BEST_BLOCK_FILE)
    with open(BEST_BLOCK_FILE, 'wb') as f:
        f.write(blockbin)

# Make RPC call to local node

def do_rpc(method, *args):
    url = 'http://%s:%s@localhost:8332' % (RPC_USER, RPC_PASS)
    headers = {'content-type': 'application/json'}
    payload = {
        "method": method,
        "params": list(args),
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    # HTTP status codes starting with 4xx indicate developer errors
    if r.status_code >= 400 and r.status_code < 500:
        r.raise_for_status()
    r = r.json()
    if r.get('error'):
        print('RPC API error:', r['error'])
    return r['result']

################################### Start of actual mining code

blocktemp = do_rpc('getblocktemplate')
#print(json.dumps(blocktemp, sort_keys=True, indent=2))

prevBlockHash = blocktemp['previousblockhash'] #Header
prevBlock = do_rpc("getblock",prevBlockHash)
merkleRoot = prevBlock['merkleroot']                 #Header
target = blocktemp['target']
version = blocktemp['version']                   #Header
height = blocktemp['height']
minTime = blocktemp['mintime']                  
bits = blocktemp['bits']                        #Header
timestamp = blocktemp['curtime']              #Header
print("Previous: ",prevBlockHash,'\nTarget:   ',target)

height = bytes( struct.pack('<H',height).hex(), 'ascii')


# #COINBASE
coinbase = b'02000000' \
           b'0001' \
           b'01' \
           b'0000000000000000000000000000000000000000000000000000000000000000' \
           b'ffffffff' \
           b'03' \
           b'02' + height +\
           b'ffffffff0200f2052a010000001600140b70136f1baa3ac39c4cd8b288dfa2a3dda146530000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf90120000000000000000000000000000000000000000000000000000000000000000000000000'

coinbaseNoSegwit = b'02000000010000000000000000000000000000000000000000000000000000000000000000ffffffff0302' + height + b'ffffffff0200f2052a010000001600140b70136f1baa3ac39c4cd8b288dfa2a3dda146530000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf900000000'


sha256 = lambda x: hashlib.sha256(x).digest()
sha256d = lambda x: sha256(sha256(x))
#Headerformattering
version = struct.pack("<I",version)
timestamp = struct.pack("<I", timestamp)
prevBlockHash = ux(prevBlockHash[::-1])
txidCoinbase = binascii.hexlify(sha256d(ux(coinbaseNoSegwit)[::-1])).decode()
merkleRoot = txidCoinbase
merkleRoot =  ux(merkleRoot)[::-1]
bits = ux(bits)[::-1]
target = target.encode()
header = version+prevBlockHash+merkleRoot+timestamp+bits


def DecodeBest(hdr,coinbase):
    noTrans = b'01'
    block = binascii.hexlify(hdr) + noTrans+coinbase
    decodeBlock(binascii.unhexlify(block))
    

nonce = struct.pack("<I",0x00000000)
keepMining = True
firstRun = True
completeHeader = ""
bestHeader =""

runtimes = 0
while keepMining == True:
    completeHeader = header + nonce

    newblockhash = sha256d(completeHeader)[::-1]
    a = struct.unpack("<I",nonce)[0]+1
    nonce = struct.pack("<I",int(hex(a),16))

    if firstRun == True:
       besthash = newblockhash
       bestHeader = completeHeader
       firstRun = False 

    compHash = binascii.hexlify(newblockhash)
    if compHash < target:
        keepMining = False
        print("Valid block found!\n",binascii.hexlify(newblockhash).decode("ascii"))
         
    if newblockhash < besthash:
        bestHeader = completeHeader
        besthash = newblockhash
        print("New best block found")
        print("Current best block: ",binascii.hexlify(besthash).decode("ascii"))
        
    if runtimes > 1000000:
        runtimes = 0
        DecodeBest(bestHeader,coinbase)
        

    runtimes = runtimes +1
        