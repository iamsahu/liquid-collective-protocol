import "Sanity.spec";

using AllowlistV1 as AL;
using CoverageFundV1 as CF;
using ELFeeRecipientV1 as ELFR;
using RedeemManagerV1Harness as RM;
using WithdrawV1 as WC;
using RiverV1Harness as River;

use rule method_reachability;

methods {
    // AllowlistV1
    function AL.onlyAllowed(address, uint256) external envfree;
    function _.onlyAllowed(address, uint256) external => DISPATCHER(true);
    function AL.isDenied(address) external returns (bool) envfree;
    function _.isDenied(address) external => DISPATCHER(true);

    // RedeemManagerV1
    function RM.resolveRedeemRequests(uint32[]) external returns(int64[]) envfree;
    function RM.getRedeemDemand() external returns (uint256) envfree;
    function _.resolveRedeemRequests(uint32[]) external => NONDET;
    
     // requestRedeem function is also defined in River:
    function _.requestRedeem(uint256 _lsETHAmount, address _recipient) external => DISPATCHER(true);
    function _.claimRedeemRequests(uint32[], uint32[], bool, uint16) external => DISPATCHER(true);
    function _.pullExceedingEth(uint256) external => DISPATCHER(true);
    function _.reportWithdraw(uint256) external => DISPATCHER(true);
    function _.getRedeemDemand() external => DISPATCHER(true);

    // RiverV1
    function River.getBalanceToDeposit() external returns(uint256) envfree;
    function River.getCommittedBalance() external returns(uint256) envfree;
    function River.getBalanceToRedeem() external returns(uint256) envfree;
    function River.consensusLayerDepositSize() external returns(uint256) envfree;
    function River.riverEthBalance() external returns(uint256) envfree;
    function River.getAllowlist() external returns (address) envfree;
    function River.getCollector() external returns (address) envfree;
    function River.getELFeeRecipient() external returns (address) envfree;
    function River.getCoverageFund() external returns (address) envfree;
    function River.getRedeemManager() external returns (address) envfree;
    function River.getOracle() external returns (address) envfree;
    function _.sendRedeemManagerExceedingFunds() external => DISPATCHER(true);
    function _.getAllowlist() external => DISPATCHER(true);
    function _.sendCLFunds() external => DISPATCHER(true);
    function _.sendCoverageFunds() external => DISPATCHER(true);
    function _.sendELFees() external => DISPATCHER(true);

    // RiverV1 : SharesManagerV1
    function _.transferFrom(address, address, uint256) external => DISPATCHER(true);
    function _.underlyingBalanceFromShares(uint256) external => DISPATCHER(true);
    function River.underlyingBalanceFromShares(uint256) external returns(uint256) envfree;
    function River.balanceOfUnderlying(address) external returns(uint256) envfree;
    function River.totalSupply() external returns(uint256) envfree;
    function River.totalUnderlyingSupply() external returns(uint256) envfree;
    function River.sharesFromUnderlyingBalance(uint256) external returns(uint256) envfree;
    function River.balanceOf(address) external returns(uint256) envfree;
    function River.consensusLayerEthBalance() external returns(uint256) envfree;
    function River.getCLValidatorCount() external returns(uint256) envfree;
    // RiverV1 : ConsensusLayerDepositManagerV1
    function River.getDepositedValidatorCount() external returns(uint256) envfree;

    // WithdrawV1
    function _.pullEth(uint256) external => DISPATCHER(true);

    // ELFeeRecipientV1
    function _.pullELFees(uint256) external => DISPATCHER(true);

    // CoverageFundV1
    function _.pullCoverageFunds(uint256) external => DISPATCHER(true);

    // OperatorsRegistryV1
    /// reportStoppedValidatorCounts only affects internal keys in the operators registry. Doesn't involve ETH/shares transfer.
    function _.reportStoppedValidatorCounts(uint32[], uint256) external => NONDET;
    /// Use OperatorsRegistryMock
    function _.pickNextValidatorsToDeposit(uint256 _count) external => DISPATCHER(true);

    /// Deposit contract
    function _.deposit(bytes,bytes,bytes,bytes32) external => DISPATCHER(true); // has no effect - CERT-4615

    function LibBytes.slice(bytes memory _bytes, uint256 _start, uint256 _length) internal returns (bytes memory) => bytesSliceSummary(_bytes, _start, _length);
}

/// All helper methods that combine into setConsensusLayerData()
definition helperMethods(method f) returns bool = 
    f.selector == sig:helper1_fillUpVarsAndPullCL(IOracleManagerV1.ConsensusLayerReport).selector
    || f.selector == sig:helper2_updateLastReport(IOracleManagerV1.ConsensusLayerReport).selector
    || f.selector == sig:helper3_checkBounds(OracleManagerV1.ConsensusLayerDataReportingVariables, ReportBounds.ReportBoundsStruct, uint256).selector
    || f.selector == sig:helper4_pullELFees(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper5_pullRedeemManagerExceedingEth(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper6_pullCoverageFunds(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper7_onEarnings(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper8_requestExitsBasedOnRedeemDemandAfterRebalancings(OracleManagerV1.ConsensusLayerDataReportingVariables, IOracleManagerV1.ConsensusLayerReport).selector
    || f.selector == sig:helper9_reportWithdrawToRedeemManager(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper10_skimExcessBalanceToRedeem(OracleManagerV1.ConsensusLayerDataReportingVariables).selector
    || f.selector == sig:helper11_commitBalanceToDeposit(OracleManagerV1.ConsensusLayerDataReportingVariables).selector;

/// Method selector for setConsensusLayerData()
definition setConsensusMethod(method f) returns bool = 
    f.selector == sig:setConsensusLayerData(IOracleManagerV1.ConsensusLayerReport).selector;

/// Method selector for claimRedeemRequests()
definition claimRedeemMethod(method f) returns bool = 
    f.selector != sig:claimRedeemRequests(uint32[],uint32[]).selector;

/// Method selector for initRiverV1_1()
definition initRiverV1Method(method f) returns bool = 
    sig:initRiverV1_1(address,uint64,uint64,uint64,uint64,uint64,uint256,uint256,uint128,uint128).selector;

/// Configurable bounds for the ETH supply and shares supply
definition MINIMUM_ETH_SUPPLY() returns uint256 = 10^16;    /// = 0.01ETH
definition MINIMUM_SHARES_SUPPLY() returns uint256 = 10^16;
definition MAXIMUM_ETH_SUPPLY() returns uint256 = (1 << 128);   /// = 2^128 (more than available ETH in the world)
definition MAXIMUM_SHARES_SUPPLY() returns uint256 = (1 << 128);

ghost mapping(bytes32 => mapping(uint => bytes32)) sliceGhost;

/// Summary for LibBytes.slice() - returns an arbitrary bytes array with the correct length (len), 
/// which is deterministic with respect to buffer and starting position.
function bytesSliceSummary(bytes buffer, uint256 start, uint256 len) returns bytes {
	bytes to_ret;
	require(to_ret.length == len);
	require(buffer.length >= require_uint256(start + len));
	bytes32 buffer_hash = keccak256(buffer);
	require keccak256(to_ret) == sliceGhost[buffer_hash][start];
	return to_ret;
}

/// Calling this function in any rule / preserved block will set the bounds on the total supply and the underlying supply (when non-zero).
function SetSuppliesBounds() {
    uint256 totalETH = totalUnderlyingSupply();
    uint256 supply = totalSupply();
    if(supply != 0 && totalETH != 0) {
        require supply >= MINIMUM_SHARES_SUPPLY();
        require totalETH >= MINIMUM_ETH_SUPPLY();
        require supply <= MAXIMUM_SHARES_SUPPLY();
        require totalETH <= MAXIMUM_ETH_SUPPLY();
    }
}

/// Exclusion of an address from being any of the system contracts.
function userIsNotAContract(address user) returns bool {
    return 
    user != getAllowlist() &&
    user != getCollector() && 
    user != getCoverageFund() &&
    user != getELFeeRecipient() &&
    user != River.getOracle() &&
    user != getRedeemManager() &&
    user != WC && 
    user != River;
}

/// The total assets value for any account consists of its native ETH balance and its shares worth in ETH.
function getUserValue(address user) returns mathint {
    if(totalSupply() == 0) {
        return to_mathint(nativeBalances[user]);
    }
    return underlyingBalanceFromShares(balanceOf(user)) + nativeBalances[user];
}

/// By definition, the share price is the ETH worth of one share unit.
function getSharePrice() returns uint256 {
    return underlyingBalanceFromShares(1);
}
