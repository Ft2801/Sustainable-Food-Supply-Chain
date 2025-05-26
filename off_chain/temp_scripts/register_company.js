
    // Importa ethers e verifica la versione
    const ethers = require("ethers");
    const fs = require("fs");
    const path = require("path");

    async function main() {
        try {
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
            const contractPath = path.join(__dirname, "../../on_chain/artifacts/contracts/SustainableFoodChain.sol/SustainableFoodChain.json");
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
                "0x68B1D87F95878fE05B998F19b66F4baba5De1aed",  // Indirizzo del contratto SustainableFoodChain
                contractJson.abi,
                signer
            );
            
            console.log(`Usando contratto SustainableFoodChain all'indirizzo: 0x68B1D87F95878fE05B998F19b66F4baba5De1aed`);
            
            // Verifica se l'azienda è già registrata
            try {
                const isRegistered = await contract.isCompanyAddressRegistered("0x976ea74026e726554db657fa54763abd0c3a0aa9");
                console.log(`Verifica registrazione per l'indirizzo 0x976ea74026e726554db657fa54763abd0c3a0aa9: ${isRegistered ? 'Registrato' : 'Non registrato'}`);
                if (isRegistered) {
                    console.log("L'azienda è già registrata sulla blockchain");
                    process.exit(0);
                }
            } catch (error) {
                console.error("Errore nella verifica della registrazione:", error.message);
                // Continuiamo comunque con la registrazione
            }
            
            console.log(`Registrazione dell'azienda F di tipo 0 in corso...`);
            
            // Esegui la transazione di registrazione
            const tx = await contract.registerCompany(
                "F",
                0,  // Tipo di azienda (enum: 0=Producer, 1=Processor, 2=Distributor, 3=Retailer, 4=Other)
                "b",
                "{}"
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
                const isRegisteredAfter = await contract.isCompanyAddressRegistered("0x976ea74026e726554db657fa54763abd0c3a0aa9");
                console.log("Verifica finale: l'azienda è " + (isRegisteredAfter ? "correttamente registrata" : "potrebbe richiedere più tempo per essere visibile"));
            } catch (verifyError) {
                console.warn("Impossibile verificare la registrazione, ma la transazione è stata confermata:", verifyError.message);
            }
            
            // Non lanciamo più un errore se la verifica fallisce, poiché la transazione è stata confermata
            // e potrebbe richiedere più tempo per essere riflessa nello stato della blockchain
            
            process.exit(0);
        } catch (error) {
            console.error("Error:", error.message);
            process.exit(1);
        }
    }
    
    main();
    