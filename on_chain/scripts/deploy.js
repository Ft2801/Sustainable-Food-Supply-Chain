// scripts/deploy.js
const fs = require('fs');
const path = require('path');

// Funzione per salvare l'indirizzo del contratto in un file
function saveContractAddress(contractName, contractAddress) {
  // Percorso del file di configurazione
  const configPath = path.join(__dirname, '..', 'contract_address.json');
  
  // Leggi il file di configurazione esistente o crea un nuovo oggetto
  let config = {};
  if (fs.existsSync(configPath)) {
    try {
      const configData = fs.readFileSync(configPath, 'utf8');
      config = JSON.parse(configData);
    } catch (error) {
      console.error(`Errore nella lettura del file di configurazione: ${error.message}`);
      // Se c'è un errore nella lettura, inizializziamo un nuovo oggetto
      config = {};
    }
  }
  
  // Aggiorna l'indirizzo del contratto
  config[contractName] = contractAddress;
  
  // Scrivi il file di configurazione
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  
  console.log(`Indirizzo del contratto ${contractName} salvato in ${configPath}: ${contractAddress}`);
  
  // Crea anche una copia del file nella directory off_chain per facilitare l'accesso
  const offChainConfigPath = path.join(__dirname, '..', '..', 'off_chain', 'contract_address.json');
  fs.writeFileSync(offChainConfigPath, JSON.stringify(config, null, 2));
  console.log(`Indirizzo del contratto ${contractName} salvato anche in ${offChainConfigPath}`);
}

async function main() {
  console.log("Starting deployment of essential contracts...");
  
  // Deploy SustainableFoodChain
  const SustainableFoodChain = await ethers.getContractFactory("SustainableFoodChain");
  console.log("Deploying SustainableFoodChain...");
  const sustainableFoodChain = await SustainableFoodChain.deploy();
  await sustainableFoodChain.waitForDeployment();
  const sustainableFoodChainAddress = await sustainableFoodChain.getAddress();
  console.log("SustainableFoodChain deployed to:", sustainableFoodChainAddress);
  
  // Salva l'indirizzo del contratto in un file
  saveContractAddress("SustainableFoodChain", sustainableFoodChainAddress);
  
  // Stampa un riepilogo degli indirizzi dei contratti deployati
  console.log("\nRiepilogo degli indirizzi dei contratti deployati:");
  console.log("=============================================");
  console.log(`SustainableFoodChain: ${sustainableFoodChainAddress}`);
  console.log("=============================================");
  console.log("Deployment completato con successo!");
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
