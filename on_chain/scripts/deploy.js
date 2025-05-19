// scripts/deploy.js

async function main() {
  console.log("Starting deployment of all contracts...");
  
  // Deploy UserRegistry
  const UserRegistry = await ethers.getContractFactory("UserRegistry");
  console.log("Deploying UserRegistry...");
  const userRegistry = await UserRegistry.deploy();
  await userRegistry.waitForDeployment();
  const userRegistryAddress = await userRegistry.getAddress();
  console.log("UserRegistry deployed to:", userRegistryAddress);
  
  // Deploy ProductRegistry
  const ProductRegistry = await ethers.getContractFactory("ProductRegistry");
  console.log("Deploying ProductRegistry...");
  const productRegistry = await ProductRegistry.deploy();
  await productRegistry.waitForDeployment();
  const productRegistryAddress = await productRegistry.getAddress();
  console.log("ProductRegistry deployed to:", productRegistryAddress);
  
  // Deploy OperationRegistry
  const OperationRegistry = await ethers.getContractFactory("OperationRegistry");
  console.log("Deploying OperationRegistry...");
  const operationRegistry = await OperationRegistry.deploy();
  await operationRegistry.waitForDeployment();
  const operationRegistryAddress = await operationRegistry.getAddress();
  console.log("OperationRegistry deployed to:", operationRegistryAddress);
  
  // Deploy SupplyChain
  const SupplyChain = await ethers.getContractFactory("SupplyChain");
  console.log("Deploying SupplyChain...");
  const supplyChain = await SupplyChain.deploy();
  await supplyChain.waitForDeployment();
  const supplyChainAddress = await supplyChain.getAddress();
  console.log("SupplyChain deployed to:", supplyChainAddress);
  
  // Deploy SupplyChainCO2
  const SupplyChainCO2 = await ethers.getContractFactory("SupplyChainCO2");
  console.log("Deploying SupplyChainCO2...");
  const supplyChainCO2 = await SupplyChainCO2.deploy();
  await supplyChainCO2.waitForDeployment();
  const supplyChainCO2Address = await supplyChainCO2.getAddress();
  console.log("SupplyChainCO2 deployed to:", supplyChainCO2Address);
  
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
  
  // Deploy ProductRequest
  const ProductRequest = await ethers.getContractFactory("ProductRequest");
  console.log("Deploying ProductRequest...");
  const productRequest = await ProductRequest.deploy();
  await productRequest.waitForDeployment();
  const productRequestAddress = await productRequest.getAddress();
  console.log("ProductRequest deployed to:", productRequestAddress);
  
  // Deploy QualityControl
  const QualityControl = await ethers.getContractFactory("QualityControl");
  console.log("Deploying QualityControl...");
  const qualityControl = await QualityControl.deploy();
  await qualityControl.waitForDeployment();
  const qualityControlAddress = await qualityControl.getAddress();
  console.log("QualityControl deployed to:", qualityControlAddress);
  
  // Deploy SustainabilityMetrics
  const SustainabilityMetrics = await ethers.getContractFactory("SustainabilityMetrics");
  console.log("Deploying SustainabilityMetrics...");
  const sustainabilityMetrics = await SustainabilityMetrics.deploy();
  await sustainabilityMetrics.waitForDeployment();
  const sustainabilityMetricsAddress = await sustainabilityMetrics.getAddress();
  console.log("SustainabilityMetrics deployed to:", sustainabilityMetricsAddress);
  
  // Stampa un riepilogo degli indirizzi dei contratti deployati
  console.log("\nRiepilogo degli indirizzi dei contratti deployati:");
  console.log("=============================================");
  console.log(`UserRegistry: ${userRegistryAddress}`);
  console.log(`ProductRegistry: ${productRegistryAddress}`);
  console.log(`OperationRegistry: ${operationRegistryAddress}`);
  console.log(`SupplyChain: ${supplyChainAddress}`);
  console.log(`SupplyChainCO2: ${supplyChainCO2Address}`);
  console.log(`CompanyRegistry: ${companyRegistryAddress}`);
  console.log(`CO2Token: ${co2TokenAddress}`);
  console.log(`TokenExchange: ${tokenExchangeAddress}`);
  console.log(`ProductRequest: ${productRequestAddress}`);
  console.log(`QualityControl: ${qualityControlAddress}`);
  console.log(`SustainabilityMetrics: ${sustainabilityMetricsAddress}`);
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
