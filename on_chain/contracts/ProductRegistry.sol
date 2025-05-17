// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ProductRegistry {
    struct Product {
        uint256 productId;
        string name;
        string description;
        string category;
        string unit;
        address producer;
        uint256 createdAt;
        bool isActive;
        string metadata; // Certificazioni, standard di qualità, etc.
    }

    uint256 private productCounter;
    mapping(uint256 => Product) private products;
    mapping(address => uint256[]) private producerProducts;
    mapping(string => uint256[]) private categoryProducts;

    event ProductCreated(uint256 indexed productId, address indexed producer, string name);
    event ProductUpdated(uint256 indexed productId, string name);
    event ProductDeactivated(uint256 indexed productId);

    modifier validProduct(uint256 _productId) {
        require(products[_productId].productId != 0, "Product does not exist");
        _;
    }

    function createProduct(
        string memory _name,
        string memory _description,
        string memory _category,
        string memory _unit,
        string memory _metadata
    ) external returns (uint256) {
        require(bytes(_name).length > 0, "Name cannot be empty");
        require(bytes(_category).length > 0, "Category cannot be empty");
        require(bytes(_unit).length > 0, "Unit cannot be empty");

        productCounter++;
        uint256 productId = productCounter;

        products[productId] = Product({
            productId: productId,
            name: _name,
            description: _description,
            category: _category,
            unit: _unit,
            producer: msg.sender,
            createdAt: block.timestamp,
            isActive: true,
            metadata: _metadata
        });

        producerProducts[msg.sender].push(productId);
        categoryProducts[_category].push(productId);

        emit ProductCreated(productId, msg.sender, _name);
        return productId;
    }

    function updateProduct(
        uint256 _productId,
        string memory _name,
        string memory _description,
        string memory _category,
        string memory _unit,
        string memory _metadata
    ) external validProduct(_productId) {
        Product storage product = products[_productId];
        require(product.producer == msg.sender, "Only producer can update product");
        require(product.isActive, "Product is not active");

        product.name = _name;
        product.description = _description;
        product.category = _category;
        product.unit = _unit;
        product.metadata = _metadata;

        emit ProductUpdated(_productId, _name);
    }

    function deactivateProduct(uint256 _productId) external validProduct(_productId) {
        Product storage product = products[_productId];
        require(product.producer == msg.sender, "Only producer can deactivate product");
        require(product.isActive, "Product already deactivated");

        product.isActive = false;
        emit ProductDeactivated(_productId);
    }

    function getProduct(uint256 _productId) external view validProduct(_productId) returns (
        uint256 productId,
        string memory name,
        string memory description,
        string memory category,
        string memory unit,
        address producer,
        uint256 createdAt,
        bool isActive,
        string memory metadata
    ) {
        Product memory product = products[_productId];
        return (
            product.productId,
            product.name,
            product.description,
            product.category,
            product.unit,
            product.producer,
            product.createdAt,
            product.isActive,
            product.metadata
        );
    }

    function getProducerProducts(address _producer) external view returns (uint256[] memory) {
        return producerProducts[_producer];
    }

    function getCategoryProducts(string memory _category) external view returns (uint256[] memory) {
        return categoryProducts[_category];
    }
} 