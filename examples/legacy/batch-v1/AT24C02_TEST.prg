//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=
// AT24C02 ATE Test Program
// Protocol: I2C
// Generated: 2026-03-22 09:54:05
// Tool: EEPROM PAT Generator v6.0.0
// Target ATE: AdaptStar-E (EStar)
// Total Vectors: 6459
//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=

DEVICE_INFO {
    Name     = "AT24C02";
    Package  = "SOP-8";
    Capacity = "2Kbit (256x8)";
    Protocol = "I2C";
    VCC      = 5.0V;
}

// ============================================================
// Step 1: Power Supply Configuration
// ============================================================
DPS_SETUP {
    DPS1.VForce  = 5.0V;   // VCC (Pin 8)
    DPS1.IClampH = 100mA;
    DPS1.IClampL = -10mA;
    DPS_GND.VForce = 0V;         // GND (Pin 4)
}

// ============================================================
// Step 2: Level and Timing Setup
// ============================================================
LOAD_LEVEL("level_5v");          // From .lvl file
LOAD_TIMING("timing_i2c");       // From .tim file

// ============================================================
// Step 3: Power-On Sequence
// ============================================================
POWER_ON_SEQUENCE {
    DPS_GND.ON();
    DPS1.ON();
    WAIT(10ms);                    // VCC ramp-up stabilization
    FORCE_PIN(A0, LOW);
    FORCE_PIN(A1, LOW);
    FORCE_PIN(A2, LOW);
    FORCE_PIN(WP, LOW);            // Write enabled
    FORCE_PIN(SDA, HIGH);           // Bus idle
    FORCE_PIN(SCL, HIGH);           // Bus idle
    WAIT(1ms);                     // Bus stabilization
}

// ============================================================
// Step 4: Test Execution Flow
// ============================================================
// NOTE: Multi-SITE aware — use SITE_MASK to skip failed sites
//       Dependency chain: OS → DC → FUNC → Memory tests
//       If OS fails, skip all subsequent tests (hard bin)
TEST_FLOW {

    // --- Open/Short Continuity Test (46 vectors) ---
    // PPMU walking: force ±100μA, measure voltage per pin
    DIGI_PPMU_SETUP(ALL, FI, 100UA, MV, CLAMP_2V);
    RUN_PATTERN(OS_TEST, 1);
    result = DIGI_PPMU_WALKING_FI_MV(ALL, 100UA, -100UA);
    JUDGE(result, VOL_LIMIT=0.8V, VOH_LIMIT=-0.8V);
    IF (FAIL) {
        SET_SITE_FLAG(FAIL, "OS_TEST");
        GOTO BIN_FAIL_OS_TEST;
    }

    // Dependency: DC_TEST requires OS_TEST PASS
    IF (SITE_FAIL(OS_TEST)) GOTO BIN_FAIL_DC_TEST;

    // --- DC Parameter Test (ISB/ICC/VOL/VOH/IDDQ) (2017 vectors) ---
    // DC parametric: ISB, ICC, VOL, VOH, IDDQ
    RUN_PATTERN(DC_TEST, 1);
    // ISB test: measure standby current
    DIGI_DPS_FV(DPS1, VCC_VAL);
    isb = DIGI_DPS_MI(DPS1);
    JUDGE(isb, MAX=1.0UA);

    // VOL test: during ACK, SDA output low
    vol = DIGI_PPMU_FI_MV(CH04, 3MA);
    JUDGE(vol, MAX=0.4V);

    // IDDQ test: quiescent current after data write
    iddq = DIGI_DPS_MI(DPS1);  // at IDDQ measurement point
    JUDGE(iddq, MAX=2.0UA);  // defective die > 10uA typical
    IF (FAIL) {
        SET_SITE_FLAG(FAIL, "DC_TEST");
        GOTO BIN_FAIL_DC_TEST;
    }

    // Dependency: FUNC_TEST requires DC_TEST PASS
    IF (SITE_FAIL(DC_TEST)) GOTO BIN_FAIL_FUNC_TEST;

    // --- I2C Functional Test (4396 vectors) ---
    // Byte/Page write-read, WP protect, boundary test
    RUN_PATTERN(FUNC_TEST, 1);
    result = GET_FAIL_COUNT();
    JUDGE(result, MAX=0);  // Zero vector mismatches = PASS
    IF (FAIL) {
        SET_SITE_FLAG(FAIL, "FUNC_TEST");
        GOTO BIN_FAIL_FUNC_TEST;
    }

    // All tests passed
    BIN(1, "PASS", SOFT);  // Good die
    GOTO TEST_END;

  BIN_FAIL_OS_TEST:
    BIN(2, "FAIL_OS_TEST", HARD);
    GOTO TEST_END;

  BIN_FAIL_DC_TEST:
    BIN(3, "FAIL_DC_TEST", HARD);
    GOTO TEST_END;

  BIN_FAIL_FUNC_TEST:
    BIN(4, "FAIL_FUNC_TEST", SOFT);
    GOTO TEST_END;

  TEST_END:
}

// ============================================================
// BIN Summary Table
// ============================================================
// BIN  | Category | Name            | Description
// -----|----------|-----------------|----------------------------
//   1  | PASS     | PASS            | All tests passed
//   2  | FAIL-HARD | FAIL_OS_TEST         | Open/Short
//   3  | FAIL-HARD | FAIL_DC_TEST         | DC Parametric
//   4  | FAIL-SOFT | FAIL_FUNC_TEST       | Functional
// ============================================================

// ============================================================
// Step 5: Power-Down Sequence
// ============================================================
POWER_OFF_SEQUENCE {
    FORCE_PIN(ALL, LOW);
    DPS1.OFF();
    WAIT(1ms);
    DPS_GND.OFF();
}
