
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
                const isRegistered = await contract.isRegistered("0x000000000000000000000000000000000000000c");
                console.log(`Verifica registrazione per l'indirizzo 0x000000000000000000000000000000000000000c: ${isRegistered ? 'Registrato' : 'Non registrato'}`);
                if (isRegistered) {
                    console.log("L'azienda è già registrata sulla blockchain");
                    process.exit(0);
                }
            } catch (error) {
                console.error("Errore nella verifica della registrazione:", error.message);
                // Continuiamo comunque con la registrazione
            }
            
            console.log(`Registrazione dell'azienda a di tipo 1 in corso...`);
            
            // Esegui la transazione di registrazione
            const tx = await contract.registerCompany(
                "a",
                1,  // Tipo di azienda (enum: 0=Producer, 1=Processor, 2=Distributor, 3=Retailer, 4=Other)
                "r",
                "{}"
            );
            console.log("Transaction hash:", tx.hash);
            
            // Attendi la conferma della transazione
            const receipt = await tx.wait();
            console.log("Transaction confirmed in block:", receipt.blockNumber);
            console.log("Transaction status:", receipt.status);
            
            // Verifica nuovamente la registrazione dopo la transazione
            const isRegisteredAfter = await contract.isRegistered("0x000000000000000000000000000000000000000c");
            console.log(`Verifica finale: l'azienda è ${isRegisteredAfter ? 'correttamente registrata' : 'ANCORA NON REGISTRATA (errore)'}`);
            
            if (!isRegisteredAfter) {
                throw new Error("La registrazione non è stata completata correttamente");
            }
            
            process.exit(0);
        } catch (error) {
            console.error("Error:", error.message);
            process.exit(1);
        }
    }
    
    main();
    