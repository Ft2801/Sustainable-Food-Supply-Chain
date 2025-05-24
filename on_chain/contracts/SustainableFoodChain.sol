// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title SustainableFoodChain
 * @dev Un contratto unificato per la supply chain sostenibile, con registro aziende,
 *      token CO2 (ERC20), e meccanismi di scambio e tracciabilità.
 *      Semplificato con l'integrazione di ERC20 da OpenZeppelin.
 */
contract SustainableFoodChain is ReentrancyGuard, ERC20 {
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
    
    // Eventi Operazioni
    event OperationCreated(
        uint256 indexed operationId,
        address indexed companyAddress,
        OperationType operationType,
        uint256 timestamp,
        string description,
        uint256 batchId
    );
    
    // Eventi Azioni Compensative
    event CompensationActionCreated(
        uint256 indexed actionId,
        address indexed companyAddress,
        string actionType,
        uint256 timestamp,
        uint256 co2Reduction,
        string description
    );
    
    // Eventi Lotti
    event BatchCreated(
        uint256 indexed batchId,
        address indexed producerAddress,
        string productName,
        uint256 quantity,
        uint256 timestamp,
        string metadata
    );
    event BatchTransferred(
        uint256 indexed batchId,
        address indexed fromAddress,
        address indexed toAddress,
        uint256 timestamp
    );
    
    // ======== STRUTTURE DATI ========
    struct User {
        string name;
        string email;
        string role;
        bool isActive;
        uint256 registrationDate;
    }
    
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
    
    enum OperationType { Production, Processing, Transport, Sale }
    
    struct Operation {
        uint256 id;
        address companyAddress;
        OperationType operationType;
        uint256 timestamp;
        string description;
        uint256 batchId;
        bool isValid;
    }
    
    struct CompensationAction {
        uint256 id;
        address companyAddress;
        string actionType;
        uint256 timestamp;
        uint256 co2Reduction;
        string description;
        bool isVerified;
    }
    
    struct Batch {
        uint256 id;
        address currentOwner;
        address producer;
        string productName;
        uint256 quantity;
        uint256 creationTimestamp;
        string metadata;
        uint256[] operationIds;
        bool isActive;
    }
    
    // ======== STATO ========
    mapping(address => User) private users;
    mapping(address => bool) private isUserRegistered;
    mapping(address => uint256[]) public companyOperations;

    
    mapping(address => Company) public companies;
    address[] public registeredCompanyAddresses; // Mantenuto per query on-chain
    
    mapping(uint256 => TokenRequest) public requests;
    uint256 public nextRequestId = 1;
    
    mapping(uint256 => Operation) public operations;
    uint256 public nextOperationId = 1;
    
    mapping(uint256 => CompensationAction) public compensationActions;
    uint256 public nextCompensationActionId = 1;
    mapping(address => uint256[]) private companyCompensationActions;
    
    mapping(uint256 => Batch) public batches;
    uint256 public nextBatchId = 1;
    mapping(address => uint256[]) private companyBatches;
    
    // Variabili e mapping per ERC20 (name, symbol, decimals, _balances, _allowances)
    // sono ora gestite dalla classe base ERC20.sol
    
    // ======== MODIFICATORI ========
    modifier onlyRegisteredUser() {
        require(isUserRegistered[msg.sender], "User not registered");
        _;
    }
    
    modifier onlyRegisteredCompany(address _companyAddress) {
        require(companies[_companyAddress].isRegistered, "Company not registered");
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
    
    constructor() ERC20("CO2 Token", "CO2") { // Inizializza il token ERC20
        // È possibile mintare una supply iniziale qui, ad es. al deployer:
        // _mint(msg.sender, 1000000 * (10**decimals())); // 1 Milione di token
    }
    
    // ======== FUNZIONI USER REGISTRY ========
    function registerUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external {
        require(!isUserRegistered[msg.sender], "User already registered");
        require(bytes(_name).length > 0, "Name cannot be empty");
        // Aggiungere validazione email se necessario (più complesso on-chain)
        require(bytes(_role).length > 0, "Role cannot be empty");

        users[msg.sender] = User(_name, _email, _role, true, block.timestamp);
        isUserRegistered[msg.sender] = true;
        emit UserRegistered(msg.sender, _name, _role);
    }

    function updateUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external onlyRegisteredUser {
        User storage user = users[msg.sender];
        require(user.isActive, "User is not active");
        
        user.name = _name;
        user.email = _email;
        user.role = _role;
        emit UserUpdated(msg.sender, _name, _role);
    }

    function deactivateUser() external onlyRegisteredUser {
        require(users[msg.sender].isActive, "User already deactivated");
        users[msg.sender].isActive = false;
        emit UserDeactivated(msg.sender);
    }

    function getUser(address _userAddress) external view returns (User memory) {
        require(isUserRegistered[_userAddress], "User not registered");
        return users[_userAddress];
    }

    function isUserAddressRegistered(address _userAddress) external view returns (bool) {
        return isUserRegistered[_userAddress];
    }
    
    // ======== FUNZIONI COMPANY REGISTRY ========
    function registerCompany(
        string calldata _name,
        CompanyType _companyType,
        string calldata _location,
        string calldata _certifications
    ) external {
        require(!companies[msg.sender].isRegistered, "Company already registered by this address");
        require(bytes(_name).length > 0, "Company name cannot be empty");
        
        companies[msg.sender] = Company(
            msg.sender,
            _name,
            true,
            _companyType,
            _location,
            _certifications,
            50, // Default sustainability score
            block.timestamp
        );
        
        registeredCompanyAddresses.push(msg.sender);
        emit CompanyRegistered(msg.sender, _name, _companyType, _location);
    }

    function updateCompanyName(string calldata _newName) external onlyRegisteredCompany(msg.sender) {
        require(bytes(_newName).length > 0, "Name cannot be empty");
        companies[msg.sender].name = _newName;
        emit CompanyUpdated(msg.sender, _newName);
    }
    
    function getCompany(address _companyAddress) external view onlyRegisteredCompany(_companyAddress) returns (Company memory) {
        return companies[_companyAddress];
    }
    
    function isCompanyAddressRegistered(address _companyAddress) external view returns (bool) {
        return companies[_companyAddress].isRegistered;
    }
    
    function getAllRegisteredCompanyAddresses() external view returns (address[] memory) {
        return registeredCompanyAddresses; 
    }
    
    function updateSustainabilityScore(address _companyAddress, uint256 _newScore) external onlyRegisteredCompany(_companyAddress) {
        require(_newScore <= 100, "Score must be between 0 and 100");
        // Solo il proprietario dell'azienda o una logica interna possono aggiornare il punteggio
        require(msg.sender == companies[_companyAddress].owner || msg.sender == address(this), "Not authorized to update score");
        
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
        for (uint256 i = 0; i < registeredCompanyAddresses.length; i++) {
            if (companies[registeredCompanyAddresses[i]].companyType == _companyType) {
                count++;
            }
        }
        address[] memory result = new address[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < registeredCompanyAddresses.length; i++) {
            if (companies[registeredCompanyAddresses[i]].companyType == _companyType) {
                result[index++] = registeredCompanyAddresses[i];
            }
        }
        return result;
    }
    
    // ======== FUNZIONI PER OPERAZIONI, AZIONI COMPENSATIVE, LOTTI ========
    // (Queste sezioni rimangono strutturalmente simili, ma l'interazione con i token è cambiata)

    event DebugOperation(uint256 operationId, address sender);

    function registerOperation( 
        OperationType operationType,
        string memory description,
        uint256 batchId
    ) public returns (uint256) {
        uint256 operationId = nextOperationId++;

        operations[operationId] = Operation(
            operationId,
            msg.sender,
            operationType,
            block.timestamp,
            description,
            batchId,
            true
        );

        companyOperations[msg.sender].push(operationId);
        emit DebugOperation(operationId, msg.sender);

        emit OperationCreated(operationId, msg.sender, operationType, block.timestamp, description, batchId);
        return operationId;
    }
    
    function getCompanyOperations(address companyAddress) external view returns (uint256[] memory) {
        return companyOperations[companyAddress];
    }
    
    function getOperation(uint256 operationId) external view returns (Operation memory) {
        require(operations[operationId].id > 0, "Operation does not exist");
        return operations[operationId];
    }

    function registerCompensationAction(
        string calldata actionType,
        uint256 co2Reduction, // in kg
        string calldata description
    ) external onlyRegisteredCompany(msg.sender) returns (uint256) {
        uint256 actionId = nextCompensationActionId++;
        compensationActions[actionId] = CompensationAction(
            actionId,
            msg.sender,
            actionType,
            block.timestamp,
            co2Reduction,
            description,
            false // Deve essere verificata
        );
        companyCompensationActions[msg.sender].push(actionId);
        emit CompensationActionCreated(actionId, msg.sender, actionType, block.timestamp, co2Reduction, description);
        return actionId;
    }

    function verifyCompensationAction(uint256 actionId, bool isVerified) external {
        CompensationAction storage action = compensationActions[actionId];
        require(action.id > 0, "Action does not exist");
        // Modello Semplificato: solo l'azienda che l'ha creata può "verificarla"
        // In un sistema reale, questo richiederebbe un ruolo di verificatore autorizzato.
        require(msg.sender == action.companyAddress, "Not authorized to verify this action");
        
        action.isVerified = isVerified;
        
        if (isVerified) {
            // Aggiorna punteggio sostenibilità
            uint256 currentScore = companies[action.companyAddress].sustainabilityScore;
            uint256 scoreIncrease = action.co2Reduction / 100; // Esempio: 1 punto ogni 100kg CO2
            uint256 newScore = currentScore + scoreIncrease;
            if (newScore > 100) newScore = 100;
            if (newScore != currentScore) {
                 companies[action.companyAddress].sustainabilityScore = newScore;
                 emit SustainabilityScoreUpdated(action.companyAddress, currentScore, newScore);
            }

            // Mint tokens come reward (esempio: 1 token per ogni 10kg di CO2 ridotta)
            uint256 tokenReward = (action.co2Reduction / 10) * (10**decimals()); // Scalato per i decimali del token
            if (tokenReward > 0) {
                _mint(action.companyAddress, tokenReward);
            }
        }
    }
    
    function getCompanyCompensationActions(address companyAddress) external view returns (uint256[] memory) {
        return companyCompensationActions[companyAddress];
    }

    function getCompensationAction(uint256 actionId) external view returns (CompensationAction memory) {
        require(compensationActions[actionId].id > 0, "Action does not exist");
        return compensationActions[actionId];
    }

    function createBatch(
        string calldata productName,
        uint256 quantity,
        string calldata metadata
    ) external onlyRegisteredCompany(msg.sender) returns (uint256) {
        uint256 batchId = nextBatchId++;
        uint256[] memory emptyOperationIds = new uint256[](0);
        
        batches[batchId] = Batch(
            batchId,
            msg.sender,
            msg.sender,
            productName,
            quantity,
            block.timestamp,
            metadata,
            emptyOperationIds,
            true
        );
        companyBatches[msg.sender].push(batchId);
        emit BatchCreated(batchId, msg.sender, productName, quantity, block.timestamp, metadata);
        
        // Registra automaticamente un'operazione di produzione
        registerOperation(OperationType.Production, "Initial batch production", batchId);
        return batchId;
    }

    function transferBatch(
        uint256 batchId,
        address toAddress,
        OperationType operationType, // es. Transport
        string calldata description
    ) external onlyRegisteredCompany(msg.sender) {
        Batch storage batch = batches[batchId];
        require(batch.id > 0, "Batch does not exist");
        require(batch.isActive, "Batch is not active");
        require(batch.currentOwner == msg.sender, "Not the batch owner");
        require(companies[toAddress].isRegistered, "Recipient not a registered company");
        
        registerOperation(operationType, description, batchId);
        
        address previousOwner = batch.currentOwner;
        batch.currentOwner = toAddress;
        companyBatches[toAddress].push(batchId);
        
        emit BatchTransferred(batchId, previousOwner, toAddress, block.timestamp);
    }

    function getCompanyBatches(address companyAddress) external view returns (uint256[] memory) {
        return companyBatches[companyAddress];
    }

    function getBatch(uint256 batchId) external view returns (Batch memory) {
        require(batches[batchId].id > 0, "Batch does not exist");
        return batches[batchId];
    }

    function getBatchOperations(uint256 batchId) external view returns (uint256[] memory) {
        require(batches[batchId].id > 0, "Batch does not exist");
        return batches[batchId].operationIds;
    }

    // ======== FUNZIONI TOKEN SPECIFICHE DEL CONTRATTO ========
    // Le funzioni standard ERC20 (balanceOf, transfer, approve, etc.) sono ereditate
    // e non necessitano di essere riscritte.

    /**
     * @dev Applica l'impatto di CO2 di un'operazione, mintando o bruciando token.
     * @param companyAddr Indirizzo dell'azienda.
     * @param consumedCO2 CO2 consumato.
     * @param thresholdCO2 Soglia di CO2.
     * @param co2TokenValue Valore in token per unità di CO2 (es. 1 token per 1kg di CO2).
     * Attenzione: questa funzione dovrebbe essere chiamata da un'entità autorizzata (es. oracolo, admin)
     * per evitare manipolazioni se i dati di CO2 non sono verificabili on-chain.
     */
    function applyCO2Impact(address companyAddr, uint256 consumedCO2, uint256 thresholdCO2, uint256 co2TokenValue) public nonReentrant {
        require(companies[companyAddr].isRegistered, "Company not registered");
        // Aggiungere qui un controllo sull'autorizzazione di msg.sender se necessario
        // require(msg.sender == <authorized_address>, "Unauthorized CO2 impact reporter");

        if (consumedCO2 < thresholdCO2) {
            uint256 rewardAmount = (thresholdCO2 - consumedCO2) * co2TokenValue;
            if (rewardAmount > 0) {
                 _mint(companyAddr, rewardAmount);
            }
        } else if (consumedCO2 > thresholdCO2) {
            uint256 penaltyAmount = (consumedCO2 - thresholdCO2) * co2TokenValue;
            if (penaltyAmount > 0) {
                if (balanceOf(companyAddr) >= penaltyAmount) { // balanceOf() è ereditato
                    _burn(companyAddr, penaltyAmount);
                } else {
                    _burn(companyAddr, balanceOf(companyAddr)); // Brucia il massimo possibile
                }
            }
        }
    }
    
    // ======== FUNZIONI TOKEN EXCHANGE ========
    function createTokenRequest(
        address _provider,
        uint256 _amount, // Quantità di token (già scalata per i decimali)
        string calldata _sustainabilityPurpose,
        uint256 _estimatedCO2Reduction
    ) external onlyRegisteredCompany(msg.sender) nonReentrant returns (uint256) {
        require(_provider != msg.sender, "Cannot request tokens from yourself");
        require(companies[_provider].isRegistered, "Provider not a registered company");
        require(_amount > 0, "Amount must be greater than zero");
        
        uint256 requestId = nextRequestId++;
        requests[requestId] = TokenRequest(
            requestId,
            msg.sender,
            _provider,
            _amount,
            RequestStatus.Pending,
            "",
            block.timestamp,
            block.timestamp,
            _sustainabilityPurpose,
            _estimatedCO2Reduction,
            false
        );
        emit RequestCreated(requestId, msg.sender, _provider, _amount, _sustainabilityPurpose, _estimatedCO2Reduction);
        return requestId;
    }
    
    function acceptTokenRequest(uint256 _requestId)
        external
        onlyRegisteredCompany(msg.sender) // Il provider (msg.sender) deve essere registrato
        onlyProvider(_requestId)
        requestExists(_requestId)
        requestIsPending(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        
        // Il provider (msg.sender) trasferisce i token al richiedente.
        // La funzione transfer() ereditata da ERC20.sol trasferisce da msg.sender.
        ERC20.transfer(currentRequest.requester, currentRequest.amount); 
        
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
    
    function getRequestDetails(uint256 _requestId) external view requestExists(_requestId) returns (TokenRequest memory) {
        return requests[_requestId];
    }
    
    function verifySustainability(uint256 _requestId, bool _verified)
        external
        // Modello Semplificato: solo il provider della richiesta può "verificare"
        // le affermazioni di sostenibilità del richiedente legate a questa richiesta.
        onlyRegisteredCompany(msg.sender)
        onlyProvider(_requestId) 
        requestExists(_requestId)
        nonReentrant
    {
        TokenRequest storage currentRequest = requests[_requestId];
        require(currentRequest.status == RequestStatus.Accepted || currentRequest.status == RequestStatus.Pending, "Request not in a verifiable state");

        currentRequest.isSustainabilityVerified = _verified;
        currentRequest.lastUpdateTimestamp = block.timestamp;
        emit SustainabilityVerified(_requestId, msg.sender, _verified);
        
        if (_verified) {
            Company storage requesterCompany = companies[currentRequest.requester];
            if (requesterCompany.isRegistered) {
                uint256 oldScore = requesterCompany.sustainabilityScore;
                uint256 scoreIncrease = 0;
                if (currentRequest.estimatedCO2Reduction > 1000) scoreIncrease = 5;
                else if (currentRequest.estimatedCO2Reduction > 500) scoreIncrease = 3;
                else if (currentRequest.estimatedCO2Reduction > 100) scoreIncrease = 1;

                if (scoreIncrease > 0) {
                    uint256 newScore = oldScore + scoreIncrease;
                    if (newScore > 100) newScore = 100;
                    if (newScore != oldScore) {
                       requesterCompany.sustainabilityScore = newScore;
                       emit SustainabilityScoreUpdated(currentRequest.requester, oldScore, newScore);
                    }
                }
            }
        }
    }
    
    function getSustainableRequests(uint256 _minCO2Reduction, bool _onlyVerified) external view returns (uint256[] memory) {
        uint256 count = 0;
        for (uint256 i = 1; i < nextRequestId; i++) {
            if (requests[i].id != 0 && 
                requests[i].estimatedCO2Reduction >= _minCO2Reduction &&
                (!_onlyVerified || requests[i].isSustainabilityVerified)) {
                count++;
            }
        }
        uint256[] memory result = new uint256[](count);
        uint256 index = 0;
        for (uint256 i = 1; i < nextRequestId; i++) {
             if (requests[i].id != 0 && 
                requests[i].estimatedCO2Reduction >= _minCO2Reduction &&
                (!_onlyVerified || requests[i].isSustainabilityVerified)) {
                result[index++] = i;
            }
        }
        return result;
    }
}