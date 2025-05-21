
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
            const contractPath = path.join(__dirname, "../artifacts/contracts/TokenExchange.sol/TokenExchange.json");
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
    
            // Crea un'istanza del contratto
            const contract = new ethers.Contract(
                "0x5FbDB2315678afecb367f032d93F642f64180aa3",
                contractJson.abi,
                signer
            );
            
            // Esegui la transazione
            const tx = await contract.rejectTokenRequest(44, "Richiesta rifiutata dall'utente");
            console.log("Transaction hash:", tx.hash);
            
            // Attendi la conferma della transazione
            const receipt = await tx.wait();
            console.log("Transaction confirmed in block:", receipt.blockNumber);
            console.log("Transaction status:", receipt.status);
            
            process.exit(0);
        } catch (error) {
            console.error("Error:", error.message);
            process.exit(1);
        }
    }
    
    main();
    