// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CompanyRegistry {
    struct Company {
        address owner; // indirizzo ethereum dell'azienda
        string name;
        bool isRegistered;
    }
    
    mapping(address => Company) public companies;
    mapping(address => bool) public isCompanyAddressRegistered;
    
    address[] public registeredCompanyAddresses;

    event CompanyRegistered(address indexed companyAddress, string name);
    event CompanyUpdated(address indexed companyAddress, string newName);

    modifier onlyRegistered(address _companyAddress) {
        require(isCompanyAddressRegistered[_companyAddress], "Company not registered");
        _;
    }
    
    modifier notRegistered(address _companyAddress) {
        require(!isCompanyAddressRegistered[_companyAddress], "Company already registered");
        _;
    }

    function registerCompany(string calldata _name) external notRegistered(msg.sender) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        companies[msg.sender] = Company(msg.sender, _name, true);
        isCompanyAddressRegistered[msg.sender] = true;
        registeredCompanyAddresses.push(msg.sender);
        emit CompanyRegistered(msg.sender, _name);
    }

    function updateCompanyName(string calldata _newName) external onlyRegistered(msg.sender) {
        require(bytes(_newName).length > 0, "Name cannot be empty");
        companies[msg.sender].name = _newName;
        emit CompanyUpdated(msg.sender, _newName);
    }
    
    function getCompany(address _companyAddress) external view onlyRegistered(_companyAddress) returns (string memory name, address owner) {
        Company storage company = companies[_companyAddress];
        return (company.name, company.owner);
    }
    
    function isRegistered(address _companyAddress) external view returns (bool) {
        return isCompanyAddressRegistered[_companyAddress];
    }
    
    function getAllRegisteredCompanyAddresses() external view returns (address[] memory) {
        return registeredCompanyAddresses; 
    }
    
}
