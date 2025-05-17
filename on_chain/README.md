# Blockchain Setup with Hardhat

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
