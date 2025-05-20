// scripts/deploy.js

async function main() {
  console.log("Starting deployment of essential contracts...");
  
  // Deploy SustainableFoodChain
  const SustainableFoodChain = await ethers.getContractFactory("SustainableFoodChain");
  console.log("Deploying SustainableFoodChain...");
  const sustainableFoodChain = await SustainableFoodChain.deploy();
  await sustainableFoodChain.waitForDeployment();
  const sustainableFoodChainAddress = await sustainableFoodChain.getAddress();
  console.log("SustainableFoodChain deployed to:", sustainableFoodChainAddress);
  
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
