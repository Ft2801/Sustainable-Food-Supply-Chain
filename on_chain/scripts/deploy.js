// scripts/deploy.js

async function main() {
  console.log("Starting deployment of essential contracts...");
  
  // Deploy UserRegistry
  const UserRegistry = await ethers.getContractFactory("UserRegistry");
  console.log("Deploying UserRegistry...");
  const userRegistry = await UserRegistry.deploy();
  await userRegistry.waitForDeployment();
  const userRegistryAddress = await userRegistry.getAddress();
  console.log("UserRegistry deployed to:", userRegistryAddress);
  
  // Deploy CompanyRegistry
  const CompanyRegistry = await ethers.getContractFactory("CompanyRegistry");
  console.log("Deploying CompanyRegistry...");
  const companyRegistry = await CompanyRegistry.deploy();
  await companyRegistry.waitForDeployment();
  const companyRegistryAddress = await companyRegistry.getAddress();
  console.log("CompanyRegistry deployed to:", companyRegistryAddress);
  
  // Deploy CO2Token
  const CO2Token = await ethers.getContractFactory("CO2Token");
  console.log("Deploying CO2Token...");
  const co2Token = await CO2Token.deploy();
  await co2Token.waitForDeployment();
  const co2TokenAddress = await co2Token.getAddress();
  console.log("CO2Token deployed to:", co2TokenAddress);
  
  // Deploy TokenExchange (requires CompanyRegistry address)
  const TokenExchange = await ethers.getContractFactory("TokenExchange");
  console.log("Deploying TokenExchange...");
  const tokenExchange = await TokenExchange.deploy(companyRegistryAddress);
  await tokenExchange.waitForDeployment();
  const tokenExchangeAddress = await tokenExchange.getAddress();
  console.log("TokenExchange deployed to:", tokenExchangeAddress);
  
  // Stampa un riepilogo degli indirizzi dei contratti deployati
  console.log("\nRiepilogo degli indirizzi dei contratti deployati:");
  console.log("=============================================");
  console.log(`UserRegistry: ${userRegistryAddress}`);
  console.log(`CompanyRegistry: ${companyRegistryAddress}`);
  console.log(`CO2Token: ${co2TokenAddress}`);
  console.log(`TokenExchange: ${tokenExchangeAddress}`);
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
