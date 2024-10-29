
deploy-offchain-agg :; forge script scripts/DeployOffchain.s.sol:DeployOracleScript --chain 18230 --rpc-url plume2 --broadcast --legacy --slow --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvv
deploy-oracle :; forge script scripts/DeployEACProxy.s.sol:DeployEACOracleScript --chain 18230 --rpc-url plume2 --broadcast --legacy --slow --gas-estimate-multiplier 150 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvv
deploy-emeg-oracle :; forge script scripts/DeployEEACProxy.s.sol:DeployEACOracleScript --chain 18230 --rpc-url plume2 --broadcast --legacy --slow --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvv
deploy-offchain-devnet :; forge script scripts/DeployOffchain.s.sol:DeployOracleScript --chain 98864 --rpc-url plume3 --broadcast --legacy --slow --gas-estimate-multiplier 5000 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvv 
deploy-oracle-devnet :; forge script scripts/DeployEACProxy.s.sol:DeployEACOracleScript --chain 98864 --rpc-url plume3 --broadcast --legacy --slow --gas-estimate-multiplier 5000 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvv

test-oracle :; forge script scripts/Offchain.s.sol:TransmitScript --chain 18230 --rpc-url plume2 --broadcast --legacy --slow --gas-estimate-multiplier 150 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvvv
test-oracle-devnet :; forge script scripts/Offchain.s.sol:TransmitScript --chain 98864 --rpc-url plume3 --broadcast --legacy --slow --gas-estimate-multiplier 5000 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvvv

run-updater :;  python offchain-updater-coingecko.py
