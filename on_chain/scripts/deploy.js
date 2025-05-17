// scripts/deploy.js
const fs = require('fs');
const path = require('path');

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
  
  // Get the ABIs from artifacts
  const userRegistryArtifact = require('../artifacts/contracts/UserRegistry.sol/UserRegistry.json');
  const productRegistryArtifact = require('../artifacts/contracts/ProductRegistry.sol/ProductRegistry.json');
  const operationRegistryArtifact = require('../artifacts/contracts/OperationRegistry.sol/OperationRegistry.json');
  const supplyChainArtifact = require('../artifacts/contracts/SupplyChain.sol/SupplyChain.json');
  const supplyChainCO2Artifact = require('../artifacts/contracts/SupplyChainCO2.sol/SupplyChainCO2.json');
  
  // Save contract data
  const contractData = {
    contracts: {
      "UserRegistry": {
        address: userRegistryAddress,
        abi: userRegistryArtifact.abi
      },
      "ProductRegistry": {
        address: productRegistryAddress,
        abi: productRegistryArtifact.abi
      },
      "OperationRegistry": {
        address: operationRegistryAddress,
        abi: operationRegistryArtifact.abi
      },
      "SupplyChain": {
        address: supplyChainAddress,
        abi: supplyChainArtifact.abi
      },
      "SupplyChainCO2": {
        address: supplyChainCO2Address,
        abi: supplyChainCO2Artifact.abi
      }
    },
    timestamp: new Date().toISOString(),
    network: "localhost"
  };
  
  const outputPath = path.join(__dirname, '../contract_addresses.json');
  fs.writeFileSync(outputPath, JSON.stringify(contractData, null, 2));
  
  console.log(`Contract addresses and ABIs saved to ${outputPath}`);
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
