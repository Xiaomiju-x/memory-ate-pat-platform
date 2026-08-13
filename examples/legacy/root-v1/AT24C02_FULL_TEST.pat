//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=
// PAT File: AT24C02_FULL_TEST
// Description: AT24C02 Complete Test (OS + DC + Functional)
// Device: AT24C02 (2Kbit I2C EEPROM)
// Generated: 2026-03-16 09:18:35
// Tool: AT24C02 PAT Generator v1.0
// Target ATE: AdaptStar-E (EStar)
//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=//=

// SIGNAL_GROUP: A0, A1, A2, SDA, SCL, WP
// Pin Mapping:
//   A0  -> DUT Pin 1 (Address Input)
//   A1  -> DUT Pin 2 (Address Input)
//   A2  -> DUT Pin 3 (Address Input)
//   SDA -> DUT Pin 5 (Serial Data I/O)
//   SCL -> DUT Pin 6 (Serial Clock)
//   WP  -> DUT Pin 7 (Write Protect)
//   VCC -> DPS Channel (Pin 8)
//   GND -> DPS Ground  (Pin 4)

// Vector States:
//   0 = Drive Low    1 = Drive High
//   L = Expect Low   H = Expect High
//   Z = Hi-Z         X = Don't Care
// TIMING CONFIGURATION
// Period: 2500ns (400.0kHz)
// I2C Clock: 400kHz (Standard/Fast Mode)

// ============================================================
// Open/Short Continuity Test
// ============================================================

PATTERN OS_TEST

// Vec#    A0   A1   A2  SDA  SCL   WP   // Comment
// ------------------------------------------------
  OS_ALL_LOW:
   V0000    0   0   0   0   0   0   // OS_TEST: All pins drive LOW
   V0001    0   0   0   0   0   0   // Hold LOW
   V0002    0   0   0   0   0   0   // Hold LOW
   V0003    0   0   0   0   0   0   // Hold LOW
  OS_ALL_HIGH:
   V0004    1   1   1   1   1   1   // OS_TEST: All pins drive HIGH
   V0005    1   1   1   1   1   1   // Hold HIGH
   V0006    1   1   1   1   1   1   // Hold HIGH
   V0007    1   1   1   1   1   1   // Hold HIGH
  OS_WALK1_A0:
   V0008    1   0   0   0   0   0   // Walking-1: A0=HIGH, others=LOW
   V0009    1   0   0   0   0   0   // Hold A0=HIGH
   V0010    1   0   0   0   0   0   // Hold A0=HIGH
  OS_WALK1_A1:
   V0011    0   1   0   0   0   0   // Walking-1: A1=HIGH, others=LOW
   V0012    0   1   0   0   0   0   // Hold A1=HIGH
   V0013    0   1   0   0   0   0   // Hold A1=HIGH
  OS_WALK1_A2:
   V0014    0   0   1   0   0   0   // Walking-1: A2=HIGH, others=LOW
   V0015    0   0   1   0   0   0   // Hold A2=HIGH
   V0016    0   0   1   0   0   0   // Hold A2=HIGH
  OS_WALK1_SDA:
   V0017    0   0   0   1   0   0   // Walking-1: SDA=HIGH, others=LOW
   V0018    0   0   0   1   0   0   // Hold SDA=HIGH
   V0019    0   0   0   1   0   0   // Hold SDA=HIGH
  OS_WALK1_SCL:
   V0020    0   0   0   0   1   0   // Walking-1: SCL=HIGH, others=LOW
   V0021    0   0   0   0   1   0   // Hold SCL=HIGH
   V0022    0   0   0   0   1   0   // Hold SCL=HIGH
  OS_WALK1_WP:
   V0023    0   0   0   0   0   1   // Walking-1: WP=HIGH, others=LOW
   V0024    0   0   0   0   0   1   // Hold WP=HIGH
   V0025    0   0   0   0   0   1   // Hold WP=HIGH
  OS_WALK0_A0:
   V0026    0   1   1   1   1   1   // Walking-0: A0=LOW, others=HIGH
   V0027    0   1   1   1   1   1   // Hold A0=LOW
   V0028    0   1   1   1   1   1   // Hold A0=LOW
  OS_WALK0_A1:
   V0029    1   0   1   1   1   1   // Walking-0: A1=LOW, others=HIGH
   V0030    1   0   1   1   1   1   // Hold A1=LOW
   V0031    1   0   1   1   1   1   // Hold A1=LOW
  OS_WALK0_A2:
   V0032    1   1   0   1   1   1   // Walking-0: A2=LOW, others=HIGH
   V0033    1   1   0   1   1   1   // Hold A2=LOW
   V0034    1   1   0   1   1   1   // Hold A2=LOW
  OS_WALK0_SDA:
   V0035    1   1   1   0   1   1   // Walking-0: SDA=LOW, others=HIGH
   V0036    1   1   1   0   1   1   // Hold SDA=LOW
   V0037    1   1   1   0   1   1   // Hold SDA=LOW
  OS_WALK0_SCL:
   V0038    1   1   1   1   0   1   // Walking-0: SCL=LOW, others=HIGH
   V0039    1   1   1   1   0   1   // Hold SCL=LOW
   V0040    1   1   1   1   0   1   // Hold SCL=LOW
  OS_WALK0_WP:
   V0041    1   1   1   1   1   0   // Walking-0: WP=LOW, others=HIGH
   V0042    1   1   1   1   1   0   // Hold WP=LOW
   V0043    1   1   1   1   1   0   // Hold WP=LOW
  OS_END:
   V0044    0   0   0   1   1   0   // Return to IDLE
   V0045    0   0   0   1   1   0   // IDLE

END_PATTERN // OS_TEST

// ============================================================
// DC Parameter Test
// ============================================================

PATTERN DC_TEST

// Vec#    A0   A1   A2  SDA  SCL   WP   // Comment
// ------------------------------------------------
  DC_ISB_START:
   V0000    0   0   0   1   1   0   // === DC ISB Test: Standby Current ===
   V0001    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0002    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0003    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0004    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0005    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0006    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0007    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
   V0008    0   0   0   1   1   0   // ISB: IDLE state (measure ICC)
  DC_ISB_MEAS:
   V0009    0   0   0   1   1   0   // ISB measurement point
   V0010    0   0   0   1   1   0   // ISB: continue IDLE
   V0011    0   0   0   1   1   0   // ISB: continue IDLE
   V0012    0   0   0   1   1   0   // ISB: continue IDLE
   V0013    0   0   0   1   1   0   // ISB: continue IDLE
  DC_ICC_START:
   V0014    0   0   0   1   1   0   // === DC ICC Test: Operating Current (Read) ===
   V0015    0   0   0   1   1   0   // START Setup
   V0016    0   0   0   0   1   0   // START Condition (SDA↓)
   V0017    0   0   0   0   0   0   // START Hold
   V0018    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[7]
   V0019    0   0   0   1   1   0   // SCL↑ (data valid)
   V0020    0   0   0   1   0   0   // SCL↓
   V0021    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[6]
   V0022    0   0   0   0   1   0   // SCL↑ (data valid)
   V0023    0   0   0   0   0   0   // SCL↓
   V0024    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[5]
   V0025    0   0   0   1   1   0   // SCL↑ (data valid)
   V0026    0   0   0   1   0   0   // SCL↓
   V0027    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[4]
   V0028    0   0   0   0   1   0   // SCL↑ (data valid)
   V0029    0   0   0   0   0   0   // SCL↓
   V0030    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[3]
   V0031    0   0   0   0   1   0   // SCL↑ (data valid)
   V0032    0   0   0   0   0   0   // SCL↓
   V0033    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[2]
   V0034    0   0   0   0   1   0   // SCL↑ (data valid)
   V0035    0   0   0   0   0   0   // SCL↓
   V0036    0   0   0   0   0   0   // Write bit=0 DevAddr+R (ICC test) bit[1]
   V0037    0   0   0   0   1   0   // SCL↑ (data valid)
   V0038    0   0   0   0   0   0   // SCL↓
   V0039    0   0   0   1   0   0   // Write bit=1 DevAddr+R (ICC test) bit[0]
   V0040    0   0   0   1   1   0   // SCL↑ (data valid)
   V0041    0   0   0   1   0   0   // SCL↓
   V0042    0   0   0   Z   0   0   // ACK
   V0043    0   0   0   L   1   0   // ACK check (expect LOW)
   V0044    0   0   0   X   0   0   // SCL↓
   V0045    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[7]
   V0046    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0047    0   0   0   X   0   0   // SCL↓
   V0048    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[6]
   V0049    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0050    0   0   0   X   0   0   // SCL↓
   V0051    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[5]
   V0052    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0053    0   0   0   X   0   0   // SCL↓
   V0054    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[4]
   V0055    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0056    0   0   0   X   0   0   // SCL↓
   V0057    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[3]
   V0058    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0059    0   0   0   X   0   0   // SCL↓
   V0060    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[2]
   V0061    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0062    0   0   0   X   0   0   // SCL↓
   V0063    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[1]
   V0064    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0065    0   0   0   X   0   0   // SCL↓
   V0066    0   0   0   Z   0   0   // Read bit Read data (ICC meas) bit[0]
   V0067    0   0   0   X   1   0   // SCL↑ (compare=X)
   V0068    0   0   0   X   0   0   // SCL↓
   V0069    0   0   0   1   0   0   // NACK from master
   V0070    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0071    0   0   0   1   0   0   // SCL↓
   V0072    0   0   0   0   0   0   // STOP Setup
   V0073    0   0   0   0   1   0   // STOP (SCL↑)
   V0074    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0075    0   0   0   1   1   0   // ICC Read complete
   V0076    0   0   0   1   1   0 
  DC_ICC_W_START:
   V0077    0   0   0   1   1   0   // === DC ICC Write Test ===
   V0078    0   0   0   1   1   0   // === Byte Write: addr=0x00 data=0x55 ===
   V0079    0   0   0   1   1   0 
   V0080    0   0   0   1   1   0   // START Setup
   V0081    0   0   0   0   1   0   // START Condition (SDA↓)
   V0082    0   0   0   0   0   0   // START Hold
   V0083    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0084    0   0   0   1   1   0   // SCL↑ (data valid)
   V0085    0   0   0   1   0   0   // SCL↓
   V0086    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0087    0   0   0   0   1   0   // SCL↑ (data valid)
   V0088    0   0   0   0   0   0   // SCL↓
   V0089    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0090    0   0   0   1   1   0   // SCL↑ (data valid)
   V0091    0   0   0   1   0   0   // SCL↓
   V0092    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0093    0   0   0   0   1   0   // SCL↑ (data valid)
   V0094    0   0   0   0   0   0   // SCL↓
   V0095    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0096    0   0   0   0   1   0   // SCL↑ (data valid)
   V0097    0   0   0   0   0   0   // SCL↓
   V0098    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0099    0   0   0   0   1   0   // SCL↑ (data valid)
   V0100    0   0   0   0   0   0   // SCL↓
   V0101    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0102    0   0   0   0   1   0   // SCL↑ (data valid)
   V0103    0   0   0   0   0   0   // SCL↓
   V0104    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0105    0   0   0   0   1   0   // SCL↑ (data valid)
   V0106    0   0   0   0   0   0   // SCL↓
   V0107    0   0   0   Z   0   0   // ACK after DevAddr
   V0108    0   0   0   L   1   0   // ACK check (expect LOW)
   V0109    0   0   0   X   0   0   // SCL↓
   V0110    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0111    0   0   0   0   1   0   // SCL↑ (data valid)
   V0112    0   0   0   0   0   0   // SCL↓
   V0113    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0114    0   0   0   0   1   0   // SCL↑ (data valid)
   V0115    0   0   0   0   0   0   // SCL↓
   V0116    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0117    0   0   0   0   1   0   // SCL↑ (data valid)
   V0118    0   0   0   0   0   0   // SCL↓
   V0119    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0120    0   0   0   0   1   0   // SCL↑ (data valid)
   V0121    0   0   0   0   0   0   // SCL↓
   V0122    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0123    0   0   0   0   1   0   // SCL↑ (data valid)
   V0124    0   0   0   0   0   0   // SCL↓
   V0125    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0126    0   0   0   0   1   0   // SCL↑ (data valid)
   V0127    0   0   0   0   0   0   // SCL↓
   V0128    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0129    0   0   0   0   1   0   // SCL↑ (data valid)
   V0130    0   0   0   0   0   0   // SCL↓
   V0131    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0132    0   0   0   0   1   0   // SCL↑ (data valid)
   V0133    0   0   0   0   0   0   // SCL↓
   V0134    0   0   0   Z   0   0   // ACK after WordAddr
   V0135    0   0   0   L   1   0   // ACK check (expect LOW)
   V0136    0   0   0   X   0   0   // SCL↓
   V0137    0   0   0   0   0   0   // Write bit=0 Data bit[7]
   V0138    0   0   0   0   1   0   // SCL↑ (data valid)
   V0139    0   0   0   0   0   0   // SCL↓
   V0140    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V0141    0   0   0   1   1   0   // SCL↑ (data valid)
   V0142    0   0   0   1   0   0   // SCL↓
   V0143    0   0   0   0   0   0   // Write bit=0 Data bit[5]
   V0144    0   0   0   0   1   0   // SCL↑ (data valid)
   V0145    0   0   0   0   0   0   // SCL↓
   V0146    0   0   0   1   0   0   // Write bit=1 Data bit[4]
   V0147    0   0   0   1   1   0   // SCL↑ (data valid)
   V0148    0   0   0   1   0   0   // SCL↓
   V0149    0   0   0   0   0   0   // Write bit=0 Data bit[3]
   V0150    0   0   0   0   1   0   // SCL↑ (data valid)
   V0151    0   0   0   0   0   0   // SCL↓
   V0152    0   0   0   1   0   0   // Write bit=1 Data bit[2]
   V0153    0   0   0   1   1   0   // SCL↑ (data valid)
   V0154    0   0   0   1   0   0   // SCL↓
   V0155    0   0   0   0   0   0   // Write bit=0 Data bit[1]
   V0156    0   0   0   0   1   0   // SCL↑ (data valid)
   V0157    0   0   0   0   0   0   // SCL↓
   V0158    0   0   0   1   0   0   // Write bit=1 Data bit[0]
   V0159    0   0   0   1   1   0   // SCL↑ (data valid)
   V0160    0   0   0   1   0   0   // SCL↓
   V0161    0   0   0   Z   0   0   // ACK after Data
   V0162    0   0   0   L   1   0   // ACK check (expect LOW)
   V0163    0   0   0   X   0   0   // SCL↓
   V0164    0   0   0   0   0   0   // STOP Setup
   V0165    0   0   0   0   1   0   // STOP (SCL↑)
   V0166    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0167    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0168    0   0   0   1   1   0 
   V0169    0   0   0   1   1   0 
   V0170    0   0   0   1   1   0 
   V0171    0   0   0   1   1   0 
   V0172    0   0   0   1   1   0 
   V0173    0   0   0   1   1   0 
   V0174    0   0   0   1   1   0 
   V0175    0   0   0   1   1   0 
   V0176    0   0   0   1   1   0 
  DC_VOL_START:
   V0177    0   0   0   1   1   0   // === DC VOL Test (SDA output LOW during ACK) ===
   V0178    0   0   0   1   1   0   // START Setup
   V0179    0   0   0   0   1   0   // START Condition (SDA↓)
   V0180    0   0   0   0   0   0   // START Hold
   V0181    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0182    0   0   0   1   1   0   // SCL↑ (data valid)
   V0183    0   0   0   1   0   0   // SCL↓
   V0184    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0185    0   0   0   0   1   0   // SCL↑ (data valid)
   V0186    0   0   0   0   0   0   // SCL↓
   V0187    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0188    0   0   0   1   1   0   // SCL↑ (data valid)
   V0189    0   0   0   1   0   0   // SCL↓
   V0190    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0191    0   0   0   0   1   0   // SCL↑ (data valid)
   V0192    0   0   0   0   0   0   // SCL↓
   V0193    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0194    0   0   0   0   1   0   // SCL↑ (data valid)
   V0195    0   0   0   0   0   0   // SCL↓
   V0196    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0197    0   0   0   0   1   0   // SCL↑ (data valid)
   V0198    0   0   0   0   0   0   // SCL↓
   V0199    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0200    0   0   0   0   1   0   // SCL↑ (data valid)
   V0201    0   0   0   0   0   0   // SCL↓
   V0202    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0203    0   0   0   0   1   0   // SCL↑ (data valid)
   V0204    0   0   0   0   0   0   // SCL↓
   V0205    0   0   0   Z   0   0   // *** VOL measurement point (ACK=LOW) ***
   V0206    0   0   0   L   1   0   // ACK check (expect LOW)
   V0207    0   0   0   X   0   0   // SCL↓
   V0208    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[7]
   V0209    0   0   0   0   1   0   // SCL↑ (data valid)
   V0210    0   0   0   0   0   0   // SCL↓
   V0211    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[6]
   V0212    0   0   0   0   1   0   // SCL↑ (data valid)
   V0213    0   0   0   0   0   0   // SCL↓
   V0214    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[5]
   V0215    0   0   0   0   1   0   // SCL↑ (data valid)
   V0216    0   0   0   0   0   0   // SCL↓
   V0217    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[4]
   V0218    0   0   0   0   1   0   // SCL↑ (data valid)
   V0219    0   0   0   0   0   0   // SCL↓
   V0220    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[3]
   V0221    0   0   0   0   1   0   // SCL↑ (data valid)
   V0222    0   0   0   0   0   0   // SCL↓
   V0223    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[2]
   V0224    0   0   0   0   1   0   // SCL↑ (data valid)
   V0225    0   0   0   0   0   0   // SCL↓
   V0226    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[1]
   V0227    0   0   0   0   1   0   // SCL↑ (data valid)
   V0228    0   0   0   0   0   0   // SCL↓
   V0229    0   0   0   0   0   0   // Write bit=0 WordAddr=0x00 bit[0]
   V0230    0   0   0   0   1   0   // SCL↑ (data valid)
   V0231    0   0   0   0   0   0   // SCL↓
   V0232    0   0   0   Z   0   0   // VOL meas point 2
   V0233    0   0   0   L   1   0   // ACK check (expect LOW)
   V0234    0   0   0   X   0   0   // SCL↓
   V0235    0   0   0   0   0   0   // STOP Setup
   V0236    0   0   0   0   1   0   // STOP (SCL↑)
   V0237    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0238    0   0   0   1   1   0   // IDLE
   V0239    0   0   0   1   1   0 
  DC_VOH_START:
   V0240    0   0   0   1   1   0   // === DC VOH Test (SDA output HIGH during Read) ===
   V0241    0   0   0   1   1   0   // === Byte Write: addr=0x10 data=0xFF ===
   V0242    0   0   0   1   1   0 
   V0243    0   0   0   1   1   0   // START Setup
   V0244    0   0   0   0   1   0   // START Condition (SDA↓)
   V0245    0   0   0   0   0   0   // START Hold
   V0246    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0247    0   0   0   1   1   0   // SCL↑ (data valid)
   V0248    0   0   0   1   0   0   // SCL↓
   V0249    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0250    0   0   0   0   1   0   // SCL↑ (data valid)
   V0251    0   0   0   0   0   0   // SCL↓
   V0252    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0253    0   0   0   1   1   0   // SCL↑ (data valid)
   V0254    0   0   0   1   0   0   // SCL↓
   V0255    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0256    0   0   0   0   1   0   // SCL↑ (data valid)
   V0257    0   0   0   0   0   0   // SCL↓
   V0258    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0259    0   0   0   0   1   0   // SCL↑ (data valid)
   V0260    0   0   0   0   0   0   // SCL↓
   V0261    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0262    0   0   0   0   1   0   // SCL↑ (data valid)
   V0263    0   0   0   0   0   0   // SCL↓
   V0264    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0265    0   0   0   0   1   0   // SCL↑ (data valid)
   V0266    0   0   0   0   0   0   // SCL↓
   V0267    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0268    0   0   0   0   1   0   // SCL↑ (data valid)
   V0269    0   0   0   0   0   0   // SCL↓
   V0270    0   0   0   Z   0   0   // ACK after DevAddr
   V0271    0   0   0   L   1   0   // ACK check (expect LOW)
   V0272    0   0   0   X   0   0   // SCL↓
   V0273    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0274    0   0   0   0   1   0   // SCL↑ (data valid)
   V0275    0   0   0   0   0   0   // SCL↓
   V0276    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0277    0   0   0   0   1   0   // SCL↑ (data valid)
   V0278    0   0   0   0   0   0   // SCL↓
   V0279    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0280    0   0   0   0   1   0   // SCL↑ (data valid)
   V0281    0   0   0   0   0   0   // SCL↓
   V0282    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V0283    0   0   0   1   1   0   // SCL↑ (data valid)
   V0284    0   0   0   1   0   0   // SCL↓
   V0285    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0286    0   0   0   0   1   0   // SCL↑ (data valid)
   V0287    0   0   0   0   0   0   // SCL↓
   V0288    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0289    0   0   0   0   1   0   // SCL↑ (data valid)
   V0290    0   0   0   0   0   0   // SCL↓
   V0291    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0292    0   0   0   0   1   0   // SCL↑ (data valid)
   V0293    0   0   0   0   0   0   // SCL↓
   V0294    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0295    0   0   0   0   1   0   // SCL↑ (data valid)
   V0296    0   0   0   0   0   0   // SCL↓
   V0297    0   0   0   Z   0   0   // ACK after WordAddr
   V0298    0   0   0   L   1   0   // ACK check (expect LOW)
   V0299    0   0   0   X   0   0   // SCL↓
   V0300    0   0   0   1   0   0   // Write bit=1 Data bit[7]
   V0301    0   0   0   1   1   0   // SCL↑ (data valid)
   V0302    0   0   0   1   0   0   // SCL↓
   V0303    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V0304    0   0   0   1   1   0   // SCL↑ (data valid)
   V0305    0   0   0   1   0   0   // SCL↓
   V0306    0   0   0   1   0   0   // Write bit=1 Data bit[5]
   V0307    0   0   0   1   1   0   // SCL↑ (data valid)
   V0308    0   0   0   1   0   0   // SCL↓
   V0309    0   0   0   1   0   0   // Write bit=1 Data bit[4]
   V0310    0   0   0   1   1   0   // SCL↑ (data valid)
   V0311    0   0   0   1   0   0   // SCL↓
   V0312    0   0   0   1   0   0   // Write bit=1 Data bit[3]
   V0313    0   0   0   1   1   0   // SCL↑ (data valid)
   V0314    0   0   0   1   0   0   // SCL↓
   V0315    0   0   0   1   0   0   // Write bit=1 Data bit[2]
   V0316    0   0   0   1   1   0   // SCL↑ (data valid)
   V0317    0   0   0   1   0   0   // SCL↓
   V0318    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V0319    0   0   0   1   1   0   // SCL↑ (data valid)
   V0320    0   0   0   1   0   0   // SCL↓
   V0321    0   0   0   1   0   0   // Write bit=1 Data bit[0]
   V0322    0   0   0   1   1   0   // SCL↑ (data valid)
   V0323    0   0   0   1   0   0   // SCL↓
   V0324    0   0   0   Z   0   0   // ACK after Data
   V0325    0   0   0   L   1   0   // ACK check (expect LOW)
   V0326    0   0   0   X   0   0   // SCL↓
   V0327    0   0   0   0   0   0   // STOP Setup
   V0328    0   0   0   0   1   0   // STOP (SCL↑)
   V0329    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0330    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0331    0   0   0   1   1   0 
   V0332    0   0   0   1   1   0 
   V0333    0   0   0   1   1   0 
   V0334    0   0   0   1   1   0 
   V0335    0   0   0   1   1   0 
   V0336    0   0   0   1   1   0 
   V0337    0   0   0   1   1   0 
   V0338    0   0   0   1   1   0 
   V0339    0   0   0   1   1   0 
   V0340    0   0   0   1   1   0   // === Random Read: addr=0x10 ===
   V0341    0   0   0   1   1   0 
   V0342    0   0   0   1   1   0   // START Setup
   V0343    0   0   0   0   1   0   // START Condition (SDA↓)
   V0344    0   0   0   0   0   0   // START Hold
   V0345    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0346    0   0   0   1   1   0   // SCL↑ (data valid)
   V0347    0   0   0   1   0   0   // SCL↓
   V0348    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0349    0   0   0   0   1   0   // SCL↑ (data valid)
   V0350    0   0   0   0   0   0   // SCL↓
   V0351    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0352    0   0   0   1   1   0   // SCL↑ (data valid)
   V0353    0   0   0   1   0   0   // SCL↓
   V0354    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0355    0   0   0   0   1   0   // SCL↑ (data valid)
   V0356    0   0   0   0   0   0   // SCL↓
   V0357    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0358    0   0   0   0   1   0   // SCL↑ (data valid)
   V0359    0   0   0   0   0   0   // SCL↓
   V0360    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0361    0   0   0   0   1   0   // SCL↑ (data valid)
   V0362    0   0   0   0   0   0   // SCL↓
   V0363    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0364    0   0   0   0   1   0   // SCL↑ (data valid)
   V0365    0   0   0   0   0   0   // SCL↓
   V0366    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0367    0   0   0   0   1   0   // SCL↑ (data valid)
   V0368    0   0   0   0   0   0   // SCL↓
   V0369    0   0   0   Z   0   0   // ACK after DevAddr
   V0370    0   0   0   L   1   0   // ACK check (expect LOW)
   V0371    0   0   0   X   0   0   // SCL↓
   V0372    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0373    0   0   0   0   1   0   // SCL↑ (data valid)
   V0374    0   0   0   0   0   0   // SCL↓
   V0375    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0376    0   0   0   0   1   0   // SCL↑ (data valid)
   V0377    0   0   0   0   0   0   // SCL↓
   V0378    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0379    0   0   0   0   1   0   // SCL↑ (data valid)
   V0380    0   0   0   0   0   0   // SCL↓
   V0381    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V0382    0   0   0   1   1   0   // SCL↑ (data valid)
   V0383    0   0   0   1   0   0   // SCL↓
   V0384    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0385    0   0   0   0   1   0   // SCL↑ (data valid)
   V0386    0   0   0   0   0   0   // SCL↓
   V0387    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0388    0   0   0   0   1   0   // SCL↑ (data valid)
   V0389    0   0   0   0   0   0   // SCL↓
   V0390    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0391    0   0   0   0   1   0   // SCL↑ (data valid)
   V0392    0   0   0   0   0   0   // SCL↓
   V0393    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0394    0   0   0   0   1   0   // SCL↑ (data valid)
   V0395    0   0   0   0   0   0   // SCL↓
   V0396    0   0   0   Z   0   0   // ACK after WordAddr
   V0397    0   0   0   L   1   0   // ACK check (expect LOW)
   V0398    0   0   0   X   0   0   // SCL↓
   V0399    0   0   0   1   0   0   // RepSTART: SDA↑
   V0400    0   0   0   1   1   0   // RepSTART: SCL↑
   V0401    0   0   0   0   1   0   // RepSTART: SDA↓
   V0402    0   0   0   0   0   0   // RepSTART: SCL↓
   V0403    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0404    0   0   0   1   1   0   // SCL↑ (data valid)
   V0405    0   0   0   1   0   0   // SCL↓
   V0406    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0407    0   0   0   0   1   0   // SCL↑ (data valid)
   V0408    0   0   0   0   0   0   // SCL↓
   V0409    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0410    0   0   0   1   1   0   // SCL↑ (data valid)
   V0411    0   0   0   1   0   0   // SCL↓
   V0412    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0413    0   0   0   0   1   0   // SCL↑ (data valid)
   V0414    0   0   0   0   0   0   // SCL↓
   V0415    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0416    0   0   0   0   1   0   // SCL↑ (data valid)
   V0417    0   0   0   0   0   0   // SCL↓
   V0418    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0419    0   0   0   0   1   0   // SCL↑ (data valid)
   V0420    0   0   0   0   0   0   // SCL↓
   V0421    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0422    0   0   0   0   1   0   // SCL↑ (data valid)
   V0423    0   0   0   0   0   0   // SCL↓
   V0424    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0425    0   0   0   1   1   0   // SCL↑ (data valid)
   V0426    0   0   0   1   0   0   // SCL↓
   V0427    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0428    0   0   0   L   1   0   // ACK check (expect LOW)
   V0429    0   0   0   X   0   0   // SCL↓
   V0430    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0431    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0432    0   0   0   X   0   0   // SCL↓
   V0433    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0434    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0435    0   0   0   X   0   0   // SCL↓
   V0436    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0437    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0438    0   0   0   X   0   0   // SCL↓
   V0439    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0440    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0441    0   0   0   X   0   0   // SCL↓
   V0442    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0443    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0444    0   0   0   X   0   0   // SCL↓
   V0445    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0446    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0447    0   0   0   X   0   0   // SCL↓
   V0448    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0449    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0450    0   0   0   X   0   0   // SCL↓
   V0451    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0452    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0453    0   0   0   X   0   0   // SCL↓
   V0454    0   0   0   1   0   0   // NACK (end read)
   V0455    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0456    0   0   0   1   0   0   // SCL↓
   V0457    0   0   0   0   0   0   // STOP Setup
   V0458    0   0   0   0   1   0   // STOP (SCL↑)
   V0459    0   0   0   1   1   0   // STOP Condition (SDA↑)
  DC_VIL_VIH_START:
   V0460    0   0   0   1   1   0   // === DC Input Threshold Test (VIL/VIH) ===
   V0461    0   0   0   1   1   0   // === Byte Write: addr=0x20 data=0xAA ===
   V0462    0   0   0   1   1   0 
   V0463    0   0   0   1   1   0   // START Setup
   V0464    0   0   0   0   1   0   // START Condition (SDA↓)
   V0465    0   0   0   0   0   0   // START Hold
   V0466    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0467    0   0   0   1   1   0   // SCL↑ (data valid)
   V0468    0   0   0   1   0   0   // SCL↓
   V0469    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0470    0   0   0   0   1   0   // SCL↑ (data valid)
   V0471    0   0   0   0   0   0   // SCL↓
   V0472    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0473    0   0   0   1   1   0   // SCL↑ (data valid)
   V0474    0   0   0   1   0   0   // SCL↓
   V0475    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0476    0   0   0   0   1   0   // SCL↑ (data valid)
   V0477    0   0   0   0   0   0   // SCL↓
   V0478    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0479    0   0   0   0   1   0   // SCL↑ (data valid)
   V0480    0   0   0   0   0   0   // SCL↓
   V0481    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0482    0   0   0   0   1   0   // SCL↑ (data valid)
   V0483    0   0   0   0   0   0   // SCL↓
   V0484    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0485    0   0   0   0   1   0   // SCL↑ (data valid)
   V0486    0   0   0   0   0   0   // SCL↓
   V0487    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0488    0   0   0   0   1   0   // SCL↑ (data valid)
   V0489    0   0   0   0   0   0   // SCL↓
   V0490    0   0   0   Z   0   0   // ACK after DevAddr
   V0491    0   0   0   L   1   0   // ACK check (expect LOW)
   V0492    0   0   0   X   0   0   // SCL↓
   V0493    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0494    0   0   0   0   1   0   // SCL↑ (data valid)
   V0495    0   0   0   0   0   0   // SCL↓
   V0496    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0497    0   0   0   0   1   0   // SCL↑ (data valid)
   V0498    0   0   0   0   0   0   // SCL↓
   V0499    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V0500    0   0   0   1   1   0   // SCL↑ (data valid)
   V0501    0   0   0   1   0   0   // SCL↓
   V0502    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0503    0   0   0   0   1   0   // SCL↑ (data valid)
   V0504    0   0   0   0   0   0   // SCL↓
   V0505    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0506    0   0   0   0   1   0   // SCL↑ (data valid)
   V0507    0   0   0   0   0   0   // SCL↓
   V0508    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0509    0   0   0   0   1   0   // SCL↑ (data valid)
   V0510    0   0   0   0   0   0   // SCL↓
   V0511    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0512    0   0   0   0   1   0   // SCL↑ (data valid)
   V0513    0   0   0   0   0   0   // SCL↓
   V0514    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0515    0   0   0   0   1   0   // SCL↑ (data valid)
   V0516    0   0   0   0   0   0   // SCL↓
   V0517    0   0   0   Z   0   0   // ACK after WordAddr
   V0518    0   0   0   L   1   0   // ACK check (expect LOW)
   V0519    0   0   0   X   0   0   // SCL↓
   V0520    0   0   0   1   0   0   // Write bit=1 Data bit[7]
   V0521    0   0   0   1   1   0   // SCL↑ (data valid)
   V0522    0   0   0   1   0   0   // SCL↓
   V0523    0   0   0   0   0   0   // Write bit=0 Data bit[6]
   V0524    0   0   0   0   1   0   // SCL↑ (data valid)
   V0525    0   0   0   0   0   0   // SCL↓
   V0526    0   0   0   1   0   0   // Write bit=1 Data bit[5]
   V0527    0   0   0   1   1   0   // SCL↑ (data valid)
   V0528    0   0   0   1   0   0   // SCL↓
   V0529    0   0   0   0   0   0   // Write bit=0 Data bit[4]
   V0530    0   0   0   0   1   0   // SCL↑ (data valid)
   V0531    0   0   0   0   0   0   // SCL↓
   V0532    0   0   0   1   0   0   // Write bit=1 Data bit[3]
   V0533    0   0   0   1   1   0   // SCL↑ (data valid)
   V0534    0   0   0   1   0   0   // SCL↓
   V0535    0   0   0   0   0   0   // Write bit=0 Data bit[2]
   V0536    0   0   0   0   1   0   // SCL↑ (data valid)
   V0537    0   0   0   0   0   0   // SCL↓
   V0538    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V0539    0   0   0   1   1   0   // SCL↑ (data valid)
   V0540    0   0   0   1   0   0   // SCL↓
   V0541    0   0   0   0   0   0   // Write bit=0 Data bit[0]
   V0542    0   0   0   0   1   0   // SCL↑ (data valid)
   V0543    0   0   0   0   0   0   // SCL↓
   V0544    0   0   0   Z   0   0   // ACK after Data
   V0545    0   0   0   L   1   0   // ACK check (expect LOW)
   V0546    0   0   0   X   0   0   // SCL↓
   V0547    0   0   0   0   0   0   // STOP Setup
   V0548    0   0   0   0   1   0   // STOP (SCL↑)
   V0549    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0550    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0551    0   0   0   1   1   0 
   V0552    0   0   0   1   1   0 
   V0553    0   0   0   1   1   0 
   V0554    0   0   0   1   1   0 
   V0555    0   0   0   1   1   0 
   V0556    0   0   0   1   1   0 
   V0557    0   0   0   1   1   0 
   V0558    0   0   0   1   1   0 
   V0559    0   0   0   1   1   0 
   V0560    0   0   0   1   1   0   // === Random Read: addr=0x20 ===
   V0561    0   0   0   1   1   0 
   V0562    0   0   0   1   1   0   // START Setup
   V0563    0   0   0   0   1   0   // START Condition (SDA↓)
   V0564    0   0   0   0   0   0   // START Hold
   V0565    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0566    0   0   0   1   1   0   // SCL↑ (data valid)
   V0567    0   0   0   1   0   0   // SCL↓
   V0568    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0569    0   0   0   0   1   0   // SCL↑ (data valid)
   V0570    0   0   0   0   0   0   // SCL↓
   V0571    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0572    0   0   0   1   1   0   // SCL↑ (data valid)
   V0573    0   0   0   1   0   0   // SCL↓
   V0574    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0575    0   0   0   0   1   0   // SCL↑ (data valid)
   V0576    0   0   0   0   0   0   // SCL↓
   V0577    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0578    0   0   0   0   1   0   // SCL↑ (data valid)
   V0579    0   0   0   0   0   0   // SCL↓
   V0580    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0581    0   0   0   0   1   0   // SCL↑ (data valid)
   V0582    0   0   0   0   0   0   // SCL↓
   V0583    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0584    0   0   0   0   1   0   // SCL↑ (data valid)
   V0585    0   0   0   0   0   0   // SCL↓
   V0586    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0587    0   0   0   0   1   0   // SCL↑ (data valid)
   V0588    0   0   0   0   0   0   // SCL↓
   V0589    0   0   0   Z   0   0   // ACK after DevAddr
   V0590    0   0   0   L   1   0   // ACK check (expect LOW)
   V0591    0   0   0   X   0   0   // SCL↓
   V0592    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0593    0   0   0   0   1   0   // SCL↑ (data valid)
   V0594    0   0   0   0   0   0   // SCL↓
   V0595    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0596    0   0   0   0   1   0   // SCL↑ (data valid)
   V0597    0   0   0   0   0   0   // SCL↓
   V0598    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V0599    0   0   0   1   1   0   // SCL↑ (data valid)
   V0600    0   0   0   1   0   0   // SCL↓
   V0601    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0602    0   0   0   0   1   0   // SCL↑ (data valid)
   V0603    0   0   0   0   0   0   // SCL↓
   V0604    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0605    0   0   0   0   1   0   // SCL↑ (data valid)
   V0606    0   0   0   0   0   0   // SCL↓
   V0607    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0608    0   0   0   0   1   0   // SCL↑ (data valid)
   V0609    0   0   0   0   0   0   // SCL↓
   V0610    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0611    0   0   0   0   1   0   // SCL↑ (data valid)
   V0612    0   0   0   0   0   0   // SCL↓
   V0613    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0614    0   0   0   0   1   0   // SCL↑ (data valid)
   V0615    0   0   0   0   0   0   // SCL↓
   V0616    0   0   0   Z   0   0   // ACK after WordAddr
   V0617    0   0   0   L   1   0   // ACK check (expect LOW)
   V0618    0   0   0   X   0   0   // SCL↓
   V0619    0   0   0   1   0   0   // RepSTART: SDA↑
   V0620    0   0   0   1   1   0   // RepSTART: SCL↑
   V0621    0   0   0   0   1   0   // RepSTART: SDA↓
   V0622    0   0   0   0   0   0   // RepSTART: SCL↓
   V0623    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0624    0   0   0   1   1   0   // SCL↑ (data valid)
   V0625    0   0   0   1   0   0   // SCL↓
   V0626    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0627    0   0   0   0   1   0   // SCL↑ (data valid)
   V0628    0   0   0   0   0   0   // SCL↓
   V0629    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0630    0   0   0   1   1   0   // SCL↑ (data valid)
   V0631    0   0   0   1   0   0   // SCL↓
   V0632    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0633    0   0   0   0   1   0   // SCL↑ (data valid)
   V0634    0   0   0   0   0   0   // SCL↓
   V0635    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0636    0   0   0   0   1   0   // SCL↑ (data valid)
   V0637    0   0   0   0   0   0   // SCL↓
   V0638    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0639    0   0   0   0   1   0   // SCL↑ (data valid)
   V0640    0   0   0   0   0   0   // SCL↓
   V0641    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0642    0   0   0   0   1   0   // SCL↑ (data valid)
   V0643    0   0   0   0   0   0   // SCL↓
   V0644    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0645    0   0   0   1   1   0   // SCL↑ (data valid)
   V0646    0   0   0   1   0   0   // SCL↓
   V0647    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0648    0   0   0   L   1   0   // ACK check (expect LOW)
   V0649    0   0   0   X   0   0   // SCL↓
   V0650    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0651    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0652    0   0   0   X   0   0   // SCL↓
   V0653    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0654    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0655    0   0   0   X   0   0   // SCL↓
   V0656    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0657    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0658    0   0   0   X   0   0   // SCL↓
   V0659    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0660    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0661    0   0   0   X   0   0   // SCL↓
   V0662    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0663    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0664    0   0   0   X   0   0   // SCL↓
   V0665    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0666    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0667    0   0   0   X   0   0   // SCL↓
   V0668    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0669    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0670    0   0   0   X   0   0   // SCL↓
   V0671    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0672    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0673    0   0   0   X   0   0   // SCL↓
   V0674    0   0   0   1   0   0   // NACK (end read)
   V0675    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0676    0   0   0   1   0   0   // SCL↓
   V0677    0   0   0   0   0   0   // STOP Setup
   V0678    0   0   0   0   1   0   // STOP (SCL↑)
   V0679    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0680    0   0   0   1   1   0   // === DC Test Complete ===
   V0681    0   0   0   1   1   0 
   V0682    0   0   0   1   1   0 
   V0683    0   0   0   1   1   0 

END_PATTERN // DC_TEST

// ============================================================
// I2C Functional Test
// ============================================================

PATTERN FUNC_TEST

// Vec#    A0   A1   A2  SDA  SCL   WP   // Comment
// ------------------------------------------------
  FUNC_BW_START:
   V0000    0   0   0   1   1   0   // === FUNC: Byte Write + Read Verify ===
   V0001    0   0   0   1   1   0   // === Byte Write: addr=0x00 data=0x55 ===
   V0002    0   0   0   1   1   0 
   V0003    0   0   0   1   1   0   // START Setup
   V0004    0   0   0   0   1   0   // START Condition (SDA↓)
   V0005    0   0   0   0   0   0   // START Hold
   V0006    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0007    0   0   0   1   1   0   // SCL↑ (data valid)
   V0008    0   0   0   1   0   0   // SCL↓
   V0009    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0010    0   0   0   0   1   0   // SCL↑ (data valid)
   V0011    0   0   0   0   0   0   // SCL↓
   V0012    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0013    0   0   0   1   1   0   // SCL↑ (data valid)
   V0014    0   0   0   1   0   0   // SCL↓
   V0015    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0016    0   0   0   0   1   0   // SCL↑ (data valid)
   V0017    0   0   0   0   0   0   // SCL↓
   V0018    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0019    0   0   0   0   1   0   // SCL↑ (data valid)
   V0020    0   0   0   0   0   0   // SCL↓
   V0021    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0022    0   0   0   0   1   0   // SCL↑ (data valid)
   V0023    0   0   0   0   0   0   // SCL↓
   V0024    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0025    0   0   0   0   1   0   // SCL↑ (data valid)
   V0026    0   0   0   0   0   0   // SCL↓
   V0027    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0028    0   0   0   0   1   0   // SCL↑ (data valid)
   V0029    0   0   0   0   0   0   // SCL↓
   V0030    0   0   0   Z   0   0   // ACK after DevAddr
   V0031    0   0   0   L   1   0   // ACK check (expect LOW)
   V0032    0   0   0   X   0   0   // SCL↓
   V0033    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0034    0   0   0   0   1   0   // SCL↑ (data valid)
   V0035    0   0   0   0   0   0   // SCL↓
   V0036    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0037    0   0   0   0   1   0   // SCL↑ (data valid)
   V0038    0   0   0   0   0   0   // SCL↓
   V0039    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0040    0   0   0   0   1   0   // SCL↑ (data valid)
   V0041    0   0   0   0   0   0   // SCL↓
   V0042    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0043    0   0   0   0   1   0   // SCL↑ (data valid)
   V0044    0   0   0   0   0   0   // SCL↓
   V0045    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0046    0   0   0   0   1   0   // SCL↑ (data valid)
   V0047    0   0   0   0   0   0   // SCL↓
   V0048    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0049    0   0   0   0   1   0   // SCL↑ (data valid)
   V0050    0   0   0   0   0   0   // SCL↓
   V0051    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0052    0   0   0   0   1   0   // SCL↑ (data valid)
   V0053    0   0   0   0   0   0   // SCL↓
   V0054    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0055    0   0   0   0   1   0   // SCL↑ (data valid)
   V0056    0   0   0   0   0   0   // SCL↓
   V0057    0   0   0   Z   0   0   // ACK after WordAddr
   V0058    0   0   0   L   1   0   // ACK check (expect LOW)
   V0059    0   0   0   X   0   0   // SCL↓
   V0060    0   0   0   0   0   0   // Write bit=0 Data bit[7]
   V0061    0   0   0   0   1   0   // SCL↑ (data valid)
   V0062    0   0   0   0   0   0   // SCL↓
   V0063    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V0064    0   0   0   1   1   0   // SCL↑ (data valid)
   V0065    0   0   0   1   0   0   // SCL↓
   V0066    0   0   0   0   0   0   // Write bit=0 Data bit[5]
   V0067    0   0   0   0   1   0   // SCL↑ (data valid)
   V0068    0   0   0   0   0   0   // SCL↓
   V0069    0   0   0   1   0   0   // Write bit=1 Data bit[4]
   V0070    0   0   0   1   1   0   // SCL↑ (data valid)
   V0071    0   0   0   1   0   0   // SCL↓
   V0072    0   0   0   0   0   0   // Write bit=0 Data bit[3]
   V0073    0   0   0   0   1   0   // SCL↑ (data valid)
   V0074    0   0   0   0   0   0   // SCL↓
   V0075    0   0   0   1   0   0   // Write bit=1 Data bit[2]
   V0076    0   0   0   1   1   0   // SCL↑ (data valid)
   V0077    0   0   0   1   0   0   // SCL↓
   V0078    0   0   0   0   0   0   // Write bit=0 Data bit[1]
   V0079    0   0   0   0   1   0   // SCL↑ (data valid)
   V0080    0   0   0   0   0   0   // SCL↓
   V0081    0   0   0   1   0   0   // Write bit=1 Data bit[0]
   V0082    0   0   0   1   1   0   // SCL↑ (data valid)
   V0083    0   0   0   1   0   0   // SCL↓
   V0084    0   0   0   Z   0   0   // ACK after Data
   V0085    0   0   0   L   1   0   // ACK check (expect LOW)
   V0086    0   0   0   X   0   0   // SCL↓
   V0087    0   0   0   0   0   0   // STOP Setup
   V0088    0   0   0   0   1   0   // STOP (SCL↑)
   V0089    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0090    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0091    0   0   0   1   1   0 
   V0092    0   0   0   1   1   0 
   V0093    0   0   0   1   1   0 
   V0094    0   0   0   1   1   0 
   V0095    0   0   0   1   1   0 
   V0096    0   0   0   1   1   0 
   V0097    0   0   0   1   1   0 
   V0098    0   0   0   1   1   0 
   V0099    0   0   0   1   1   0 
   V0100    0   0   0   1   1   0   // === Random Read: addr=0x00 ===
   V0101    0   0   0   1   1   0 
   V0102    0   0   0   1   1   0   // START Setup
   V0103    0   0   0   0   1   0   // START Condition (SDA↓)
   V0104    0   0   0   0   0   0   // START Hold
   V0105    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0106    0   0   0   1   1   0   // SCL↑ (data valid)
   V0107    0   0   0   1   0   0   // SCL↓
   V0108    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0109    0   0   0   0   1   0   // SCL↑ (data valid)
   V0110    0   0   0   0   0   0   // SCL↓
   V0111    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0112    0   0   0   1   1   0   // SCL↑ (data valid)
   V0113    0   0   0   1   0   0   // SCL↓
   V0114    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0115    0   0   0   0   1   0   // SCL↑ (data valid)
   V0116    0   0   0   0   0   0   // SCL↓
   V0117    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0118    0   0   0   0   1   0   // SCL↑ (data valid)
   V0119    0   0   0   0   0   0   // SCL↓
   V0120    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0121    0   0   0   0   1   0   // SCL↑ (data valid)
   V0122    0   0   0   0   0   0   // SCL↓
   V0123    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0124    0   0   0   0   1   0   // SCL↑ (data valid)
   V0125    0   0   0   0   0   0   // SCL↓
   V0126    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0127    0   0   0   0   1   0   // SCL↑ (data valid)
   V0128    0   0   0   0   0   0   // SCL↓
   V0129    0   0   0   Z   0   0   // ACK after DevAddr
   V0130    0   0   0   L   1   0   // ACK check (expect LOW)
   V0131    0   0   0   X   0   0   // SCL↓
   V0132    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0133    0   0   0   0   1   0   // SCL↑ (data valid)
   V0134    0   0   0   0   0   0   // SCL↓
   V0135    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0136    0   0   0   0   1   0   // SCL↑ (data valid)
   V0137    0   0   0   0   0   0   // SCL↓
   V0138    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0139    0   0   0   0   1   0   // SCL↑ (data valid)
   V0140    0   0   0   0   0   0   // SCL↓
   V0141    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0142    0   0   0   0   1   0   // SCL↑ (data valid)
   V0143    0   0   0   0   0   0   // SCL↓
   V0144    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0145    0   0   0   0   1   0   // SCL↑ (data valid)
   V0146    0   0   0   0   0   0   // SCL↓
   V0147    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0148    0   0   0   0   1   0   // SCL↑ (data valid)
   V0149    0   0   0   0   0   0   // SCL↓
   V0150    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0151    0   0   0   0   1   0   // SCL↑ (data valid)
   V0152    0   0   0   0   0   0   // SCL↓
   V0153    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0154    0   0   0   0   1   0   // SCL↑ (data valid)
   V0155    0   0   0   0   0   0   // SCL↓
   V0156    0   0   0   Z   0   0   // ACK after WordAddr
   V0157    0   0   0   L   1   0   // ACK check (expect LOW)
   V0158    0   0   0   X   0   0   // SCL↓
   V0159    0   0   0   1   0   0   // RepSTART: SDA↑
   V0160    0   0   0   1   1   0   // RepSTART: SCL↑
   V0161    0   0   0   0   1   0   // RepSTART: SDA↓
   V0162    0   0   0   0   0   0   // RepSTART: SCL↓
   V0163    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0164    0   0   0   1   1   0   // SCL↑ (data valid)
   V0165    0   0   0   1   0   0   // SCL↓
   V0166    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0167    0   0   0   0   1   0   // SCL↑ (data valid)
   V0168    0   0   0   0   0   0   // SCL↓
   V0169    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0170    0   0   0   1   1   0   // SCL↑ (data valid)
   V0171    0   0   0   1   0   0   // SCL↓
   V0172    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0173    0   0   0   0   1   0   // SCL↑ (data valid)
   V0174    0   0   0   0   0   0   // SCL↓
   V0175    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0176    0   0   0   0   1   0   // SCL↑ (data valid)
   V0177    0   0   0   0   0   0   // SCL↓
   V0178    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0179    0   0   0   0   1   0   // SCL↑ (data valid)
   V0180    0   0   0   0   0   0   // SCL↓
   V0181    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0182    0   0   0   0   1   0   // SCL↑ (data valid)
   V0183    0   0   0   0   0   0   // SCL↓
   V0184    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0185    0   0   0   1   1   0   // SCL↑ (data valid)
   V0186    0   0   0   1   0   0   // SCL↓
   V0187    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0188    0   0   0   L   1   0   // ACK check (expect LOW)
   V0189    0   0   0   X   0   0   // SCL↓
   V0190    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0191    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0192    0   0   0   X   0   0   // SCL↓
   V0193    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0194    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0195    0   0   0   X   0   0   // SCL↓
   V0196    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0197    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0198    0   0   0   X   0   0   // SCL↓
   V0199    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0200    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0201    0   0   0   X   0   0   // SCL↓
   V0202    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0203    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0204    0   0   0   X   0   0   // SCL↓
   V0205    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0206    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0207    0   0   0   X   0   0   // SCL↓
   V0208    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0209    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0210    0   0   0   X   0   0   // SCL↓
   V0211    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0212    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0213    0   0   0   X   0   0   // SCL↓
   V0214    0   0   0   1   0   0   // NACK (end read)
   V0215    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0216    0   0   0   1   0   0   // SCL↓
   V0217    0   0   0   0   0   0   // STOP Setup
   V0218    0   0   0   0   1   0   // STOP (SCL↑)
   V0219    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0220    0   0   0   1   1   0   // === Byte Write: addr=0x01 data=0xAA ===
   V0221    0   0   0   1   1   0 
   V0222    0   0   0   1   1   0   // START Setup
   V0223    0   0   0   0   1   0   // START Condition (SDA↓)
   V0224    0   0   0   0   0   0   // START Hold
   V0225    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0226    0   0   0   1   1   0   // SCL↑ (data valid)
   V0227    0   0   0   1   0   0   // SCL↓
   V0228    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0229    0   0   0   0   1   0   // SCL↑ (data valid)
   V0230    0   0   0   0   0   0   // SCL↓
   V0231    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0232    0   0   0   1   1   0   // SCL↑ (data valid)
   V0233    0   0   0   1   0   0   // SCL↓
   V0234    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0235    0   0   0   0   1   0   // SCL↑ (data valid)
   V0236    0   0   0   0   0   0   // SCL↓
   V0237    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0238    0   0   0   0   1   0   // SCL↑ (data valid)
   V0239    0   0   0   0   0   0   // SCL↓
   V0240    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0241    0   0   0   0   1   0   // SCL↑ (data valid)
   V0242    0   0   0   0   0   0   // SCL↓
   V0243    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0244    0   0   0   0   1   0   // SCL↑ (data valid)
   V0245    0   0   0   0   0   0   // SCL↓
   V0246    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0247    0   0   0   0   1   0   // SCL↑ (data valid)
   V0248    0   0   0   0   0   0   // SCL↓
   V0249    0   0   0   Z   0   0   // ACK after DevAddr
   V0250    0   0   0   L   1   0   // ACK check (expect LOW)
   V0251    0   0   0   X   0   0   // SCL↓
   V0252    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0253    0   0   0   0   1   0   // SCL↑ (data valid)
   V0254    0   0   0   0   0   0   // SCL↓
   V0255    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0256    0   0   0   0   1   0   // SCL↑ (data valid)
   V0257    0   0   0   0   0   0   // SCL↓
   V0258    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0259    0   0   0   0   1   0   // SCL↑ (data valid)
   V0260    0   0   0   0   0   0   // SCL↓
   V0261    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0262    0   0   0   0   1   0   // SCL↑ (data valid)
   V0263    0   0   0   0   0   0   // SCL↓
   V0264    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0265    0   0   0   0   1   0   // SCL↑ (data valid)
   V0266    0   0   0   0   0   0   // SCL↓
   V0267    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0268    0   0   0   0   1   0   // SCL↑ (data valid)
   V0269    0   0   0   0   0   0   // SCL↓
   V0270    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0271    0   0   0   0   1   0   // SCL↑ (data valid)
   V0272    0   0   0   0   0   0   // SCL↓
   V0273    0   0   0   1   0   0   // Write bit=1 WordAddr bit[0]
   V0274    0   0   0   1   1   0   // SCL↑ (data valid)
   V0275    0   0   0   1   0   0   // SCL↓
   V0276    0   0   0   Z   0   0   // ACK after WordAddr
   V0277    0   0   0   L   1   0   // ACK check (expect LOW)
   V0278    0   0   0   X   0   0   // SCL↓
   V0279    0   0   0   1   0   0   // Write bit=1 Data bit[7]
   V0280    0   0   0   1   1   0   // SCL↑ (data valid)
   V0281    0   0   0   1   0   0   // SCL↓
   V0282    0   0   0   0   0   0   // Write bit=0 Data bit[6]
   V0283    0   0   0   0   1   0   // SCL↑ (data valid)
   V0284    0   0   0   0   0   0   // SCL↓
   V0285    0   0   0   1   0   0   // Write bit=1 Data bit[5]
   V0286    0   0   0   1   1   0   // SCL↑ (data valid)
   V0287    0   0   0   1   0   0   // SCL↓
   V0288    0   0   0   0   0   0   // Write bit=0 Data bit[4]
   V0289    0   0   0   0   1   0   // SCL↑ (data valid)
   V0290    0   0   0   0   0   0   // SCL↓
   V0291    0   0   0   1   0   0   // Write bit=1 Data bit[3]
   V0292    0   0   0   1   1   0   // SCL↑ (data valid)
   V0293    0   0   0   1   0   0   // SCL↓
   V0294    0   0   0   0   0   0   // Write bit=0 Data bit[2]
   V0295    0   0   0   0   1   0   // SCL↑ (data valid)
   V0296    0   0   0   0   0   0   // SCL↓
   V0297    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V0298    0   0   0   1   1   0   // SCL↑ (data valid)
   V0299    0   0   0   1   0   0   // SCL↓
   V0300    0   0   0   0   0   0   // Write bit=0 Data bit[0]
   V0301    0   0   0   0   1   0   // SCL↑ (data valid)
   V0302    0   0   0   0   0   0   // SCL↓
   V0303    0   0   0   Z   0   0   // ACK after Data
   V0304    0   0   0   L   1   0   // ACK check (expect LOW)
   V0305    0   0   0   X   0   0   // SCL↓
   V0306    0   0   0   0   0   0   // STOP Setup
   V0307    0   0   0   0   1   0   // STOP (SCL↑)
   V0308    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0309    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0310    0   0   0   1   1   0 
   V0311    0   0   0   1   1   0 
   V0312    0   0   0   1   1   0 
   V0313    0   0   0   1   1   0 
   V0314    0   0   0   1   1   0 
   V0315    0   0   0   1   1   0 
   V0316    0   0   0   1   1   0 
   V0317    0   0   0   1   1   0 
   V0318    0   0   0   1   1   0 
   V0319    0   0   0   1   1   0   // === Random Read: addr=0x01 ===
   V0320    0   0   0   1   1   0 
   V0321    0   0   0   1   1   0   // START Setup
   V0322    0   0   0   0   1   0   // START Condition (SDA↓)
   V0323    0   0   0   0   0   0   // START Hold
   V0324    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0325    0   0   0   1   1   0   // SCL↑ (data valid)
   V0326    0   0   0   1   0   0   // SCL↓
   V0327    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0328    0   0   0   0   1   0   // SCL↑ (data valid)
   V0329    0   0   0   0   0   0   // SCL↓
   V0330    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0331    0   0   0   1   1   0   // SCL↑ (data valid)
   V0332    0   0   0   1   0   0   // SCL↓
   V0333    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0334    0   0   0   0   1   0   // SCL↑ (data valid)
   V0335    0   0   0   0   0   0   // SCL↓
   V0336    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0337    0   0   0   0   1   0   // SCL↑ (data valid)
   V0338    0   0   0   0   0   0   // SCL↓
   V0339    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0340    0   0   0   0   1   0   // SCL↑ (data valid)
   V0341    0   0   0   0   0   0   // SCL↓
   V0342    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0343    0   0   0   0   1   0   // SCL↑ (data valid)
   V0344    0   0   0   0   0   0   // SCL↓
   V0345    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0346    0   0   0   0   1   0   // SCL↑ (data valid)
   V0347    0   0   0   0   0   0   // SCL↓
   V0348    0   0   0   Z   0   0   // ACK after DevAddr
   V0349    0   0   0   L   1   0   // ACK check (expect LOW)
   V0350    0   0   0   X   0   0   // SCL↓
   V0351    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0352    0   0   0   0   1   0   // SCL↑ (data valid)
   V0353    0   0   0   0   0   0   // SCL↓
   V0354    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0355    0   0   0   0   1   0   // SCL↑ (data valid)
   V0356    0   0   0   0   0   0   // SCL↓
   V0357    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0358    0   0   0   0   1   0   // SCL↑ (data valid)
   V0359    0   0   0   0   0   0   // SCL↓
   V0360    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0361    0   0   0   0   1   0   // SCL↑ (data valid)
   V0362    0   0   0   0   0   0   // SCL↓
   V0363    0   0   0   0   0   0   // Write bit=0 WordAddr bit[3]
   V0364    0   0   0   0   1   0   // SCL↑ (data valid)
   V0365    0   0   0   0   0   0   // SCL↓
   V0366    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0367    0   0   0   0   1   0   // SCL↑ (data valid)
   V0368    0   0   0   0   0   0   // SCL↓
   V0369    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0370    0   0   0   0   1   0   // SCL↑ (data valid)
   V0371    0   0   0   0   0   0   // SCL↓
   V0372    0   0   0   1   0   0   // Write bit=1 WordAddr bit[0]
   V0373    0   0   0   1   1   0   // SCL↑ (data valid)
   V0374    0   0   0   1   0   0   // SCL↓
   V0375    0   0   0   Z   0   0   // ACK after WordAddr
   V0376    0   0   0   L   1   0   // ACK check (expect LOW)
   V0377    0   0   0   X   0   0   // SCL↓
   V0378    0   0   0   1   0   0   // RepSTART: SDA↑
   V0379    0   0   0   1   1   0   // RepSTART: SCL↑
   V0380    0   0   0   0   1   0   // RepSTART: SDA↓
   V0381    0   0   0   0   0   0   // RepSTART: SCL↓
   V0382    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0383    0   0   0   1   1   0   // SCL↑ (data valid)
   V0384    0   0   0   1   0   0   // SCL↓
   V0385    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0386    0   0   0   0   1   0   // SCL↑ (data valid)
   V0387    0   0   0   0   0   0   // SCL↓
   V0388    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0389    0   0   0   1   1   0   // SCL↑ (data valid)
   V0390    0   0   0   1   0   0   // SCL↓
   V0391    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0392    0   0   0   0   1   0   // SCL↑ (data valid)
   V0393    0   0   0   0   0   0   // SCL↓
   V0394    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0395    0   0   0   0   1   0   // SCL↑ (data valid)
   V0396    0   0   0   0   0   0   // SCL↓
   V0397    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0398    0   0   0   0   1   0   // SCL↑ (data valid)
   V0399    0   0   0   0   0   0   // SCL↓
   V0400    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0401    0   0   0   0   1   0   // SCL↑ (data valid)
   V0402    0   0   0   0   0   0   // SCL↓
   V0403    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0404    0   0   0   1   1   0   // SCL↑ (data valid)
   V0405    0   0   0   1   0   0   // SCL↓
   V0406    0   0   0   Z   0   0   // ACK after DevAddr+R
   V0407    0   0   0   L   1   0   // ACK check (expect LOW)
   V0408    0   0   0   X   0   0   // SCL↓
   V0409    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V0410    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0411    0   0   0   X   0   0   // SCL↓
   V0412    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V0413    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0414    0   0   0   X   0   0   // SCL↓
   V0415    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V0416    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0417    0   0   0   X   0   0   // SCL↓
   V0418    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V0419    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0420    0   0   0   X   0   0   // SCL↓
   V0421    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V0422    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0423    0   0   0   X   0   0   // SCL↓
   V0424    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V0425    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0426    0   0   0   X   0   0   // SCL↓
   V0427    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V0428    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0429    0   0   0   X   0   0   // SCL↓
   V0430    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V0431    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0432    0   0   0   X   0   0   // SCL↓
   V0433    0   0   0   1   0   0   // NACK (end read)
   V0434    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V0435    0   0   0   1   0   0   // SCL↓
   V0436    0   0   0   0   0   0   // STOP Setup
   V0437    0   0   0   0   1   0   // STOP (SCL↑)
   V0438    0   0   0   1   1   0   // STOP Condition (SDA↑)
  FUNC_PW_START:
   V0439    0   0   0   1   1   0   // === FUNC: Page Write + Sequential Read ===
   V0440    0   0   0   1   1   0   // === Page Write: addr=0x08 len=8 ===
   V0441    0   0   0   1   1   0 
   V0442    0   0   0   1   1   0   // START Setup
   V0443    0   0   0   0   1   0   // START Condition (SDA↓)
   V0444    0   0   0   0   0   0   // START Hold
   V0445    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0446    0   0   0   1   1   0   // SCL↑ (data valid)
   V0447    0   0   0   1   0   0   // SCL↓
   V0448    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0449    0   0   0   0   1   0   // SCL↑ (data valid)
   V0450    0   0   0   0   0   0   // SCL↓
   V0451    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0452    0   0   0   1   1   0   // SCL↑ (data valid)
   V0453    0   0   0   1   0   0   // SCL↓
   V0454    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0455    0   0   0   0   1   0   // SCL↑ (data valid)
   V0456    0   0   0   0   0   0   // SCL↓
   V0457    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0458    0   0   0   0   1   0   // SCL↑ (data valid)
   V0459    0   0   0   0   0   0   // SCL↓
   V0460    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0461    0   0   0   0   1   0   // SCL↑ (data valid)
   V0462    0   0   0   0   0   0   // SCL↓
   V0463    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0464    0   0   0   0   1   0   // SCL↑ (data valid)
   V0465    0   0   0   0   0   0   // SCL↓
   V0466    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0467    0   0   0   0   1   0   // SCL↑ (data valid)
   V0468    0   0   0   0   0   0   // SCL↓
   V0469    0   0   0   Z   0   0   // ACK after DevAddr
   V0470    0   0   0   L   1   0   // ACK check (expect LOW)
   V0471    0   0   0   X   0   0   // SCL↓
   V0472    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0473    0   0   0   0   1   0   // SCL↑ (data valid)
   V0474    0   0   0   0   0   0   // SCL↓
   V0475    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0476    0   0   0   0   1   0   // SCL↑ (data valid)
   V0477    0   0   0   0   0   0   // SCL↓
   V0478    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0479    0   0   0   0   1   0   // SCL↑ (data valid)
   V0480    0   0   0   0   0   0   // SCL↓
   V0481    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0482    0   0   0   0   1   0   // SCL↑ (data valid)
   V0483    0   0   0   0   0   0   // SCL↓
   V0484    0   0   0   1   0   0   // Write bit=1 WordAddr bit[3]
   V0485    0   0   0   1   1   0   // SCL↑ (data valid)
   V0486    0   0   0   1   0   0   // SCL↓
   V0487    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0488    0   0   0   0   1   0   // SCL↑ (data valid)
   V0489    0   0   0   0   0   0   // SCL↓
   V0490    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0491    0   0   0   0   1   0   // SCL↑ (data valid)
   V0492    0   0   0   0   0   0   // SCL↓
   V0493    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0494    0   0   0   0   1   0   // SCL↑ (data valid)
   V0495    0   0   0   0   0   0   // SCL↓
   V0496    0   0   0   Z   0   0   // ACK after WordAddr
   V0497    0   0   0   L   1   0   // ACK check (expect LOW)
   V0498    0   0   0   X   0   0   // SCL↓
   V0499    0   0   0   0   0   0   // Write bit=0 Data[0] bit[7]
   V0500    0   0   0   0   1   0   // SCL↑ (data valid)
   V0501    0   0   0   0   0   0   // SCL↓
   V0502    0   0   0   0   0   0   // Write bit=0 Data[0] bit[6]
   V0503    0   0   0   0   1   0   // SCL↑ (data valid)
   V0504    0   0   0   0   0   0   // SCL↓
   V0505    0   0   0   0   0   0   // Write bit=0 Data[0] bit[5]
   V0506    0   0   0   0   1   0   // SCL↑ (data valid)
   V0507    0   0   0   0   0   0   // SCL↓
   V0508    0   0   0   0   0   0   // Write bit=0 Data[0] bit[4]
   V0509    0   0   0   0   1   0   // SCL↑ (data valid)
   V0510    0   0   0   0   0   0   // SCL↓
   V0511    0   0   0   0   0   0   // Write bit=0 Data[0] bit[3]
   V0512    0   0   0   0   1   0   // SCL↑ (data valid)
   V0513    0   0   0   0   0   0   // SCL↓
   V0514    0   0   0   0   0   0   // Write bit=0 Data[0] bit[2]
   V0515    0   0   0   0   1   0   // SCL↑ (data valid)
   V0516    0   0   0   0   0   0   // SCL↓
   V0517    0   0   0   0   0   0   // Write bit=0 Data[0] bit[1]
   V0518    0   0   0   0   1   0   // SCL↑ (data valid)
   V0519    0   0   0   0   0   0   // SCL↓
   V0520    0   0   0   1   0   0   // Write bit=1 Data[0] bit[0]
   V0521    0   0   0   1   1   0   // SCL↑ (data valid)
   V0522    0   0   0   1   0   0   // SCL↓
   V0523    0   0   0   Z   0   0   // ACK after Data[0]
   V0524    0   0   0   L   1   0   // ACK check (expect LOW)
   V0525    0   0   0   X   0   0   // SCL↓
   V0526    0   0   0   0   0   0   // Write bit=0 Data[1] bit[7]
   V0527    0   0   0   0   1   0   // SCL↑ (data valid)
   V0528    0   0   0   0   0   0   // SCL↓
   V0529    0   0   0   0   0   0   // Write bit=0 Data[1] bit[6]
   V0530    0   0   0   0   1   0   // SCL↑ (data valid)
   V0531    0   0   0   0   0   0   // SCL↓
   V0532    0   0   0   0   0   0   // Write bit=0 Data[1] bit[5]
   V0533    0   0   0   0   1   0   // SCL↑ (data valid)
   V0534    0   0   0   0   0   0   // SCL↓
   V0535    0   0   0   0   0   0   // Write bit=0 Data[1] bit[4]
   V0536    0   0   0   0   1   0   // SCL↑ (data valid)
   V0537    0   0   0   0   0   0   // SCL↓
   V0538    0   0   0   0   0   0   // Write bit=0 Data[1] bit[3]
   V0539    0   0   0   0   1   0   // SCL↑ (data valid)
   V0540    0   0   0   0   0   0   // SCL↓
   V0541    0   0   0   0   0   0   // Write bit=0 Data[1] bit[2]
   V0542    0   0   0   0   1   0   // SCL↑ (data valid)
   V0543    0   0   0   0   0   0   // SCL↓
   V0544    0   0   0   1   0   0   // Write bit=1 Data[1] bit[1]
   V0545    0   0   0   1   1   0   // SCL↑ (data valid)
   V0546    0   0   0   1   0   0   // SCL↓
   V0547    0   0   0   0   0   0   // Write bit=0 Data[1] bit[0]
   V0548    0   0   0   0   1   0   // SCL↑ (data valid)
   V0549    0   0   0   0   0   0   // SCL↓
   V0550    0   0   0   Z   0   0   // ACK after Data[1]
   V0551    0   0   0   L   1   0   // ACK check (expect LOW)
   V0552    0   0   0   X   0   0   // SCL↓
   V0553    0   0   0   0   0   0   // Write bit=0 Data[2] bit[7]
   V0554    0   0   0   0   1   0   // SCL↑ (data valid)
   V0555    0   0   0   0   0   0   // SCL↓
   V0556    0   0   0   0   0   0   // Write bit=0 Data[2] bit[6]
   V0557    0   0   0   0   1   0   // SCL↑ (data valid)
   V0558    0   0   0   0   0   0   // SCL↓
   V0559    0   0   0   0   0   0   // Write bit=0 Data[2] bit[5]
   V0560    0   0   0   0   1   0   // SCL↑ (data valid)
   V0561    0   0   0   0   0   0   // SCL↓
   V0562    0   0   0   0   0   0   // Write bit=0 Data[2] bit[4]
   V0563    0   0   0   0   1   0   // SCL↑ (data valid)
   V0564    0   0   0   0   0   0   // SCL↓
   V0565    0   0   0   0   0   0   // Write bit=0 Data[2] bit[3]
   V0566    0   0   0   0   1   0   // SCL↑ (data valid)
   V0567    0   0   0   0   0   0   // SCL↓
   V0568    0   0   0   1   0   0   // Write bit=1 Data[2] bit[2]
   V0569    0   0   0   1   1   0   // SCL↑ (data valid)
   V0570    0   0   0   1   0   0   // SCL↓
   V0571    0   0   0   0   0   0   // Write bit=0 Data[2] bit[1]
   V0572    0   0   0   0   1   0   // SCL↑ (data valid)
   V0573    0   0   0   0   0   0   // SCL↓
   V0574    0   0   0   0   0   0   // Write bit=0 Data[2] bit[0]
   V0575    0   0   0   0   1   0   // SCL↑ (data valid)
   V0576    0   0   0   0   0   0   // SCL↓
   V0577    0   0   0   Z   0   0   // ACK after Data[2]
   V0578    0   0   0   L   1   0   // ACK check (expect LOW)
   V0579    0   0   0   X   0   0   // SCL↓
   V0580    0   0   0   0   0   0   // Write bit=0 Data[3] bit[7]
   V0581    0   0   0   0   1   0   // SCL↑ (data valid)
   V0582    0   0   0   0   0   0   // SCL↓
   V0583    0   0   0   0   0   0   // Write bit=0 Data[3] bit[6]
   V0584    0   0   0   0   1   0   // SCL↑ (data valid)
   V0585    0   0   0   0   0   0   // SCL↓
   V0586    0   0   0   0   0   0   // Write bit=0 Data[3] bit[5]
   V0587    0   0   0   0   1   0   // SCL↑ (data valid)
   V0588    0   0   0   0   0   0   // SCL↓
   V0589    0   0   0   0   0   0   // Write bit=0 Data[3] bit[4]
   V0590    0   0   0   0   1   0   // SCL↑ (data valid)
   V0591    0   0   0   0   0   0   // SCL↓
   V0592    0   0   0   1   0   0   // Write bit=1 Data[3] bit[3]
   V0593    0   0   0   1   1   0   // SCL↑ (data valid)
   V0594    0   0   0   1   0   0   // SCL↓
   V0595    0   0   0   0   0   0   // Write bit=0 Data[3] bit[2]
   V0596    0   0   0   0   1   0   // SCL↑ (data valid)
   V0597    0   0   0   0   0   0   // SCL↓
   V0598    0   0   0   0   0   0   // Write bit=0 Data[3] bit[1]
   V0599    0   0   0   0   1   0   // SCL↑ (data valid)
   V0600    0   0   0   0   0   0   // SCL↓
   V0601    0   0   0   0   0   0   // Write bit=0 Data[3] bit[0]
   V0602    0   0   0   0   1   0   // SCL↑ (data valid)
   V0603    0   0   0   0   0   0   // SCL↓
   V0604    0   0   0   Z   0   0   // ACK after Data[3]
   V0605    0   0   0   L   1   0   // ACK check (expect LOW)
   V0606    0   0   0   X   0   0   // SCL↓
   V0607    0   0   0   0   0   0   // Write bit=0 Data[4] bit[7]
   V0608    0   0   0   0   1   0   // SCL↑ (data valid)
   V0609    0   0   0   0   0   0   // SCL↓
   V0610    0   0   0   0   0   0   // Write bit=0 Data[4] bit[6]
   V0611    0   0   0   0   1   0   // SCL↑ (data valid)
   V0612    0   0   0   0   0   0   // SCL↓
   V0613    0   0   0   0   0   0   // Write bit=0 Data[4] bit[5]
   V0614    0   0   0   0   1   0   // SCL↑ (data valid)
   V0615    0   0   0   0   0   0   // SCL↓
   V0616    0   0   0   1   0   0   // Write bit=1 Data[4] bit[4]
   V0617    0   0   0   1   1   0   // SCL↑ (data valid)
   V0618    0   0   0   1   0   0   // SCL↓
   V0619    0   0   0   0   0   0   // Write bit=0 Data[4] bit[3]
   V0620    0   0   0   0   1   0   // SCL↑ (data valid)
   V0621    0   0   0   0   0   0   // SCL↓
   V0622    0   0   0   0   0   0   // Write bit=0 Data[4] bit[2]
   V0623    0   0   0   0   1   0   // SCL↑ (data valid)
   V0624    0   0   0   0   0   0   // SCL↓
   V0625    0   0   0   0   0   0   // Write bit=0 Data[4] bit[1]
   V0626    0   0   0   0   1   0   // SCL↑ (data valid)
   V0627    0   0   0   0   0   0   // SCL↓
   V0628    0   0   0   0   0   0   // Write bit=0 Data[4] bit[0]
   V0629    0   0   0   0   1   0   // SCL↑ (data valid)
   V0630    0   0   0   0   0   0   // SCL↓
   V0631    0   0   0   Z   0   0   // ACK after Data[4]
   V0632    0   0   0   L   1   0   // ACK check (expect LOW)
   V0633    0   0   0   X   0   0   // SCL↓
   V0634    0   0   0   0   0   0   // Write bit=0 Data[5] bit[7]
   V0635    0   0   0   0   1   0   // SCL↑ (data valid)
   V0636    0   0   0   0   0   0   // SCL↓
   V0637    0   0   0   0   0   0   // Write bit=0 Data[5] bit[6]
   V0638    0   0   0   0   1   0   // SCL↑ (data valid)
   V0639    0   0   0   0   0   0   // SCL↓
   V0640    0   0   0   1   0   0   // Write bit=1 Data[5] bit[5]
   V0641    0   0   0   1   1   0   // SCL↑ (data valid)
   V0642    0   0   0   1   0   0   // SCL↓
   V0643    0   0   0   0   0   0   // Write bit=0 Data[5] bit[4]
   V0644    0   0   0   0   1   0   // SCL↑ (data valid)
   V0645    0   0   0   0   0   0   // SCL↓
   V0646    0   0   0   0   0   0   // Write bit=0 Data[5] bit[3]
   V0647    0   0   0   0   1   0   // SCL↑ (data valid)
   V0648    0   0   0   0   0   0   // SCL↓
   V0649    0   0   0   0   0   0   // Write bit=0 Data[5] bit[2]
   V0650    0   0   0   0   1   0   // SCL↑ (data valid)
   V0651    0   0   0   0   0   0   // SCL↓
   V0652    0   0   0   0   0   0   // Write bit=0 Data[5] bit[1]
   V0653    0   0   0   0   1   0   // SCL↑ (data valid)
   V0654    0   0   0   0   0   0   // SCL↓
   V0655    0   0   0   0   0   0   // Write bit=0 Data[5] bit[0]
   V0656    0   0   0   0   1   0   // SCL↑ (data valid)
   V0657    0   0   0   0   0   0   // SCL↓
   V0658    0   0   0   Z   0   0   // ACK after Data[5]
   V0659    0   0   0   L   1   0   // ACK check (expect LOW)
   V0660    0   0   0   X   0   0   // SCL↓
   V0661    0   0   0   0   0   0   // Write bit=0 Data[6] bit[7]
   V0662    0   0   0   0   1   0   // SCL↑ (data valid)
   V0663    0   0   0   0   0   0   // SCL↓
   V0664    0   0   0   1   0   0   // Write bit=1 Data[6] bit[6]
   V0665    0   0   0   1   1   0   // SCL↑ (data valid)
   V0666    0   0   0   1   0   0   // SCL↓
   V0667    0   0   0   0   0   0   // Write bit=0 Data[6] bit[5]
   V0668    0   0   0   0   1   0   // SCL↑ (data valid)
   V0669    0   0   0   0   0   0   // SCL↓
   V0670    0   0   0   0   0   0   // Write bit=0 Data[6] bit[4]
   V0671    0   0   0   0   1   0   // SCL↑ (data valid)
   V0672    0   0   0   0   0   0   // SCL↓
   V0673    0   0   0   0   0   0   // Write bit=0 Data[6] bit[3]
   V0674    0   0   0   0   1   0   // SCL↑ (data valid)
   V0675    0   0   0   0   0   0   // SCL↓
   V0676    0   0   0   0   0   0   // Write bit=0 Data[6] bit[2]
   V0677    0   0   0   0   1   0   // SCL↑ (data valid)
   V0678    0   0   0   0   0   0   // SCL↓
   V0679    0   0   0   0   0   0   // Write bit=0 Data[6] bit[1]
   V0680    0   0   0   0   1   0   // SCL↑ (data valid)
   V0681    0   0   0   0   0   0   // SCL↓
   V0682    0   0   0   0   0   0   // Write bit=0 Data[6] bit[0]
   V0683    0   0   0   0   1   0   // SCL↑ (data valid)
   V0684    0   0   0   0   0   0   // SCL↓
   V0685    0   0   0   Z   0   0   // ACK after Data[6]
   V0686    0   0   0   L   1   0   // ACK check (expect LOW)
   V0687    0   0   0   X   0   0   // SCL↓
   V0688    0   0   0   1   0   0   // Write bit=1 Data[7] bit[7]
   V0689    0   0   0   1   1   0   // SCL↑ (data valid)
   V0690    0   0   0   1   0   0   // SCL↓
   V0691    0   0   0   0   0   0   // Write bit=0 Data[7] bit[6]
   V0692    0   0   0   0   1   0   // SCL↑ (data valid)
   V0693    0   0   0   0   0   0   // SCL↓
   V0694    0   0   0   0   0   0   // Write bit=0 Data[7] bit[5]
   V0695    0   0   0   0   1   0   // SCL↑ (data valid)
   V0696    0   0   0   0   0   0   // SCL↓
   V0697    0   0   0   0   0   0   // Write bit=0 Data[7] bit[4]
   V0698    0   0   0   0   1   0   // SCL↑ (data valid)
   V0699    0   0   0   0   0   0   // SCL↓
   V0700    0   0   0   0   0   0   // Write bit=0 Data[7] bit[3]
   V0701    0   0   0   0   1   0   // SCL↑ (data valid)
   V0702    0   0   0   0   0   0   // SCL↓
   V0703    0   0   0   0   0   0   // Write bit=0 Data[7] bit[2]
   V0704    0   0   0   0   1   0   // SCL↑ (data valid)
   V0705    0   0   0   0   0   0   // SCL↓
   V0706    0   0   0   0   0   0   // Write bit=0 Data[7] bit[1]
   V0707    0   0   0   0   1   0   // SCL↑ (data valid)
   V0708    0   0   0   0   0   0   // SCL↓
   V0709    0   0   0   0   0   0   // Write bit=0 Data[7] bit[0]
   V0710    0   0   0   0   1   0   // SCL↑ (data valid)
   V0711    0   0   0   0   0   0   // SCL↓
   V0712    0   0   0   Z   0   0   // ACK after Data[7]
   V0713    0   0   0   L   1   0   // ACK check (expect LOW)
   V0714    0   0   0   X   0   0   // SCL↓
   V0715    0   0   0   0   0   0   // STOP Setup
   V0716    0   0   0   0   1   0   // STOP (SCL↑)
   V0717    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V0718    0   0   0   1   1   0   // Write cycle wait (tWR)
   V0719    0   0   0   1   1   0 
   V0720    0   0   0   1   1   0 
   V0721    0   0   0   1   1   0 
   V0722    0   0   0   1   1   0 
   V0723    0   0   0   1   1   0 
   V0724    0   0   0   1   1   0 
   V0725    0   0   0   1   1   0 
   V0726    0   0   0   1   1   0 
   V0727    0   0   0   1   1   0 
   V0728    0   0   0   1   1   0   // === Sequential Read: addr=0x08 count=8 ===
   V0729    0   0   0   1   1   0 
   V0730    0   0   0   1   1   0   // START Setup
   V0731    0   0   0   0   1   0   // START Condition (SDA↓)
   V0732    0   0   0   0   0   0   // START Hold
   V0733    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V0734    0   0   0   1   1   0   // SCL↑ (data valid)
   V0735    0   0   0   1   0   0   // SCL↓
   V0736    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V0737    0   0   0   0   1   0   // SCL↑ (data valid)
   V0738    0   0   0   0   0   0   // SCL↓
   V0739    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V0740    0   0   0   1   1   0   // SCL↑ (data valid)
   V0741    0   0   0   1   0   0   // SCL↓
   V0742    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V0743    0   0   0   0   1   0   // SCL↑ (data valid)
   V0744    0   0   0   0   0   0   // SCL↓
   V0745    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V0746    0   0   0   0   1   0   // SCL↑ (data valid)
   V0747    0   0   0   0   0   0   // SCL↓
   V0748    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V0749    0   0   0   0   1   0   // SCL↑ (data valid)
   V0750    0   0   0   0   0   0   // SCL↓
   V0751    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V0752    0   0   0   0   1   0   // SCL↑ (data valid)
   V0753    0   0   0   0   0   0   // SCL↓
   V0754    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V0755    0   0   0   0   1   0   // SCL↑ (data valid)
   V0756    0   0   0   0   0   0   // SCL↓
   V0757    0   0   0   Z   0   0   // ACK from slave
   V0758    0   0   0   L   1   0   // ACK check (expect LOW)
   V0759    0   0   0   X   0   0   // SCL↓
   V0760    0   0   0   0   0   0   // Write bit=0 WordAddr bit[7]
   V0761    0   0   0   0   1   0   // SCL↑ (data valid)
   V0762    0   0   0   0   0   0   // SCL↓
   V0763    0   0   0   0   0   0   // Write bit=0 WordAddr bit[6]
   V0764    0   0   0   0   1   0   // SCL↑ (data valid)
   V0765    0   0   0   0   0   0   // SCL↓
   V0766    0   0   0   0   0   0   // Write bit=0 WordAddr bit[5]
   V0767    0   0   0   0   1   0   // SCL↑ (data valid)
   V0768    0   0   0   0   0   0   // SCL↓
   V0769    0   0   0   0   0   0   // Write bit=0 WordAddr bit[4]
   V0770    0   0   0   0   1   0   // SCL↑ (data valid)
   V0771    0   0   0   0   0   0   // SCL↓
   V0772    0   0   0   1   0   0   // Write bit=1 WordAddr bit[3]
   V0773    0   0   0   1   1   0   // SCL↑ (data valid)
   V0774    0   0   0   1   0   0   // SCL↓
   V0775    0   0   0   0   0   0   // Write bit=0 WordAddr bit[2]
   V0776    0   0   0   0   1   0   // SCL↑ (data valid)
   V0777    0   0   0   0   0   0   // SCL↓
   V0778    0   0   0   0   0   0   // Write bit=0 WordAddr bit[1]
   V0779    0   0   0   0   1   0   // SCL↑ (data valid)
   V0780    0   0   0   0   0   0   // SCL↓
   V0781    0   0   0   0   0   0   // Write bit=0 WordAddr bit[0]
   V0782    0   0   0   0   1   0   // SCL↑ (data valid)
   V0783    0   0   0   0   0   0   // SCL↓
   V0784    0   0   0   Z   0   0   // ACK from slave
   V0785    0   0   0   L   1   0   // ACK check (expect LOW)
   V0786    0   0   0   X   0   0   // SCL↓
   V0787    0   0   0   1   0   0   // RepSTART: SDA↑
   V0788    0   0   0   1   1   0   // RepSTART: SCL↑
   V0789    0   0   0   0   1   0   // RepSTART: SDA↓
   V0790    0   0   0   0   0   0   // RepSTART: SCL↓
   V0791    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V0792    0   0   0   1   1   0   // SCL↑ (data valid)
   V0793    0   0   0   1   0   0   // SCL↓
   V0794    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V0795    0   0   0   0   1   0   // SCL↑ (data valid)
   V0796    0   0   0   0   0   0   // SCL↓
   V0797    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V0798    0   0   0   1   1   0   // SCL↑ (data valid)
   V0799    0   0   0   1   0   0   // SCL↓
   V0800    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V0801    0   0   0   0   1   0   // SCL↑ (data valid)
   V0802    0   0   0   0   0   0   // SCL↓
   V0803    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V0804    0   0   0   0   1   0   // SCL↑ (data valid)
   V0805    0   0   0   0   0   0   // SCL↓
   V0806    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V0807    0   0   0   0   1   0   // SCL↑ (data valid)
   V0808    0   0   0   0   0   0   // SCL↓
   V0809    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V0810    0   0   0   0   1   0   // SCL↑ (data valid)
   V0811    0   0   0   0   0   0   // SCL↓
   V0812    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V0813    0   0   0   1   1   0   // SCL↑ (data valid)
   V0814    0   0   0   1   0   0   // SCL↓
   V0815    0   0   0   Z   0   0   // ACK from slave
   V0816    0   0   0   L   1   0   // ACK check (expect LOW)
   V0817    0   0   0   X   0   0   // SCL↓
   V0818    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[7]
   V0819    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0820    0   0   0   X   0   0   // SCL↓
   V0821    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[6]
   V0822    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0823    0   0   0   X   0   0   // SCL↓
   V0824    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[5]
   V0825    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0826    0   0   0   X   0   0   // SCL↓
   V0827    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[4]
   V0828    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0829    0   0   0   X   0   0   // SCL↓
   V0830    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[3]
   V0831    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0832    0   0   0   X   0   0   // SCL↓
   V0833    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[2]
   V0834    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0835    0   0   0   X   0   0   // SCL↓
   V0836    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[1]
   V0837    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0838    0   0   0   X   0   0   // SCL↓
   V0839    0   0   0   Z   0   0   // Read bit SeqRead[0] bit[0]
   V0840    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0841    0   0   0   X   0   0   // SCL↓
   V0842    0   0   0   0   0   0   // ACK (continue read 0)
   V0843    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0844    0   0   0   0   0   0   // SCL↓
   V0845    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[7]
   V0846    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0847    0   0   0   X   0   0   // SCL↓
   V0848    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[6]
   V0849    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0850    0   0   0   X   0   0   // SCL↓
   V0851    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[5]
   V0852    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0853    0   0   0   X   0   0   // SCL↓
   V0854    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[4]
   V0855    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0856    0   0   0   X   0   0   // SCL↓
   V0857    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[3]
   V0858    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0859    0   0   0   X   0   0   // SCL↓
   V0860    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[2]
   V0861    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0862    0   0   0   X   0   0   // SCL↓
   V0863    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[1]
   V0864    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0865    0   0   0   X   0   0   // SCL↓
   V0866    0   0   0   Z   0   0   // Read bit SeqRead[1] bit[0]
   V0867    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0868    0   0   0   X   0   0   // SCL↓
   V0869    0   0   0   0   0   0   // ACK (continue read 1)
   V0870    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0871    0   0   0   0   0   0   // SCL↓
   V0872    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[7]
   V0873    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0874    0   0   0   X   0   0   // SCL↓
   V0875    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[6]
   V0876    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0877    0   0   0   X   0   0   // SCL↓
   V0878    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[5]
   V0879    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0880    0   0   0   X   0   0   // SCL↓
   V0881    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[4]
   V0882    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0883    0   0   0   X   0   0   // SCL↓
   V0884    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[3]
   V0885    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0886    0   0   0   X   0   0   // SCL↓
   V0887    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[2]
   V0888    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0889    0   0   0   X   0   0   // SCL↓
   V0890    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[1]
   V0891    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0892    0   0   0   X   0   0   // SCL↓
   V0893    0   0   0   Z   0   0   // Read bit SeqRead[2] bit[0]
   V0894    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0895    0   0   0   X   0   0   // SCL↓
   V0896    0   0   0   0   0   0   // ACK (continue read 2)
   V0897    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0898    0   0   0   0   0   0   // SCL↓
   V0899    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[7]
   V0900    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0901    0   0   0   X   0   0   // SCL↓
   V0902    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[6]
   V0903    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0904    0   0   0   X   0   0   // SCL↓
   V0905    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[5]
   V0906    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0907    0   0   0   X   0   0   // SCL↓
   V0908    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[4]
   V0909    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0910    0   0   0   X   0   0   // SCL↓
   V0911    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[3]
   V0912    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0913    0   0   0   X   0   0   // SCL↓
   V0914    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[2]
   V0915    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0916    0   0   0   X   0   0   // SCL↓
   V0917    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[1]
   V0918    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0919    0   0   0   X   0   0   // SCL↓
   V0920    0   0   0   Z   0   0   // Read bit SeqRead[3] bit[0]
   V0921    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0922    0   0   0   X   0   0   // SCL↓
   V0923    0   0   0   0   0   0   // ACK (continue read 3)
   V0924    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0925    0   0   0   0   0   0   // SCL↓
   V0926    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[7]
   V0927    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0928    0   0   0   X   0   0   // SCL↓
   V0929    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[6]
   V0930    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0931    0   0   0   X   0   0   // SCL↓
   V0932    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[5]
   V0933    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0934    0   0   0   X   0   0   // SCL↓
   V0935    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[4]
   V0936    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0937    0   0   0   X   0   0   // SCL↓
   V0938    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[3]
   V0939    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0940    0   0   0   X   0   0   // SCL↓
   V0941    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[2]
   V0942    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0943    0   0   0   X   0   0   // SCL↓
   V0944    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[1]
   V0945    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0946    0   0   0   X   0   0   // SCL↓
   V0947    0   0   0   Z   0   0   // Read bit SeqRead[4] bit[0]
   V0948    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0949    0   0   0   X   0   0   // SCL↓
   V0950    0   0   0   0   0   0   // ACK (continue read 4)
   V0951    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0952    0   0   0   0   0   0   // SCL↓
   V0953    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[7]
   V0954    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0955    0   0   0   X   0   0   // SCL↓
   V0956    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[6]
   V0957    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0958    0   0   0   X   0   0   // SCL↓
   V0959    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[5]
   V0960    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0961    0   0   0   X   0   0   // SCL↓
   V0962    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[4]
   V0963    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0964    0   0   0   X   0   0   // SCL↓
   V0965    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[3]
   V0966    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0967    0   0   0   X   0   0   // SCL↓
   V0968    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[2]
   V0969    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0970    0   0   0   X   0   0   // SCL↓
   V0971    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[1]
   V0972    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0973    0   0   0   X   0   0   // SCL↓
   V0974    0   0   0   Z   0   0   // Read bit SeqRead[5] bit[0]
   V0975    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0976    0   0   0   X   0   0   // SCL↓
   V0977    0   0   0   0   0   0   // ACK (continue read 5)
   V0978    0   0   0   0   1   0   // ACK (SDA=LOW)
   V0979    0   0   0   0   0   0   // SCL↓
   V0980    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[7]
   V0981    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0982    0   0   0   X   0   0   // SCL↓
   V0983    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[6]
   V0984    0   0   0   H   1   0   // SCL↑ (compare=H)
   V0985    0   0   0   X   0   0   // SCL↓
   V0986    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[5]
   V0987    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0988    0   0   0   X   0   0   // SCL↓
   V0989    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[4]
   V0990    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0991    0   0   0   X   0   0   // SCL↓
   V0992    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[3]
   V0993    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0994    0   0   0   X   0   0   // SCL↓
   V0995    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[2]
   V0996    0   0   0   L   1   0   // SCL↑ (compare=L)
   V0997    0   0   0   X   0   0   // SCL↓
   V0998    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[1]
   V0999    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1000    0   0   0   X   0   0   // SCL↓
   V1001    0   0   0   Z   0   0   // Read bit SeqRead[6] bit[0]
   V1002    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1003    0   0   0   X   0   0   // SCL↓
   V1004    0   0   0   0   0   0   // ACK (continue read 6)
   V1005    0   0   0   0   1   0   // ACK (SDA=LOW)
   V1006    0   0   0   0   0   0   // SCL↓
   V1007    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[7]
   V1008    0   0   0   H   1   0   // SCL↑ (compare=H)
   V1009    0   0   0   X   0   0   // SCL↓
   V1010    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[6]
   V1011    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1012    0   0   0   X   0   0   // SCL↓
   V1013    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[5]
   V1014    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1015    0   0   0   X   0   0   // SCL↓
   V1016    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[4]
   V1017    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1018    0   0   0   X   0   0   // SCL↓
   V1019    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[3]
   V1020    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1021    0   0   0   X   0   0   // SCL↓
   V1022    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[2]
   V1023    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1024    0   0   0   X   0   0   // SCL↓
   V1025    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[1]
   V1026    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1027    0   0   0   X   0   0   // SCL↓
   V1028    0   0   0   Z   0   0   // Read bit SeqRead[7] bit[0]
   V1029    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1030    0   0   0   X   0   0   // SCL↓
   V1031    0   0   0   1   0   0   // NACK (end sequential read)
   V1032    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V1033    0   0   0   1   0   0   // SCL↓
   V1034    0   0   0   0   0   0   // STOP Setup
   V1035    0   0   0   0   1   0   // STOP (SCL↑)
   V1036    0   0   0   1   1   0   // STOP Condition (SDA↑)
  FUNC_BOUND_START:
   V1037    0   0   0   1   1   0   // === FUNC: Address Boundary Test ===
   V1038    0   0   0   1   1   0   // === Byte Write: addr=0xFF data=0x42 ===
   V1039    0   0   0   1   1   0 
   V1040    0   0   0   1   1   0   // START Setup
   V1041    0   0   0   0   1   0   // START Condition (SDA↓)
   V1042    0   0   0   0   0   0   // START Hold
   V1043    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V1044    0   0   0   1   1   0   // SCL↑ (data valid)
   V1045    0   0   0   1   0   0   // SCL↓
   V1046    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V1047    0   0   0   0   1   0   // SCL↑ (data valid)
   V1048    0   0   0   0   0   0   // SCL↓
   V1049    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V1050    0   0   0   1   1   0   // SCL↑ (data valid)
   V1051    0   0   0   1   0   0   // SCL↓
   V1052    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V1053    0   0   0   0   1   0   // SCL↑ (data valid)
   V1054    0   0   0   0   0   0   // SCL↓
   V1055    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V1056    0   0   0   0   1   0   // SCL↑ (data valid)
   V1057    0   0   0   0   0   0   // SCL↓
   V1058    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V1059    0   0   0   0   1   0   // SCL↑ (data valid)
   V1060    0   0   0   0   0   0   // SCL↓
   V1061    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V1062    0   0   0   0   1   0   // SCL↑ (data valid)
   V1063    0   0   0   0   0   0   // SCL↓
   V1064    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V1065    0   0   0   0   1   0   // SCL↑ (data valid)
   V1066    0   0   0   0   0   0   // SCL↓
   V1067    0   0   0   Z   0   0   // ACK after DevAddr
   V1068    0   0   0   L   1   0   // ACK check (expect LOW)
   V1069    0   0   0   X   0   0   // SCL↓
   V1070    0   0   0   1   0   0   // Write bit=1 WordAddr bit[7]
   V1071    0   0   0   1   1   0   // SCL↑ (data valid)
   V1072    0   0   0   1   0   0   // SCL↓
   V1073    0   0   0   1   0   0   // Write bit=1 WordAddr bit[6]
   V1074    0   0   0   1   1   0   // SCL↑ (data valid)
   V1075    0   0   0   1   0   0   // SCL↓
   V1076    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V1077    0   0   0   1   1   0   // SCL↑ (data valid)
   V1078    0   0   0   1   0   0   // SCL↓
   V1079    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V1080    0   0   0   1   1   0   // SCL↑ (data valid)
   V1081    0   0   0   1   0   0   // SCL↓
   V1082    0   0   0   1   0   0   // Write bit=1 WordAddr bit[3]
   V1083    0   0   0   1   1   0   // SCL↑ (data valid)
   V1084    0   0   0   1   0   0   // SCL↓
   V1085    0   0   0   1   0   0   // Write bit=1 WordAddr bit[2]
   V1086    0   0   0   1   1   0   // SCL↑ (data valid)
   V1087    0   0   0   1   0   0   // SCL↓
   V1088    0   0   0   1   0   0   // Write bit=1 WordAddr bit[1]
   V1089    0   0   0   1   1   0   // SCL↑ (data valid)
   V1090    0   0   0   1   0   0   // SCL↓
   V1091    0   0   0   1   0   0   // Write bit=1 WordAddr bit[0]
   V1092    0   0   0   1   1   0   // SCL↑ (data valid)
   V1093    0   0   0   1   0   0   // SCL↓
   V1094    0   0   0   Z   0   0   // ACK after WordAddr
   V1095    0   0   0   L   1   0   // ACK check (expect LOW)
   V1096    0   0   0   X   0   0   // SCL↓
   V1097    0   0   0   0   0   0   // Write bit=0 Data bit[7]
   V1098    0   0   0   0   1   0   // SCL↑ (data valid)
   V1099    0   0   0   0   0   0   // SCL↓
   V1100    0   0   0   1   0   0   // Write bit=1 Data bit[6]
   V1101    0   0   0   1   1   0   // SCL↑ (data valid)
   V1102    0   0   0   1   0   0   // SCL↓
   V1103    0   0   0   0   0   0   // Write bit=0 Data bit[5]
   V1104    0   0   0   0   1   0   // SCL↑ (data valid)
   V1105    0   0   0   0   0   0   // SCL↓
   V1106    0   0   0   0   0   0   // Write bit=0 Data bit[4]
   V1107    0   0   0   0   1   0   // SCL↑ (data valid)
   V1108    0   0   0   0   0   0   // SCL↓
   V1109    0   0   0   0   0   0   // Write bit=0 Data bit[3]
   V1110    0   0   0   0   1   0   // SCL↑ (data valid)
   V1111    0   0   0   0   0   0   // SCL↓
   V1112    0   0   0   0   0   0   // Write bit=0 Data bit[2]
   V1113    0   0   0   0   1   0   // SCL↑ (data valid)
   V1114    0   0   0   0   0   0   // SCL↓
   V1115    0   0   0   1   0   0   // Write bit=1 Data bit[1]
   V1116    0   0   0   1   1   0   // SCL↑ (data valid)
   V1117    0   0   0   1   0   0   // SCL↓
   V1118    0   0   0   0   0   0   // Write bit=0 Data bit[0]
   V1119    0   0   0   0   1   0   // SCL↑ (data valid)
   V1120    0   0   0   0   0   0   // SCL↓
   V1121    0   0   0   Z   0   0   // ACK after Data
   V1122    0   0   0   L   1   0   // ACK check (expect LOW)
   V1123    0   0   0   X   0   0   // SCL↓
   V1124    0   0   0   0   0   0   // STOP Setup
   V1125    0   0   0   0   1   0   // STOP (SCL↑)
   V1126    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V1127    0   0   0   1   1   0   // Write cycle wait (tWR)
   V1128    0   0   0   1   1   0 
   V1129    0   0   0   1   1   0 
   V1130    0   0   0   1   1   0 
   V1131    0   0   0   1   1   0 
   V1132    0   0   0   1   1   0 
   V1133    0   0   0   1   1   0 
   V1134    0   0   0   1   1   0 
   V1135    0   0   0   1   1   0 
   V1136    0   0   0   1   1   0 
   V1137    0   0   0   1   1   0   // === Random Read: addr=0xFF ===
   V1138    0   0   0   1   1   0 
   V1139    0   0   0   1   1   0   // START Setup
   V1140    0   0   0   0   1   0   // START Condition (SDA↓)
   V1141    0   0   0   0   0   0   // START Hold
   V1142    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[7]
   V1143    0   0   0   1   1   0   // SCL↑ (data valid)
   V1144    0   0   0   1   0   0   // SCL↓
   V1145    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[6]
   V1146    0   0   0   0   1   0   // SCL↑ (data valid)
   V1147    0   0   0   0   0   0   // SCL↓
   V1148    0   0   0   1   0   0   // Write bit=1 DevAddr+W bit[5]
   V1149    0   0   0   1   1   0   // SCL↑ (data valid)
   V1150    0   0   0   1   0   0   // SCL↓
   V1151    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[4]
   V1152    0   0   0   0   1   0   // SCL↑ (data valid)
   V1153    0   0   0   0   0   0   // SCL↓
   V1154    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[3]
   V1155    0   0   0   0   1   0   // SCL↑ (data valid)
   V1156    0   0   0   0   0   0   // SCL↓
   V1157    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[2]
   V1158    0   0   0   0   1   0   // SCL↑ (data valid)
   V1159    0   0   0   0   0   0   // SCL↓
   V1160    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[1]
   V1161    0   0   0   0   1   0   // SCL↑ (data valid)
   V1162    0   0   0   0   0   0   // SCL↓
   V1163    0   0   0   0   0   0   // Write bit=0 DevAddr+W bit[0]
   V1164    0   0   0   0   1   0   // SCL↑ (data valid)
   V1165    0   0   0   0   0   0   // SCL↓
   V1166    0   0   0   Z   0   0   // ACK after DevAddr
   V1167    0   0   0   L   1   0   // ACK check (expect LOW)
   V1168    0   0   0   X   0   0   // SCL↓
   V1169    0   0   0   1   0   0   // Write bit=1 WordAddr bit[7]
   V1170    0   0   0   1   1   0   // SCL↑ (data valid)
   V1171    0   0   0   1   0   0   // SCL↓
   V1172    0   0   0   1   0   0   // Write bit=1 WordAddr bit[6]
   V1173    0   0   0   1   1   0   // SCL↑ (data valid)
   V1174    0   0   0   1   0   0   // SCL↓
   V1175    0   0   0   1   0   0   // Write bit=1 WordAddr bit[5]
   V1176    0   0   0   1   1   0   // SCL↑ (data valid)
   V1177    0   0   0   1   0   0   // SCL↓
   V1178    0   0   0   1   0   0   // Write bit=1 WordAddr bit[4]
   V1179    0   0   0   1   1   0   // SCL↑ (data valid)
   V1180    0   0   0   1   0   0   // SCL↓
   V1181    0   0   0   1   0   0   // Write bit=1 WordAddr bit[3]
   V1182    0   0   0   1   1   0   // SCL↑ (data valid)
   V1183    0   0   0   1   0   0   // SCL↓
   V1184    0   0   0   1   0   0   // Write bit=1 WordAddr bit[2]
   V1185    0   0   0   1   1   0   // SCL↑ (data valid)
   V1186    0   0   0   1   0   0   // SCL↓
   V1187    0   0   0   1   0   0   // Write bit=1 WordAddr bit[1]
   V1188    0   0   0   1   1   0   // SCL↑ (data valid)
   V1189    0   0   0   1   0   0   // SCL↓
   V1190    0   0   0   1   0   0   // Write bit=1 WordAddr bit[0]
   V1191    0   0   0   1   1   0   // SCL↑ (data valid)
   V1192    0   0   0   1   0   0   // SCL↓
   V1193    0   0   0   Z   0   0   // ACK after WordAddr
   V1194    0   0   0   L   1   0   // ACK check (expect LOW)
   V1195    0   0   0   X   0   0   // SCL↓
   V1196    0   0   0   1   0   0   // RepSTART: SDA↑
   V1197    0   0   0   1   1   0   // RepSTART: SCL↑
   V1198    0   0   0   0   1   0   // RepSTART: SDA↓
   V1199    0   0   0   0   0   0   // RepSTART: SCL↓
   V1200    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[7]
   V1201    0   0   0   1   1   0   // SCL↑ (data valid)
   V1202    0   0   0   1   0   0   // SCL↓
   V1203    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[6]
   V1204    0   0   0   0   1   0   // SCL↑ (data valid)
   V1205    0   0   0   0   0   0   // SCL↓
   V1206    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[5]
   V1207    0   0   0   1   1   0   // SCL↑ (data valid)
   V1208    0   0   0   1   0   0   // SCL↓
   V1209    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[4]
   V1210    0   0   0   0   1   0   // SCL↑ (data valid)
   V1211    0   0   0   0   0   0   // SCL↓
   V1212    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[3]
   V1213    0   0   0   0   1   0   // SCL↑ (data valid)
   V1214    0   0   0   0   0   0   // SCL↓
   V1215    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[2]
   V1216    0   0   0   0   1   0   // SCL↑ (data valid)
   V1217    0   0   0   0   0   0   // SCL↓
   V1218    0   0   0   0   0   0   // Write bit=0 DevAddr+R bit[1]
   V1219    0   0   0   0   1   0   // SCL↑ (data valid)
   V1220    0   0   0   0   0   0   // SCL↓
   V1221    0   0   0   1   0   0   // Write bit=1 DevAddr+R bit[0]
   V1222    0   0   0   1   1   0   // SCL↑ (data valid)
   V1223    0   0   0   1   0   0   // SCL↓
   V1224    0   0   0   Z   0   0   // ACK after DevAddr+R
   V1225    0   0   0   L   1   0   // ACK check (expect LOW)
   V1226    0   0   0   X   0   0   // SCL↓
   V1227    0   0   0   Z   0   0   // Read bit ReadData bit[7]
   V1228    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1229    0   0   0   X   0   0   // SCL↓
   V1230    0   0   0   Z   0   0   // Read bit ReadData bit[6]
   V1231    0   0   0   H   1   0   // SCL↑ (compare=H)
   V1232    0   0   0   X   0   0   // SCL↓
   V1233    0   0   0   Z   0   0   // Read bit ReadData bit[5]
   V1234    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1235    0   0   0   X   0   0   // SCL↓
   V1236    0   0   0   Z   0   0   // Read bit ReadData bit[4]
   V1237    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1238    0   0   0   X   0   0   // SCL↓
   V1239    0   0   0   Z   0   0   // Read bit ReadData bit[3]
   V1240    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1241    0   0   0   X   0   0   // SCL↓
   V1242    0   0   0   Z   0   0   // Read bit ReadData bit[2]
   V1243    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1244    0   0   0   X   0   0   // SCL↓
   V1245    0   0   0   Z   0   0   // Read bit ReadData bit[1]
   V1246    0   0   0   H   1   0   // SCL↑ (compare=H)
   V1247    0   0   0   X   0   0   // SCL↓
   V1248    0   0   0   Z   0   0   // Read bit ReadData bit[0]
   V1249    0   0   0   L   1   0   // SCL↑ (compare=L)
   V1250    0   0   0   X   0   0   // SCL↓
   V1251    0   0   0   1   0   0   // NACK (end read)
   V1252    0   0   0   1   1   0   // NACK (SDA=HIGH)
   V1253    0   0   0   1   0   0   // SCL↓
   V1254    0   0   0   0   0   0   // STOP Setup
   V1255    0   0   0   0   1   0   // STOP (SCL↑)
   V1256    0   0   0   1   1   0   // STOP Condition (SDA↑)
   V1257    0   0   0   1   1   0   // === Functional Test Complete ===
   V1258    0   0   0   1   1   0 
   V1259    0   0   0   1   1   0 
   V1260    0   0   0   1   1   0 

END_PATTERN // FUNC_TEST
