# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 20:55:07 2022
#decenralizing bc
@author: Zorana Krsmanovic
"""

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests #for consensus
from uuid import uuid4
from urllib.parse import urlparse


#Blockchain 
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = [] #list of transactions before it is added to block
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set() 
    def create_block(self, proof, previous_hash):
        block = {'index' : len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof' : proof,
                 'previous_hash' : previous_hash,
                 'transactions': self.transactions}
        self.transactions = [] 
        self.chain.append(block)
        return block

    #function for getting the previous block from current chain
    def get_previous_block(self):
        return self.chain[-1]
    #calculating proof of work
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
        return new_proof
    #hashing the block
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    #checking to validate if the hash of each block is equal to the hash of the prevous block
    def is_chain_vaild(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000' :
                return False
            previous_block  = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1


    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    #replacing the chain if it is not the longest
    def replace_chain(self):
        network = self.nodes
        longest_chain = None 
        max_length = len(self.chain)
        for node in network: 
            response = requests.get(f'http://{node}/get_chain') 
            if response.status_code == 200:
               length = response.json()['length'] 
               chain = response.json()['chain']
               if length > max_length and self.is_chain_vaild(chain): 
                   max_length = length
                   longest_chain = chain
        if longest_chain:
            self .chain = longest_chain
            return True
        return False




#Mining the block

#Creating web app
app = Flask(__name__)
#Creating address for the node on Port 5001
node_address = str(uuid4()).replace('-', '') 


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

#creating a Blockchain
blockchain = Blockchain()

#Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Zorana', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message':'You just mined a block',
                'index': block['index'],
                'timestamp' : block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200


#Get the full blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

#checking if the blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_vaild(blockchain.chain)
    if is_valid :
        response = {'message': 'Blockchain is valid'}
    else:
        response = {'message': 'PROBLEM ! Blockchain is not valid'}
    return jsonify(response), 200


#Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver', 'amount']
    if not all ( key in json for key in transaction_keys):
        return 'Some properties are missing', 400
    index = blockchain.add_transaction(json['sender'],json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block{index}'}
    return jsonify(response), 201



# Decentralizing blockchain

#Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now conncected. The Atacoin Blockchain contains following nodes',
                'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

#Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced :
        response = {'message': 'The chain was replaced',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good, the chain is the largest one',
                    'chain': blockchain.chain}
    return jsonify(response), 200







#Running the app
app.run(host='0.0.0.0', port = 5001)







