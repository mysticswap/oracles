// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/AccessControlledOffchainAggregator.sol";

// interface AccessControllerInterface {
//   function hasAccess(address user, bytes calldata data) external view returns (bool);
// }

contract DeployOracleScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        uint256 minAnswer = vm.envUint("MIN_ANSWER");
        uint256 maxAnswer = vm.envUint("MAX_ANSWER");
        uint256 decimals = vm.envUint("DECIMALS");
        address operator = vm.envAddress("OPERATOR");
        string memory description = vm.envString("DESCRIPTION");
        uint256 initValue = vm.envUint("INIT_VALUE");

        vm.startBroadcast(deployerPrivateKey);

        AccessControlledOffchainAggregator transmitter = new AccessControlledOffchainAggregator(
          int192(int256(minAnswer)), int192(int256(maxAnswer)), AccessControllerInterface(operator), uint8(decimals),description
        );

        transmitter.disableAccessCheck();
        
        console.log("New Oracle Address:", address(transmitter));

        transmitter.transmit(int192(int256(initValue)));
        console.log("Initialized Value");

        vm.stopBroadcast();
    }
}