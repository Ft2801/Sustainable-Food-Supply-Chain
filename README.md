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
- Node.js 14.x o superiore
- npm 6.x o superiore

### Per la parte off_chain (Python)
- PyQt5
- SQLite (incluso in Python)
- Web3.py
- PyOTP (per autenticazione a due fattori)
- PyYAML (per file di configurazione)

### Per la parte on_chain (Blockchain)
- Hardhat
- Ethers.js
- OpenZeppelin Contracts

## Installazione

### Clonare il Repository

```bash
git clone https://github.com/Ft2801/Sustainable-Food-Supply-Chain.git
cd Sustainable-Food-Supply-Chain
```

### Installazione Dipendenze off_chain (Python)

```bash
pip install -r requirements.txt
```

Il file requirements.txt contiene tutte le dipendenze Python necessarie per l'applicazione.

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

L'applicazione utilizza Hardhat per simulare una blockchain Ethereum locale. Il contratto principale SustainableFoodChain integra diverse funzionalità:

- **Registro Utenti**: Registrazione e gestione degli utenti nel sistema
- **Registro Aziende**: Gestione delle aziende di diversi tipi (Agricola, Trasportatore, Trasformatore, Rivenditore, Certificatore)
- **Token CO2**: Sistema di token per la compensazione delle emissioni di carbonio
- **Scambio Token**: Meccanismo per lo scambio di token tra aziende per compensare l'impatto ambientale
- **Certificazioni**: Verifica e registrazione delle certificazioni di sostenibilità
- Scambio di token tra aziende

I contratti vengono compilati e deployati automaticamente all'avvio dell'applicazione, creando un ambiente blockchain completo per testare e utilizzare tutte le funzionalità del sistema.

---

