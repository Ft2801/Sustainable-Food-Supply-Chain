const SustainabilityMetrics = artifacts.require("SustainabilityMetrics");

module.exports = function (deployer) {
  deployer.deploy(SustainabilityMetrics);
};