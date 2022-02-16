//SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../../libraries/UnstructuredStorage.sol";

library BeaconValidatorCount {
    bytes32 public constant BEACON_VALIDATOR_COUNT_SLOT =
        bytes32(uint256(keccak256("river.state.beaconValidatorCount")) - 1);

    struct Slot {
        uint256 value;
    }

    function get() internal view returns (uint256) {
        return UnstructuredStorage.getStorageUint256(BEACON_VALIDATOR_COUNT_SLOT);
    }

    function set(uint256 newValue) internal {
        UnstructuredStorage.setStorageUint256(BEACON_VALIDATOR_COUNT_SLOT, newValue);
    }
}
