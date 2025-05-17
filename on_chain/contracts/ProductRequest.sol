// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductRequest {
    struct Request {
        uint256 requestId;
        address requester;
        string productName;
        uint256 quantity;
        string unit;
        uint256 deadline;
        string status; // "PENDING", "ACCEPTED", "REJECTED", "COMPLETED"
        uint256 createdAt;
        uint256 updatedAt;
    }

    uint256 private requestCounter;
    mapping(uint256 => Request) private requests;
    mapping(address => uint256[]) private userRequests;

    event RequestCreated(uint256 indexed requestId, address indexed requester, string productName);
    event RequestStatusUpdated(uint256 indexed requestId, string newStatus);
    event RequestCompleted(uint256 indexed requestId);

    modifier validRequest(uint256 _requestId) {
        require(requests[_requestId].requestId != 0, "Request does not exist");
        _;
    }

    function createRequest(
        string memory _productName,
        uint256 _quantity,
        string memory _unit,
        uint256 _deadline
    ) external returns (uint256) {
        require(bytes(_productName).length > 0, "Product name cannot be empty");
        require(_quantity > 0, "Quantity must be greater than 0");
        require(bytes(_unit).length > 0, "Unit cannot be empty");
        require(_deadline > block.timestamp + 60, "Deadline must be at least 1 minute in the future");

        requestCounter++;
        uint256 requestId = requestCounter;

        requests[requestId] = Request({
            requestId: requestId,
            requester: msg.sender,
            productName: _productName,
            quantity: _quantity,
            unit: _unit,
            deadline: _deadline,
            status: "PENDING",
            createdAt: block.timestamp,
            updatedAt: block.timestamp
        });

        userRequests[msg.sender].push(requestId);
        emit RequestCreated(requestId, msg.sender, _productName);
        return requestId;
    }

    function updateRequestStatus(uint256 _requestId, string memory _newStatus) 
        external 
        validRequest(_requestId) 
    {
        Request storage request = requests[_requestId];
        require(
            keccak256(bytes(_newStatus)) == keccak256(bytes("ACCEPTED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("REJECTED")) ||
            keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED")),
            "Invalid status"
        );

        request.status = _newStatus;
        request.updatedAt = block.timestamp;

        emit RequestStatusUpdated(_requestId, _newStatus);
        
        if (keccak256(bytes(_newStatus)) == keccak256(bytes("COMPLETED"))) {
            emit RequestCompleted(_requestId);
        }
    }

    function getRequest(uint256 _requestId) 
        external 
        view 
        validRequest(_requestId) 
        returns (
            uint256 requestId,
            address requester,
            string memory productName,
            uint256 quantity,
            string memory unit,
            uint256 deadline,
            string memory status,
            uint256 createdAt,
            uint256 updatedAt
        ) 
    {
        Request memory request = requests[_requestId];
        return (
            request.requestId,
            request.requester,
            request.productName,
            request.quantity,
            request.unit,
            request.deadline,
            request.status,
            request.createdAt,
            request.updatedAt
        );
    }

    function getUserRequests(address _user) external view returns (uint256[] memory) {
        return userRequests[_user];
    }
} 