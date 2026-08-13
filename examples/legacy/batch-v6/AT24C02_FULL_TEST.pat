// PAT File: AT24C02_TEST
// Description: AT24C02 I2C Full Test
// Generated: 2026-03-22 10:17:56
// Tool: EEPROM PAT Generator v6.0.0
// Target ATE: AdaptStar-E (EStar)

HEAD[PIN_NAME]:
  
 A0,
 A1,
 A2,
 WP,
 SCL,
 SDA;
 
END_HEAD;
TIMING timing_i2c {
    PERIOD  = 2500ns;   // 400.0 kHz
    tDRV    = 0ns;        // Drive data at period start
    tCMP    = 1250ns;    // Compare strobe at mid-period
    tPLC    = 0ns;        // Pin Low  clock edge
    tPHC    = 1250ns;    // Pin High clock edge
}

LEVEL level_5v {
    VCC  = 5.0V;
    VIH  = 3.5V;    // Input High threshold
    VIL  = 1.5V;    // Input Low  threshold
    VOH  = 2.4V;    // Output High minimum
    VOL  = 0.4V;    // Output Low  maximum
    IOL  = 3.0mA;   // Output Low  sink current
    VCLH = 6.0V;    // Clamp High
    VCLL = -0.3V;   // Clamp Low
}

@@PATTERN_DEFINE  
// AT24C02_FULL_TEST
// A0,A1,A2,WP,SCL,SDA

OS_ALL_LOW:         000000;AC_SET 1;
                    000000;    //Hold LOW
                    000000;    //Hold LOW
                    000000;    //Hold LOW
OS_ALL_HIGH:        111111;    //OS_TEST: All pins drive HIGH
                    111111;    //Hold HIGH
                    111111;    //Hold HIGH
                    111111;    //Hold HIGH
OS_WALK1_A0:        100000;    //Walking-1: A0=HIGH, others=LOW
                    100000;    //Hold A0=HIGH
                    100000;    //Hold A0=HIGH
OS_WALK1_A1:        010000;    //Walking-1: A1=HIGH, others=LOW
                    010000;    //Hold A1=HIGH
                    010000;    //Hold A1=HIGH
OS_WALK1_A2:        001000;    //Walking-1: A2=HIGH, others=LOW
                    001000;    //Hold A2=HIGH
                    001000;    //Hold A2=HIGH
OS_WALK1_WP:        000100;    //Walking-1: WP=HIGH, others=LOW
                    000100;    //Hold WP=HIGH
                    000100;    //Hold WP=HIGH
OS_WALK1_SCL:       000010;    //Walking-1: SCL=HIGH, others=LOW
                    000010;    //Hold SCL=HIGH
                    000010;    //Hold SCL=HIGH
OS_WALK1_SDA:       000001;    //Walking-1: SDA=HIGH, others=LOW
                    000001;    //Hold SDA=HIGH
                    000001;    //Hold SDA=HIGH
OS_WALK0_A0:        011111;    //Walking-0: A0=LOW, others=HIGH
                    011111;    //Hold A0=LOW
                    011111;    //Hold A0=LOW
OS_WALK0_A1:        101111;    //Walking-0: A1=LOW, others=HIGH
                    101111;    //Hold A1=LOW
                    101111;    //Hold A1=LOW
OS_WALK0_A2:        110111;    //Walking-0: A2=LOW, others=HIGH
                    110111;    //Hold A2=LOW
                    110111;    //Hold A2=LOW
OS_WALK0_WP:        111011;    //Walking-0: WP=LOW, others=HIGH
                    111011;    //Hold WP=LOW
                    111011;    //Hold WP=LOW
OS_WALK0_SCL:       111101;    //Walking-0: SCL=LOW, others=HIGH
                    111101;    //Hold SCL=LOW
                    111101;    //Hold SCL=LOW
OS_WALK0_SDA:       111110;    //Walking-0: SDA=LOW, others=HIGH
                    111110;    //Hold SDA=LOW
                    111110;    //Hold SDA=LOW
OS_END:             000011;    //Return to IDLE
                    000011;
DC_ISB_START:       000011;    //=== DC ISB Test: Standby Current ===
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
                    000011;    //ISB: IDLE state (measure ICC)
DC_ISB_MEAS:        000011;    //ISB measurement point
                    000011;    //ISB: continue IDLE
                    000011;    //ISB: continue IDLE
                    000011;    //ISB: continue IDLE
                    000011;    //ISB: continue IDLE
DC_ICC_START:       000011;    //=== DC ICC Test: Operating Current (Read) ===
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+R (ICC test) bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (ICC test) bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R (ICC test) bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (ICC test) bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (ICC test) bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (ICC test) bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (ICC test) bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R (ICC test) bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[7]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[6]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[5]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[4]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[3]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[2]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[1]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    00000Z;    //Read bit Read data (ICC meas) bit[0]
                    00001X;    //SCL↑ (compare=X)
                    00000X;    //SCL↓
                    000001;    //NACK from master
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //ICC Read complete
                    000011;
DC_ICC_W_START:     000011;    //=== DC ICC Write Test ===
                    000011;    //=== Byte Write: addr=0x00 data=0x55 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
DC_VOL_START:       000011;    //=== DC VOL Test (SDA output LOW during ACK) ===
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //*** VOL measurement point (ACK=LOW) ***
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr=0x00 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //VOL meas point 2
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //IDLE
                    000011;
DC_VOH_START:       000011;    //=== DC VOH Test (SDA output HIGH during Read) ===
                    000011;    //=== Byte Write: addr=0x10 data=0xFF ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x10 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
DC_VIL_VIH_START:   000011;    //=== DC Input Threshold Test (VIL/VIH via LEVEL set) ===
                    000011;    //=== Byte Write: addr=0x20 data=0xAA ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x20 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
DC_IDDQ_START:      000011;    //=== DC-7: IDDQ Quiescent Current Test ===
                    000011;    //=== Byte Write: addr=0x30 data=0x00 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
                    000011;    //IDDQ State-1: all-zero written, quiescent (measure IDD)
DC_IDDQ_MEAS1:      000011;    //*** IDDQ measurement point 1 (data=0x00) ***
                    000011;    //=== Byte Write: addr=0x30 data=0xFF ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
                    000011;    //IDDQ State-2: all-one written, quiescent (measure IDD)
DC_IDDQ_MEAS2:      000011;    //*** IDDQ measurement point 2 (data=0xFF) ***
                    000011;    //=== Byte Write: addr=0x30 data=0x55 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
                    000011;    //IDDQ State-3: checkerboard, quiescent (measure IDD)
DC_IDDQ_MEAS3:      000011;    //*** IDDQ measurement point 3 (data=0x55) ***
                    000011;    //=== DC Test Complete ===
                    000011;
                    000011;
                    000011;
FUNC_BW_START:      000011;    //=== FUNC: Byte Write + Read Verify ===
                    000011;    //=== Byte Write: addr=0x00 data=0x55 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x00 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Byte Write: addr=0x01 data=0xAA ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x01 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_PW_START:      000011;    //=== FUNC: Page Write + Sequential Read ===
                    000011;    //=== Page Write: addr=0x08 len=8 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[0] bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data[0]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[1] bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[1]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[2] bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[2]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[3] bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[3]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[4] bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[4] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[4]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[5] bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[5] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[5]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[6] bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[6] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[6]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data[7] bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[7] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[7]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Sequential Read: addr=0x08 count=8 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK from slave
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK from slave
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 0)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 1)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[2] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 2)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[3] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 3)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[4] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 4)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[5] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 5)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[6] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 6)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[7] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end sequential read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_BOUND_START:   000011;    //=== FUNC: Address Boundary Test ===
                    000011;    //=== Byte Write: addr=0xFF data=0x42 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0xFF ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_WRAP_BASELINE: 000011;    //Verify addr 0x00 baseline before wraparound test
                    000011;    //=== Random Read: addr=0x00 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_WRAP:          000011;    //Address wraparound: sequential read 0xFF->0x00
                    000011;    //=== Sequential Read: addr=0xFF count=2 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK from slave
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK from slave
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[0] bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000000;    //ACK (continue read 0)
                    000010;    //ACK (SDA=LOW)
                    000000;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit SeqRead[1] bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end sequential read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_WP_START:      000011;    //=== FUNC: WP Write Protect Test ===
                    000011;    //=== Byte Write: addr=0x40 data=0x5A ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 Data bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
WP_PROTECT:         000111;    //WP=1: write protect enabled, attempt overwrite (data unchanged)
                    000111;    //=== Byte Write: addr=0x40 data=0xA5 ===
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 DevAddr+W bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 DevAddr+W bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 DevAddr+W bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //ACK after DevAddr
                    00011L;    //ACK check (expect LOW)
                    00010X;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[7]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 WordAddr bit[6]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[5]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 WordAddr bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //ACK after WordAddr
                    00011L;    //ACK check (expect LOW)
                    00010X;    //SCL↓
                    000101;    //Write bit=1 Data bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Data bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Data bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Data bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Data bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Data bit[2]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Data bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Data bit[0]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    00010Z;    //ACK after Data
                    00011L;    //ACK check (expect LOW)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //=== ACK Polling (wait for write cycle) ===
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 Poll attempt 0 bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Poll attempt 0 bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 0 bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //Poll NACK (device busy, attempt 0)
                    00011H;    //NACK check (expect HIGH)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 Poll attempt 1 bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Poll attempt 1 bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 1 bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //Poll NACK (device busy, attempt 1)
                    00011H;    //NACK check (expect HIGH)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 Poll attempt 2 bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Poll attempt 2 bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 2 bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //Poll NACK (device busy, attempt 2)
                    00011H;    //NACK check (expect HIGH)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 Poll attempt 3 bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Poll attempt 3 bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 3 bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //Poll NACK (device busy, attempt 3)
                    00011H;    //NACK check (expect HIGH)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
                    000111;    //START Setup
                    000110;    //START Condition (SDA↓)
                    000100;    //START Hold
                    000101;    //Write bit=1 Poll attempt 4 bit[7]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[6]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000101;    //Write bit=1 Poll attempt 4 bit[5]
                    000111;    //SCL↑ (data valid)
                    000101;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[4]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[3]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[2]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[1]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    000100;    //Write bit=0 Poll attempt 4 bit[0]
                    000110;    //SCL↑ (data valid)
                    000100;    //SCL↓
                    00010Z;    //Poll ACK (device ready, attempt 4)
                    00011L;    //ACK check (expect LOW)
                    00010X;    //SCL↓
                    000100;    //STOP Setup
                    000110;    //STOP (SCL↑)
                    000111;    //STOP Condition (SDA↑)
                    000111;    //Poll interval
                    000111;
WP_VERIFY:          000011;    //WP=0: read back to verify data unchanged (expect 0x5A)
                    000011;    //=== Random Read: addr=0x40 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_PAGE_WRAP:     000011;    //=== FUNC-6: Page Boundary Wrap-Around Test ===
                    000011;    //=== Page Write: addr=0x06 len=4 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data[0] bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[0] bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[0] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[0] bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data[0]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data[1] bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[1] bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data[1] bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[1] bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[1] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[1]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data[2] bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data[2] bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[2] bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[2] bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data[2] bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after Data[2]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data[3] bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data[3] bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[3] bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data[3] bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data[3] bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data[3]
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x06 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Random Read: addr=0x07 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Random Read: addr=0x00 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Random Read: addr=0x01 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
FUNC_CURR_READ:     000011;    //=== FUNC-7: Current Address Read Test ===
                    000011;    //=== Byte Write: addr=0x10 data=0xCA ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Data bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Byte Write: addr=0x11 data=0xFE ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //Write bit=1 Data bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[6]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[3]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[2]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000001;    //Write bit=1 Data bit[1]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Data bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after Data
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== ACK Polling (wait for write cycle) ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 0 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 0 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 0 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 0)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 1 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 1 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 1 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 1)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 2 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 2 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 2 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 2)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 3 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 3 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 3 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll NACK (device busy, attempt 3)
                    00001H;    //NACK check (expect HIGH)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 Poll attempt 4 bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 Poll attempt 4 bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 Poll attempt 4 bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //Poll ACK (device ready, attempt 4)
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //Poll interval
                    000011;
                    000011;    //=== Random Read: addr=0x10 ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+W bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+W bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+W bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after DevAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[7]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[5]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 WordAddr bit[4]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 WordAddr bit[0]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    00000Z;    //ACK after WordAddr
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    000001;    //RepSTART: SDA↑
                    000011;    //RepSTART: SCL↑
                    000010;    //RepSTART: SDA↓
                    000000;    //RepSTART: SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[5]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[4]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[2]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit ReadData bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Current Address Read ===
                    000011;
                    000011;    //START Setup
                    000010;    //START Condition (SDA↓)
                    000000;    //START Hold
                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[7]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[6]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[5]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[4]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[3]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[2]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000000;    //Write bit=0 DevAddr+R (Current Addr Read) bit[1]
                    000010;    //SCL↑ (data valid)
                    000000;    //SCL↓
                    000001;    //Write bit=1 DevAddr+R (Current Addr Read) bit[0]
                    000011;    //SCL↑ (data valid)
                    000001;    //SCL↓
                    00000Z;    //ACK after DevAddr+R
                    00001L;    //ACK check (expect LOW)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[7]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[6]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[5]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[4]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[3]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[2]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[1]
                    00001H;    //SCL↑ (compare=H)
                    00000X;    //SCL↓
                    00000Z;    //Read bit CurrentAddrRead data bit[0]
                    00001L;    //SCL↑ (compare=L)
                    00000X;    //SCL↓
                    000001;    //NACK (end current addr read)
                    000011;    //NACK (SDA=HIGH)
                    000001;    //SCL↓
                    000000;    //STOP Setup
                    000010;    //STOP (SCL↑)
                    000011;    //STOP Condition (SDA↑)
                    000011;    //=== Functional Test Complete ===
                    000011;
                    000011;
                    000011;

@@END_PATTERN_DEFINE
