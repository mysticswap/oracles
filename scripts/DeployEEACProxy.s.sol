// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/EmergencyEACProxy.sol";

// interface AccessControllerInterface {
//   function hasAccess(address user, bytes calldata data) external view returns (bool);
// }

contract DeployEACOracleScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
                address contractAddress = 0x36dA71ccAd7A67053f0a4d9D5f55b725C9A25A3E;

        // address operator = vm.envAddress("OPERATOR");

        vm.startBroadcast(deployerPrivateKey);

        EEACAggregatorProxy oracleBTC = new EEACAggregatorProxy(contractAddress, address(0), 0x21c4f9a7edaefc4d28ba07193e0a7f13858fc363002378434608f3296ae1c676); //WBTC
        EEACAggregatorProxy oracleETH = new EEACAggregatorProxy(contractAddress, address(0), 0x327c1685e416b2076961afde5adfe14662bdf8e9fce3262ade45f6acab857503);
        
        console.log("New Oracle BTC Address:", address(oracleBTC));
        console.log("New Oracle ETH Address:", address(oracleETH));

        vm.stopBroadcast();
    }
}

// WBTC 0x830ED9E3461667BAE2765131Ae784dd307a24fBF
// WETH 0x59AB56F7285e723CD417aFf63EEea800fD037995