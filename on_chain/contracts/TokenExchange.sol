// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./IERC20.sol";
import "./CompanyRegistry.sol";

/**
 * @title TokenExchange
 * @dev Facilitates token exchanges between companies in the sustainable food supply chain
 * with additional sustainability incentives and tracking
 */

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
        string sustainabilityPurpose; // Scopo sostenibile della richiesta
        uint256 estimatedCO2Reduction; // Stima della riduzione di CO2 in kg
        bool isSustainabilityVerified; // Verifica dello scopo sostenibile
    }
    
    mapping (uint256 => TokenRequest) public requests;
    uint256 public nextRequestId;
    
    event RequestCreated(
        uint256 indexed requestId,
        address indexed requester,
        address indexed provider,
        address tokenContract,
        uint256 amount,
        string sustainabilityPurpose,
        uint256 estimatedCO2Reduction
    );
    
    event RequestAccepted(uint256 indexed requestId, address indexed provider);
    event RequestRejected(uint256 indexed requestId, address indexed provider, string reason);
    event RequestCancelled(uint256 indexed requestId, address indexed requester);
    event SustainabilityVerified(uint256 indexed requestId, address indexed verifier, bool verified);
    
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
        companyRegistry = CompanyRegistry(_companyRegistryAddress);
        nextRequestId = 1; // Iniziamo gli ID da 1 per evitare collisioni con lo zero di default
    }
    
    function createTokenRequest(
        address _provider,
        address _tokenContract,
        uint256 _amount,
        string calldata _sustainabilityPurpose,
        uint256 _estimatedCO2Reduction
    ) external onlyRegisteredCompany(msg.sender) nonReentrant returns (uint256) {
        require(_provider != msg.sender, "TokenExchange: Cannot request tokens from yourself");
        require(companyRegistry.isRegistered(_provider), "TokenExchange: Provider not a registered company");
        require(_tokenContract != address(0), "TokenExchange: Invalid token contract address");
        require(_amount > 0, "TokenExchange: Amount must be greater than zero");
        require(bytes(_sustainabilityPurpose).length > 0, "TokenExchange: Sustainability purpose required");
        
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
            lastUpdateTimestamp: block.timestamp,
            sustainabilityPurpose: _sustainabilityPurpose,
            estimatedCO2Reduction: _estimatedCO2Reduction,
            isSustainabilityVerified: false
        });
        nextRequestId++;
        emit RequestCreated(
            requestId, 
            msg.sender, 
            _provider, 
            _tokenContract, 
            _amount, 
            _sustainabilityPurpose, 
            _estimatedCO2Reduction
        );
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
    
    /**
     * @dev Verify the sustainability claims of a token request
     * @param _requestId The ID of the request to verify
     * @param _verified Whether the sustainability claims are verified
     * @notice Only the provider of the request can verify the sustainability claims
     */
    function verifySustainability(uint256 _requestId, bool _verified)
        external
        onlyRegisteredCompany(msg.sender)
        onlyProvider(_requestId)
        requestExists(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        currentRequest.isSustainabilityVerified = _verified;
        currentRequest.lastUpdateTimestamp = block.timestamp;
        
        emit SustainabilityVerified(_requestId, msg.sender, _verified);
        
        // If sustainability claims are verified and the request is still pending,
        // we can optionally provide incentives or update company sustainability scores
        if (_verified && currentRequest.status == RequestStatus.Pending) {
            // Example: Update the sustainability score of the requester
            // This is just an example and would need proper implementation
            // companyRegistry.updateSustainabilityScore(currentRequest.requester, newScore);
        }
    }
    
    /**
     * @dev Get all token requests with CO2 reduction above a certain threshold
     * @param _minCO2Reduction Minimum CO2 reduction in kg
     * @param _onlyVerified Whether to only include verified sustainability claims
     * @return Array of request IDs meeting the criteria
     */
    function getSustainableRequests(uint256 _minCO2Reduction, bool _onlyVerified) 
        external 
        view 
        returns (uint256[] memory) 
    {
        // First, count the number of requests that meet our criteria
        uint256 count = 0;
        for (uint256 i = 1; i < nextRequestId; i++) {
            if (requests[i].id != 0 && 
                requests[i].estimatedCO2Reduction >= _minCO2Reduction &&
                (!_onlyVerified || requests[i].isSustainabilityVerified)) {
                count++;
            }
        }
        
        // Create an array to hold the results
        uint256[] memory result = new uint256[](count);
        
        // Fill the array with request IDs that meet our criteria
        uint256 index = 0;
        for (uint256 i = 1; i < nextRequestId; i++) {
            if (requests[i].id != 0 && 
                requests[i].estimatedCO2Reduction >= _minCO2Reduction &&
                (!_onlyVerified || requests[i].isSustainabilityVerified)) {
                result[index] = i;
                index++;
            }
        }
        
        return result;
    }
}