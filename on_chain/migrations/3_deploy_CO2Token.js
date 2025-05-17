
const CO2Token = artifacts.require("CO2Token");

module.exports = function (deployer) {
  deployer.deploy(CO2Token);
};