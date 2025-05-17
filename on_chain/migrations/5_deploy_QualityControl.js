const QualityControl = artifacts.require("QualityControl");

module.exports = function (deployer) {
  deployer.deploy(QualityControl);
};