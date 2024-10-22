# Blockchain Concepts

A blockchain é uma corrente de blocos, cada um com até no máximo 1MB, que guardam transações de criptomoedas. O primeiro bloco é o `genesis` e o último é o `head`. Cada bloco tem um head que aponta para o bloco imediatamente anterior, sendo ligados porque o hash depende também da identificação do bloco anterior e dos hashes das transactions que suporta.

- Distributed database;
- Protected against modifications or deletions;
- Can only grow with new data;
- Data recorded in a blockchain are transactions in chronological order;
- No repudiation due to criptographic verifications and dependencies;

## Techniques

Blockchain uses transactions based on Digital Signatures to initiate the process. After that, there is a broadcast to the chain nodes and each of them can validate the transaction and aggree in a Consensus Protocol. Steps:

- `Initiation and Broadcasting of transaction`: using digital signatures and private/public keys;
- `Validation of transaction`: using Proof of Work;
- `Creating a new chain block`: using hash functions;

## Ethereum

Pode ser usado com as bibliotecas `web3`, `ethers` e `geth`, como visto na SEED Lab correspondente. Há criação de *Smart Contracts* e *Accounts*.

### Accounts:

Admite dois tipos de contas:

- `Externally owned account` (EOA), que é controlado por private keys;
- `Contract account` (CA), que contém o EVM (Ethereum Virtual Machine) code;

160 bits são usados para identificar as contas, se for EOA usa private keys, se for CA usa o sender address e um nonce.

### Transactions

- `Contract creation`, que cria um contract account;
- `Message call`, que cria uma mensagem entre um EOA e um (EOA ou CA);

### Messages

Podem ser triggered usando:

- transações, entre um EOA e uma Account;
- EVM code, entre um Contract Account e uma Account;

Desisto.