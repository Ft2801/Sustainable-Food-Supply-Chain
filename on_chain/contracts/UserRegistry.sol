// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserRegistry {
    struct User {
        string name;
        string email;
        string role; // "PRODUCER", "DISTRIBUTOR", "RETAILER", "CONSUMER"
        bool isActive;
        uint256 registrationDate;
    }

    mapping(address => User) private users;
    mapping(address => bool) private isRegistered;

    event UserRegistered(address indexed userAddress, string name, string role);
    event UserUpdated(address indexed userAddress, string name, string role);
    event UserDeactivated(address indexed userAddress);

    modifier onlyRegistered() {
        require(isRegistered[msg.sender], "User not registered");
        _;
    }

    function registerUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external {
        require(!isRegistered[msg.sender], "User already registered");
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

        isRegistered[msg.sender] = true;
        emit UserRegistered(msg.sender, _name, _role);
    }

    function updateUser(
        string memory _name,
        string memory _email,
        string memory _role
    ) external onlyRegistered {
        require(users[msg.sender].isActive, "User is not active");
        
        users[msg.sender].name = _name;
        users[msg.sender].email = _email;
        users[msg.sender].role = _role;

        emit UserUpdated(msg.sender, _name, _role);
    }

    function deactivateUser() external onlyRegistered {
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
        require(isRegistered[_userAddress], "User not registered");
        User memory user = users[_userAddress];
        return (user.name, user.email, user.role, user.isActive, user.registrationDate);
    }

    function isUserRegistered(address _userAddress) external view returns (bool) {
        return isRegistered[_userAddress];
    }
} 