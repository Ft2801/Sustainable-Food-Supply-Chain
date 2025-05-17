const OperationRegistry = artifacts.require("OperationRegistry");

module.exports = function (deployer) {
  deployer.deploy(OperationRegistry);
};