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
// DC_TEST
// A0,A1,A2,WP,SCL,SDA

DC_ISB_START:       000011;AC_SET 1;
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

@@END_PATTERN_DEFINE
