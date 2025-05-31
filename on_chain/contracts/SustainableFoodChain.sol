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
        uint256 batchId,
        uint256 quantita
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

    event LottoComposto(
        uint256 indexed id_lotto_output,
        uint256 indexed id_lotto_input,
        uint256 quantita
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
        uint256 batchId;
        uint256 quantita;
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

    struct ComposizioneLotto {
        uint256 id_lotto_output;
        uint256 id_lotto_input;
        uint256 quantita;
    }

    event ComposizioneLottoCreata(
        uint256 indexed id_lotto_output,
        uint256 indexed id_lotto_input,
        uint256 quantita
    );

    ComposizioneLotto[] public composizioniLotto;

    function getComposizioneLotto(uint256 id_lotto_output)
        public
        view
        returns (uint256[] memory id_lotti_input, uint256[] memory quantita)
    {
        // Conta quante composizioni esistono per l'id richiesto
        uint256 count = 0;
        for (uint256 i = 0; i < composizioniLotto.length; i++) {
            if (composizioniLotto[i].id_lotto_output == id_lotto_output) {
                count++;
            }
        }

        // Inizializza array per i risultati
        uint256[] memory inputs = new uint256[](count);
        uint256[] memory quantitaInputs = new uint256[](count);

        uint256 index = 0;
        for (uint256 i = 0; i < composizioniLotto.length; i++) {
            if (composizioniLotto[i].id_lotto_output == id_lotto_output) {
                inputs[index] = composizioniLotto[i].id_lotto_input;
                quantitaInputs[index] = composizioniLotto[i].quantita;
                index++;
            }
        }

        return (inputs, quantitaInputs);
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

    struct Lotto {
        uint256 id_lotto;
        address creatore;
        uint256 quantita_totale;
        uint256 timestamp;
    }

    mapping(uint256 => Lotto) public lotti;
    uint256[] public tuttiLotti;

    function creaLotto(uint256 id_lotto, uint256 quantita) public returns (uint256) {
        require(quantita > 0, "Quantita deve essere maggiore di zero");
        require(lotti[id_lotto].id_lotto == 0, "ID gia usato");

        lotti[id_lotto] = Lotto({
            id_lotto: id_lotto,
            creatore: msg.sender,
            quantita_totale: quantita,
            timestamp: block.timestamp
        });

        tuttiLotti.push(id_lotto);
        return id_lotto;
    }

    function getAllLotti() public view returns (Lotto[] memory) {
        Lotto[] memory elenco = new Lotto[](tuttiLotti.length);
        for (uint256 i = 0; i < tuttiLotti.length; i++) {
            elenco[i] = lotti[tuttiLotti[i]];
        }
        return elenco;
    }


    Message[] private messaggi;

    function getAllOperations() public view returns (Message[] memory) {
        return messaggi;
    }


    
    mapping(uint256 => bool) private usedBatchIds;
    mapping(uint256 => bool) private lista_op;

    mapping(address => User) private users;
    mapping(address => bool) private isUserRegistered;
    mapping(address => uint256[]) public companyOperations;
    
    mapping(address => Company) public companies;
    address[] public registeredCompanyAddresses; // Mantenuto per query on-chain
    
    mapping(uint256 => TokenRequest) public requests;
    uint256 public nextRequestId = 1;
    
    mapping(uint256 => Operation) public operations;
    
    
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
        // Assegna 100 token iniziali all'indirizzo del deployer
        _mint(msg.sender, 100);
        
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

        
        // Assegna 100 token iniziali all'azienda registrata
        _mint(msg.sender, 100);
        
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
        uint256 id_operazione,
        OperationType operationType,
        uint256 batchId,
        uint256 quantita,
        uint256[] calldata id_lotti,
        uint256[] calldata quantita_lotti
    ) external returns (uint256) {
        require(id_lotti.length == quantita_lotti.length, "Array length mismatch");
        require(!usedBatchIds[batchId], "Batch ID already used");
        require(!lista_op[id_operazione], "Operazione  registrata");
        
        usedBatchIds[batchId] = true;
        lista_op[id_operazione] = true;


        operations[id_operazione] = Operation(
            id_operazione,
            msg.sender,
            operationType,
            batchId,
            quantita,
            true
        );
    

        companyOperations[msg.sender].push(id_operazione);
        emit OperationCreated(id_operazione, msg.sender, operationType, batchId, quantita);

        creaLotto(batchId,quantita);


        return id_operazione;
    }


    function createComposizioneLotto(
        uint256 id_lotto_output,
        uint256[] calldata id_lotti_input,
        uint256[] calldata quantita_input
    ) external {
        require(id_lotti_input.length == quantita_input.length, "Array length mismatch");

        for (uint256 i = 0; i < id_lotti_input.length; i++) {
            uint256 idInput = id_lotti_input[i];
            uint256 quantitaRichiesta = quantita_input[i];

            // Verifica che il lotto esista
            require(lotti[idInput].id_lotto != 0, "Lotto input inesistente");

            // Verifica disponibilità quantità
            require(lotti[idInput].quantita_totale >= quantitaRichiesta, "Quantita insufficiente nel lotto");

            // Sottrai la quantità dal lotto input
            lotti[idInput].quantita_totale -= quantitaRichiesta;

            // Registra la composizione
            composizioniLotto.push(ComposizioneLotto({
                id_lotto_output: id_lotto_output,
                id_lotto_input: idInput,
                quantita: quantitaRichiesta
            }));
            emit ComposizioneLottoCreata(id_lotto_output, idInput, quantitaRichiesta);


        }
    }


    function getCatenaConCreatori(uint256 idLotto)  public  view returns (uint256[] memory ids,
            address[] memory creatori ) {
        uint256[] memory buffer = new uint256[](tuttiLotti.length);
        uint256 count = 0;
        uint256 index = 0;
 
        buffer[count++] = idLotto;
 
        while (index < count) {
            uint256 current = buffer[index++];
            for (uint256 i = 0; i < composizioniLotto.length; i++) {
                // Cerca tutti i lotti che sono stati utilizzati come input per creare il lotto corrente
                if (composizioniLotto[i].id_lotto_output == current) {
                    // Verifica se questo lotto di input è già nel buffer per evitare duplicati
                    bool isDuplicate = false;
                    for (uint256 k = 0; k < count; k++) {
                        if (buffer[k] == composizioniLotto[i].id_lotto_input) {
                            isDuplicate = true;
                            break;
                        }
                    }
                    
                    // Aggiungi solo se non è un duplicato
                    if (!isDuplicate) {
                        buffer[count++] = composizioniLotto[i].id_lotto_input;
                    }
                }
            }
        }
 
        uint256[] memory idsOut = new uint256[](count);
        address[] memory creatoriOut = new address[](count);
 
        for (uint256 j = 0; j < count; j++) {
            idsOut[j] = buffer[j];
            creatoriOut[j] = lotti[buffer[j]].creatore;
        }
 
        return (idsOut, creatoriOut);
    }



    function getAllComposizioni() public view returns (ComposizioneLotto[] memory) {
        return composizioniLotto;
    }
    
    function getCompanyOperations(address companyAddress) external view returns (uint256[] memory) {
        return companyOperations[companyAddress];
    }
    
    function getOperation(uint256 operationId) external view returns (Operation memory) {
        require(operations[operationId].id > 0, "Operation does not exist");
        return operations[operationId];
    }

    function getMyTokenBalance() external view returns (uint256) {
        uint256 rawBalance = balanceOf(msg.sender);
        return rawBalance;
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

        _mint(msg.sender, uint256(co2Reduction));

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
        //registerOperation(OperationType.Production, "Initial batch production", batchId);
        return batchId;
    }

    function transferBatch(
        uint256 batchId,
        address toAddress
    ) external onlyRegisteredCompany(msg.sender) {
        Batch storage batch = batches[batchId];
        require(batch.id > 0, "Batch does not exist");
        require(batch.isActive, "Batch is not active");
        require(batch.currentOwner == msg.sender, "Not the batch owner");
        require(companies[toAddress].isRegistered, "Recipient not a registered company");
        
        //registerOperation(operationType, description, batchId);
        
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
        uint256[] calldata rawMaterialBatchIds
    ) external onlyRegisteredCompany(msg.sender) returns (uint256) {
        require(rawMaterialBatchIds.length > 0, "Deve essere fornito almeno un lotto di materia prima");
        
        // Verifica che l'azienda possieda tutte le materie prime indicate
        _verifyRawMaterialsOwnership(rawMaterialBatchIds);
        
        // Crea il nuovo lotto trasformato
        uint256 batchId = nextBatchId++;
        _createProcessedBatchData(batchId, productName, quantity, metadata, rawMaterialBatchIds);
        
        // Registra un'operazione di trasformazione
        //registerOperation(OperationType.Processing, description, batchId);
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
     * @param soglia_co2 del prodotto
     * @param co2Consumed CO2 consumata effettivamente dall'operazione
     * @return Restituisce la quantità di token assegnati (positiva) o rimossi (negativa)
     */
    function assignTokensByConsumption( uint256 soglia_co2, uint256 co2Consumed) external returns (int256) {
        require(companies[msg.sender].isRegistered, "Azienda non registrata");
        
        
        int256 tokensToAssign = int256(soglia_co2) - int256(co2Consumed); // positivo se premio, negativo se penalità

        if (tokensToAssign > 0) {
            // Premio: assegna token
            _mint(msg.sender, uint256(tokensToAssign));
        } else if (tokensToAssign < 0) {
            // Penalità: brucia token
            uint256 toBurn = uint256(-tokensToAssign); // usa il valore assoluto
            require(balanceOf(msg.sender) >= toBurn, "Saldo token insufficiente");
            _burn(msg.sender, toBurn);
        }
        return tokensToAssign;
    }
}