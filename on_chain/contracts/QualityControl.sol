// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract QualityControl {
    struct QualityCheck {
        uint256 checkId;
        uint256 productId;
        address inspector;
        string checkType; // "CERTIFICATION", "INSPECTION", "TEST"
        string result; // "PASS", "FAIL", "PENDING"
        string details;
        uint256 timestamp;
        string metadata; // Risultati dettagliati, certificazioni, etc.
    }

    uint256 private checkCounter;
    mapping(uint256 => QualityCheck) private qualityChecks;
    mapping(uint256 => uint256[]) private productChecks;
    mapping(address => uint256[]) private inspectorChecks;

    event QualityCheckCreated(uint256 indexed checkId, uint256 indexed productId, address indexed inspector);
    event QualityCheckUpdated(uint256 indexed checkId, string result);
    event QualityCheckCompleted(uint256 indexed checkId);

    modifier validCheck(uint256 _checkId) {
        require(qualityChecks[_checkId].checkId != 0, "Quality check does not exist");
        _;
    }

    function createQualityCheck(
        uint256 _productId,
        string memory _checkType,
        string memory _details,
        string memory _metadata
    ) external returns (uint256) {
        require(bytes(_checkType).length > 0, "Check type cannot be empty");
        require(bytes(_details).length > 0, "Details cannot be empty");

        checkCounter++;
        uint256 checkId = checkCounter;

        qualityChecks[checkId] = QualityCheck({
            checkId: checkId,
            productId: _productId,
            inspector: msg.sender,
            checkType: _checkType,
            result: "PENDING",
            details: _details,
            timestamp: block.timestamp,
            metadata: _metadata
        });

        productChecks[_productId].push(checkId);
        inspectorChecks[msg.sender].push(checkId);

        emit QualityCheckCreated(checkId, _productId, msg.sender);
        return checkId;
    }

    function updateQualityCheck(
        uint256 _checkId,
        string memory _result,
        string memory _details,
        string memory _metadata
    ) external validCheck(_checkId) {
        QualityCheck storage check = qualityChecks[_checkId];
        require(check.inspector == msg.sender, "Only inspector can update check");
        require(
            keccak256(bytes(_result)) == keccak256(bytes("PASS")) ||
            keccak256(bytes(_result)) == keccak256(bytes("FAIL")) ||
            keccak256(bytes(_result)) == keccak256(bytes("PENDING")),
            "Invalid result"
        );

        check.result = _result;
        check.details = _details;
        check.metadata = _metadata;

        emit QualityCheckUpdated(_checkId, _result);

        if (
            keccak256(bytes(_result)) == keccak256(bytes("PASS")) ||
            keccak256(bytes(_result)) == keccak256(bytes("FAIL"))
        ) {
            emit QualityCheckCompleted(_checkId);
        }
    }

    function getQualityCheck(uint256 _checkId) external view validCheck(_checkId) returns (
        uint256 checkId,
        uint256 productId,
        address inspector,
        string memory checkType,
        string memory result,
        string memory details,
        uint256 timestamp,
        string memory metadata
    ) {
        QualityCheck memory check = qualityChecks[_checkId];
        return (
            check.checkId,
            check.productId,
            check.inspector,
            check.checkType,
            check.result,
            check.details,
            check.timestamp,
            check.metadata
        );
    }

    function getProductQualityChecks(uint256 _productId) external view returns (uint256[] memory) {
        return productChecks[_productId];
    }

    function getInspectorQualityChecks(address _inspector) external view returns (uint256[] memory) {
        return inspectorChecks[_inspector];
    }
} 