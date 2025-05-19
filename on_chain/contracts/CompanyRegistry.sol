// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CompanyRegistry
 * @dev Registry for companies in the sustainable food supply chain
 */
contract CompanyRegistry {
    enum CompanyType { Producer, Processor, Distributor, Retailer, Other }
    
    struct Company {
        address owner; // indirizzo ethereum dell'azienda
        string name;
        bool isRegistered;
        CompanyType companyType;
        string location;
        string sustainabilityCertifications; // JSON string with certifications
        uint256 sustainabilityScore; // Score from 0-100
        uint256 registrationDate;
    }
    
    mapping(address => Company) public companies;
    mapping(address => bool) public isCompanyAddressRegistered;
    
    address[] public registeredCompanyAddresses;

    event CompanyRegistered(address indexed companyAddress, string name, CompanyType companyType, string location);
    event CompanyUpdated(address indexed companyAddress, string newName);
    event SustainabilityScoreUpdated(address indexed companyAddress, uint256 oldScore, uint256 newScore);
    event CertificationsUpdated(address indexed companyAddress, string certifications);

    modifier onlyRegistered(address _companyAddress) {
        require(isCompanyAddressRegistered[_companyAddress], "Company not registered");
        _;
    }
    
    modifier notRegistered(address _companyAddress) {
        require(!isCompanyAddressRegistered[_companyAddress], "Company already registered");
        _;
    }

    function registerCompany(
        string calldata _name,
        CompanyType _companyType,
        string calldata _location,
        string calldata _certifications
    ) external notRegistered(msg.sender) {
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

    function updateCompanyName(string calldata _newName) external onlyRegistered(msg.sender) {
        require(bytes(_newName).length > 0, "Name cannot be empty");
        companies[msg.sender].name = _newName;
        emit CompanyUpdated(msg.sender, _newName);
    }
    
    function getCompany(address _companyAddress) external view onlyRegistered(_companyAddress) returns (
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
    
    function isRegistered(address _companyAddress) external view returns (bool) {
        return isCompanyAddressRegistered[_companyAddress];
    }
    
    function getAllRegisteredCompanyAddresses() external view returns (address[] memory) {
        return registeredCompanyAddresses; 
    }
    
    /**
     * @dev Update the sustainability score of a company
     * @param _companyAddress The address of the company
     * @param _newScore The new sustainability score (0-100)
     */
    function updateSustainabilityScore(address _companyAddress, uint256 _newScore) external onlyRegistered(_companyAddress) {
        require(_newScore <= 100, "Score must be between 0 and 100");
        require(msg.sender == address(this) || msg.sender == companies[_companyAddress].owner, "Not authorized");
        
        uint256 oldScore = companies[_companyAddress].sustainabilityScore;
        companies[_companyAddress].sustainabilityScore = _newScore;
        
        emit SustainabilityScoreUpdated(_companyAddress, oldScore, _newScore);
    }
    
    /**
     * @dev Update the sustainability certifications of a company
     * @param _certifications JSON string with certifications
     */
    function updateCertifications(string calldata _certifications) external onlyRegistered(msg.sender) {
        companies[msg.sender].sustainabilityCertifications = _certifications;
        emit CertificationsUpdated(msg.sender, _certifications);
    }
    
    /**
     * @dev Get companies by type
     * @param _companyType The type of companies to retrieve
     */
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
}
