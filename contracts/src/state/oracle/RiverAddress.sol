//SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.10;

import "../../libraries/UnstructuredStorage.sol";

library RiverAddress {
    bytes32 public constant RIVER_ADDRESS_SLOT = bytes32(uint256(keccak256("river.state.riverAddress")) - 1);

    function get() internal view returns (address) {
        return UnstructuredStorage.getStorageAddress(RIVER_ADDRESS_SLOT);
    }

    function set(address newValue) internal {
        UnstructuredStorage.setStorageAddress(RIVER_ADDRESS_SLOT, newValue);
    }
}
