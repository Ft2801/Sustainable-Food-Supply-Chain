// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title SustainableFoodChain
 * @dev Un contratto unificato che integra tutte le funzionalità della supply chain sostenibile:
 * - Registro utenti
 * - Registro aziende
 * - Token CO2 per la sostenibilità
 * - Scambio di token tra aziende
 */
contract SustainableFoodChain is ReentrancyGuard {
    // ======== EVENTI ========
    // Eventi User Registry
    event UserRegistered(address indexed userAddress, string name, string role);
    event UserUpdated(address indexed userAddress, string name, string role);
    event UserDeactivated(address indexed userAddress);
    
    // Eventi Company Registry
    event CompanyRegistered(address indexed companyAddress, string name, CompanyType companyType, string location);
    event CompanyUpdated(address indexed companyAddress, string newName);
    event SustainabilityScoreUpdated(address indexed companyAddress, uint256 oldScore, uint256 newScore);
    event CertificationsUpdated(address indexed companyAddress, string certifications);
    
    // Eventi Token
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);
    
    // Eventi Token Exchange
    event RequestCreated(
        uint256 indexed requestId,
        address indexed requester,
        address indexed provider,
        uint256 amount,
        string sustainabilityPurpose,
        uint256 estimatedCO2Reduction
    );
    event RequestAccepted(uint256 indexed requestId, address indexed provider);
    event RequestRejected(uint256 indexed requestId, address indexed provider, string reason);
    event RequestCancelled(uint256 indexed requestId, address indexed requester);
    event SustainabilityVerified(uint256 indexed requestId, address indexed verifier, bool verified);
    
    // ======== STRUTTURE DATI ========
    // User Registry
    struct User {
        string name;
        string email;
        string role; // "PRODUCER", "DISTRIBUTOR", "RETAILER", "CONSUMER"
        bool isActive;
        uint256 registrationDate;
    }
    
    // Company Registry
    enum CompanyType { Producer, Processor, Distributor, Retailer, Other }
    
    struct Company {
        address owner;
        string name;
        bool isRegistered;
        CompanyType companyType;
        string location;
        string sustainabilityCertifications;
        uint256 sustainabilityScore;
        uint256 registrationDate;
    }
    
    // Token Exchange
    enum RequestStatus { Pending, Accepted, Rejected, Cancelled }
    
    struct TokenRequest {
        uint256 id;
        address requester;
        address provider;
        uint256 amount;
        RequestStatus status;
        string reasonForRejection;
        uint256 creationTimestamp;
        uint256 lastUpdateTimestamp;
        string sustainabilityPurpose;
        uint256 estimatedCO2Reduction;
        bool isSustainabilityVerified;
    }
    
    // ======== STATO ========
    // User Registry
    mapping(address => User) private users;
    mapping(address => bool) private isUserRegistered;
    
    // Company Registry
    mapping(address => Company) public companies;
    mapping(address => bool) public isCompanyAddressRegistered;
    address[] public registeredCompanyAddresses;
    
    // Token (CO2Token)
    string public name = "CO2 Token";
    string public symbol = "CO2";
    uint8 public decimals = 18;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    // Token Exchange
    mapping(uint256 => TokenRequest) public requests;
    uint256 public nextRequestId = 1;
    
    // ======== MODIFICATORI ========
    modifier onlyRegisteredUser() {
        require(isUserRegistered[msg.sender], "User not registered");
        _;
    }
    
    modifier onlyRegisteredCompany(address _companyAddress) {
        require(isCompanyAddressRegistered[_companyAddress], "Company not registered");
        _;
    }
    
    modifier notRegisteredCompany(address _companyAddress) {
        require(!isCompanyAddressRegistered[_companyAddress], "Company already registered");
        _;
    }
    
    modifier onlyRequester(uint256 _requestId) {
        require(requests[_requestId].requester == msg.sender, "Not the requester");
        _;
    }
    
    modifier onlyProvider(uint256 _requestId) {
        require(requests[_requestId].provider == msg.sender, "Not the provider");
        _;
    }
    
    modifier requestExists(uint256 _requestId) {
        require(requests[_requestId].id != 0, "Request does not exist");
        _;
    }
    
    modifier requestIsPending(uint256 _requestId) {
        require(requests[_requestId].status == RequestStatus.Pending, "Request not pending");
        _;
    }
    
    constructor() {
        // Inizializzazione del contratto
    }
    
    // ======== FUNZIONI USER REGISTRY ========
    function registerUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external {
        require(!isUserRegistered[msg.sender], "User already registered");
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_email).length > 0, "Email cannot be empty");
        require(bytes(_role).length > 0, "Role cannot be empty");

        users[msg.sender] = User({
            name: _name,
            email: _email,
            role: _role,
            isActive: true,
            registrationDate: block.timestamp
        });

        isUserRegistered[msg.sender] = true;
        emit UserRegistered(msg.sender, _name, _role);
    }

    function updateUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external onlyRegisteredUser {
        require(users[msg.sender].isActive, "User is not active");
        
        users[msg.sender].name = _name;
        users[msg.sender].email = _email;
        users[msg.sender].role = _role;

        emit UserUpdated(msg.sender, _name, _role);
    }

    function deactivateUser() external onlyRegisteredUser {
        require(users[msg.sender].isActive, "User already deactivated");
        users[msg.sender].isActive = false;
        emit UserDeactivated(msg.sender);
    }

    function getUser(address _userAddress) external view returns (
        string memory name,
        string memory email,
        string memory role,
        bool isActive,
        uint256 registrationDate
    ) {
        require(isUserRegistered[_userAddress], "User not registered");
        User memory user = users[_userAddress];
        return (user.name, user.email, user.role, user.isActive, user.registrationDate);
    }

    function isUserRegisteredCheck(address _userAddress) external view returns (bool) {
        return isUserRegistered[_userAddress];
    }
    
    // ======== FUNZIONI COMPANY REGISTRY ========
    function registerCompany(
        string calldata _name,
        CompanyType _companyType,
        string calldata _location,
        string calldata _certifications
    ) external notRegisteredCompany(msg.sender) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_location).length > 0, "Location cannot be empty");
        
        companies[msg.sender] = Company({
            owner: msg.sender,
            name: _name,
            isRegistered: true,
            companyType: _companyType,
            location: _location,
            sustainabilityCertifications: _certifications,
            sustainabilityScore: 50, // Default starting score
            registrationDate: block.timestamp
        });
        
        isCompanyAddressRegistered[msg.sender] = true;
        registeredCompanyAddresses.push(msg.sender);
        emit CompanyRegistered(msg.sender, _name, _companyType, _location);
    }

    function updateCompanyName(string calldata _newName) external onlyRegisteredCompany(msg.sender) {
        require(bytes(_newName).length > 0, "Name cannot be empty");
        companies[msg.sender].name = _newName;
        emit CompanyUpdated(msg.sender, _newName);
    }
    
    function getCompany(address _companyAddress) external view onlyRegisteredCompany(_companyAddress) returns (
        string memory name,
        address owner,
        CompanyType companyType,
        string memory location,
        string memory certifications,
        uint256 sustainabilityScore,
        uint256 registrationDate
    ) {
        Company storage company = companies[_companyAddress];
        return (
            company.name,
            company.owner,
            company.companyType,
            company.location,
            company.sustainabilityCertifications,
            company.sustainabilityScore,
            company.registrationDate
        );
    }
    
    function isCompanyRegistered(address _companyAddress) external view returns (bool) {
        return isCompanyAddressRegistered[_companyAddress];
    }
    
    function getAllRegisteredCompanyAddresses() external view returns (address[] memory) {
        return registeredCompanyAddresses; 
    }
    
    function updateSustainabilityScore(address _companyAddress, uint256 _newScore) external onlyRegisteredCompany(_companyAddress) {
        require(_newScore <= 100, "Score must be between 0 and 100");
        require(msg.sender == address(this) || msg.sender == companies[_companyAddress].owner, "Not authorized");
        
        uint256 oldScore = companies[_companyAddress].sustainabilityScore;
        companies[_companyAddress].sustainabilityScore = _newScore;
        
        emit SustainabilityScoreUpdated(_companyAddress, oldScore, _newScore);
    }
    
    function updateCertifications(string calldata _certifications) external onlyRegisteredCompany(msg.sender) {
        companies[msg.sender].sustainabilityCertifications = _certifications;
        emit CertificationsUpdated(msg.sender, _certifications);
    }
    
    function getCompaniesByType(CompanyType _companyType) external view returns (address[] memory) {
        uint256 count = 0;
        
        // Count companies of the specified type
        for (uint256 i = 0; i < registeredCompanyAddresses.length; i++) {
            if (companies[registeredCompanyAddresses[i]].companyType == _companyType) {
                count++;
            }
        }
        
        // Create and populate the result array
        address[] memory result = new address[](count);
        uint256 index = 0;
        
        for (uint256 i = 0; i < registeredCompanyAddresses.length; i++) {
            if (companies[registeredCompanyAddresses[i]].companyType == _companyType) {
                result[index] = registeredCompanyAddresses[i];
                index++;
            }
        }
        
        return result;
    }
    
    // ======== FUNZIONI TOKEN (CO2TOKEN) ========
    function totalSupply() public view returns (uint256) {
        return 1000000 * 10**uint256(decimals); // Initial supply of 1M tokens
    }
    
    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }
    
    function transfer(address recipient, uint256 amount) public returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }
    
    function allowance(address owner, address spender) public view returns (uint256) {
        return _allowances[owner][spender];
    }
    
    function approve(address spender, uint256 amount) public returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address sender, address recipient, uint256 amount) public returns (bool) {
        _transfer(sender, recipient, amount);
        _approve(sender, msg.sender, _allowances[sender][msg.sender] - amount);
        return true;
    }
    
    function rewardCompensatoryAction(uint256 amount) public {
        _mint(msg.sender, amount);
    }
    
    function processOperationCO2(uint256 consumedCO2, uint256 thresholdCO2) public returns (bool) {
        if (consumedCO2 < thresholdCO2) {
            uint256 rewardAmount = thresholdCO2 - consumedCO2;
            _mint(msg.sender, rewardAmount);
            return true;
        } else if (consumedCO2 > thresholdCO2) {
            uint256 penaltyAmount = consumedCO2 - thresholdCO2;
            require(_balances[msg.sender] >= penaltyAmount, "Insufficient tokens for CO2 penalty");
            _burn(msg.sender, penaltyAmount);
            return true;
        }
        return false;
    }
    
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "Transfer from zero address");
        require(recipient != address(0), "Transfer to zero address");
        require(_balances[sender] >= amount, "Insufficient balance");
        
        _balances[sender] -= amount;
        _balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    }
    
    function _approve(address owner, address spender, uint256 amount) internal {
        require(owner != address(0), "Approve from zero address");
        require(spender != address(0), "Approve to zero address");
        
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }
    
    function _mint(address account, uint256 amount) internal {
        require(account != address(0), "Mint to zero address");
        
        _balances[account] += amount;
        emit TokensMinted(account, amount);
        emit Transfer(address(0), account, amount);
    }
    
    function _burn(address account, uint256 amount) internal {
        require(account != address(0), "Burn from zero address");
        require(_balances[account] >= amount, "Burn amount exceeds balance");
        
        _balances[account] -= amount;
        emit TokensBurned(account, amount);
        emit Transfer(account, address(0), amount);
    }
    
    // ======== FUNZIONI TOKEN EXCHANGE ========
    function createTokenRequest(
        address _provider,
        uint256 _amount,
        string calldata _sustainabilityPurpose,
        uint256 _estimatedCO2Reduction
    ) external onlyRegisteredCompany(msg.sender) nonReentrant returns (uint256) {
        require(_provider != msg.sender, "Cannot request tokens from yourself");
        require(isCompanyAddressRegistered[_provider], "Provider not a registered company");
        require(_amount > 0, "Amount must be greater than zero");
        require(bytes(_sustainabilityPurpose).length > 0, "Sustainability purpose required");
        
        uint256 requestId = nextRequestId;
        requests[requestId] = TokenRequest({
            id: requestId,
            requester: msg.sender,
            provider: _provider,
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
        
        uint256 providerBalance = _balances[currentRequest.provider];
        require(providerBalance >= currentRequest.amount, "Insufficient balance from provider");
        
        // Trasferimento diretto dei token (non è necessario l'allowance perché è tutto interno)
        _transfer(currentRequest.provider, currentRequest.requester, currentRequest.amount);
        
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
        // we can directly update company sustainability scores
        if (_verified && currentRequest.status == RequestStatus.Pending) {
            // Aggiornamento del punteggio di sostenibilità del richiedente
            // Questo è un esempio di come l'integrazione in un unico contratto semplifica le operazioni
            uint256 oldScore = companies[currentRequest.requester].sustainabilityScore;
            uint256 newScore = oldScore;
            
            // Incrementa il punteggio in base alla riduzione di CO2 stimata
            if (currentRequest.estimatedCO2Reduction > 1000) {
                newScore = oldScore + 5 > 100 ? 100 : oldScore + 5;
            } else if (currentRequest.estimatedCO2Reduction > 500) {
                newScore = oldScore + 3 > 100 ? 100 : oldScore + 3;
            } else if (currentRequest.estimatedCO2Reduction > 100) {
                newScore = oldScore + 1 > 100 ? 100 : oldScore + 1;
            }
            
            if (newScore != oldScore) {
                companies[currentRequest.requester].sustainabilityScore = newScore;
                emit SustainabilityScoreUpdated(currentRequest.requester, oldScore, newScore);
            }
        }
    }
    
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
