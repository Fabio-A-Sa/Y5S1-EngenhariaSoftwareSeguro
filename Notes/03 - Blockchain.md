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

--- 

## What is Blockchain?

Blockchain is a distributed database that can only grow with new data, acting as a ledger. It is organized as a chain of data blocks, each block contains a collection of transactions. Transactions are cryptographically secured, ensuring non-repudiation (the sender cannot deny their transaction). Ownership transfers are a common use of blockchain transactions. The ledger is maintained by a peer-to-peer network, which eliminates the need for a central authority.

- `Centralized Systems`: a single server holds and controls all data, defining the state. All clients rely on this single server for transactions and data consistency;
- `Distributed Systems`: the ledger is replicated across many nodes. Nodes use a consensus protocol to agree on the true state and verify new transactions. This decentralization ensures resilience and security.

## How Blockchain Works

Users initiate a transaction by submitting data to the network. Block Creation: Transactions are grouped into blocks. Consensus: The network nodes agree on the validity of the block through consensus mechanisms (e.g., Proof of Work, Proof of Stake). Chain Addition: Validated blocks are cryptographically linked to the previous block, creating an immutable chain.

- `Hashing`: Ensures data integrity by converting transaction data into a fixed-length string;
- `Digital Signatures`: Verify the identity of transaction senders and ensure authenticity;
- `Encryption`: Protects sensitive transaction data from unauthorized access;

### Properties

- `Immutability`: Data cannot be altered or deleted once added to the blockchain;
- `Transparency`: Transactions are publicly verifiable;
- `Decentralization`: No single entity controls the blockchain;
- `Security`: Achieved through cryptographic techniques and consensus protocols;

## Ethereum Blockchain

Ethereum extends blockchain functionality by supporting smart contracts and decentralized applications (DApps).
It features its own cryptocurrency, Ether (ETH). Nodes in Ethereum store the **blockchain’s state**, **process transactions**, and **execute smart contracts**.

EVM (Ethereum Virtual Machine) acts as a decentralized computational environment where smart contracts are executed. Ensures security and prevents interference between contracts.
Smart-Contracts are self-executing contracts with terms encoded directly in code. Used in various applications, including decentralized finance (DeFi) and automated processes.

### Accounts

- Externally Owned Accounts (EOAs): Controlled by private keys (individuals or organizations).
- Contract Accounts: Smart contract accounts that execute code upon receiving transactions.

### Transactions

Include details such as sender, recipient, value, data payload, and gas fees. Must be signed with the sender’s private key for authentication.

Gas - A unit measuring the computational effort required to execute transactions or operations on the Ethereum network.
Fees - Paid in Ether, gas fees incentivize miners or validators and regulate network usage to prevent spam.

Interaction with Nodes: The document likely details how users and applications interact with Ethereum nodes to submit transactions or query blockchain data.
Transaction Lifecycle: Covers how transactions are processed, validated, and added to the blockchain.
EVM Execution Model: Describes how the EVM executes bytecode and ensures isolation between smart contracts.