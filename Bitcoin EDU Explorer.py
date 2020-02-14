#Anton Brottare 
import requests
import json
from datetime import datetime

#rpc Variabler
rpc_user='anton'
rpc_pass = 'brottare'
url = 'http://%s:%s@localhost:8332'%(rpc_user, rpc_pass)
headers = {'content-type':'application/json'}

choice = 0

def MainMenu():
    print("  Bitcoin Edu Explorer  \n========================")
    print("Antal Block: "+str(BlockCount()))
    print("Senaste Block: "+str(GetBlockHash(BlockCount())))
    print("MemPool Size: "+MemSize()+" st transaktioner")
    print("Connections : "+ConCount()+" noder")
    print("========================\nMeny")
    PrintChoices()
    choice = input("Välj funktion: ")
    MakeDecision(choice)

def PrintChoices():
    print(" 1. Visa block (ange nr)")
    print(" 2. Visa block (ange hash)")
    print(" 3. Visa transaktion")
    print(" 4. Lista outputs för adress")
    
    
#Hämtar antalet blocks    
def BlockCount():
    payload = {
    "method":"getblockcount"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return(response['result'])

#Hämtar hashen för ett definierat block
def GetBlockHash(block):
    payload = {
    "method":"getblockhash",
    "params":[block]
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return(response['result'])

#Hämtar nuvarande storlek på mempoolen
def MemSize():
    payload = {
    "method":"getmempoolinfo"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return(str(response['result']['size']))

#Hämtar antal connections
def ConCount():
    payload = {
    "method":"getconnectioncount"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    return(str(response['result']))

#Funktionsväljare
def MakeDecision(yourChoice):
    if yourChoice == '1':
        block = input("Ange blocknr: ")
        ShowBlock(block)
    elif yourChoice == '2':
        blockhash = input("Ange blockhash: ")
        ShowBlock(blockhash)        
    elif yourChoice == '3':
        transhash = input("Ange transaktionshash:")
        TransViewer(transhash)
    elif yourChoice == '4':
        address = input("Ange adress:")
        ListOutputs(address)
    else:
        print("Felaktig input.. Försök igen..")
        PrintChoices()
        choice = input("Välj funktion: ")
        MakeDecision(choice)

#Visar ett definierat block utifrån definierat block eller blockhash
def ShowBlock(blockorhash):

    #Försöker konvertera input till en int (funkar om man angett blocknr)
    try:
        blockorhash = int(blockorhash)
    #Fångar error och behåller input som en str
    except:
        blockorhash = str(blockorhash)
    
    #kontrollerar inputens typ och fyller requesten därefter
    if str(type(blockorhash)) == "<class 'str'>":
        payload = {
        "method":"getblock",
        "params":[blockorhash]
        }
    else:
         payload = {
        "method":"getblock",
        "params":[str(GetBlockHash(blockorhash))]
        }
    
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print("Block hash:   " + str(response['result']['hash']))
    print("Prev. hash:   " + str(response['result']['previousblockhash']))
    print("Merkle Root:  " + str(response['result']['merkleroot']))
    print("Height:       " + str(response['result']['height']))
    time = ConvertTime(response['result']['time'])
    print("Time:         " + str(time))
    print("Difficulty:   " + str(response['result']['difficulty']))
    print("Transactions: " + str(len(response['result']['tx'])))
    for i in range(len(response['result']['tx'])):
        print("      Tx "+str(i)+": "+str(response['result']['tx'][i]))
                   
#Funktion för att med hjälp av datetime räkna om timestampen till läsbart format
def ConvertTime(time):
    formattedTime = datetime.utcfromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
    return(formattedTime)

#Funktion för att hämta transaktionsinfo från en definierad transaktionshash
def TransViewer(transhash):
    payload = {
    "method":"getrawtransaction",
    "params":[transhash,True]
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    print(response['result'])
    print("Txid (hash):   " + str(transhash))
    print("Med i block:   "+str(response['result']['hash']))
    print("Inputs:        "+str(len(response['result']['vin'])))
    print("Outputs:       "+str(len(response['result']['vout'])))
    for i in range(len(response['result']['vout'])):
        try:
            print("   output "+str(i)+": "+str(format(response['result']['vout'][i]['value'],'.6f'))+" BTE till adress "+str(response['result']['vout'][i]['scriptPubKey']['addresses'][0]))
        except:
            print("   output "+str(i)+": Ingen adress")


def ListOutputs(address):
    print("Söker efter adress:" + address)
    noBlocksToCheck = 2000
    maxblock = BlockCount()
    for i in range(noBlocksToCheck):
        targetBlock = maxblock-noBlocksToCheck+1+i
        if i == 0 or i == 500 or i == 1000 or i == 1500 or i == 2000:
            print(i)
            
        
        payload = {
            "method":"getblock",
            "params": [str(GetBlockHash(targetBlock))]
            }
        response = requests.post(url, data=json.dumps(payload), headers=headers).json()
        currentTx = response['result']['tx']

        
        for j in range(len(currentTx)):
        
            payloadTwo = {
            "method":"getrawtransaction",
            "params": [response['result']['tx'][j],True]
            }
            responseTwo = requests.post(url, data=json.dumps(payloadTwo), headers=headers).json()
            currentVouts = responseTwo['result']['vout']
           
            for k in range(len(currentVouts)):
                try:
                    currentAddress = currentVouts[k]['scriptPubKey']['addresses'][0]
                except:
                    pass
               
                if currentAddress == address:
                    print("Block: "+str(targetBlock)+", Tx: "+str(currentTx[j])+"\n output "+str(k)+": "+str(currentVouts[k]['value']))
            
    
            
        


    
MainMenu()

