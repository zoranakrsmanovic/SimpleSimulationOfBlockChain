# Simple Simulation Of Blockchain
Built with Flask.
End points : '/get_chain', method = GET - returns all mined blocks
              '/is_valid', methods = GET - checks for all blocks in the chain, if the previous hash of the current block is the same as the hash of the prevoius blok
              '/add_transaction', method = POST - adds transaction to the transaction list
              '/connect_node', method = POST - connects nodes
              '/replace_chain', method = GET - checks if the current chain is the longest, and if it is not, replaces it with the longest one.

              

https://user-images.githubusercontent.com/81091010/170130190-c5a1b6f5-30b5-40ab-84b2-d553d341a134.mov

