import logging
import math

import global_params
from cfg_builder.opcodes import *
from cfg_builder.utils import *

log = logging.getLogger(__name__)


def set_cur_file(c_file):
    global cur_file
    cur_file = c_file


def init_analysis():
    analysis = {
        "gas": 0,
        "gas_mem": 0,
    }
    return analysis


def calculate_gas(opcode, stack, mem, global_state, analysis, solver):
    gas_increment = get_ins_cost(opcode)  # base cost
    gas_memory = analysis["gas_mem"]
    # In some opcodes, gas cost is not only depend on opcode itself but also current state of evm
    # For symbolic variables, we only add base cost part for simplicity
    if opcode in ("LOG0", "LOG1", "LOG2", "LOG3", "LOG4") and len(stack) > 1:
        if isReal(stack[1]):
            gas_increment += GCOST["Glogdata"] * stack[1]
    elif opcode == "EXP" and len(stack) > 1:
        if isReal(stack[1]) and stack[1] > 0:
            gas_increment += GCOST["Gexpbyte"] * (
                1 + math.floor(math.log(stack[1], 256))
            )
    elif opcode == "EXTCODECOPY" and len(stack) > 2:
        if isReal(stack[2]):
            gas_increment += GCOST["Gcopy"] * math.ceil(stack[2] / 32)
    elif opcode in ("CALLDATACOPY", "CODECOPY") and len(stack) > 3:
        if isReal(stack[3]):
            gas_increment += GCOST["Gcopy"] * math.ceil(stack[3] / 32)
    elif opcode == "SSTORE" and len(stack) > 1:
        if isReal(stack[1]):
            try:
                try:
                    storage_value = global_state["Ia"][int(stack[0])]
                except Exception:
                    storage_value = global_state["Ia"][str(stack[0])]
                # when we change storage value from zero to non-zero
                if storage_value == 0 and stack[1] != 0:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
            except Exception:  # when storage address at considered key is empty
                if stack[1] != 0:
                    gas_increment += GCOST["Gsset"]
                elif stack[1] == 0:
                    gas_increment += GCOST["Gsreset"]
        else:
            try:
                try:
                    storage_value = global_state["Ia"][int(stack[0])]
                except Exception:
                    storage_value = global_state["Ia"][str(stack[0])]
                solver.push()
                solver.add(Not(And(storage_value == 0, stack[1] != 0)))
                if solver.check() == unsat:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
                solver.pop()
            except Exception as e:
                if str(e) == "canceled":
                    solver.pop()
                solver.push()
                solver.add(Not(stack[1] != 0))
                if solver.check() == unsat:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
                solver.pop()
    elif opcode == "SUICIDE" and len(stack) > 1:
        if isReal(stack[1]):
            address = stack[1] % 2**160
            if address not in global_state:
                gas_increment += GCOST["Gnewaccount"]
        else:
            address = str(stack[1])
            if address not in global_state:
                gas_increment += GCOST["Gnewaccount"]
    elif opcode in ("CALL", "CALLCODE", "DELEGATECALL") and len(stack) > 2:
        # Not fully correct yet
        gas_increment += GCOST["Gcall"]
        if isReal(stack[2]):
            if stack[2] != 0:
                gas_increment += GCOST["Gcallvalue"]
        else:
            solver.push()
            solver.add(Not(stack[2] != 0))
            if check_sat(solver) == unsat:
                gas_increment += GCOST["Gcallvalue"]
            solver.pop()
    elif opcode == "SHA3" and isReal(stack[1]):
        pass  # Not handle
    elif opcode == "KECCAK256" and isReal(stack[1]):
        pass

    # Calculate gas memory, add it to total gas used
    length = len(mem.keys())  # number of memory words
    new_gas_memory = GCOST["Gmemory"] * length + (length**2) // 512
    gas_increment += new_gas_memory - gas_memory

    return (gas_increment, new_gas_memory)


def semantic_analysis(
    analysis,
    opcode,
    stack,
    mem,
    global_state,
    global_problematic_pcs,
    current_func_name,
    g_src_map,
    path_conditions_and_vars,
    solver,
    instructions,
    g_slot_map,
):
    gas_increment, gas_memory = calculate_gas(
        opcode, stack, mem, global_state, analysis, solver
    )
    analysis["gas"] += gas_increment
    analysis["gas_mem"] = gas_memory

    # MSTORE slotid to MEM32
    if opcode == "MSTORE":
        stored_address = stack[0]
        stored_value = stack[1]

        if isReal(stored_address):
            value = stored_value
            if global_state["mint"]["trigger"] is True:
                # *Other cases, the second param of mint is quantity
                # if value == global_state["mint"]["token_id"]:
                # global_state["mint"]["MSTORE_1"] = True
                if value in g_slot_map.owner_index:
                    global_state["mint"]["MSTORE_2"] = True

            if global_state["approve"]["trigger"] is True:
                if value == global_state["approve"]["token_id"]:
                    global_state["approve"]["MSTORE_1"] = True
                elif value in g_slot_map.owner_index:
                    global_state["approve"]["MSTORE_owner"] = True
                elif value in g_slot_map.approval_index:
                    global_state["approve"]["MSTORE_2"] = True

            if global_state["burn"]["trigger"] is True:
                if value == global_state["burn"]["token_id"]:
                    global_state["burn"]["MSTORE_1"] = True
                elif value in g_slot_map.owner_index:
                    global_state["burn"]["MSTORE_2"] = True

            if global_state["setApprovalForAll"]["trigger"] is True:
                if str(global_state["sender_address"]) in str(value):
                    global_state["setApprovalForAll"]["MSTORE_1"] = True
                elif value in g_slot_map.approval_index:
                    global_state["setApprovalForAll"]["MSTORE_2"] = True
                elif str(global_state["setApprovalForAll"]["operator"]) in str(value):
                    global_state["setApprovalForAll"]["MSTORE_3"] = True

    elif opcode == "SSTORE":
        stored_address = stack[0]
        stored_value = stack[1]

        # *Risky Mutable Proxy DEFECT
        if g_src_map:
            if stored_address in g_slot_map.proxy_index and current_func_name:
                name_upper = current_func_name.upper()
                if (
                    "ACTIVE" not in name_upper
                    and "START" not in name_upper
                    and "SETPROXY" in name_upper
                ):
                    solver = Solver()
                    solver.set("timeout", global_params.TIMEOUT)
                    solver.add([global_state["Ia"][stored_address] != stored_value])
                    if solver.check() == sat:
                        global_problematic_pcs["proxy_defect"].append(
                            global_state["pc"]
                        )

        if global_state["mint"]["hash"] == stored_address:
            vars = get_vars(stored_value)
            if global_state["mint"]["to"] in vars:
                global_state["mint"]["valid"] = True
                global_state["mint"]["trigger"] = False

                path_condition = path_conditions_and_vars["path_condition"]
                # *Check the standard implementation of _mint
                # require(to != address(0), "ERC721: mint to the zero address");
                # require(!_exists(tokenId), "ERC721: token already minted");

                new_path_condition = []
                for expr in path_condition:
                    if not is_expr(expr):
                        continue
                    list_vars = get_vars(expr)
                    for var in list_vars:
                        # check if a var is global
                        if str(global_state["mint"]["to"]) == str(var):
                            new_path_condition.append(var == BitVecVal(0, 256))
                        elif is_storage_var(var):
                            if str(global_state["mint"]["hash"]) in str(var):
                                new_path_condition.append(var != BitVecVal(0, 256))
                solver = Solver()
                solver.set("timeout", global_params.TIMEOUT)

                solver.add(path_condition)
                solver.push()
                solver.add(new_path_condition)
                # *True => problematic mint
                if solver.check() == sat:
                    for pc in global_state["standard_violation"]["mint_pc"]:
                        global_problematic_pcs["violation_defect"].append(pc)

                # *Unlimited Minting DEFECT
                check = False
                owner = False
                for expr in path_condition:
                    if not is_expr(expr):
                        continue
                    list_vars = get_vars(expr)
                    for var in list_vars:
                        # check if a var is global
                        if is_storage_var(var):
                            pos = get_storage_position(var)
                            var_name = get_storage_var_name(var)
                            # *onlyOwner
                            if var_name == "":
                                if pos in g_slot_map.simpler_slot_map:
                                    var_names = g_slot_map.simpler_slot_map[pos]
                                    for var_name in var_names:
                                        if "owner" in var_name.lower():
                                            owner = True
                            else:
                                if "owner" in var_name:
                                    owner = True
                            if pos in g_slot_map.supply_index:
                                check = True

                if (
                    not check
                    and owner
                    and not global_state["unlimited_minting"]["check"]
                ):
                    for pc in global_state["unlimited_minting"]["pc"]:
                        global_problematic_pcs["unlimited_minting_defect"].append(pc)

        # *_tokenApprovals[tokenId] = to;
        if global_state["approve"]["hash"] == stored_address:
            vars = get_vars(stored_value)
            if global_state["approve"]["to"] in vars:
                global_state["approve"]["valid"] = True
                global_state["approve"]["trigger"] = False

                # *Check the standard implementation of approve
                # *Example A
                # require(to != owner, "ERC721: approval to current owner");
                # require(
                #     _msgSender() == owner || isApprovedForAll(owner, _msgSender()),
                #     "ERC721: approve caller is not token owner nor approved for all"
                # );
                # *Example B
                # if (to == owner) revert ApprovalToCurrentOwner();
                # if (_msgSender() != owner && !isApprovedForAll(owner, _msgSender())) {
                #     revert ApprovalCallerNotOwnerNorApproved();
                # }
                path_condition = path_conditions_and_vars["path_condition"]
                solver = Solver()
                solver.set("timeout", global_params.TIMEOUT)
                solver.add(path_condition)
                new_path_condition = []
                check_to = False
                check_permission = False

                for expr in path_condition:
                    if not is_expr(expr):
                        continue
                    list_vars = get_vars(expr)
                    for var in list_vars:
                        # check if a var is global
                        if is_storage_var(var):
                            # *some_var_x in Ia_store_some_var_x
                            if global_state["approve"]["owner_hash"] != None and str(
                                global_state["approve"]["owner_hash"]
                            ) in str(var):
                                # *Step1: Do not approve to current owner
                                # *Cannot through solver checking
                                solver.push()
                                solver.add([var == global_state["approve"]["to"]])
                                if not (solver.check() == sat):
                                    check_to = True
                                solver.pop()

                        elif str(var) == str(global_state["sender_address"]):
                            # *Step2 msg.sender == owner
                            # TODO isApprovedForAll(owner, _msgSender())
                            solver.push()
                            solver.add([var != global_state["approve"]["to"]])
                            if not (solver.check() == sat):
                                check_permission = True
                            solver.pop()

                if not (check_to and check_permission):
                    for pc in global_state["standard_violation"]["approve_pc"]:
                        global_problematic_pcs["violation_defect"].append(pc)

                # *Check the invalid approval DEFECT
                if (
                    global_state["approve"]["to"] != None
                    and global_state["mint"]["to"] != None
                    and global_state["approve"]["to"] == global_state["mint"]["to"]
                ):
                    for pc in global_state["invalid_approval"]["pc"]:
                        global_problematic_pcs["invalid_approval_defect"].append(pc)

                # *Cannot transfer the approval permission
                # *Sample:
                #   _mint(address(this), id)
                #   setApprovalForAll(contract, true)
                if str(global_state["mint"]["to"]) == str(
                    path_conditions_and_vars["Ia"]
                ):
                    for pc in global_state["invalid_approval"]["pc"]:
                        global_problematic_pcs["invalid_approval_defect"].append(pc)

        # *Public Burn DEFECT
        if (
            global_state["burn"]["valid"]
            and global_state["burn"]["hash"] == stored_address
        ):
            path_condition = path_conditions_and_vars["path_condition"]
            check = False
            for expr in path_condition:
                if not is_expr(expr):
                    continue
                list_vars = get_vars(expr)
                for var in list_vars:
                    if str(var) == str(global_state["sender_address"]):
                        check = True
            if not check:
                global_problematic_pcs["burn_defect"].append(global_state["burn"]["pc"])
    elif opcode.startswith("PUSH", 0):
        source_code = g_src_map.get_source_code(global_state["pc"])
        if source_code.strip().startswith("_safeMint"):
            # find 4 pc count before to find the exit of the for loop to judge the end of the function (for _safeMint)
            if (global_state["pc"] - 4) in instructions:
                src_c = g_src_map.get_source_code(global_state["pc"] - 4)
                if src_c.startswith("for"):
                    instr = instructions[global_state["pc"] - 4]
                    instr_parts = str.split(instr, " ")
                    opcode = instr_parts[0]
                    pushed_value = int(instr_parts[1], 16)
                    global_state["ERC721_reentrancy"]["key"] = pushed_value

    elif opcode == "JUMP":
        source_code = ""
        if g_src_map:
            source_code = g_src_map.get_source_code(global_state["pc"])
            # *Is function call
            if source_code in g_src_map.func_call_names:
                # *Reentrancy DEFECT
                # *For _safeMint and safetTransferFrom
                # *Need to validate the intention => the exitence of calling onERC721Received
                if source_code.startswith("_safeMint") or source_code.startswith(
                    "safeTransferFrom"
                ):
                    global_state["unlimited_minting"]["pc"].append(global_state["pc"])
                    global_state["ERC721_reentrancy"]["pc"].append(global_state["pc"])

                    path_condition = path_conditions_and_vars["path_condition"]
                    for expr in path_condition:
                        if not is_expr(expr):
                            continue
                        list_vars = get_vars(expr)

                        for var in list_vars:
                            if is_storage_var(var):
                                pos = get_storage_position(var)

                                var_name = get_storage_var_name(var)
                                if pos in global_state["Ia"]:
                                    new_path_condition = []
                                    new_path_condition.append(
                                        var == global_state["Ia"][pos]
                                    )
                                    solver = Solver()
                                    solver.set("timeout", global_params.TIMEOUT)
                                    solver.add(new_path_condition)
                                    if not (solver.check() == unsat):
                                        global_state["ERC721_reentrancy"]["var"].append(
                                            var_name
                                        )

                # *Check mint and validate it
                # find our focus function _mint/_safeMint
                if (
                    source_code.startswith("_mint")
                    or source_code.startswith("_safeMint")
                ) and current_func_name:
                    global_state["mint"]["trigger"] = True
                    # TODO check the parameter of _mint, default sequence(token_owner,token_id)
                    global_state["mint"]["to"] = stack[2]
                    global_state["mint"]["token_id"] = stack[1]
                    global_state["mint"]["quantity"] = stack[1]
                    global_state["standard_violation"]["mint_pc"].append(
                        global_state["pc"]
                    )
                    path_condition = path_conditions_and_vars["path_condition"]
                    for expr in path_condition:
                        if not is_expr(expr):
                            continue
                        list_vars = get_vars(expr)
                        for var in list_vars:
                            # judge the quantity comparison
                            if str(global_state["mint"]["quantity"]) in str(var):
                                check = True
                                global_state["unlimited_minting"]["check"] = True

                # *Check approve and validate it
                elif source_code.startswith("approve") and current_func_name:
                    global_state["approve"]["trigger"] = True
                    # TODO check the parameter of approve, default sequence(operator, token_id)
                    global_state["approve"]["to"] = stack[2]
                    global_state["approve"]["token_id"] = stack[1]
                    global_state["standard_violation"]["approve_pc"].append(
                        global_state["pc"]
                    )
                    global_state["invalid_approval"]["pc"].append(global_state["pc"])

                elif source_code.startswith("setApprovalForAll") and current_func_name:
                    global_state["setApprovalForAll"]["trigger"] = True
                    global_state["setApprovalForAll"]["operator"] = stack[2]
                    global_state["setApprovalForAll"]["approved"] = stack[1]
                    global_state["standard_violation"]["setApprovalForAll_pc"].append(
                        global_state["pc"]
                    )
                    global_state["invalid_approval"]["pc"].append(global_state["pc"])

                # *Check burn and validate it
                elif source_code.startswith("_burn") and current_func_name:
                    global_state["burn"]["trigger"] = True
                    # TODO check the parameter of burn, default sequence(token_id)
                    global_state["burn"]["token_id"] = stack[1]
                    global_state["burn"]["pc"] = global_state["pc"]

    elif opcode == "CALL":
        if global_state["ERC721_reentrancy"]["pc"]:
            reentrancy_result = check_reentrancy_bug(
                g_src_map, global_state, stack, mem
            )
            if reentrancy_result:
                global_problematic_pcs["reentrancy_defect"] = global_state[
                    "ERC721_reentrancy"
                ]["pc"]


def check_reentrancy_bug(g_src_map, global_state, stack, mem):
    # onERC721Received() Selector: 150b7a02
    ret_val = False
    # stack[8] represents the hash of onERC721Received
    # *Read memory from 160 to 224/mem_64 => 160, 164 + mem_mem_64 => 224
    # *The values should be the shift-lefted value of OnERC721Received selector
    start_data_input = stack[3]
    _ = stack[4]
    if (
        str(start_data_input) == "mem_64"
        or mem[start_data_input] == global_params.ONERC721RECEIVED_SELECTOR_SHL
    ):
        # *check the call location and aftwards operations from AST walker
        location = g_src_map.get_location(global_state["ERC721_reentrancy"]["pc"][0])
        ret_val = is_same_location(
            global_state["ERC721_reentrancy"]["var"],
            location,
            g_src_map.safe_func_call_info,
        )
    # check the location and the determined variable are changed from the AST walker
    if global_params.DEBUG_MODE:
        log.info("ERC721 Reentrancy_bug? " + str(ret_val))
    return ret_val


def is_same_location(unchanged_vars, se_location, src_map_locations):
    for loc, var_names in src_map_locations:
        if (
            loc["begin"]["line"] == se_location["begin"]["line"]
            and loc["begin"]["column"] == se_location["begin"]["column"]
        ):
            for var in unchanged_vars:
                for var_name in var_names:
                    if var_name in var:
                        return True
    return False
