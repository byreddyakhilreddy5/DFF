import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


def get_q_value(dut):
    """
    Safely get q value, handling 'X' values gracefully
    """
    try:
        return dut.q.value.to_unsigned()
    except ValueError as e:
        if "non-0/1 values" in str(e):
            raise AssertionError(
                f"q contains 'X' (unknown) values - output is not being driven properly. "
                f"Current value: {dut.q.value}. "
                f"Ensure q is always assigned in all code paths."
            ) from e
        raise


@cocotb.test()
async def test_d_flipflop(dut):
    """Cocotb test for d_flipflop"""

    # Start clock: 10ns period
    cocotb.start_soon(Clock(dut.clock, 10, unit="ns").start())

    # Initialize inputs
    dut.reset_n.value = 0
    dut.d.value = 0

    await Timer(20, unit="ns")

    # Release reset
    dut.reset_n.value = 1
    await RisingEdge(dut.clock)

    dut._log.info("Reset released")

    # ----------------------------------------------------
    # Test 1: Basic operation - capture input on clock edge
    # ----------------------------------------------------
    dut.d.value = 1
    await RisingEdge(dut.clock)
    await FallingEdge(dut.clock)  # Check output at falling edge
    got = get_q_value(dut)
    assert got == 1, f"Expected q=1 after clock edge with d=1, got {got}"

    dut._log.info("Test 1: Basic capture verified")

    # ----------------------------------------------------
    # Test 2: Input change between clock edges doesn't affect output
    # ----------------------------------------------------
    dut.d.value = 0  # Change input
    await Timer(5, unit="ns")  # Wait some time (no clock edge)
    got = get_q_value(dut)
    assert got == 1, f"Expected q=1 (unchanged), got {got}"

    # Now capture on next clock edge
    await RisingEdge(dut.clock)
    await FallingEdge(dut.clock)
    got = get_q_value(dut)
    assert got == 0, f"Expected q=0 after clock edge with d=0, got {got}"

    dut._log.info("Test 2: Input stability verified")

    # ----------------------------------------------------
    # Test 3: Multiple clock cycles
    # ----------------------------------------------------
    test_pattern = [1, 0, 1, 1, 0, 0, 1, 0]
    for i, expected_d in enumerate(test_pattern):
        dut.d.value = expected_d
        await RisingEdge(dut.clock)
        await FallingEdge(dut.clock)
        got = get_q_value(dut)
        assert got == expected_d, (
            f"Cycle {i}: Expected q={expected_d} with d={expected_d}, got {got}"
        )

    dut._log.info("Test 3: Multiple clock cycles verified")

    # ----------------------------------------------------
    # Test 4: Asynchronous reset
    # ----------------------------------------------------
    dut.d.value = 1
    await RisingEdge(dut.clock)
    await FallingEdge(dut.clock)
    got = get_q_value(dut)
    assert got == 1, f"Expected q=1 before reset, got {got}"

    # Assert reset (asynchronous, no clock needed)
    dut.reset_n.value = 0
    await Timer(5, unit="ns")  # Small delay to allow reset to propagate
    got = get_q_value(dut)
    assert got == 0, f"Expected q=0 after reset, got {got}"

    # Reset should work even if d changes
    dut.d.value = 1
    await Timer(5, unit="ns")
    got = get_q_value(dut)
    assert got == 0, f"Expected q=0 during reset (d=1), got {got}"

    dut._log.info("Test 4: Asynchronous reset verified")

    # ----------------------------------------------------
    # Test 5: Reset release and normal operation resumes
    # ----------------------------------------------------
    dut.reset_n.value = 1
    await RisingEdge(dut.clock)
    await FallingEdge(dut.clock)
    got = get_q_value(dut)
    assert got == 1, f"Expected q=1 after reset release with d=1, got {got}"

    dut._log.info("Test 5: Reset release verified")

    dut._log.info("✅ D flip-flop cocotb test PASSED")


# ✅ CRITICAL: Pytest wrapper function
def test_d_flipflop_runner():
    import os
    from pathlib import Path
    from cocotb_tools.runner import get_runner
    
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    
    sources = [
        proj_path / "sources/d_flipflop.sv",
    ]
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="d_flipflop",
        always=True,
    )
    
    runner.test(
        hdl_toplevel="d_flipflop",
        test_module="test_d_flipflop"
    )

