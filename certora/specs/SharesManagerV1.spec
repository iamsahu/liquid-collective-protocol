import "RiverV1.spec";

use rule method_reachability;

methods {
    function allowance(address, address) external returns(uint256) envfree;
    function balanceOf(address) external returns(uint256) envfree;
    function balanceOfUnderlying(address) external returns(uint256) envfree;
    function totalSupply() external returns(uint256) envfree;

    // Tracking earnings (rewards):
    function _._onEarningsCalledMunged(uint256 amount) internal => ghostUpdate_onEarnings(amount) expect bool ALL;
    // Tracking deposits:
    function _._onDepositCalledMunged(address _depositor, address _recipient, uint256 _amount) internal => ghostUpdate_onDeposits(_amount) expect bool ALL;
}

// We have ETH only in the Consensus layer or in the River.
// Inside River, there are 3 storage variables that take care of internal accounting of Rivers balance: 
//   * BalanceToDeposit
//   * CommittedBalance
//   * BalanceToRedeem
// On the other hand, the Consensus layer has balance in two compounds:
//   * LastConsensusLayerReport.get().validatorsCount is number of those that we already account for in the storedReport.validatorsBalance.
//   * DepositedValidatorCount.get(). is number of all validators that deposited totally
//   * The difference multiplied by ConsensusLayerDepositManagerV1.DEPOSIT_SIZE is the consensus layer amount of ETH
// You can track each of them or their sum.
// Given the amount of ETH that exists on the Consensus layer

// First thing to prove: Invariant The sum of the three storage variables is equal to the actual River balance.
// Secondly with requiring the first invariant, we want to say that call to _assetBalance() is equal to the River balance PLUS the consensus layer balance.
// We would probably find holes (like donations?) and so instead of using the actual River balance, we would use the ghosts.
// Secondly have a ghost total_river_balance and to create it correctly, we need
// We want to prove, that
//     1. the one ghost is equal to the actual balance of the contract River is equal to this ghost.

// Lastly: Excluding the action of oracle update (setConsensusLayerData) The ratio between the total shares and the total underlying eth is preserved.
// In other words: When no oracle update takes place, the exchange rate stays the same


ghost mathint counter_onEarnings{ // counter checking number of calls to _onDeposit
    init_state axiom counter_onEarnings == 0;
}
ghost mathint total_onEarnings{ // counter checking number of calls to _onDeposit
    init_state axiom total_onEarnings == 0;// this is total earned ETH
}
ghost mathint total_onDeposits{ // counter checking number of calls to _onDeposit
    init_state axiom total_onDeposits == 0;// this is total earned ETH
}

function ghostUpdate_onEarnings(uint256 amount) returns bool
{
    counter_onEarnings = counter_onEarnings + 1;
    total_onEarnings = total_onEarnings + amount;
    return true;
}

function ghostUpdate_onDeposits(uint256 amount) returns bool
{
    total_onDeposits = total_onDeposits + amount;
    return true;
}

// Partially proved here (with some sanity fails and eror for claimRedeemRequests):
// https://vaas-stg.certora.com/output/40577/e0f17bcec1594338ad6a53b432cdb04a/?anonymousKey=28d9005d1fe0729067a0749a6fdc28dd043ced24
// TODO: filter oracle change and remove the ' + total_onEarnings'
// invariant totalUnderlyingSupplyBasicIntegrity(env e)
//     to_mathint(totalUnderlyingSupply()) == total_onDeposits + total_onEarnings
//     filtered {
//         f -> f.selector != sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector
//     } {
//         preserved
//         {
//             require total_onDeposits <= 2^128;
//             require total_onEarnings <= 2^128;
//             require total_onDeposits >= 0;
//             require total_onEarnings >= 0;
//         }
//     }

invariant totalUnderlyingSupplyBasicIntegrity()
    to_mathint(totalUnderlyingSupply()) == total_onDeposits
    filtered {
        f -> f.selector != sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector
          && f.selector != sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport).selector
    } {
        preserved
        {
            require total_onDeposits <= 2^128;
            require total_onEarnings <= 2^128;
            require total_onDeposits >= 0;
            require total_onEarnings >= 0;
        }
    }

// total underlying = (TotalDepositedETH + (TotalEarnedEth - TotalPenaltyAmounts) * Fee_Ratio)) 
// 1. start with the following. It only tracks ETH:
// UnderlyingAssetBalance = TotalDepositedETh + totalEarnedEth) // TODO: Also subtract penalties=fees. Note we don't take fees from deposits.

 //total supply of LsEth = (total supply of staked ETH 
 // + (consensus layer + execution layer rewards) 
 // - (fees + penalties)) * ConversionRate
 // I.e. given a conversion rate and balances, that LsEth balance/total supply is correct The same invariant for every owner's balance

// TODO: Add _pullCLFunds (consensus layer rewards) tracking
// TODO: Add _onEarnings (consensus layer rewards) tracking - takes rewards as an argument and computes fees from it

// @title The allowance can only be changed by functions listed in the filter:
// initRiverV1_1, setConsensusLayerData, decreaseAllowance, increaseAllowance, approve, transferFrom
// Almost fixed. Latest run:
// https://prover.certora.com/output/40577/c70e8e35cce446d495beb2c3904cf368?anonymousKey=11133ef88d529912cc091efea5f4f344eb2cf077
// We need this bug to be fixed:
// https://certora.atlassian.net/browse/CERT-4453
rule allowanceChangesRestrictively(method f) filtered {
    f -> !f.isView
        && f.selector != sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector
        && f.selector != sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport).selector
        && f.selector != sig:decreaseAllowance(address,uint256).selector
        && f.selector != sig:increaseAllowance(address,uint256).selector
        && f.selector != sig:approve(address,uint256).selector
        && f.selector != sig:transferFrom(address,address,uint256).selector
} {
    env e;
    calldataarg args;
    address owner;
    address spender;
    uint256 allowance_before = allowance(owner, spender);
    // require allowance_before == 12345;
    require owner != spender;
    f(e, args);
    uint256 allowance_after = allowance(owner, spender);
    // require allowance_after == 23456;
    assert allowance_after == allowance_before;
}

// @title The allowance of spender given by owner can always be decreased to 0 by the owner.
// Proved:
// https://prover.certora.com/output/40577/8985ea476a404c22801668777b60cb1e/?anonymousKey=67dc2147dcdd5e40466d907f809241856718be06
rule alwaysPossibleToDecreaseAllowance()
{
    env e;
    address owner;
    address spender;
    uint256 amount;
    decreaseAllowance(e, spender, amount);
    uint256 allowance_after = allowance(owner, spender);
    satisfy e.msg.sender == owner && allowance_after == 0;
}

// @title It is impossible to increase any allowance by calling decreaseAllowance or transferFrom.
// Proved:
// https://prover.certora.com/output/40577/8985ea476a404c22801668777b60cb1e/?anonymousKey=67dc2147dcdd5e40466d907f809241856718be06
rule decreaseAllowanceAndTransferCannotIncreaseAllowance(env e, method f, calldataarg args) filtered {
    f -> f.selector == sig:decreaseAllowance(address,uint256).selector
        || f.selector == sig:transferFrom(address,address,uint256).selector
} {
    address owner;
    address spender;
    uint256 allowance_before = allowance(owner, spender);
    f(e, args);
    uint256 allowance_after = allowance(owner, spender);
    assert allowance_after <= allowance_before;
}

// @title Allowance increases only by owner
// Same issue as in allowanceChangesRestrictively
// https://prover.certora.com/output/40577/8985ea476a404c22801668777b60cb1e/?anonymousKey=67dc2147dcdd5e40466d907f809241856718be06
rule allowanceIncreasesOnlyByOwner(method f) filtered {
    f -> !f.isView
        && f.selector != sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector
        && f.selector != sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport).selector
}  {
    env e;
    calldataarg args;
    address owner;
    address spender;
    uint256 allowance_before = allowance(owner, spender);
    f(e, args);
    uint256 allowance_after = allowance(owner, spender);
    assert allowance_before < allowance_after => e.msg.sender == owner;
}

// @title The shares balance can only be changed by functions listed in the filter:
// transferFrom, transfer, setConsensusLayerData, depositAndTransfer, deposit, requestRedeem
rule sharesBalanceChangesRestrictively(method f) filtered {
    f -> !f.isView
        && f.selector != sig:transferFrom(address,address,uint256).selector
        && f.selector != sig:transfer(address,uint256).selector
        && f.selector != sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport).selector
        && f.selector != sig:depositAndTransfer(address).selector
        && f.selector != sig:deposit().selector
        && f.selector != sig:requestRedeem(uint256,address).selector
        // f.selector != sig:claimRedeemRequests(uint32[],uint32[]).selector
} {
    env e;
    calldataarg args;
    address owner;
    uint256 shares_balance_before = balanceOf(owner);
    f(e, args);
    uint256 shares_balance_after = balanceOf(owner);
    assert shares_balance_after == shares_balance_before;
}


// @title If the balance changes and shares balance is the same, it must have been one of these functions:
// initRiverV1_1, depositToConsensusLayer, claimRedeemRequests, deposit, depositAndTransfer
rule pricePerShareChangesRespectively(method f) filtered {
    f -> !f.isView
        && f.selector != sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector
        && f.selector != sig:depositToConsensusLayer(uint256).selector
        && f.selector != sig:claimRedeemRequests(uint32[],uint32[]).selector
        && f.selector != sig:deposit().selector
        && f.selector != sig:depositAndTransfer(address).selector
} {
    env e;
    calldataarg args;
    address owner;
    uint256 shares_balance_before = balanceOf(owner);
    uint256 underlying_balance_before = balanceOfUnderlying(owner);
    f(e, args);
    uint256 shares_balance_after = balanceOf(owner);
    uint256 underlying_balance_after = balanceOfUnderlying(owner);
    assert shares_balance_before == shares_balance_after => underlying_balance_before == underlying_balance_after;
}

// This rule does not hold for setConsensusLayerData:
// https://prover.certora.com/output/40577/e5a7a762228c45d29adfbdc3ace30530/?anonymousKey=6206b628e02ad22f68fd8f33c537f4eebe44847f
rule sharesMonotonicWithAssets(env e, method f) filtered {
    f -> !f.isView
       // && f.selector != sig:requestRedeem(uint256,address).selector // Prover error
       && f.selector != sig:claimRedeemRequests(uint32[],uint32[]).selector // Claiming rewards can violate the property.
       && f.selector != sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport calldata).selector
} {
    calldataarg args;

    mathint totalETHBefore = totalSupply();
    mathint totalLsETHBefore = totalUnderlyingSupply();

    f(e, args);

    mathint totalETHAfter = totalSupply();
    mathint totalLsETHAfter = totalUnderlyingSupply();

    // require totalETHBefore + totalLsETHBefore + totalETHAfter + totalLsETHAfter <= max_uint256;
    require totalETHBefore <= 2^128;
    require totalLsETHBefore <= 2^128;
    require totalETHAfter <= 2^128;
    require totalLsETHAfter <= 2^128;

    // assert totalETHBefore > totalETHAfter => totalLsETHBefore >= totalLsETHAfter;
    // assert totalETHBefore < totalETHAfter => totalLsETHBefore <= totalLsETHAfter;
    // assert totalLsETHBefore > totalLsETHAfter => totalETHBefore >= totalETHAfter;
    assert totalLsETHBefore < totalLsETHAfter => totalETHBefore <= totalETHAfter;
}

rule conversionRateStable(env e, method f) filtered {
    f -> !f.isView
        // && f.selector == sig:RiverV1Harness.depositToConsensusLayer(uint256).selector
} {
    calldataarg args;

    mathint totalETHBefore = totalSupply();
    mathint totalLsETHBefore = totalUnderlyingSupply();

    f(e, args);

    mathint totalETHAfter = totalSupply();
    mathint totalLsETHAfter = totalUnderlyingSupply();

    assert totalETHBefore * totalLsETHAfter == totalETHAfter * totalLsETHBefore;
}

rule conversionRateStableRewardsFeesPenalties(env e, method f) filtered {
    f -> !f.isView
        // && f.selector == sig:RiverV1Harness.depositToConsensusLayer(uint256).selector
} {
    calldataarg args;

    mathint totalETHBefore = totalSupply();
    mathint totalLsETHBefore = totalUnderlyingSupply();

    f(e, args);

    mathint totalETHAfter = totalSupply();
    mathint totalLsETHAfter = totalUnderlyingSupply();

    assert false;
}

// rule totalEthEqualsTotalDepositedPlusEarned(env e, method f) filtered {
//     f -> !f.isView
//         // && f.selector == sig:RiverV1Harness.depositToConsensusLayer(uint256).selector
// } {
//     calldataarg args;

//     mathint totalETHBefore = totalSupply();
//     mathint totalEarnedBefore = total_onEarnings;
//     mathint totalDepositedBefore = total_onDeposits;

//     f(e, args);

//     mathint totalETHAfter = totalSupply();
//     mathint totalEarnedAfter = total_onEarnings;
//     mathint totalDepositedAfter = total_onDeposits;

//     assert false;
// }

// @title After transfer from, balances are updated accordingly, but not of any other user. Also, totalSupply stays the same.
// Proved:
// https://prover.certora.com/output/40577/0d75136142bd4b458c77e73f4394f101/?anonymousKey=7c99f012e75eb4143a0c3f5dbc180eda79a0c0db
rule transferUpdatesBalances(env e) {
    address from;
    address to;
    address other;
    uint256 amount;
    mathint balanceSenderBefore = balanceOf(from);
    mathint balanceReceiverBefore = balanceOf(to);
    mathint balanceOtherBefore = balanceOf(other);
    mathint totalSupplyBefore = totalSupply();

    transferFrom(e, from, to, amount);

    mathint balanceSenderAfter = balanceOf(from);
    mathint balanceReceiverAfter = balanceOf(to);
    mathint balanceOtherAfter = balanceOf(other);
    mathint totalSupplyAfter = totalSupply();

    assert to != from => balanceSenderBefore - balanceSenderAfter == to_mathint(amount);
    assert to != from => balanceReceiverAfter - balanceReceiverBefore == to_mathint(amount);
    assert other != from && other != to => balanceOtherAfter == balanceOtherBefore;
    assert totalSupplyAfter == totalSupplyBefore;
}
