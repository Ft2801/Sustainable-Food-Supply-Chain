// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./UserRegistry.sol";
import "./ProductRequest.sol";
import "./OperationRegistry.sol";

contract SupplyChain {
    UserRegistry public userRegistry;
    ProductRequest public productRequest;
    OperationRegistry public operationRegistry;

    address public owner;
    mapping(address => bool) public authorizedOperators;

    event OperatorAuthorized(address indexed operator);
    event OperatorRevoked(address indexed operator);
    event ContractUpgraded(string contractType, address newAddress);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    modifier onlyAuthorized() {
        require(authorizedOperators[msg.sender] || msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedOperators[msg.sender] = true;
    }

    function initialize(
        address _userRegistry,
        address _productRequest,
        address _operationRegistry
    ) external onlyOwner {
        require(_userRegistry != address(0), "Invalid UserRegistry address");
        require(_productRequest != address(0), "Invalid ProductRequest address");
        require(_operationRegistry != address(0), "Invalid OperationRegistry address");

        userRegistry = UserRegistry(_userRegistry);
        productRequest = ProductRequest(_productRequest);
        operationRegistry = OperationRegistry(_operationRegistry);
    }

    function authorizeOperator(address _operator) external onlyOwner {
        require(_operator != address(0), "Invalid operator address");
        require(!authorizedOperators[_operator], "Operator already authorized");
        
        authorizedOperators[_operator] = true;
        emit OperatorAuthorized(_operator);
    }

    function revokeOperator(address _operator) external onlyOwner {
        require(authorizedOperators[_operator], "Operator not authorized");
        
        authorizedOperators[_operator] = false;
        emit OperatorRevoked(_operator);
    }

    function upgradeContract(string memory _contractType, address _newAddress) external onlyOwner {
        require(_newAddress != address(0), "Invalid contract address");
        
        if (keccak256(bytes(_contractType)) == keccak256(bytes("UserRegistry"))) {
            userRegistry = UserRegistry(_newAddress);
        } else if (keccak256(bytes(_contractType)) == keccak256(bytes("ProductRequest"))) {
            productRequest = ProductRequest(_newAddress);
        } else if (keccak256(bytes(_contractType)) == keccak256(bytes("OperationRegistry"))) {
            operationRegistry = OperationRegistry(_newAddress);
        } else {
            revert("Invalid contract type");
        }

        emit ContractUpgraded(_contractType, _newAddress);
    }

    // Funzioni di utilità per interagire con i contratti collegati
    function registerUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external returns (bool) {
        try userRegistry.registerUser(_name, _email, _role) {
            return true;
        } catch {
            return false;
        }
    }

    function createProductRequest(
        string memory _productName,
        uint256 _quantity,
        string memory _unit,
        uint256 _deadline
    ) external onlyAuthorized returns (uint256) {
        return productRequest.createRequest(_productName, _quantity, _unit, _deadline);
    }

    function createOperation(
        string memory _operationType,
        string memory _description,
        string memory _location,
        string memory _metadata
    ) external onlyAuthorized returns (uint256) {
        return operationRegistry.createOperation(_operationType, _description, _location, _metadata);
    }

    // Funzioni di query
    function getUserInfo(address _user) external view returns (
        string memory name,
        string memory email,
        string memory role,
        bool isActive,
        uint256 registrationDate
    ) {
        return userRegistry.getUser(_user);
    }

    function getRequestInfo(uint256 _requestId) external view returns (
        uint256 requestId,
        address requester,
        string memory productName,
        uint256 quantity,
        string memory unit,
        uint256 deadline,
        string memory status,
        uint256 createdAt,
        uint256 updatedAt
    ) {
        return productRequest.getRequest(_requestId);
    }

    function getOperationInfo(uint256 _operationId) external view returns (
        uint256 operationId,
        address operator,
        string memory operationType,
        string memory description,
        string memory location,
        uint256 timestamp,
        string memory status,
        string memory metadata
    ) {
        return operationRegistry.getOperation(_operationId);
    }
} 