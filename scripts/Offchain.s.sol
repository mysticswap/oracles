// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "forge-std/console.sol";
// import "../src/AccessControlledOffchainAggregator.sol";
import "../src/EACAggregatorProxy.sol";


contract TransmitScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        // address contractAddress = vm.envAddress("CONTRACT_ADDRESS");
        address oracleAddress = vm.envAddress("ORACLE");

        vm.startBroadcast(deployerPrivateKey);

        // AccessControlledOffchainAggregator transmitter = AccessControlledOffchainAggregator(contractAddress);
        // // transmitter.hasAccess(msg.sender, bytes(""));
        // transmitter.disableAccessCheck();
        
        // transmitter.transmit(2525000000000000000000);
        EACAggregatorProxy oracle = EACAggregatorProxy(oracleAddress);
        console.log("oracle value:", uint256(oracle.latestAnswer())/1e8);
        // console.log("oracle value:", address(oracle.accessController()));

        vm.stopBroadcast();
    }
}