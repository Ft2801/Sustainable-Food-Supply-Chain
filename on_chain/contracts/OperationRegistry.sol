// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OperationRegistry {
    struct Operation {
        uint256 operationId;
        address operator;
        string operationType; // "PRODUCTION", "PROCESSING", "TRANSPORT", "STORAGE", "DISTRIBUTION"
        string description;
        string location;
        uint256 timestamp;
        string status; // "IN_PROGRESS", "COMPLETED", "CANCELLED"
        string metadata; // JSON string with additional data
    }

    uint256 private operationCounter;
    mapping(uint256 => Operation) private operations;
    mapping(address => uint256[]) private userOperations;

    event OperationCreated(uint256 indexed operationId, address indexed operator, string operationType);
    event OperationStatusUpdated(uint256 indexed operationId, string newStatus);
    event OperationMetadataUpdated(uint256 indexed operationId, string metadata);

    modifier validOperation(uint256 _operationId) {
        require(operations[_operationId].operationId != 0, "Operation does not exist");
        _;
    }

    function createOperation(
        string memory _operationType,
        string memory _description,
        string memory _location,
        string memory _metadata
    ) external returns (uint256) {
        require(bytes(_operationType).length > 0, "Operation type cannot be empty");
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(bytes(_location).length > 0, "Location cannot be empty");

        operationCounter++;
        uint256 operationId = operationCounter;

        operations[operationId] = Operation({
            operationId: operationId,
            operator: msg.sender,
            operationType: _operationType,
            description: _description,
            location: _location,
            timestamp: block.timestamp,
            status: "IN_PROGRESS",
            metadata: _metadata
        });

        userOperations[msg.sender].push(operationId);
        emit OperationCreated(operationId, msg.sender, _operationType);
        return operationId;
    }

    function updateOperationStatus(uint256 _operationId, string memory _newStatus)
        external
        validOperation(_operationId)
    {
        Operation storage operation = operations[_operationId];
        require(
            keccak256(bytes(_newStatus)) == keccak256(bytes("IN_PROGRESS")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("CANCELLED")),
            "Invalid status"
        );

        operation.status = _newStatus;
        emit OperationStatusUpdated(_operationId, _newStatus);
    }

    function updateOperationMetadata(uint256 _operationId, string memory _metadata)
        external
        validOperation(_operationId)
    {
        Operation storage operation = operations[_operationId];
        operation.metadata = _metadata;
        emit OperationMetadataUpdated(_operationId, _metadata);
    }

    function getOperation(uint256 _operationId)
        external
        view
        validOperation(_operationId)
        returns (
            uint256 operationId,
            address operator,
            string memory operationType,
            string memory description,
            string memory location,
            uint256 timestamp,
            string memory status,
            string memory metadata
        )
    {
        Operation memory operation = operations[_operationId];
        return (
            operation.operationId,
            operation.operator,
            operation.operationType,
            operation.description,
            operation.location,
            operation.timestamp,
            operation.status,
            operation.metadata
        );
    }

    function getUserOperations(address _user) external view returns (uint256[] memory) {
        return userOperations[_user];
    }
} 