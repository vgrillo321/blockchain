# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 16:21:47 2021

@author: vgril
"""

#Module 2 - Create a Cryptocurrency

#Import necesarry libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4 
from urllib.parse import urlparse


#Part 1 - Building a Blockchain
#best way to build a blockchain is with classes rather than functions

class Blockchain:
    
    def __init__(self): #initialize the class
    
        #List that will contain the blocks
        self.chain = [] 
        
        #List that will contain the transactions before they are integrated to a block. MUST BE CREATED BEFORE THE CREATE BLOCK FUNCTION.
        self.transactions = []
        
        #Create the genesis block and assign the proof and prev_hash arguments
        self.create_block(proof = 1, previous_hash = '0') 
        
        #Nodes initialized as a set variable
        self.nodes = set()
    
    #Function to create the block and append it to the blockchain
    def create_block(self, proof, previous_hash): 
            
            #Block containing the block number, date created, proof of work
            #function and previous hash to connect the blobk to the chain
            block = {'index': len(self.chain) + 1, 
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions,
                 #'data': anything can be added here (function, json file, etc)
                     }
            self.transactions = [] #Updating the transactions list to be empty after block gets created
            self.chain.append(block)
            return block
    
    
    #Function to create the format for the transactions and add it to the list of transactions
    def add_transaction(self, sender, receiver, amount):
       #Add sender, receiver and amount of coins in the transactions list
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_prev_block
        return previous_block['index']+1
    
    #Add a node to the coin network
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) #Netloc is the URL including the port. This is unique identifier
    
    #Function to get the previous block in the blockchain
    def get_prev_block(self):
        return self.chain[-1]

    #Define the problem for miners to solve. This is the number that miners 
    #need to find
    def proof_of_work(self, previous_proof):
        new_proof = 1 #counter
        check_proof = False
        while check_proof is False:
            #String of 64 characters (SHA256) which will be compared to the 
            #challenge
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            #Condition to check if the result of hash op starts with 0
            #the more 0s the harder it is.
            if hash_operation[:4] == '0000': #Miner wins and check_proof is true
                check_proof = True
            else: #Miner lose and increments the new proof to check if the 
                    #new proof solves the problem
                new_proof += 1 
        return new_proof

    #Hash function that returns the cryptographic hash   
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #Function to check if the chain is valid
    def is_chain_valid(self, chain):
        previous_block = chain[0] #Get the first block of the chain
        block_index = 1 
        while block_index < len(chain): #Loop through all of the chains
            block = chain[block_index]
            #Check if the previous hash is different as the hash in prev block
            if block['previous_hash'] !=  self.hash(previous_block):
                return False
            #Check if the proof of each block is valid
            previous_proof = previous_block['proof'] #proof of the previous block
            proof = block['proof'] #proof of current block
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            #Is the proof solved with the leading zeros?
            if hash_operation[:4] != '0000': 
                return False
            previous_block = block
            block_index += 1
        return True
        
    #Chain consensus function
    def replace_chain(self):
        network = self.nodes #Set of nodes in the network
        longest_chain = None
        max_length = len(self.chain)
        for nodes in network:
            response = requests.get(f 'http://{node}/get_chain')
                if response.status_code == 200:
                    length = response.json()['lenght']
                    chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length 
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    
#Part 2 - Mining our Blockchain

#Create Web App
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '') #uuid library is used to create the ID's used for the addresses

#Creating a blockchain
blockchain = Blockchain()

#Mining a new block
@app.route('/mine_block', methods=['GET']) #HTTP Get method
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    transactions = blockchain.add_transaction(sender = node_address, receiver = 'Vic', amount = 300000) #Add transactions to the block
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a new block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods=['GET']) #HTTP Get method
def get_chain():
    response = {'chain': blockchain.chain,
                'lenght': len(blockchain.chain)}
   
    return jsonify(response), 200

#Check if the blockchain is valid request
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Blockchain is valid'}
    else:
        response = {'message': 'Bro, blockchain is not valid'}
        
    return jsonify(response), 200
     
#Adding a new transaction to the Blockchain
@app.route('/add_transacton', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (for key in transaction_keys):
        return 'Some elements of the transactions are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f 'This transaction will be added to block {index}'} 
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain

#Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes.json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Grillocoin Blockchain now contains the following nodes',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so it was replaced by longest one',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good, the chain is the largest one.'
                    'actual_chain': blockchain.chain}
        
    return jsonify(response), 200


# Running the app
app.run(host = '0.0.0.0', port = 5000)









