// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./CompanyRegistry.sol";

contract TokenExchange is ReentrancyGuard {
    CompanyRegistry public companyRegistry;
    
    enum RequestStatus { Pending, Accepted, Rejected, Cancelled }
    
    struct TokenRequest {
        uint256 id;
        address requester; // Azienda che richiede i token
        address provider; // Azienda che dovrebbe fornire i token
        address tokenContract; // Indirizzo del contratto token ERC20
        uint256 amount; // Quantità di token richiesta
        RequestStatus status;
        string reasonForRejection; // Opzionale: motivo del rifiuto
        uint256 creationTimestamp; // Timestamp di creazione
        uint256 lastUpdateTimestamp; // Timestamp ultimo aggiornamento
    }
    
    mapping (uint256 => TokenRequest) public requests;
    uint256 public nextRequestId;
    
    event RequestCreated(
        uint256 indexed requestId,
        address indexed requester,
        address indexed provider,
        address tokenContract,
        uint256 amount
    );
    
    event RequestAccepted(uint256 indexed requestId, address indexed provider);
    event RequestRejected(uint256 indexed requestId, address indexed provider, string reason);
    event RequestCancelled(uint256 indexed requestId, address indexed requester);
    
    modifier onlyRegisteredCompany(address _companyAddress) {
        require(companyRegistry.isRegistered(_companyAddress), "TokenExchange: Company not registered");
        _;
    }
    
    modifier onlyRequester(uint256 _requestId) {
        require(requests[_requestId].requester == msg.sender, "TokenExchange: Not the requester");
        _;
    }
    
    modifier onlyProvider(uint256 _requestId) {
        require(requests[_requestId].provider == msg.sender, "TokenExchange: Not the provider");
        _;
    }
    
    modifier requestExists(uint256 _requestId) {
        require(requests[_requestId].id != 0, "TokenExchange: Request does not exist");
        _;
    }
    
    modifier requestIsPending(uint256 _requestId) {
        require(requests[_requestId].status == RequestStatus.Pending, "TokenExchange: Request not pending");
        _;
    }
    
    constructor(address _companyRegistryAddress) {
        require(_companyRegistryAddress != address(0), "TokenExchange: Invalid registry address");
        companyRegistry = ICompanyRegistry(_companyRegistryAddress);
        nextRequestId = 1; // Iniziamo gli ID da 1 per evitare collisioni con lo zero di default
    }
    
    function createTokenRequest(
        address _provider,
        address _tokenContract,
        uint256 _amount
    ) external onlyRegisteredCompany(msg.sender) nonReentrant returns (uint256) {
        require(_provider != msg.sender, "TokenExchange: Cannot request tokens from yourself");
        require(companyRegistry.isRegistered(_provider), "TokenExchange: Provider not a registered company");
        require(_tokenContract != address(0), "TokenExchange: Invalid token contract address");
        require(_amount > 0, "TokenExchange: Amount must be greater than zero");
        
        uint256 requestId = nextRequestId;
        requests[requestId] = TokenRequest({
            id: requestId,
            requester: msg.sender,
            provider: _provider,
            tokenContract: _tokenContract,
            amount: _amount,
            status: RequestStatus.Pending,
            reasonForRejection: "",
            creationTimestamp: block.timestamp,
            lastUpdateTimestamp: block.timestamp
        });
        nextRequestId++;
        emit RequestCreated(requestId, msg.sender, _provider, _tokenContract, _amount);
        return requestId;
    }
    
    function acceptTokenRequest(uint256 _requestId)
        external
        onlyRegisteredCompany(msg.sender)
        onlyProvider(_requestId)
        requestExists(_requestId)
        requestIsPending(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        IERC20 token = IERC20(currentRequest.tokenContract);
        
        uint256 allowance = token.allowance(currentRequest.provider, address(this));
        require(allowance >= currentRequest.amount, "TokenExchange: Insufficient allowance from provider");
        
        uint256 providerBalance = token.balanceOf(currentRequest.provider);
        require(providerBalance >= currentRequest.amount, "TokenExchange: Insufficient balance from provider");
        
        bool success = token.transferFrom(currentRequest.provider, currentRequest.requester, currentRequest.amount);
        require(success, "TokenExchange: Token transfer failed");
        
        currentRequest.status = RequestStatus.Accepted;
        currentRequest.lastUpdateTimestamp = block.timestamp;
        
        emit RequestAccepted(_requestId, msg.sender);
    }
    
    function rejectTokenRequest(uint256 _requestId, string calldata _reason)
        external
        onlyRegisteredCompany(msg.sender)
        onlyProvider(_requestId)
        requestExists(_requestId)
        requestIsPending(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        currentRequest.status = RequestStatus.Rejected;
        currentRequest.reasonForRejection = _reason;
        currentRequest.lastUpdateTimestamp = block.timestamp;
        
        emit RequestRejected(_requestId, msg.sender, _reason);
    }
    
    function cancelTokenRequest(uint256 _requestId)
        external
        onlyRegisteredCompany(msg.sender)
        onlyRequester(_requestId)
        requestExists(_requestId)
        requestIsPending(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        currentRequest.status = RequestStatus.Cancelled;
        currentRequest.lastUpdateTimestamp = block.timestamp;
        
        emit RequestCancelled(_requestId, msg.sender);
    }
    
    function getRequestDetails(uint256 _requestId)
        external
        view
        requestExists(_requestId)
        returns (TokenRequest memory)
    {
        return requests[_requestId];
    }
}