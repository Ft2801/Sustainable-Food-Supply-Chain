// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./IERC20.sol";

/**
 * @title CO2Token
 * @dev Implementation of the IERC20 interface for a sustainability token
 * that rewards eco-friendly operations and penalizes high carbon emissions
 */
contract CO2Token is IERC20 {
    string public name = "CO2 Token";
    string public symbol = "CO2";
    uint8 public decimals = 18;
    
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TokensMinted(address indexed to, uint256 amount);
    event TokensBurned(address indexed from, uint256 amount);
    
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
}