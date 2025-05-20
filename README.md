# Sustainable Food Supply Chain

## Presentazione dell'Applicazione

Il progetto Sustainable Food Supply Chain è un'applicazione innovativa che integra tecnologie blockchain con un'interfaccia utente tradizionale per gestire e tracciare la filiera alimentare in modo sostenibile. Questo sistema permette di registrare, verificare e monitorare ogni fase della catena di approvvigionamento alimentare, garantendo trasparenza, sicurezza e sostenibilità ambientale.

L'applicazione è divisa in due componenti principali:
- **off_chain**: Interfaccia utente e logica applicativa in Python con PyQt5
- **on_chain**: Smart contracts e interazione blockchain basati su Ethereum/Hardhat

## Features

- **Registrazione Utenti e Aziende**: Gestione di utenti e aziende nel sistema
- **Tracciabilità Prodotti**: Monitoraggio completo del ciclo di vita dei prodotti alimentari
- **Gestione Operazioni**: Registrazione e verifica delle operazioni nella filiera
- **Controllo Qualità**: Verifica della qualità dei prodotti in ogni fase
- **Metriche di Sostenibilità**: Monitoraggio dell'impatto ambientale
- **Token CO2**: Sistema di tokenizzazione per la compensazione delle emissioni di carbonio
- **Scambio Token**: Piattaforma per lo scambio di token tra aziende
- **Richieste Prodotti**: Sistema di richiesta e approvazione di nuovi prodotti

## Prerequisiti

### Requisiti Generali
- Git
- Python 3.8 o superiore
- Node.js 16.x o superiore
- npm 8.x o superiore

### Per la parte off_chain (Python)
- PyQt5
- PostgreSQL
- Web3.py

### Per la parte on_chain (Blockchain)
- Hardhat
- Ethers.js
- OpenZeppelin Contracts

## Installazione

### Clonare il Repository

```bash
git clone https://github.com/yourusername/Sustainable-Food-Supply-Chain.git
cd Sustainable-Food-Supply-Chain
```

### Installazione Dipendenze off_chain (Python)

```bash
pip install PyQt5 web3
```

### Installazione Dipendenze on_chain (Blockchain)

```bash
cd on_chain
npm install
```

### Configurazione Environment

L'applicazione utilizza SQLite come database, quindi non è necessario configurare un server database esterno. Il database verrà creato automaticamente al primo avvio dell'applicazione.

### Setup dell'Ambiente Hardhat

#### Per MacOS

```bash
cd on_chain
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox ethers @openzeppelin/contracts
```

#### Per Windows

```bash
cd on_chain
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox ethers @openzeppelin/contracts
```

## Come Avviare l'Applicazione

### Avvio Automatico (Consigliato)

L'applicazione può essere avviata direttamente dal modulo principale, che gestirà automaticamente tutte le operazioni necessarie:

```bash
cd off_chain
python main.py
```

Questo script eseguirà automaticamente le seguenti operazioni:

1. Verifica e installazione di Hardhat se necessario
2. Avvio di un nodo Hardhat in un terminale separato
3. Compilazione e deployment dei contratti smart
4. Configurazione del database
5. Avvio dell'interfaccia grafica

### Avvio Manuale (Passo-Passo)

Se preferisci avere un maggiore controllo sul processo di avvio, puoi seguire questi passaggi manuali:

#### 1. Installare Hardhat e avviare il nodo

```bash
# Navigare alla directory on_chain
cd on_chain

# Installare hardhat (se non già fatto)
npm install --save-dev hardhat

# Avviare il nodo Hardhat
npx hardhat node
```

Questo comando avvierà un nodo Hardhat locale sulla porta 8545. Lascia questa finestra del terminale aperta mentre lavori con l'applicazione.

#### 2. Compilare i contratti

In una nuova finestra del terminale:

```bash
# Navigare alla directory on_chain
cd on_chain

# Compilare i contratti
npx hardhat compile
```

#### 3. Deployare i contratti

Nella stessa finestra del terminale:

```bash
# Deployare i contratti sul nodo locale
npx hardhat run scripts/deploy.js --network localhost
```

Questo comando deployerà tutti i contratti sul nodo Hardhat locale e creerà il file `contract_addresses.json` con gli indirizzi e le ABI dei contratti.

#### 4. Avviare l'applicazione

```bash
# Navigare alla directory off_chain
cd off_chain

# Avviare l'applicazione
python main.py
```

## Struttura del Progetto

### Struttura Principale

```
Sustainable-Food-Supply-Chain/
├── off_chain/         # Componente Python dell'applicazione
├── on_chain/          # Componente blockchain dell'applicazione
└── log/               # Directory per i file di log
```

### Struttura off_chain

```
off_chain/
├── configuration/     # Impostazioni e configurazioni
├── database/          # Gestione del database SQLite
├── domain/            # Logica di dominio
├── enforcement/       # Validazione e sicurezza
├── model/             # Modelli di dati
├── persistence/       # Layer di persistenza dati
├── presentation/      # Interfaccia utente (GUI)
├── tests/             # Test unitari
├── blockchain_manager.py  # Gestione dell'interazione con la blockchain
├── gui_manager.py     # Gestione dell'interfaccia grafica
└── main.py            # Punto di ingresso dell'applicazione
```

### Struttura on_chain

```
on_chain/
├── contracts/         # Smart contracts Solidity
│   ├── CO2Token.sol           # Token per la compensazione CO2
│   ├── CompanyRegistry.sol     # Registro delle aziende
│   ├── IERC20.sol              # Interfaccia standard per token
│   ├── OperationRegistry.sol   # Registro delle operazioni
│   ├── ProductRegistry.sol     # Registro dei prodotti
│   ├── ProductRequest.sol      # Gestione richieste prodotti
│   ├── QualityControl.sol      # Controllo qualità
│   ├── SupplyChain.sol         # Gestione della filiera
│   ├── SupplyChainCO2.sol      # Gestione CO2 nella filiera
│   ├── SustainabilityMetrics.sol # Metriche di sostenibilità
│   ├── TokenExchange.sol       # Scambio di token
│   └── UserRegistry.sol        # Registro degli utenti
├── migrations/        # Script di migrazione/deployment
├── scripts/           # Script di utilità
├── hardhat.config.js  # Configurazione di Hardhat
└── package.json       # Dipendenze Node.js
```

## Funzionalità Blockchain

L'applicazione utilizza Hardhat per simulare una blockchain Ethereum locale. Gli smart contract gestiscono:

- Registrazione e autenticazione utenti
- Tracciabilità dei prodotti nella filiera
- Certificazioni di qualità e sostenibilità
- Tokenizzazione delle emissioni di CO2
- Scambio di token tra aziende

I contratti vengono compilati e deployati automaticamente all'avvio dell'applicazione, creando un ambiente blockchain completo per testare e utilizzare tutte le funzionalità del sistema.

---

## Blockchain Setup with Hardhat

This directory contains the smart contracts and blockchain setup for the Sustainable Food Supply Chain project. The project uses Hardhat for local development and deployment.

## Setup

1. Install dependencies:
```
npm install
```

2. Start a local Hardhat node:
```
npm run node
```

3. In a separate terminal, deploy the contracts:
```
npm run deploy
```

## Project Structure

- `contracts/`: Contains all Solidity smart contracts
- `scripts/`: Contains deployment scripts
- `test/`: Contains test files for smart contracts
- `hardhat.config.js`: Hardhat configuration file
- `artifacts/`: Contains compiled contract ABIs and bytecode (generated after compilation)

## Using with the Application

The application automatically starts a Hardhat node and deploys contracts when needed. The contract addresses and ABIs are stored in `contract_addresses.json`.

---

© 2025 Sustainable Food Supply Chain - Progetto universitario