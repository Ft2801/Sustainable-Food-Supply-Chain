// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract SustainableFoodChain is ReentrancyGuard, ERC20 {
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
    
    // Eventi CO2 Threshold
    event TokensAssigned(address indexed companyAddress, int256 tokensAmount, uint256 co2Consumed, uint256 threshold);
    
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
        uint256[] rawMaterialBatchIds; // IDs dei lotti di materie prime utilizzati
        bool isActive;
        bool isProcessed; // Indica se è un prodotto trasformato
    }
    
    // Struttura per le soglie di CO2 per operazione e prodotto
    struct CO2Threshold {
        uint256 maxThreshold;
        bool isActive;
    }

    struct Message {
        address utente;
        string tipo;
        string messaggio;
        uint256 valore;
    }

    Message[] private messaggi;

    function getAllOperations() public view returns (Message[] memory) {
        return messaggi;
    }

    
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
    
    // Mapping per le soglie di CO2: operationType => productId => threshold
    mapping(string => mapping(uint256 => CO2Threshold)) public co2Thresholds;
    
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
    
    constructor() ERC20("CO2 Token", "CO2") {
        // Assegna 1000 token iniziali all'indirizzo del deployer
        _mint(msg.sender, 1000 * 10**decimals());
        
        // Inserimento diretto delle soglie dal database
        // Soglie per operazione "produzione"
        co2Thresholds["produzione"][1] = CO2Threshold(52, true);
        co2Thresholds["produzione"][2] = CO2Threshold(54, true);
        co2Thresholds["produzione"][3] = CO2Threshold(56, true);
        co2Thresholds["produzione"][4] = CO2Threshold(58, true);
        co2Thresholds["produzione"][5] = CO2Threshold(60, true);
        co2Thresholds["produzione"][6] = CO2Threshold(62, true);
        co2Thresholds["produzione"][7] = CO2Threshold(64, true);
        co2Thresholds["produzione"][8] = CO2Threshold(66, true);
        co2Thresholds["produzione"][9] = CO2Threshold(68, true);
        co2Thresholds["produzione"][10] = CO2Threshold(70, true);
        
        // Soglie per operazione "trasporto"
        co2Thresholds["trasporto"][1] = CO2Threshold(52, true);
        co2Thresholds["trasporto"][2] = CO2Threshold(54, true);
        co2Thresholds["trasporto"][3] = CO2Threshold(56, true);
        co2Thresholds["trasporto"][4] = CO2Threshold(58, true);
        co2Thresholds["trasporto"][5] = CO2Threshold(60, true);
        co2Thresholds["trasporto"][6] = CO2Threshold(62, true);
        co2Thresholds["trasporto"][7] = CO2Threshold(64, true);
        co2Thresholds["trasporto"][8] = CO2Threshold(66, true);
        co2Thresholds["trasporto"][9] = CO2Threshold(68, true);
        co2Thresholds["trasporto"][10] = CO2Threshold(70, true);
        co2Thresholds["trasporto"][11] = CO2Threshold(72, true);
        co2Thresholds["trasporto"][12] = CO2Threshold(74, true);
        co2Thresholds["trasporto"][13] = CO2Threshold(76, true);
        co2Thresholds["trasporto"][14] = CO2Threshold(78, true);
        co2Thresholds["trasporto"][15] = CO2Threshold(80, true);
        co2Thresholds["trasporto"][16] = CO2Threshold(82, true);
        co2Thresholds["trasporto"][17] = CO2Threshold(84, true);
        co2Thresholds["trasporto"][18] = CO2Threshold(86, true);
        co2Thresholds["trasporto"][19] = CO2Threshold(88, true);
        co2Thresholds["trasporto"][20] = CO2Threshold(90, true);
        
        // Soglie per operazione "trasformazione"
        co2Thresholds["trasformazione"][11] = CO2Threshold(72, true);
        co2Thresholds["trasformazione"][12] = CO2Threshold(74, true);
        co2Thresholds["trasformazione"][13] = CO2Threshold(76, true);
        co2Thresholds["trasformazione"][14] = CO2Threshold(78, true);
        co2Thresholds["trasformazione"][15] = CO2Threshold(80, true);
        co2Thresholds["trasformazione"][16] = CO2Threshold(82, true);
        co2Thresholds["trasformazione"][17] = CO2Threshold(84, true);
        co2Thresholds["trasformazione"][18] = CO2Threshold(86, true);
        co2Thresholds["trasformazione"][19] = CO2Threshold(88, true);
        co2Thresholds["trasformazione"][20] = CO2Threshold(90, true);
        
        // Soglie per operazione "vendita"
        co2Thresholds["vendita"][11] = CO2Threshold(72, true);
        co2Thresholds["vendita"][12] = CO2Threshold(74, true);
        co2Thresholds["vendita"][13] = CO2Threshold(76, true);
        co2Thresholds["vendita"][14] = CO2Threshold(78, true);
        co2Thresholds["vendita"][15] = CO2Threshold(80, true);
        co2Thresholds["vendita"][16] = CO2Threshold(82, true);
        co2Thresholds["vendita"][17] = CO2Threshold(84, true);
        co2Thresholds["vendita"][18] = CO2Threshold(86, true);
        co2Thresholds["vendita"][19] = CO2Threshold(88, true);
        co2Thresholds["vendita"][20] = CO2Threshold(90, true);
    }
    
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

        messaggi.push(Message({
            utente: msg.sender,
            tipo : "registrazione",
            messaggio: _name,
            valore: 1
        }));
        
        // Assegna 100 token iniziali all'azienda registrata
        _mint(msg.sender, 100 * 10**decimals());
        
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
    
    function updateCertifications(string calldata _certifications) external onlyRegisteredCompany(msg.sender) {
        companies[msg.sender].sustainabilityCertifications = _certifications;
        emit CertificationsUpdated(msg.sender, _certifications);
    }

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

        messaggi.push(Message({
            utente: msg.sender,
            tipo : "operazione",
            messaggio: description,
            valore: batchId
        }));

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
    ) external returns (uint256) {
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

        messaggi.push(Message({
            utente: msg.sender,
            tipo : "azione",
            messaggio: description,
            valore: co2Reduction
        }));


        companyCompensationActions[msg.sender].push(actionId);
        emit CompensationActionCreated(actionId, msg.sender, actionType, block.timestamp, co2Reduction, description);
        return actionId;
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
        uint256[] memory emptyRawMaterialIds = new uint256[](0);
        
        batches[batchId] = Batch(
            batchId,
            msg.sender,
            msg.sender,
            productName,
            quantity,
            block.timestamp,
            metadata,
            emptyOperationIds,
            emptyRawMaterialIds, // Nessuna materia prima per un lotto iniziale
            true,
            false // Non è un prodotto trasformato
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

    function createProcessedBatch(
        string calldata productName,
        uint256 quantity,
        string calldata metadata,
        uint256[] calldata rawMaterialBatchIds,
        string calldata description
    ) external onlyRegisteredCompany(msg.sender) returns (uint256) {
        require(rawMaterialBatchIds.length > 0, "Deve essere fornito almeno un lotto di materia prima");
        
        // Verifica che l'azienda possieda tutte le materie prime indicate
        _verifyRawMaterialsOwnership(rawMaterialBatchIds);
        
        // Crea il nuovo lotto trasformato
        uint256 batchId = nextBatchId++;
        _createProcessedBatchData(batchId, productName, quantity, metadata, rawMaterialBatchIds);
        
        // Registra un'operazione di trasformazione
        registerOperation(OperationType.Processing, description, batchId);
        return batchId;
    }
    
    function _verifyRawMaterialsOwnership(uint256[] calldata rawMaterialBatchIds) internal view {
        for (uint256 i = 0; i < rawMaterialBatchIds.length; i++) {
            uint256 batchId = rawMaterialBatchIds[i];
            require(batches[batchId].id > 0, "Lotto di materia prima non esistente");
            require(batches[batchId].isActive, "Lotto di materia prima non attivo");
            require(batches[batchId].currentOwner == msg.sender, "Non sei il proprietario di tutti i lotti di materie prime");
        }
    }
    
    function _createProcessedBatchData(
        uint256 batchId,
        string calldata productName,
        uint256 quantity,
        string calldata metadata,
        uint256[] calldata rawMaterialBatchIds
    ) internal {
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
            rawMaterialBatchIds, // Collega le materie prime utilizzate
            true,
            true // Contrassegna come prodotto trasformato
        );
        companyBatches[msg.sender].push(batchId);
        emit BatchCreated(batchId, msg.sender, productName, quantity, block.timestamp, metadata);
    }
    
    function getBatchRawMaterials(uint256 batchId) external view returns (uint256[] memory) {
        require(batches[batchId].id > 0, "Lotto non esistente");
        return batches[batchId].rawMaterialBatchIds;
    }
    
    function isBatchProcessed(uint256 batchId) external view returns (bool) {
        require(batches[batchId].id > 0, "Lotto non esistente");
        return batches[batchId].isProcessed;
    }
    
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

        messaggi.push(Message({
            utente: msg.sender,
            tipo : "richiesta",
            messaggio: "id_request",
            valore: requestId
        }));
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
    
    function getRequestDetails(uint256 _requestId) external view requestExists(_requestId) returns (TokenRequest memory) {
        return requests[_requestId];
    }
    
    /**
     * @dev Restituisce la soglia di CO2 per un tipo di operazione e un prodotto
     * @param operationType Tipo di operazione
     * @param productId ID del prodotto
     * @return La soglia massima di CO2 consentita
     */
    function getThreshold(string calldata operationType, uint256 productId) external view returns (uint256) {
        require(co2Thresholds[operationType][productId].isActive, "Soglia non trovata");
        return co2Thresholds[operationType][productId].maxThreshold;
    }
    
    /**
     * @dev Assegna o rimuove token in base alla differenza tra soglia e consumo effettivo di CO2
     * @param operationType Tipo di operazione (deve corrispondere a quello impostato nel costruttore)
     * @param productId ID del prodotto
     * @param co2Consumed CO2 consumata effettivamente dall'operazione
     * @return Restituisce la quantità di token assegnati (positiva) o rimossi (negativa)
     */
    function assignTokensByConsumption(string calldata operationType, uint256 productId, uint256 co2Consumed) external returns (int256) {
        require(co2Thresholds[operationType][productId].isActive, "Soglia non trovata per questa operazione e prodotto");
        require(companies[msg.sender].isRegistered, "Azienda non registrata");
        
        uint256 threshold = co2Thresholds[operationType][productId].maxThreshold;
        int256 tokensToAssign;
        
        if (co2Consumed <= threshold) {
            // Se il consumo è minore o uguale alla soglia, l'azienda guadagna token
            tokensToAssign = int256(threshold - co2Consumed);
            _mint(msg.sender, uint256(tokensToAssign));
        } else {
            // Se il consumo è maggiore della soglia, l'azienda perde token
            tokensToAssign = -int256(co2Consumed - threshold);
            // Assicurati che l'azienda abbia abbastanza token da perdere
            require(balanceOf(msg.sender) >= uint256(-tokensToAssign), "Saldo token insufficiente");
            _burn(msg.sender, uint256(-tokensToAssign));
        }
        
        emit TokensAssigned(msg.sender, tokensToAssign, co2Consumed, threshold);
        return tokensToAssign;
    }
}