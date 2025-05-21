// save_contract_address.js - Salva l'indirizzo del contratto deployato in un file

const fs = require('fs');
const path = require('path');

// Funzione per salvare l'indirizzo del contratto in un file
async function saveContractAddress(contractName, contractAddress) {
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
}

// Esporta la funzione
module.exports = saveContractAddress;

// Se il file viene eseguito direttamente, salva l'indirizzo passato come argomento
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length >= 2) {
        const contractName = args[0];
        const contractAddress = args[1];
        saveContractAddress(contractName, contractAddress);
    } else {
        console.error('Utilizzo: node save_contract_address.js <nome_contratto> <indirizzo_contratto>');
        process.exit(1);
    }
}
