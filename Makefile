
deploy-offchain-agg :; forge script scripts/DeployOffchain.s.sol:DeployOracleScript --chain 11155111 --rpc-url sepolia --broadcast --verify --legacy --slow --gas-estimate-multiplier 150 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5
deploy-oracle :; forge script scripts/DeployEACProxy.s.sol:DeployEACOracleScript --chain 11155111 --rpc-url sepolia --broadcast --verify --legacy --slow --gas-estimate-multiplier 150 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5
deploy-emeg-oracle :; forge script scripts/DeployEEACProxy.s.sol:DeployEACOracleScript --chain 137 --rpc-url polygon --broadcast --verify --legacy --slow --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 --vvv


test-oracle :; forge script scripts/Offchain.s.sol:TransmitScript --chain 11155111 --rpc-url sepolia --broadcast --legacy --slow --verifier blockscout --verifier-url https://plume-testnet.explorer.caldera.xyz/api --gas-estimate-multiplier 150 --sender 0x0fbAecF514Ab7145e514ad4c448f417BE9292D63 --delay 5 -vvvv

run-updater :;  python offchain-updater-coingecko.py
