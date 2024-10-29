// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/EACAggregatorProxy.sol";

// interface AccessControllerInterface {
//   function hasAccess(address user, bytes calldata data) external view returns (bool);
// }

contract DeployEACOracleScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address contractAddress = vm.envAddress("CONTRACT_ADDRESS");
        

        vm.startBroadcast(deployerPrivateKey);

        EACAggregatorProxy oracle = new EACAggregatorProxy(contractAddress, address(0));
        console.log("New Oracle Address:", address(oracle));

        vm.stopBroadcast();
    }
}