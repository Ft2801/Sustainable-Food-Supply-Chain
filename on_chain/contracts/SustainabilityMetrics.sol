// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SustainabilityMetrics {
    struct Metric {
        uint256 metricId;
        uint256 productId;
        address reporter;
        string metricType; // "CARBON_FOOTPRINT", "WATER_USAGE", "ENERGY_CONSUMPTION", "WASTE_REDUCTION"
        uint256 value;
        string unit;
        string methodology;
        uint256 timestamp;
        string metadata; // Dettagli aggiuntivi sulla metodologia, certificazioni, etc.
    }

    uint256 private metricCounter;
    mapping(uint256 => Metric) private metrics;
    mapping(uint256 => uint256[]) private productMetrics;
    mapping(address => uint256[]) private reporterMetrics;
    mapping(string => uint256[]) private typeMetrics;

    event MetricRecorded(uint256 indexed metricId, uint256 indexed productId, string metricType);
    event MetricUpdated(uint256 indexed metricId, uint256 newValue);
    event MetricVerified(uint256 indexed metricId, address verifier);

    modifier validMetric(uint256 _metricId) {
        require(metrics[_metricId].metricId != 0, "Metric does not exist");
        _;
    }

    function recordMetric(
        uint256 _productId,
        string memory _metricType,
        uint256 _value,
        string memory _unit,
        string memory _methodology,
        string memory _metadata
    ) external returns (uint256) {
        require(bytes(_metricType).length > 0, "Metric type cannot be empty");
        require(bytes(_unit).length > 0, "Unit cannot be empty");
        require(bytes(_methodology).length > 0, "Methodology cannot be empty");

        metricCounter++;
        uint256 metricId = metricCounter;

        metrics[metricId] = Metric({
            metricId: metricId,
            productId: _productId,
            reporter: msg.sender,
            metricType: _metricType,
            value: _value,
            unit: _unit,
            methodology: _methodology,
            timestamp: block.timestamp,
            metadata: _metadata
        });

        productMetrics[_productId].push(metricId);
        reporterMetrics[msg.sender].push(metricId);
        typeMetrics[_metricType].push(metricId);

        emit MetricRecorded(metricId, _productId, _metricType);
        return metricId;
    }

    function updateMetric(
        uint256 _metricId,
        uint256 _value,
        string memory _methodology,
        string memory _metadata
    ) external validMetric(_metricId) {
        Metric storage metric = metrics[_metricId];
        require(metric.reporter == msg.sender, "Only reporter can update metric");

        metric.value = _value;
        metric.methodology = _methodology;
        metric.metadata = _metadata;

        emit MetricUpdated(_metricId, _value);
    }

    function verifyMetric(uint256 _metricId) external validMetric(_metricId) {
        emit MetricVerified(_metricId, msg.sender);
    }

    function getMetric(uint256 _metricId) external view validMetric(_metricId) returns (
        uint256 metricId,
        uint256 productId,
        address reporter,
        string memory metricType,
        uint256 value,
        string memory unit,
        string memory methodology,
        uint256 timestamp,
        string memory metadata
    ) {
        Metric memory metric = metrics[_metricId];
        return (
            metric.metricId,
            metric.productId,
            metric.reporter,
            metric.metricType,
            metric.value,
            metric.unit,
            metric.methodology,
            metric.timestamp,
            metric.metadata
        );
    }

    function getProductMetrics(uint256 _productId) external view returns (uint256[] memory) {
        return productMetrics[_productId];
    }

    function getReporterMetrics(address _reporter) external view returns (uint256[] memory) {
        return reporterMetrics[_reporter];
    }

    function getTypeMetrics(string memory _metricType) external view returns (uint256[] memory) {
        return typeMetrics[_metricType];
    }
} 