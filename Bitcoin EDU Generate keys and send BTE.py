#Anton Brottare 
import requests
import json
import random
import binascii
#---------------------------------------#
from pycoin import ecdsa, key, encoding
import hashlib


#rpc Variabler
rpc_user='anton'
rpc_pass = 'brottare'
url = 'http://%s:%s@localhost:8332'%(rpc_user, rpc_pass)
headers = {'content-type':'application/json'}



def MainMenu():
    print("1. Genera nycklar")
    print("2. Skicka BTE")
    choice = input("Välj funktion ")
    MakeDecision(choice)

#Funktionsväljare
def MakeDecision(yourChoice):
    if yourChoice == '1':
        choice = input("Ange ett tal för generering alt 0 för ett 'slumpmässigt tal': ")
        GenerateKeys(choice)
    elif yourChoice == '2':
        SendBTE()        
    else:
        print("Felaktig input.. Försök igen..")
        MainMenu()


def double_sha256(x):
    return hashlib.sha256(hashlib.sha256(binascii.unhexlify(x)).digest()).hexdigest()
def hash160(x):
    return hashlib.new('ripemd160',hashlib.sha256(binascii.unhexlify(x)).digest()).hexdigest()

def GenerateKeys(indata):
    #Secret integer
    if indata == '0':
        k = random.randrange(1,1000000) #Valde bara mellan 1-1000,000 som ex. randrange är ju inte totalt random heller..
    else:
        k = int(indata)

    #Kodar om secret integer till uncompressed public key
    secp = ecdsa.secp256k1
    G = secp.generator_secp256k1
    P = k * G

    #Kodar om P till compressed format
    x = '%064x' % P.x()
    comp_pk = ('02' if P.x() % 2 == 0 else '03') + x

    #Kodar om secret integer till wif format 
    wif = encoding.secret_exponent_to_wif(k) #Skrev ingen kod för att göra om till wif då det fanns en färdig metod för det.. 

    print("Public key")
    print("   Public uncompressed key is:")
    print("    x:",P.x())
    print("    y:",P.y())
    print("   Public compressed key is:")
    print("    ",comp_pk)

    print("------------")
    print("Private key")
    print("   Tal: ",k)
    print("   Hex: ",hex(k)[2:])
    print("   Wif: ", wif)

    publicPair = [P.x(),P.y()] #Array som sparar X,Y för att kunna kodas om till bitcoin address
    print("------------------")
    print("Bitcoin Address: ") #Samma sak här, finns färdiga metoder för att koda om till bitcoin address
    print("   Uncompressed: ",encoding.public_pair_to_bitcoin_address(publicPair,False))
    print("   Compressed:   ",encoding.public_pair_to_bitcoin_address(publicPair,True))

def validateAddress(x):
    payload = {
        "method":"validateaddress",
        "params": [x]
        }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return(response['result']['scriptPubKey'])

def SendBTE():
    
    sendFrom = input("Ange adress att skicka från: ")
    sendTo = input("Ange adress att skicka till: ")
    value = input("Ange belopp: " )
    spendable = input("Ange spenderbart belopp (för att inte bli av med changen): ")
    change = input("Ange växeladress: ")
    fee = input("Ange fee: ")
    wifKey = input("Ange wif:")
    tx = input("Ange TX: ")

    pubKeyHash = validateAddress(sendFrom)
    
     
    # CREATE
    changeVal = float(spendable) - float(value) - float(fee)
    print(str(changeVal))
    payload = {
        "method":"createrawtransaction",
        "params": [[{"txid":tx,"vout":0}],{sendTo:value,change:changeVal}]
        }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    transaction = response['result']
   
    
    #SIGN
    payload = {
        "method":"signrawtransaction",
        "params": [transaction,[{"txid":tx,"vout":0,"scriptPubKey":pubKeyHash}],[wifKey]]
        }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(str(response))
    
    hextx = response['result']['hex']
    #SEND
    payload = {
        "method":"sendrawtransaction",
        "params": [hextx,True]
        }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(str(response))


MainMenu()

