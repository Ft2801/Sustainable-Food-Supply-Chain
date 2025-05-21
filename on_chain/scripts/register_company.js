// Importa ethers e verifica la versione
const ethers = require("ethers");
const fs = require("fs");
const path = require("path");

async function main() {
    try {
        // Ottieni i parametri dalla riga di comando
        const args = process.argv.slice(2);
        const company_address = args[0] || "0x000000000000000000000000000000000000000c";
        const company_name = args[1] || "Azienda Default";
        const company_type = parseInt(args[2] || "1"); // Default a Processor (1) se non specificato
        const company_location = args[3] || "Italia";
        const certifications = args[4] || "{}";

        console.log("Parametri di registrazione:");
        console.log("- Indirizzo:", company_address);
        console.log("- Nome:", company_name);
        console.log("- Tipo:", company_type, "(", ["Producer", "Processor", "Distributor", "Retailer", "Other"][company_type], ")");
        console.log("- Posizione:", company_location);
        console.log("- Certificazioni:", certifications);

        // Verifica la versione di ethers.js
        const isEthersV6 = ethers.version && parseInt(ethers.version.split('.')[0]) >= 6;
        console.log(`Usando ethers.js ${isEthersV6 ? 'v6+' : 'v5-'}`);
        
        // Configura il provider in modo compatibile con entrambe le versioni
        let provider;
        if (isEthersV6) {
            provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
        } else {
            provider = new ethers.providers.JsonRpcProvider("http://127.0.0.1:8545");
        }
        
        // Carica l'ABI del contratto
        const contractPath = path.join(__dirname, "../artifacts/contracts/SustainableFoodChain.sol/SustainableFoodChain.json");
        const contractJson = JSON.parse(fs.readFileSync(contractPath));
        
        // Ottieni il signer in modo compatibile con entrambe le versioni
        let signer;
        if (isEthersV6) {
            const accounts = await provider.listAccounts();
            signer = await provider.getSigner(accounts[0].address);
        } else {
            const accounts = await provider.listAccounts();
            signer = provider.getSigner(accounts[0]);
        }
        
        // Verifica che il provider sia connesso
        const blockNumber = await provider.getBlockNumber();
        console.log(`Provider connesso. Blocco corrente: ${blockNumber}`);

        // Crea un'istanza del contratto SustainableFoodChain
        const contract = new ethers.Contract(
            "0x5FbDB2315678afecb367f032d93F642f64180aa3",  // Indirizzo del contratto SustainableFoodChain
            contractJson.abi,
            signer
        );
        
        console.log(`Usando contratto SustainableFoodChain all'indirizzo: 0x5FbDB2315678afecb367f032d93F642f64180aa3`);
        
        // Verifica se l'azienda è già registrata
        try {
            const isRegistered = await contract.isCompanyAddressRegistered(company_address);
            console.log(`Verifica registrazione per l'indirizzo ${company_address}: ${isRegistered ? 'Registrato' : 'Non registrato'}`);
            if (isRegistered) {
                console.log("L'azienda è già registrata sulla blockchain");
                process.exit(0);
            }
        } catch (error) {
            console.error("Errore nella verifica della registrazione:", error.message);
            // Continuiamo comunque con la registrazione
        }
        
        console.log(`Registrazione dell'azienda ${company_name} di tipo ${company_type} in corso...`);
        
        // Esegui la transazione di registrazione
        const tx = await contract.registerCompany(
            company_name,
            company_type,  // Tipo di azienda (enum: 0=Producer, 1=Processor, 2=Distributor, 3=Retailer, 4=Other)
            company_location,
            certifications
        );
        console.log("Transaction hash:", tx.hash);
        
        // Attendi la conferma della transazione
        const receipt = await tx.wait();
        console.log("Transaction confirmed in block:", receipt.blockNumber);
        console.log("Transaction status:", receipt.status);
        
        // Attendiamo un momento per assicurarci che la transazione sia completamente processata
        console.log("Attesa di 2 secondi per la propagazione della transazione...");
        await new Promise(resolve => setTimeout(resolve, 2000)); // Attesa di 2 secondi
        
        // Verifica nuovamente la registrazione dopo la transazione
        try {
            const isRegisteredAfter = await contract.isCompanyAddressRegistered(company_address);
            console.log("Verifica finale: l'azienda è " + (isRegisteredAfter ? "correttamente registrata" : "potrebbe richiedere più tempo per essere visibile"));
        } catch (verifyError) {
            console.warn("Impossibile verificare la registrazione, ma la transazione è stata confermata:", verifyError.message);
        }
        
        process.exit(0);
    } catch (error) {
        console.error("Error:", error.message);
        process.exit(1);
    }
}

main();
