// SPDX-License-Identifier: MIT
// block.timestamp is used only for logging, not for decision making

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title Supply Chain CO2 Tracker
 * @dev Traccia i lotti alimentari lungo la filiera, includendo emissioni di CO₂.
 */
contract SupplyChainCO2 is Ownable, AccessControl {
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    constructor() Ownable(msg.sender) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }

    struct Lot {
        uint256 lotId;
        string productName;
        address producer;
        uint256 productionDate;
        uint256 co2Produced;
        bool exists;
    }

    struct Transformation {
        uint256 fromLotId;
        uint256 toLotId;
        address transformer;
        uint256 co2Emitted;
        uint256 date;
    }

    struct Transport {
        uint256 lotId;
        address transporter;
        uint256 co2Emitted;
        uint256 date;
        string fromLocation;
        string toLocation;
    }

    uint256 public lotCounter;
    mapping(uint256 => Lot) public lots;
    mapping(uint256 => Transformation[]) public transformations;
    mapping(uint256 => Transport[]) public transports;

    event LotCreated(uint256 lotId, string productName, address producer, uint256 co2Produced);
    event TransformationLogged(uint256 fromLotId, uint256 toLotId, address transformer, uint256 co2Emitted);
    event TransportLogged(uint256 lotId, address transporter, uint256 co2Emitted, string from, string to);

    modifier onlyOperator() {
        require(hasRole(OPERATOR_ROLE, msg.sender), "Not an operator");
        _;
    }

    function createLot(string memory productName, uint256 co2Produced) public onlyOperator {
        lotCounter++;
        lots[lotCounter] = Lot(lotCounter, productName, msg.sender, block.timestamp, co2Produced, true);
        emit LotCreated(lotCounter, productName, msg.sender, co2Produced);
    }

    function logTransformation(uint256 fromLotId, string memory newProductName, uint256 co2Emitted) public onlyOperator {
        require(lots[fromLotId].exists, "Original lot does not exist");
        lotCounter++;
        lots[lotCounter] = Lot(lotCounter, newProductName, msg.sender, block.timestamp, co2Emitted, true);
        transformations[fromLotId].push(Transformation(fromLotId, lotCounter, msg.sender, co2Emitted, block.timestamp));
        emit TransformationLogged(fromLotId, lotCounter, msg.sender, co2Emitted);
    }

    function logTransport(uint256 lotId, uint256 co2Emitted, string memory fromLocation, string memory toLocation) public onlyOperator {
        require(lots[lotId].exists, "Lot does not exist");
        transports[lotId].push(Transport(lotId, msg.sender, co2Emitted, block.timestamp, fromLocation, toLocation));
        emit TransportLogged(lotId, msg.sender, co2Emitted, fromLocation, toLocation);
    }

    function grantOperatorRole(address account) public onlyOwner {
        _grantRole(OPERATOR_ROLE, account);
    }

    function revokeOperatorRole(address account) public onlyOwner {
        _revokeRole(OPERATOR_ROLE, account);
    }
}
