import "Sanity.spec";
import "CVLMath.spec";
import "OperatorRegistryV1_base.spec";

//Holds for loop iter 3 and at most 3 operators
//https://prover.certora.com/output/6893/3a9868a0e6644417a20fc6ab467b2674/?anonymousKey=9120cd1a469c6f54a750187052fdd95efdd53c9f
rule exitingValidatorsDecreasesDiscrepancy(env e) 
{
    require isValidState();
    uint index1; uint index2;
    uint discrepancyBefore = getOperatorsSaturationDiscrepancy(index1, index2);
    uint count;
    require count <= 1;
    requestValidatorExits(e, count);
    uint discrepancyAfter = getOperatorsSaturationDiscrepancy(index1, index2);
    assert discrepancyBefore > 0 => discrepancyBefore >= discrepancyAfter;
}

rule witness4_3ExitingValidatorsDecreasesDiscrepancy(env e) 
{
    require isValidState();
    uint index1; uint index2;
    uint discrepancyBefore = getOperatorsSaturationDiscrepancy(index1, index2);
    uint count;
    require count <= 1;
    requestValidatorExits(e, count);
    uint discrepancyAfter = getOperatorsSaturationDiscrepancy(index1, index2);
    satisfy discrepancyBefore == 4 && discrepancyAfter == 3;
}

// https://prover.certora.com/output/6893/9c93d379dbfb40058cb49f16ac5969ae/?anonymousKey=d30b8e9640702d57adfac94fbc1e2fbe1641c90c
invariant operatorsAddressesRemainUnique_LI4(uint opIndex1, uint opIndex2) 
    isValidState() => (getOperatorAddress(opIndex1) == getOperatorAddress(opIndex2)
    => opIndex1 == opIndex2)
    filtered { f -> !ignoredMethod(f) && needsLoopIter4(f) && 
        f.selector != sig:setOperatorAddress(uint256,address).selector } //method is allowed to break this

// https://prover.certora.com/output/6893/d30f35befc754188b887309de5ffa30f/?anonymousKey=da737f977281de9c86fe7561dd63c6b11dbfd644
invariant operatorsAddressesRemainUnique_LI2(uint opIndex1, uint opIndex2) 
    isValidState() => (getOperatorAddress(opIndex1) == getOperatorAddress(opIndex2)
    => opIndex1 == opIndex2)
    filtered { f -> !ignoredMethod(f) && !needsLoopIter4(f) && 
        f.selector != sig:setOperatorAddress(uint256,address).selector } //method is allowed to break this

// https://prover.certora.com/output/6893/360d2ea0c38c48f88ba600ce16e5b4f0/?anonymousKey=b52535f640d13bdae23463ed46a8496081887813
rule whoCanChangeOperatorsCount_IL2(method f, env e, calldataarg args) 
    filtered { f -> f.contract == currentContract && 
    !ignoredMethod(f) && !needsLoopIter4(f) } 
{
    require isValidState();
    uint countBefore = getOperatorsCount();
    f(e, args);
    uint countAfter = getOperatorsCount();
    assert countAfter > countBefore => canIncreaseOperatorsCount(f);
    assert countAfter < countBefore => canDecreaseOperatorsCount(f);
}

// https://prover.certora.com/output/6893/7e7ba2e6ef0c41c699671b492d536593/?anonymousKey=42f042f43a88d9c6a55b681021881a5875dbac2c
rule whoCanChangeOperatorsCount_IL4(method f, env e, calldataarg args) 
    filtered { f -> f.contract == currentContract && 
    !ignoredMethod(f) && needsLoopIter4(f) } 
{
    require isValidState();
    uint countBefore = getOperatorsCount();
    f(e, args);
    uint countAfter = getOperatorsCount();
    assert countAfter > countBefore => canIncreaseOperatorsCount(f);
    assert countAfter < countBefore => canDecreaseOperatorsCount(f);
}

// https://prover.certora.com/output/6893/bbc5621023d04a75a04fe98fb76940b9/?anonymousKey=eb4b48fcd1912b632d79a6b325063023ecab3d40
rule whoCanDeactivateOperator_LI2(method f, env e, calldataarg args)
    filtered { f -> f.contract == currentContract 
        && !ignoredMethod(f) && !needsLoopIter4(f) } 
{
    require isValidState();
    uint opIndex;
    bool isActiveBefore = operatorIsActive(opIndex);
    f(e, args);
    bool isActiveAfter = operatorIsActive(opIndex);
    assert (isActiveBefore && !isActiveAfter) => canDeactivateOperators(f);
    assert (!isActiveBefore && isActiveAfter) => canActivateOperators(f);
}

// requires a specific conf! depth: 0
// https://prover.certora.com/output/6893/3764dc7b05e84c6c89dcc879fcfe63dc/?anonymousKey=f68a1cff027251750c8b662638cadd81b9e03938
rule whoCanDeactivateOperator_LI4(method f, env e, calldataarg args)
    filtered { f -> f.contract == currentContract && 
        !ignoredMethod(f) && needsLoopIter4(f) } 
{
    require isValidState();
    uint opIndex;
    bool isActiveBefore = operatorIsActive(opIndex);
    f(e, args);
    bool isActiveAfter = operatorIsActive(opIndex);
    assert (isActiveBefore && !isActiveAfter) => canDeactivateOperators(f);
    assert (!isActiveBefore && isActiveAfter) => canActivateOperators(f);
}

// https://prover.certora.com/output/6893/bfd27cb65484472da1ead2b8178d7bb5/?anonymousKey=66caae5f45e04af246224f114442200d9e7fa8c0
invariant operatorsStatesRemainValid_LI2_easyMethods(uint opIndex) 
    isValidState() => (operatorStateIsValid(opIndex))
    filtered { f -> !ignoredMethod(f) && 
    !needsLoopIter4(f) &&
    f.selector != sig:requestValidatorExits(uint256).selector &&
    f.selector != sig:pickNextValidatorsToDeposit(uint256).selector &&
    f.selector != sig:removeValidators(uint256,uint256[]).selector
    }

// proves the invariant for reportStoppedValidatorCounts
// requires special configuration!
// https://prover.certora.com/output/6893/06b7de4c27ad4ef8b519282a831c3823/?anonymousKey=35f5112dd9eac39c2e9aa81dd87a3edc1a452670
invariant operatorsStatesRemainValid_LI4_m1(uint opIndex) 
    isValidState() => (operatorStateIsValid(opIndex))
    filtered { f -> !ignoredMethod(f) && 
    f.selector == sig:reportStoppedValidatorCounts(uint32[],uint256).selector }

// proves the invariant for addValidators
// requires special configuration!
// https://prover.certora.com/output/6893/850c24ab14cc4a2eb3a372abcebc9069/?anonymousKey=c697aaa0f8f6c857e14b8820888fb657caa89e70
invariant operatorsStatesRemainValid_LI4_m2(uint opIndex) 
    isValidState() => (operatorStateIsValid(opIndex))
    filtered { f -> !ignoredMethod(f) && 
    f.selector == sig:addValidators(uint256,uint32,bytes).selector }