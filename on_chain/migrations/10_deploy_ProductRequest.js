const ProductRequest = artifacts.require("ProductRequest");

module.exports = function (deployer) {
  deployer.deploy(ProductRequest);
};