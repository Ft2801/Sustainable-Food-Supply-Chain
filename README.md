# Sustainable Food Supply Chain

## Presentazione dell'Applicazione

Il progetto Sustainable Food Supply Chain è un'applicazione innovativa che integra tecnologie blockchain con un'interfaccia utente tradizionale per gestire e tracciare la filiera alimentare in modo sostenibile. Questo sistema permette di registrare, verificare e monitorare ogni fase della catena di approvvigionamento alimentare, garantendo trasparenza, sicurezza e sostenibilità ambientale. Permette anche agli utenti comuni la possibilità di accedere come Guest per visualizzare tutti i dati relativi al consumo di CO2 dei prodotti e lotti, oltre che alle certificazioni di qualità.

L'applicazione è divisa in due componenti principali:
- **off_chain**: Interfaccia utente e logica applicativa in Python con PyQt5
- **on_chain**: Smart contracts e interazione blockchain basati su Ethereum e Hardhat

L'applicazione utilizza MetaMask per l'interazione con la blockchain, consentendo agli utenti di firmare transazioni in modo sicuro per operazioni che coinvolgono token e richieste di prodotti; questo viene fatto poiché non è una buona pratica inserire la propria chiave privata all'interno dell'applicazione.

## Features

- **Registrazione Aziende**: Gestione di aziende nel sistema
- **Tracciabilità Prodotti**: Monitoraggio completo del ciclo di vita dei prodotti alimentari
- **Gestione Operazioni**: Registrazione e verifica delle operazioni nella filiera
- **Metriche di Sostenibilità**: Monitoraggio dell'impatto ambientale
- **Token CO2**: Sistema di tokenizzazione per la gestione delle emissioni di CO2, utilizzato sia per le operazioni che per le azioni compensative
- **Scambio Token**: Piattaforma per lo scambio di token tra aziende
- **Richieste Prodotti**: Sistema di richiesta e approvazione per lo scambio di prodotti tra aziende
- **Certificazioni**: Sistema per le certificazioni di qualità

### Requisiti Generali
- Git
- Python 3.8 o superiore
- Node.js 14.x o superiore
- npm 6.x o superiore
- PyQt5
- Web3
- PyOTP
- PyYAML
- SQLite
- Flask
- Flask-CORS
- Hardhat
- Ethers.js
- OpenZeppelin Contracts
- Metamask

## Installazione

### Clonare il Repository

```bash
git clone https://github.com/Ft2801/Sustainable-Food-Supply-Chain.git
cd Sustainable-Food-Supply-Chain
```

### Installazione Dipendenze

```bash
pip install -r requirements.txt
```

Il file requirements.txt contiene tutte le dipendenze Python necessarie per l'applicazione.

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

### Installazione Ethers.js

```bash
cd ..
npm install ethers
```
### Setup smart contract

```bash
cd on_chain
npx hardhat clean
npx hardhat compile
```

### Setup database

```bash
cd off_chain
cd database
python db_migrations.py
```

## Come Avviare l'Applicazione

Per avviare l'applicazione completa, è necessario eseguire due componenti:

1. Avviare il server backend per la comunicazione con MetaMask:
```bash
cd off_chain
python backend.py
```

2. Avviare l'interfaccia utente principale:
```bash
cd off_chain
python main.py
```

Questi script eseguiranno automaticamente le seguenti operazioni:

1. Configurazione dell'ambiente Python e installazione delle dipendenze
2. Verifica e installazione di Hardhat se necessario
3. Avvio di un nodo Hardhat in un terminale separato
4. Compilazione e deployment dei contratti smart
5. Configurazione del database
6. Avvio dell'interfaccia grafica

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
├── main.py            # Punto di ingresso principale dell'applicazione (avvia l'interfaccia PyQt5)
└── backend.py         # Server Flask per la comunicazione con MetaMask e la blockchain
```

### Struttura on_chain

```
on_chain/
├── contracts/         # Smart contracts Solidity
│   ├── SustainableFoodChain.sol   # Contratto principale per le operazioni sui Token
├── migrations/        # Script di migrazione/deployment
├── scripts/           # Script di utilità
├── controller/        # Controller per le operazioni
├── hardhat.config.js  # Configurazione di Hardhat
└── package.json       # Dipendenze Node.js
```

## Funzionalità Blockchain

L'applicazione utilizza Hardhat per simulare una blockchain Ethereum locale. Il contratto principale SustainableFoodChain integra diverse funzionalità:

- **Registro Aziende**: Registrazione e gestione delle aziende di diversi tipi (Agricola, Trasportatore, Trasformatore, Rivenditore, Certificatore)
- **Token CO2**: Sistema di token per la gestione delle emissioni di carbonio, utilizzato sia per le operazioni che per le azioni compensative
- **Scambio Token**: Meccanismo per lo scambio di token tra aziende per compensare l'impatto ambientale
- **Richieste di prodotti**: Meccanismo per la richiesta e approvazione di prodotti tra aziende
- **Gestione dei lotti**: Meccanismo per la gestione dei lotti di prodotti


Il contratto viene compilato e deployato automaticamente all'avvio dell'applicazione, creando un ambiente blockchain completo per testare e utilizzare tutte le funzionalità del sistema.

Viene utilizzato MetaMask per interagire con la blockchain; infatti per confermare tutti i tipi di operazione che riguardano i token e le richieste di prodotti viene sfruttato MetaMask per firmare in modo sicuro le transazioni. Per i test e le dimostrazioni del progetto è stato utilizzato un account di prova.